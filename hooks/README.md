# Plugin Hooks

This directory contains opt-in lifecycle hooks for the securable engineering plugin. Both hooks are **off by default** and do nothing unless you set the corresponding environment variable to `1`.

## Hooks

### 1. Session Kernel Injection (`SessionStart`)

**Script:** `hooks/scripts/session_kernel.sh`
**Env var:** `SECURABLE_KERNEL_HOOK=1`

When enabled, prints the securability kernel (`core/kernel.md`) into the session context at startup, so the five securable engineering rules are always visible to the agent without consuming a skill slot.

### 2. Post-Edit Opengrep Held Checks (`PostToolUse: Edit|Write|MultiEdit`)

**Script:** `hooks/scripts/post_edit_opengrep.sh`
**Env var:** `SECURABLE_HELD_CHECKS=1`

When enabled, runs the plugin's opengrep rule pack against each edited file (Python, JavaScript, TypeScript) after every Edit, Write, or MultiEdit tool use. Prints a one-line summary per finding (rule id, line, message).

**Requirements:**
- `opengrep` must already be installed and on PATH. If absent, the hook silently does nothing. **Nothing is ever installed by this hook** (see Tooling Policy in AGENTS.md).
- `python3` is used to parse opengrep JSON output. If absent, a fallback notice is printed.

This hook is strictly advisory: it always exits 0 and never blocks the tool action.

## Enabling

Set the environment variables before starting your Claude Code session:

```bash
export SECURABLE_KERNEL_HOOK=1
export SECURABLE_HELD_CHECKS=1
```

Or in your project's `.claude/settings.json`:

```json
{
  "env": {
    "SECURABLE_KERNEL_HOOK": "1",
    "SECURABLE_HELD_CHECKS": "1"
  }
}
```

## Disabling

Unset the environment variables or set them to any value other than `1`. The hooks will exit immediately without output.

## Design Principles

- **Opt-in only** — both hooks require explicit environment variables.
- **Nothing is installed** — hooks use only tools already present on the system.
- **Advisory, never blocking** — hooks always exit 0; findings are informational.
- **POSIX sh compatible** — scripts work with any POSIX-compliant shell.
