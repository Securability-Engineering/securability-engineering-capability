---
description: Triage scanner or tool findings through the FIASSE/SSEM securability lens
argument-hint: "[SARIF/JSON/text findings file(s)] [--scope <diff or paths>]"
---

Run the **securability-triage** skill against: $ARGUMENTS

If no target is given, look for findings files in the current project.

Load and follow the skill at `${CLAUDE_PLUGIN_ROOT}/skills/securability-triage/SKILL.md` (in a repo checkout: `skills/securability-triage/SKILL.md`). That file is authoritative for the triage procedure, severity re-classification criteria, and output format — do not restate or improvise a different procedure here.
