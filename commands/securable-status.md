---
description: Show the status of the project's .securable/ contract (requirements and boundaries)
argument-hint: "[--json] [--changed-files <paths or @file>] [--fail-on-unverified-touched]"
allowed-tools: Bash(python3 *)
---

Run the **securable-status** script against: $ARGUMENTS

The script is at `${CLAUDE_PLUGIN_ROOT}/scripts/securable_status.py` (in a repo checkout: `scripts/securable_status.py`). Build the Bash invocation yourself from the recognized flags below — do not splice user text directly into the shell command.

**Recognized flags** (pass only these to the script):

| Flag | Value | Purpose |
|------|-------|---------|
| `--dir` | directory path | Contract directory (default `.securable`) |
| `--json` | *(none)* | Machine-readable JSON output |
| `--changed-files` | comma-separated paths or `@file` | Report which boundaries are touched |
| `--fail-on-unverified-touched` | *(none)* | Exit 1 if touched boundaries have unverified requirements |

Construct the command by parsing the user's request, selecting only recognized flags and quoting any path values. Always include `--dir .securable` unless the user specifies a different directory. Ignore anything that is not a recognized flag.

If the script is not found, say so and show the path that was tried. If PyYAML is not installed, say so. Never install dependencies (tooling policy tier 1).

Summarize the output for the user.
