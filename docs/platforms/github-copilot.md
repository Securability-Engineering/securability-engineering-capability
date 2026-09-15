# Securable Engineering on GitHub Copilot

GitHub Copilot (VS Code agent mode, Copilot CLI, and the GitHub.com coding agent) supports custom instructions, custom agents, and prompt files. This guide covers installing the securable engineering skill pack and its persona bindings for Copilot.

## 1. What this pack gives you on GitHub Copilot

| Layer | Feature | Copilot support |
|-------|---------|-----------------|
| Always-on | Securability kernel | **Generated binding** — `bindings/copilot/copilot-instructions.md` placed at `.github/copilot-instructions.md` |
| Skills | 11 SKILL.md procedures | **Manual** — Copilot does not natively discover `SKILL.md` files; reference them via `@` syntax in instructions or agent prompts |
| Commands / prompts | 12 slash commands | **Manual** — create `.github/prompts/<name>.prompt.md` wrappers, or use `@` references in agent prompts |
| Personas | 10 agent personas | **Generated binding** — `bindings/copilot/agents/*.agent.md` placed at `.github/agents/` |
| Hooks | Session kernel injection, post-edit held checks | **Not available** — Copilot does not expose lifecycle hooks; run opengrep in CI instead |
| Merge-time report | Securability Report via `scripts/securability_report.sh` | **Manual** — see section 8 |

## 2. Install

### Option A: layout-preserving installer (recommended)

Clone the plugin repository and run the installer into a location Copilot's `@` syntax can reach:

```bash
git clone --depth 1 https://github.com/Securability-Engineering/securable-claude-plugin.git /tmp/securable-plugin

# Install the skills tree into the project
/tmp/securable-plugin/scripts/install_skills.sh --target .agents

# Copy the generated Copilot bindings
cp /tmp/securable-plugin/bindings/copilot/copilot-instructions.md .github/copilot-instructions.md
mkdir -p .github/agents
cp /tmp/securable-plugin/bindings/copilot/agents/*.agent.md .github/agents/

rm -rf /tmp/securable-plugin
```

### Option B: AGENTS.md discovery

Copilot CLI discovers and reads `AGENTS.md` in the repository root, current working directory, and intermediate directories. It supports the `@` file-reference syntax inside `AGENTS.md`. If the repository already has an `AGENTS.md` that imports the skill pack (or is this repository itself), Copilot picks up the kernel and skill references automatically. The generated `bindings/copilot/copilot-instructions.md` provides a more targeted Copilot-native alternative.

### Where files land

| File | Destination | Scope |
|------|-------------|-------|
| `bindings/copilot/copilot-instructions.md` | `.github/copilot-instructions.md` | Repository-wide, always-on |
| `bindings/copilot/agents/*.agent.md` | `.github/agents/` | Project-level custom agents |
| Skills tree (via installer) | `.agents/skills/`, `.agents/data/`, etc. | Referenced by `@` paths in agent prompts |

User-level equivalents can be placed under `~/.copilot/` (`copilot-instructions.md` for always-on, `agents/` for agents). The environment variable `COPILOT_HOME` overrides the base directory, and `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` adds comma-separated additional instruction directories.

## 3. Always-on kernel

The securability kernel (~300 tokens) is pre-generated at:

    bindings/copilot/copilot-instructions.md

Copy it to `.github/copilot-instructions.md`. This file requires no YAML frontmatter. Its contents are automatically included in every Copilot interaction for the repository.

If you already have a `.github/copilot-instructions.md`, append the kernel contents or use the `@` syntax to reference the installed copy:

```markdown
@.agents/core/kernel.md
```

The kernel is generated from `core/kernel.md` by `scripts/build_bindings.py`. Never edit the generated file directly; rebuild with:

```bash
python3 scripts/build_bindings.py
```

## 4. Skills

Copilot does not natively discover `SKILL.md` files from a skills directory. The eleven skills ship under `.agents/skills/` after installation:

- `securability-engineering-review`
- `securability-engineering`
- `prd-securability-enhancement`
- `fiasse-lookup`
- `threat-modeling`
- `dependency-stewardship`
- `securability-triage`
- `securability-remediation`
- `securability-verification`
- `securability-postmortem`
- `fiasse-adoption`

To make a skill available to Copilot, reference it in an agent prompt body or an instruction file using the `@` syntax:

```markdown
Follow the procedure in @.agents/skills/securability-engineering-review/SKILL.md
```

**Verify** by prompting Copilot:

> Review this file for securability using the SSEM model.

The agent should load the referenced skill and produce a scored report.

## 5. Commands and prompt equivalents

The pack ships twelve slash commands (under `commands/`). Copilot's native equivalent is **prompt files** stored in `.github/prompts/`. Each `.prompt.md` file has YAML frontmatter (`description`, optional `agent`, `tools`, `model`) and a Markdown body, invoked by typing `/` followed by the filename in VS Code chat.

To expose a command as a Copilot prompt file, create a wrapper that delegates to the skill. Example for the securability review:

```markdown
---
description: 'Run a FIASSE/SSEM securability review on the current codebase'
agent: 'agent'
tools:
  - read
  - search
  - execute
---

Follow the procedure in @.agents/skills/securability-engineering-review/SKILL.md
against the files in the current workspace. Produce the three-part report.
```

Save as `.github/prompts/securability-review.prompt.md` and invoke with `/securability-review` in VS Code chat.

The twelve commands available for wrapping:

`securability-review` `secure-generate` `prd-securability-enhance` `fiasse-lookup` `threat-model` `dependency-steward` `securability-triage` `securability-remediate` `securability-verify` `securable-status` `securability-postmortem` `fiasse-adoption`

## 6. Personas

Ten persona bindings are pre-generated at `bindings/copilot/agents/` in Copilot's native `.agent.md` format with the correct frontmatter (`description`, `tools`, optional `model`). Each persona's Markdown body contains the full system prompt, tool restrictions, loaded skills, and behavioural constraints.

### Generated agent files

| Persona | File | Layer |
|---------|------|-------|
| Requirements Partner | `bindings/copilot/agents/requirements-partner.agent.md` | L1 |
| Boundary Mapper | `bindings/copilot/agents/boundary-mapper.agent.md` | L1 |
| Securable Builder | `bindings/copilot/agents/securable-builder.agent.md` | L2 |
| Dependency Steward | `bindings/copilot/agents/dependency-steward.agent.md` | L2 |
| Merge Steward | `bindings/copilot/agents/merge-steward.agent.md` | L3 |
| Triage Analyst | `bindings/copilot/agents/triage-analyst.agent.md` | L3 |
| Remediation Engineer | `bindings/copilot/agents/remediation-engineer.agent.md` | L3 |
| Verification Engineer | `bindings/copilot/agents/verification-engineer.agent.md` | L4 |
| Incident Learner | `bindings/copilot/agents/incident-learner.agent.md` | L5 |
| Adoption Coach | `bindings/copilot/agents/adoption-coach.agent.md` | Program |

Copy them to `.github/agents/` (or `~/.copilot/agents/` for user-level availability).

### Invoking personas

Copilot custom agents can be invoked four ways:

1. **`/agent` command** in VS Code chat to list and select interactively.
2. **`--agent` CLI flag**: `copilot --agent merge-steward`.
3. **Mention by name** in a prompt for inference-based selection.
4. **Automatic delegation** when `disable-model-invocation` is false (the default) and the task matches the agent's description.

Example invocations by persona group:

```
# Review persona (read-only advisors)
copilot --agent merge-steward "Review the diff on this branch for securability"

# Builder persona (writes code)
copilot --agent securable-builder "Implement the password-reset endpoint against the contract"

# Requirements persona
copilot --agent requirements-partner "Enhance this PRD with ASVS L2 coverage"
```

### Tool restrictions

Each generated agent binding restricts the `tools` field to what the persona's design allows. For example, `merge-steward` has `read`, `search`, `execute`, and `edit` — though its prompt constrains writes to persisted reports only, never application code. `securable-builder` has the same tool set but its prompt permits editing application code and tests.

### Generic fallback

If the Copilot agent format changes or a field is not recognised, the harness-neutral persona prompts at `bindings/generic/agents/<name>.md` can be pasted into any agent configuration as a system prompt.

## 7. Hooks and held checks

Copilot does not expose lifecycle hooks (pre-edit, post-edit, session-start). The pack's two opt-in hooks (`session_kernel.sh` for kernel injection, `post_edit_opengrep.sh` for held checks) are not directly usable.

**CI alternative**: run the opengrep rule pack in your CI pipeline against changed files. The rules live under `rules/opengrep/` in the installed tree. Example GitHub Actions step:

```yaml
- name: Opengrep held checks
  run: |
    opengrep scan --config .agents/rules/opengrep/ --target .
```

Opengrep must be provisioned by the consumer's CI workflow. This pack never installs it.

## 8. Merge-time Securability Report

`scripts/securability_report.sh` generates a FIASSE v1.1 S5.2.1 Securability Report by piping a diff and the review skill into a non-interactive agent CLI. Copilot CLI's non-interactive mode is not verified against vendor documentation at the time of writing. If a non-interactive invocation is available, set `AGENT_CLI` accordingly:

```bash
AGENT_CLI="copilot-cli-command" scripts/securability_report.sh --base origin/main
```

Otherwise, invoke the merge-steward persona on the diff:

```bash
copilot --agent merge-steward "Review the diff between origin/main and HEAD for securability"
```

Or run the script with another agent CLI the team already has (`claude`, `opencode run`, etc.):

```bash
AGENT_CLI="claude -p --output-format text" scripts/securability_report.sh
```

## 9. Tooling policy reminder

This pack never installs runtime tooling into a consumer's project. Skills, personas, and instructions use only the tools already present. If opengrep is absent, the held-check step reports that absence rather than implying verification. CI provisioning (opengrep, agent CLIs, linters) is the consumer's explicit decision. See the Tooling Policy section in `AGENTS.md`.

## 10. Limitations and unverified items

1. **No native SKILL.md discovery** — Copilot does not auto-discover skills from a directory. Skills must be referenced explicitly via `@` syntax in instructions or agent prompts.
2. **Copilot CLI non-interactive mode** — whether Copilot CLI supports a non-interactive mode suitable for `AGENT_CLI` in `scripts/securability_report.sh` is not verified against vendor documentation at the time of writing.
3. **Agent prompt length** — Copilot agent prompts have a maximum length of 30,000 characters. The generated persona prompts fit within this limit; if you append additional instructions, verify the total stays under the cap.
4. **Tool allowlists are held, path restrictions are promised** — Copilot respects the `tools` field in agent frontmatter, but file-path write restrictions stated in a persona's prompt body are conventions the model follows, not enforced boundaries.
5. **Hook support** — Copilot has no lifecycle hook mechanism. The pack's `SessionStart` and `PostToolUse` hooks are not usable.
6. **`excludeAgent` frontmatter field** — the `.instructions.md` `excludeAgent` field is not verified against vendor documentation at the time of writing.
7. **IDE-only fields** — `handoffs`, `argument-hint` (on agents), and `model` are IDE-only (VS Code, JetBrains); they are ignored by the GitHub.com cloud agent and may behave differently in Copilot CLI.
