---
description: Show the status of the project's .securable/ contract (requirements and boundaries)
argument-hint: "[--summary|--coverage|--gaps|--json] [paths]"
allowed-tools: Bash(python3 *)
---

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/securable_status.py --dir .securable $ARGUMENTS` (in a repo checkout: `python3 scripts/securable_status.py --dir .securable $ARGUMENTS`).

If the script is not found, say so and show the path that was tried. If PyYAML is not installed, say so. Never install dependencies (tooling policy tier 1).

Summarize the output for the user.
