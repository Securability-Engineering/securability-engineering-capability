#!/bin/sh
# Post-edit opengrep held-check hook (PostToolUse: Edit|Write|MultiEdit).
# Opt-in: fires only when SECURABLE_HELD_CHECKS=1 AND opengrep is installed.
# Advisory only — always exits 0, never blocks (S5.2.2).
# No installs, no network, no writes. POSIX sh compatible.
set -eu

# Read the hook JSON from stdin into a variable (PostToolUse pipes it).
HOOK_JSON="$(cat)"

# Gate: opt-in env var
if [ "${SECURABLE_HELD_CHECKS:-0}" != "1" ]; then
  exit 0
fi

# Gate: opengrep must already be installed
if ! command -v opengrep >/dev/null 2>&1; then
  exit 0
fi

# Extract the file path from the hook JSON.
# PostToolUse provides tool_input.file_path for Edit/Write/MultiEdit.
FILE_PATH=""
if command -v python3 >/dev/null 2>&1; then
  FILE_PATH="$(printf '%s' "$HOOK_JSON" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    fp = d.get("tool_input", {}).get("file_path", "")
    print(fp)
except Exception:
    pass
' 2>/dev/null)" || true
fi

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# Gate: only run on file extensions the rule pack covers (py, js, ts).
case "$FILE_PATH" in
  *.py|*.js|*.ts) ;;
  *) exit 0 ;;
esac

RULES="${CLAUDE_PLUGIN_ROOT}/rules/opengrep/securable.yaml"
if [ ! -f "$RULES" ]; then
  exit 0
fi

# Run opengrep with a timeout (advisory — never block).
OG_OUTPUT=""
OG_OUTPUT="$(timeout 30 opengrep scan --config "$RULES" --json "$FILE_PATH" 2>/dev/null)" || true

if [ -z "$OG_OUTPUT" ]; then
  exit 0
fi

# Parse and summarize hits.
if command -v python3 >/dev/null 2>&1; then
  printf '%s' "$OG_OUTPUT" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    results = data.get("results", [])
    if not results:
        sys.exit(0)
    print("opengrep held-check hits:")
    for r in results:
        rule_id = r.get("check_id", "unknown")
        line = r.get("start", {}).get("line", "?")
        msg = r.get("extra", {}).get("message", "")
        print(f"  {rule_id} (line {line}): {msg}")
except Exception:
    pass
' 2>/dev/null || echo "opengrep: findings present but summary could not be parsed"
else
  echo "opengrep: findings present but summary could not be parsed (python3 not available)"
fi

exit 0
