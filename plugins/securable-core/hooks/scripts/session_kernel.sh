#!/bin/sh
# Securable kernel injection hook (SessionStart).
# Opt-in: fires only when SECURABLE_KERNEL_HOOK=1.
# Prints the kernel body (core/kernel.md minus the leading HTML comment)
# so Claude Code merges it as session context.
# No network, no writes, no installs. POSIX sh compatible.
set -eu

if [ "${SECURABLE_KERNEL_HOOK:-0}" != "1" ]; then
  exit 0
fi

kernel="${CLAUDE_PLUGIN_ROOT}/core/kernel.md"

if [ ! -f "$kernel" ]; then
  exit 0
fi

# Strip the leading HTML comment (<!-- ... -->) and any blank lines after it,
# then print the rest.
awk '
  BEGIN { in_comment = 0; past_comment = 0 }
  !past_comment && /^<!--/  { in_comment = 1 }
  in_comment && /-->/ { in_comment = 0; next }
  in_comment { next }
  !past_comment && /^[[:space:]]*$/ { next }
  { past_comment = 1; print }
' "$kernel"
