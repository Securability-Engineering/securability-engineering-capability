---
description: Remediate a securability finding with FIASSE/SSEM-aligned fixes
argument-hint: "[finding id or description] [--scope <files or PR>]"
---

Run the **securability-remediation** skill against: $ARGUMENTS

If no target is given, look for outstanding findings in the current project.

Load and follow the skill at `${CLAUDE_PLUGIN_ROOT}/skills/securability-remediation/SKILL.md` (in a repo checkout: `skills/securability-remediation/SKILL.md`). That file is authoritative for the remediation procedure, fix-quality criteria, and verification steps — do not restate or improvise a different procedure here.
