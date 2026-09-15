# Claude Code

Platform guide for the Securable Engineering skill pack on **Claude Code** (plugin install and repo-as-project).

---

## 1. What this pack gives you on Claude Code

| Layer | Feature | How it ships |
|-------|---------|-------------|
| Always-on kernel | Securability rules injected every session | **Native** — `SessionStart` hook prints `core/kernel.md` when `SECURABLE_KERNEL_HOOK=1` |
| Skills (11) | Review, generation, PRD enhancement, triage, remediation, verification, postmortem, threat modeling, dependency stewardship, FIASSE adoption, FIASSE lookup | **Native** — `skills/<name>/SKILL.md` |
| Commands (12) | Slash commands (`/securability-review`, `/secure-generate`, etc.) | **Native** — `commands/*.md` |
| Personas (10) | Subagent definitions with tool allowlists, model hints, fixed outputs | **Native** — `agents/*.md` |
| Hooks | Session kernel injection, post-edit opengrep held checks | **Native** — `hooks/hooks.json` merged when plugin enabled |
| Merge-time report | Advisory Securability Report | **Native** — `scripts/securability_report.sh` with `claude -p --output-format text` |

## 2. Install

### Plugin install (recommended)

Open the interactive plugin manager with `/plugin`, then use the Discover and Marketplaces tabs to add and install graphically. Or from the command line within a Claude Code session:

```
/plugin marketplace add Securability-Engineering/securable-claude-plugin
/plugin install securable-claude-plugin@securable-claude-plugins
```

Files land at `<plugin-root>/`: `.claude-plugin/plugin.json` (manifest), `skills/` (11 skills), `commands/` (12 slash commands), `agents/` (10 personas), `hooks/` (lifecycle hooks and scripts), `data/asvs/` (ASVS 5.0 V1-V17), `data/fiasse/` (FIASSE v1.1 sections), `core/kernel.md`, `plays/`, `templates/`, `scripts/`.

### Repo-as-project (for plugin development)

```bash
git clone https://github.com/Securability-Engineering/securable-claude-plugin.git
cd securable-claude-plugin
claude --plugin-dir .
```

This loads commands, skills, agents, and hooks exactly as a plugin install would. Paths inside skills resolve via `${CLAUDE_PLUGIN_ROOT}`.

## 3. Always-on kernel

The securability kernel (`core/kernel.md`) contains five non-negotiable rules: parse don't trust, authority is server-side, never-emit list, observable security, securability notes.

**Injection.** The plugin ships a `SessionStart` hook that prints the kernel into session context. Opt in:

```bash
export SECURABLE_KERNEL_HOOK=1
```

Or in `.claude/settings.json`: `{ "env": { "SECURABLE_KERNEL_HOOK": "1" } }`

The hook (`hooks/scripts/session_kernel.sh`) always exits 0 and is advisory only. When the variable is unset or not `1`, it exits immediately without output. The hook uses `type: command` (not `mcp_tool`, which is unavailable at `SessionStart` because MCP servers have not started yet).

## 4. Skills

Skills are discovered from `skills/<name>/SKILL.md`. Plugin skills are namespaced `/securable-claude-plugin:<skill-name>`.

The eleven skills: `securability-engineering-review`, `securability-engineering`, `prd-securability-enhancement`, `fiasse-lookup`, `threat-modeling`, `securability-triage`, `securability-remediation`, `securability-verification`, `securability-postmortem`, `dependency-stewardship`, `fiasse-adoption`.

**Invocation.** Claude auto-invokes based on `description` and `when_to_use` frontmatter (capped at 1536 characters combined). Users invoke explicitly with `/<skill-name>` or `/securable-claude-plugin:<skill-name>`.

**Verify the install:**

```
/securable-claude-plugin:fiasse-lookup What is Canonical Parsing?
```

Expected: a response citing FIASSE S4.4.1.1 from `data/fiasse/`.

## 5. Commands

Twelve slash commands in `commands/`: `/securability-review`, `/secure-generate`, `/prd-securability-enhance`, `/fiasse-lookup`, `/threat-model`, `/securability-triage`, `/securability-remediate`, `/securability-verify`, `/securability-postmortem`, `/dependency-steward`, `/fiasse-adoption`, `/securable-status`.

Each command delegates to its corresponding skill; commands hold no procedure content of their own. Commands and skills share the same frontmatter fields.

## 6. Personas

Ten subagent personas in `agents/`, discovered natively by Claude Code.

| Persona | Layer | FIASSE role |
|---------|-------|-------------|
| requirements-partner | L1 | Security teammate in refinement (S4.1.2, S5.3, S7.1) |
| boundary-mapper | L1 | Threats follow data (S4.2.2, S4.3) |
| securable-builder | L2 | Pair programmer for securable code (S4.4, S2.6, S2.7) |
| dependency-steward | L2 | Ongoing relationship with third-party code (S4.5, S4.6) |
| merge-steward | L3 | Advisory Securability Report (S5.2.1-S5.2.5) |
| triage-analyst | L3 | Actionable Security Intelligence (S6.3) |
| remediation-engineer | L3 | Fix half of triage: one root cause, one patch (S6) |
| verification-engineer | L4 | Verified means checked; Testability made real (S3.2.1.3) |
| incident-learner | L5 | Lessons fed back upstream (S8.2.2) |
| adoption-coach | Program | Organizational FIASSE adoption (S8, S7.1.4) |

**Invocation methods** (all native):

1. **Automatic delegation** — Claude selects based on the task and `description` field.
2. **Natural language** — name the persona in a prompt.
3. **@-mention** — `@agent-merge-steward` (or `@agent-securable-claude-plugin:merge-steward`) for guaranteed invocation.
4. **Session-wide** — `claude --agent merge-steward` makes it the default.

**Example invocations:**

```
# L1 — Requirements and architecture
@agent-requirements-partner Harden the auth spec in docs/auth-prd.md to ASVS L2

# L2 — Build
@agent-securable-builder Implement the file-upload endpoint from the acceptance criteria

# L3 — Review and fix
@agent-merge-steward Review the diff on this branch
@agent-triage-analyst Triage the SARIF output in reports/sast-results.sarif

# L4/L5 — Verify and learn
@agent-verification-engineer Generate boundary contract tests for the auth requirements
@agent-incident-learner Postmortem the credential-leak incident from last Tuesday
```

**Model tiering.** Smaller model tolerated: `dependency-steward`, `adoption-coach`. Strongest model recommended: `merge-steward`, `triage-analyst`, `securable-builder`, `incident-learner`. Set per-agent via the `model` frontmatter field (aliases: `sonnet`, `opus`, `haiku`, `fable`, `inherit`; or full model IDs).

**Subagent nesting.** This pack's personas do not spawn subagents. Orchestration (e.g., merge-steward wanting triage) is a handoff recommendation the main session executes.

## 7. Hooks and held checks

Two hooks in `hooks/hooks.json`, both opt-in via environment variables.

**Session kernel injection** (`SessionStart`) — prints the kernel into context at startup. Env var: `SECURABLE_KERNEL_HOOK=1`. Script: `hooks/scripts/session_kernel.sh`. Timeout: 10s. Always exits 0.

**Post-edit opengrep held checks** (`PostToolUse: Edit|Write|MultiEdit`) — runs the opengrep rule pack (`rules/opengrep/`) against each edited file. Env var: `SECURABLE_HELD_CHECKS=1`. Script: `hooks/scripts/post_edit_opengrep.sh`. Timeout: 30s. Always exits 0; advisory, never blocks. Requires `opengrep` on `PATH`; if absent the hook silently does nothing. **Nothing is ever installed by this hook.**

**Manual equivalent (CI):** run opengrep directly: `opengrep scan --json --config rules/opengrep/securable.yaml <target-files>`.

## 8. Merge-time Securability Report

`scripts/securability_report.sh` produces an advisory Securability Report (FIASSE v1.1 S5.2.1) for a diff.

```bash
scripts/securability_report.sh --base origin/main --head HEAD --out report.md
scripts/securability_report.sh --dry-run   # shows the prompt without calling the agent
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `AGENT_CLI` | `claude -p --output-format text` | Non-interactive agent command reading the prompt from stdin |
| `SKILL_PATH` | `skills/securability-engineering-review/SKILL.md` | Review skill path (resolved against the repo) |

The report is advisory (S5.2.2): posture and direction, not a gate.

**Alternative:** run the merge-steward persona directly:

```bash
claude --agent merge-steward "Review the diff origin/main...HEAD"
```

## 9. Tooling policy reminder

Runtime (skills, kernel, commands, personas) **never installs tooling**. Hooks use only tools already present. When a check cannot run because tooling is absent, the pack reports absence as evidence (Testability/Observability gap). CI provisioning is the consumer's decision. Only community-governed, non-commercial tools may be named or used.

## 10. Limitations and unverified items

- **Tool allowlists are held, path restrictions are promised.** Claude Code enforces `tools`/`disallowedTools` frontmatter on subagents. Path restrictions in persona instructions are behavioral guidance the harness does not enforce at the filesystem level.
- **Persona bindings are native.** Claude Code reads `agents/*.md` directly. The generated bindings under `bindings/` are for other harnesses; Claude Code does not need them.
- **`settings.json` agent key.** A `settings.json` at the plugin root with an `agent` key can make one persona the session default. The pack does not ship this so no persona is forced; teams can add it.
- **Hook exit semantics.** Exit code 2 blocks actions on supporting events. Both plugin hooks are advisory (exit 0 always).
