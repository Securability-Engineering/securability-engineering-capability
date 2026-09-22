---
description: Produce or refine a threat model using FIASSE/SSEM securability analysis
argument-hint: "[design doc, PRD, code path, or 'escalation: <finding>']"
---

Run the **threat-modeling** skill against: $ARGUMENTS

If no target is given, threat-model the current project's architecture.

Load and follow the skill at `${CLAUDE_PLUGIN_ROOT}/skills/threat-modeling/SKILL.md` (in a repo checkout: `skills/threat-modeling/SKILL.md`). That file is authoritative for the threat-modeling procedure, boundary identification, and output format — do not restate or improvise a different procedure here.
