---
description: Verify securability controls — tests, config, release gates, or requirement flips
argument-hint: "[--tests|--config|--release <range>|--flip] [paths]"
---

Run the **securability-verification** skill against: $ARGUMENTS

If no target is given, verify securability controls in the current project.

Load and follow the skill at `${CLAUDE_PLUGIN_ROOT}/skills/securability-verification/SKILL.md` (in a repo checkout: `skills/securability-verification/SKILL.md`). That file is authoritative for the verification procedure, pass/fail criteria, and output format — do not restate or improvise a different procedure here.
