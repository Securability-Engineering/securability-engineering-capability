# Devin

Platform guide for using the Securable Engineering skill pack with [Devin](https://devin.ai).

## What this pack gives you on Devin

| Capability | Status |
|---|---|
| Kernel (always-on) | Native — `AGENTS.md` at bundle root loaded automatically |
| Skills (11) | Native — `skills/` directories listed in `plugin.json` `skills` array |
| Commands / prompts | Manual — no native slash-command system; use Playbooks or paste skill invocation prompts |
| Personas (10) | Not verified — `agents/<name>.md` subagent format is not verified against vendor documentation at the time of writing; generic fallback available |
| Hooks | Partial — `hooks.json` is part of the Devin plugin bundle format, but the specific hook types supported and their equivalence to Claude Code's `SessionStart` / `PostToolUse` are not verified against vendor documentation at the time of writing |
| Merge-time report | Manual — run the merge-steward persona on the diff, or use `scripts/securability_report.sh` in CI |

## Install

Install the plugin bundle from the repository:

```
devin plugins install Securability-Engineering/securable-claude-plugin
```

Alternatively, install from a local clone or a Git URL:

```
devin plugins install ./securability-engineering-capability
devin plugins install https://github.com/Securability-Engineering/securable-claude-plugin.git
```

The plugin manifest lives at `.devin-plugin/plugin.json`. Devin discovers it there first, falling back to `.claude-plugin/plugin.json` and then a root `plugin.json`.

After installation, the following are available inside the plugin bundle:

| Path | Purpose |
|---|---|
| `AGENTS.md` | Always-on securability kernel and skill index |
| `skills/*/SKILL.md` | Eleven skill definitions |
| `data/asvs/`, `data/fiasse/` | ASVS 5.0 and FIASSE v1.1 reference data |
| `plays/` | Multi-skill runbooks |
| `templates/` | Output format templates |

## Always-on kernel

The securability kernel is the ~300-token distillation of the five core securable engineering rules. On Devin, it loads automatically from `AGENTS.md` at the plugin bundle root. Every prompt in the session sees it.

You can also add the kernel content to Devin's **Knowledge** feature (configured via the Devin web UI) so it persists across sessions and outside of plugin context.

No generated binding file is needed for Devin: `AGENTS.md` is the native always-on format for plugin bundles.

## Skills

All eleven skills ship inside the plugin bundle under `skills/`:

- `securability-engineering-review` — Score code against the ten SSEM attributes
- `securability-engineering` — Generate code with FIASSE/SSEM constraints
- `prd-securability-enhancement` — Enhance PRDs with ASVS 5.0 coverage
- `fiasse-lookup` — Answer FIASSE/SSEM questions from bundled reference
- `threat-modeling` — Map trust boundaries and threat scenarios
- `securability-triage` — Triage scanner output into actionable findings
- `securability-remediation` — Fix confirmed findings with review-ready patches
- `securability-verification` — Verify implemented requirements with executed evidence
- `securability-postmortem` — Derive lessons and corrective requirements from incidents
- `dependency-stewardship` — Manage the relationship with third-party code
- `fiasse-adoption` — Assess and plan organizational FIASSE adoption

Skills are listed in the `skills` array of `.devin-plugin/plugin.json` and are discovered automatically. Devin's skill system supports `model` and `agent` fields in SKILL.md frontmatter, allowing skills to specify their preferred model.

**Verify the install** by asking Devin:

> Review the securability of `src/auth/login.py` using the FIASSE/SSEM framework.

Devin should activate the `securability-engineering-review` skill and produce a ten-attribute scored report.

## Commands or prompt equivalents

The pack ships twelve slash commands under `commands/` for Claude Code. Devin does not have a native user-defined slash-command system. The equivalent approaches on Devin are:

1. **Playbooks** — Create Playbooks in the Devin web UI that invoke the corresponding skill by name. For example, a "Securability Review" Playbook could contain the prompt: "Run the securability-engineering-review skill against the current diff."

2. **Direct prompts** — Ask Devin directly using the skill's trigger language. The commands and their prompt equivalents:

| Command | Prompt equivalent |
|---|---|
| `/securability-review` | "Review the securability of [target]" |
| `/secure-generate` | "Generate securable code for [component]" |
| `/prd-securability-enhance` | "Enhance the PRD at [path] with ASVS coverage" |
| `/fiasse-lookup` | "What does FIASSE say about [topic]?" |
| `/threat-model` | "Map the trust boundaries in [scope]" |
| `/securability-triage` | "Triage the scanner output at [path]" |
| `/securability-remediate` | "Fix the confirmed finding [id] in [file]" |
| `/securability-verify` | "Verify the implemented requirement [id]" |
| `/securability-postmortem` | "Run a postmortem on [incident description]" |
| `/dependency-steward` | "Assess the dependency [name] for stewardship" |
| `/fiasse-adoption` | "Assess our FIASSE adoption readiness" |
| `/securable-status` | "Show the securable contract status" |

> **Note**: Playbooks are not verified against vendor documentation at the time of writing. The description here is based on publicly available product announcements.

## Personas

The pack defines ten task-scoped personas under `agents/`:

- **requirements-partner** (L1) — Security teammate in refinement
- **boundary-mapper** (L1) — Trust boundary and threat mapping
- **securable-builder** (L2) — Pair programmer with securability constraints
- **dependency-steward** (L2) — Third-party code relationship management
- **merge-steward** (L3) — Advisory Securability Report at merge time
- **triage-analyst** (L3) — Scanner output triage
- **remediation-engineer** (L3) — Fix confirmed findings
- **verification-engineer** (L4) — Verify implemented requirements with evidence
- **incident-learner** (L5) — Postmortem lessons fed back to requirements
- **adoption-coach** (Program) — Organizational FIASSE adoption

### Native agent format (not verified)

Devin's plugin system is reported to support subagent definitions as `agents/<name>.md` files with frontmatter fields including `name`, `description`, `model`, `allowed-tools`, and `max-nesting`, invoked as `<plugin>:<name>`. However, this format is **not verified against vendor documentation at the time of writing**, and plugin subagents may be limited to local Devin agents (CLI and Desktop) rather than cloud sessions.

If Devin's native subagent format works in your environment, the personas in `agents/` should be discovered automatically after plugin installation.

### Generic fallback

If the native agent format does not work or you are using Devin in a mode that does not support plugin subagents, use the generic persona bindings:

```
bindings/generic/agents/<name>.md
```

Each file contains the full persona system prompt. Paste it into Devin's Knowledge or into your session context to activate a persona. The available generic bindings are:

- `bindings/generic/agents/adoption-coach.md`
- `bindings/generic/agents/boundary-mapper.md`
- `bindings/generic/agents/dependency-steward.md`
- `bindings/generic/agents/incident-learner.md`
- `bindings/generic/agents/merge-steward.md`
- `bindings/generic/agents/remediation-engineer.md`
- `bindings/generic/agents/requirements-partner.md`
- `bindings/generic/agents/securable-builder.md`
- `bindings/generic/agents/triage-analyst.md`
- `bindings/generic/agents/verification-engineer.md`

### Example invocations

**Requirements and design (L1):**

> Using the requirements-partner persona, enhance the PRD at `docs/prd.md` with ASVS Level 2 coverage for our authentication features.

**Build and review (L2-L3):**

> As securable-builder, implement the session management endpoint from the acceptance criteria in `.securable/requirements.yaml`.

**Verification and operations (L4-L5):**

> As verification-engineer, write boundary contract tests for the requirements marked `implemented` in `.securable/requirements.yaml`.

## Hooks and held checks

The Devin plugin bundle format includes `hooks.json` for lifecycle hooks, but the specific hook types supported (and whether they cover session-start or post-edit events equivalent to Claude Code's `SessionStart` / `PostToolUse`) are not verified against vendor documentation at the time of writing. The pack's two opt-in hooks (session kernel injection and post-edit opengrep held checks) have not been adapted for Devin's hook format.

**Manual equivalent for held checks**: run opengrep with the pack's rule file in CI:

```bash
opengrep scan --config rules/opengrep/securable.yaml --json <target_files>
```

This requires `opengrep` to be provisioned in your CI environment. The plugin never installs it.

## Merge-time Securability Report

The `scripts/securability_report.sh` script produces a FIASSE v1.1 S5.2.1 Securability Report for a diff. It requires a non-interactive agent CLI set via the `AGENT_CLI` environment variable.

Devin does not have a verified non-interactive CLI mode suitable for use as `AGENT_CLI`. Instead:

1. **In a Devin session**: ask the merge-steward persona to review the current diff directly. It will produce an advisory Securability Report with a score block, escalations, and requirement verdicts.

2. **In CI** (outside Devin): use the script with another agent CLI that has a non-interactive mode:

```bash
AGENT_CLI="claude -p --output-format text" scripts/securability_report.sh --base origin/main
```

The report is advisory (S5.2.2): it directs attention but never blocks a merge. Gating on it is a separate, explicit policy decision (S5.2.3).

## Tooling policy reminder

Nothing is installed at runtime. Skills, personas, and hooks use only tools already present in the environment. When a check cannot run because tooling is absent (e.g. `opengrep` is not on PATH), the result says so rather than implying verification happened. That absence is itself evidence (Testability / Observability).

CI provisioning (opengrep, agent CLI, language runtimes) is the consumer's explicit decision. The pack's example CI workflows mark provisioning steps as yours to replace with whatever your team already runs.

## Limitations and unverified items

1. **Subagent persona format not verified** — The `agents/<name>.md` frontmatter fields (`name`, `description`, `model`, `allowed-tools`, `max-nesting`) and the `<plugin>:<name>` invocation pattern are not verified against vendor documentation at the time of writing. Use the generic fallback under `bindings/generic/agents/` if the native format does not work.

2. **Playbooks not verified** — Devin Playbooks (step-by-step workflow documents configured via the web UI) are referenced as a command equivalent but are not verified against vendor documentation at the time of writing.

3. **Plugin subagents may be local-only** — Reports indicate that plugin subagents currently load in local Devin agents only (CLI and Desktop), not cloud sessions. This is not verified.

4. **Hook support not verified** — The Devin plugin bundle format includes `hooks.json` for lifecycle hooks, but the specific hook types supported and their equivalence to Claude Code's session-start and post-edit hooks are not verified against vendor documentation at the time of writing. The pack's kernel injection and held-check hooks have not been adapted for Devin's hook format.

5. **No non-interactive CLI mode verified** — `scripts/securability_report.sh` cannot be used with Devin as `AGENT_CLI` because no non-interactive invocation mode has been verified.

6. **Knowledge persistence** — While Knowledge is verified as a feature for sharing documentation and conventions, the exact steps for adding multi-file pack content to Knowledge are not detailed here; consult Devin's current documentation.
