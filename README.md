# securable-claude-plugin

A Claude Code plugin offering secure code generation and securability analysis through application of the OWASP FIASSE: The Securable framework. Also, part of [OWASP Secure Agent Playbook](https://github.com/OWASP/secure-agent-playbook).

## Overview

This plugin augments a coding agent with eleven capabilities grouped by the five FIASSE integration layers:

**L1 — Requirements, pre-programming**
1. **PRD Securability Enhancement** — Enhance product requirements with ASVS 5.0 coverage and FIASSE/SSEM implementation guidance.
2. **Threat Modeling** — Produce boundary maps, threat scenarios, and escalations from code and specifications.

**L2 — Guardrails while building**
3. **Securability Engineering Code Generation** — Generate code that embodies securable qualities by default.
4. **Dependency Stewardship** — Audit, record, and monitor third-party dependencies against stewardship criteria.

**L3 — Code control at merge time**
5. **Securability Engineering Review** — Analyze existing code for securable qualities using the ten SSEM attributes (FIASSE v1.1) across three pillars (Maintainability, Trustworthiness, Reliability), producing scored assessments with actionable findings.
6. **Securability Triage** — Turn scanner output into actionable security intelligence with root-cause grouping.
7. **Securability Remediation** — Produce review-ready patches for confirmed findings, each with a test and Securability Note.

**L4 — Pre-deployment validation**
8. **Securability Verification** — Generate boundary contract tests, validate deployment configuration, flip implemented to verified with evidence.

**L5 — Production and incident response**
9. **Securability Postmortem** — Extract failed attributes, regression tests, candidate rules, and new requirements from incident reports.

**Program**
10. **FIASSE Adoption** — Assess organizational readiness, produce leading/lagging indicators, and map roles to FIASSE responsibilities.
11. **FIASSE Lookup** — Answer FIASSE/SSEM questions from the bundled framework reference, citing section numbers.

Agent-facing guidance lives in [AGENTS.md](AGENTS.md) (the [AGENTS.md standard](https://agents.md) entry point, imported by `CLAUDE.md`). A critical assessment of this plugin and its enhancement roadmap lives in [docs/critical-review-2026-08.md](docs/critical-review-2026-08.md).

## Elevating any harness

Beyond the skills, the pack carries its impact in four layers so *any* code-generation harness — not only the one it's loaded into — is bound by it:

1. **The securability kernel** (`core/kernel.md`) — a ~300-token always-on distillation of the non-negotiables (parse-don't-trust, server-side authority, the never-emit list, observable security, Securability Notes). `scripts/build_bindings.py` generates per-harness bindings from it — Cursor rule, Copilot instructions, Gemini CLI context, Aider conventions, and the kernel block inside AGENTS.md — with a size budget and a CI drift guard (`--check`). Bindings are generated, never edited.
   *Measured (kernel A/B, `tests/kernel_ab.py`, deterministic detectors, claude CLI)*: on a strong frontier model the baseline already avoided all detector anti-patterns (0/0 — verified real, not detector blindness), while the kernel's process contract was adopted 3/3 (Securability Notes present) vs 0/3 baseline. Anti-pattern deltas are expected to show on weaker models — measuring that per harness is the cross-harness scoreboard's job (roadmap M5).
2. **The securable contract** (`.securable/requirements.yaml` + `boundaries.yaml` + `policy.yaml` + `dependencies.yaml` in consuming projects) — repo-resident, machine-readable requirements with testable acceptance criteria and a `planned → implemented → verified` lifecycle. Emitted by the PRD skill, honored by generation in any harness, verified at review. `scripts/validate_securable.py` enforces the semantics — including that every cited ASVS ID exists in the bundled 5.0 catalog. See [docs/securable-contract.md](docs/securable-contract.md).
3. **Agent personas** (`agents/*.md`) — ten role-scoped personas (requirements-partner, boundary-mapper, securable-builder, dependency-steward, merge-steward, triage-analyst, remediation-engineer, verification-engineer, incident-learner, adoption-coach) spanning all five FIASSE layers. Each has a tool allowlist, a never list, and a fixed output artifact. `scripts/build_agents.py` generates per-harness persona bindings (Cursor, Copilot, opencode, generic) with a CI drift guard (`--check`). See [docs/personas.md](docs/personas.md).
4. **Held checks** — `rules/opengrep/securable.yaml` maps the skills' anti-pattern tags to enforceable [opengrep](https://github.com/opengrep/opengrep) rules (SSEM/ASVS metadata on each; opengrep is the LGPL, community-governed scanner), tested against paired fail/pass fixtures; and `scripts/securability_report.sh` + `.github/workflows/securability-report.yml` produce the FIASSE S5.2.1 Securability Report on pull requests via any agent CLI (`claude`, `codex`, `opencode`) — advisory by default, per S5.2.2.

Run everything CI runs with `scripts/run_checks.sh`.

## Installation

One skills tree, one adapter per agent — the multi-agent packaging methodology of [obra/superpowers](https://github.com/obra/superpowers). Each supported harness gets a root-level adapter (a manifest in that harness's plugin format, or an agent-followable `INSTALL.md`), and every adapter points at the same `skills/` + `data/` tree. `scripts/check_manifests.py` (run by CI) keeps the manifests in lockstep.

| Agent | Adapter | Install |
| ----- | ------- | ------- |
| Claude Code | `.claude-plugin/` | `/plugin` marketplace |
| Cursor | `.cursor-plugin/` | plugin marketplace, or kernel rule + skills copy |
| Devin | `.devin-plugin/` | `devin plugins install Securability-Engineering/securable-claude-plugin` |
| opencode | `.opencode/INSTALL.md` | fetch-and-follow |
| Any AGENTS.md/SKILL.md agent | `.agents/INSTALL.md` | fetch-and-follow, or `scripts/install_skills.sh` |

### Claude Code

Install through the Claude Code plugin manager: open the interactive manager with `/plugin`, then use the Discover and Marketplaces tabs to add/install graphically. Or from this repository's marketplace manifest:

```text
/plugin marketplace add Securability-Engineering/securable-claude-plugin
/plugin install securable-claude-plugin@securable-claude-plugins
```

### Cursor

`.cursor-plugin/plugin.json` declares the pack in Cursor's plugin format, with `skills` pointing at the shared `skills/` tree — in Cursor Agent chat, install with `/add-plugin` (or search "securable" in the plugin marketplace, where listed). Independent of the plugin, the always-apply securability kernel rule ships pre-generated at `bindings/cursor/securable.mdc`; copy it into your project's `.cursor/rules/` to bind every generation to the kernel.

### Devin

Install from this repository:

```bash
devin plugins install Securability-Engineering/securable-claude-plugin
```

Update later with `devin plugins update securable-claude-plugin`. The manifest lives at `.devin-plugin/plugin.json`.

### opencode

Tell opencode:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/Securability-Engineering/securable-claude-plugin/refs/heads/main/.opencode/INSTALL.md
```

Or by hand: [.opencode/INSTALL.md](.opencode/INSTALL.md) — a clone plus `scripts/install_skills.sh --target .opencode` (project) or `--target "$HOME/.config/opencode"` (global).

### Any AGENTS.md / SKILL.md agent (Codex, Zed, Amp, …)

The skills follow the [Agent Skills](https://agentskills.io) standard (`SKILL.md` + YAML frontmatter) and the repo ships a tool-agnostic [AGENTS.md](AGENTS.md) entry point, so the pack works in any conforming harness. Tell the agent:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/Securability-Engineering/securable-claude-plugin/refs/heads/main/.agents/INSTALL.md
```

Or run the installer yourself from a checkout:

```bash
# Into the current project (agent-standard path):
scripts/install_skills.sh --target .agents

# opencode project config, or global:
scripts/install_skills.sh --target .opencode
scripts/install_skills.sh --target "$HOME/.config/opencode"

# Claude Code project skills (without installing the plugin):
scripts/install_skills.sh --target .claude
```

The script copies `skills/`, `data/`, `plays/`, `templates/`, `agents/`, `schema/`, `core/`, and `rules/` together under one root — the layout the skills' internal references depend on. Persona definitions in `agents/` ride along with the skills tree; pre-generated persona bindings for each harness ship under `bindings/`.

### Developing this plugin

Run `claude --plugin-dir .` from the repo root so commands and skills load exactly as a plugin install would. Note that the repo's root `CLAUDE.md`/`AGENTS.md` is read only when the repo is opened as a project; installed plugin users get the skills and commands, not that file.

## Slash Commands

Commands live in `commands/` (the plugin-standard location) and are thin dispatchers — each delegates to its skill, which holds the authoritative procedure.

| Command                       | Description                                                |
| ----------------------------- | ---------------------------------------------------------- |
| `/securability-review`        | Run a full SSEM securability assessment on code            |
| `/secure-generate`            | Generate code with FIASSE/SSEM constraints applied         |
| `/prd-securability-enhance`   | Enhance PRD features with ASVS + FIASSE/SSEM requirements  |
| `/fiasse-lookup`              | Look up FIASSE/SSEM reference material by topic            |
| `/threat-model`               | Produce a boundary map and threat scenarios                 |
| `/securability-triage`        | Triage scanner output into actionable intelligence         |
| `/securability-remediate`     | Produce review-ready patches for confirmed findings        |
| `/securability-verify`        | Generate boundary tests and validate deployment config     |
| `/securability-postmortem`    | Extract lessons and new requirements from an incident      |
| `/dependency-steward`         | Audit and record dependency stewardship                    |
| `/fiasse-adoption`            | Assess organizational readiness for FIASSE adoption        |
| `/securable-status`           | Print contract status (planned/implemented/verified)       |

## Personas

Ten agent personas scope the skills by accountability and permission. Each persona carries a tool allowlist, a never list, and a fixed output artifact. See [docs/personas.md](docs/personas.md) for the full roster, design rules, orchestration patterns, and per-platform invocation.

| Persona | Layer | Primary skill |
| ------- | ----- | ------------- |
| `requirements-partner` | L1 | prd-securability-enhancement |
| `boundary-mapper` | L1 | threat-modeling |
| `securable-builder` | L2 | securability-engineering |
| `dependency-steward` | L2 | dependency-stewardship |
| `merge-steward` | L3 | securability-engineering-review |
| `triage-analyst` | L3 | securability-triage |
| `remediation-engineer` | L3 | securability-remediation |
| `verification-engineer` | L4 | securability-verification |
| `incident-learner` | L5 | securability-postmortem |
| `adoption-coach` | Program | fiasse-adoption |

## Platform Guides

Per-harness guides at [docs/platforms/](docs/platforms/) explain what the pack provides natively on each harness, how to install, invoke skills and personas, and what remains manual or unavailable. See the [platform index](docs/platforms/README.md) for a capability matrix across all nine guides.

## Example: PRD Enhancement

See the before/after example in:

- `examples/prd-enhancement/input-prd.md`
- `examples/prd-enhancement/enhanced-prd.md`
- `examples/prd-enhancement/README.md`

## SSEM Model (FIASSE v1.1)

The Securable Software Engineering Model (SSEM) defines ten attributes across three pillars:

| **Maintainability** | **Trustworthiness** | **Reliability** |
| ------------------- | :-----------------: | --------------: |
| Analyzability       |   Confidentiality   |    Availability |
| Modifiability       |    Accountability   |       Integrity |
| Testability         |     Authenticity    |      Resilience |
| Observability       |                     |                 |

Each attribute is scored 0–10 and carries **equal weight** (1/10 of the overall score). The overall score is the mean of the attribute scores, subject to a weakest-link floor:

```text
raw mean = mean of all assessed attribute scores
floor    = lowest assessed attribute score + 3.0
overall  = min(raw mean, floor)
```

The floor keeps a single catastrophic attribute from being averaged away — a service that is strong everywhere except input handling is not an adequate service. Pillar scores are reported as diagnostics and never feed the overall score. See `skills/securability-engineering-review/SKILL.md` for the full rubric, the `Not assessed` / `N/A` states, and severity classification.

> **Scoring conduct**: Per FIASSE v1.1 Appendix A.4, a composite SSEM score is a directional management aid for tracking a system against itself over time — not a statement of assurance, compliance, or security. Every report pairs the score with its rationale and a prioritized list of changes.

> **v1.1 update**: "Request Surface Minimization" is now **Canonical Parsing** (S4.4.1.1) and "Derived Integrity" is now **Isolated Integrity** (S4.4.1.2). v1.1 also adds the Quality-Security Relationship (S2.4), the Securability Report (S5.2.1–S5.2.5), and scoring guidance (SA.4). Measurement guidance lives in Appendix A (`data/fiasse/SA.*.md`).

## Project Structure

```text
AGENTS.md                          # Canonical agent entry point (AGENTS.md standard, tool-agnostic)
CLAUDE.md                          # Thin stub importing AGENTS.md (project-mode Claude Code)
core/
  kernel.md                        # Securability kernel — source of truth for all bindings
agents/                            # Canonical persona definitions (ten personas, five FIASSE layers)
bindings/                          # GENERATED per-harness kernel + persona bindings (never edit)
  cursor/securable.mdc             # Cursor always-apply rule
  cursor/agents/                   # Cursor persona bindings
  copilot/copilot-instructions.md  # GitHub Copilot custom instructions
  copilot/agents/                  # Copilot persona bindings
  gemini/GEMINI.md                 # Gemini CLI context
  aider/CONVENTIONS.md             # Aider conventions
  opencode/agents/                 # opencode persona bindings
  generic/agents/                  # Generic AGENTS.md persona bindings
hooks/                             # Opt-in Claude Code hooks (SessionStart kernel, post-edit opengrep)
schema/
  securable/                       # JSON Schemas for the securable contract (.securable/*)
rules/
  opengrep/securable.yaml          # Held-check rule pack mapped to the anti-pattern tags
.claude-plugin/
  plugin.json                      # Plugin manifest (Claude Code) — canonical version source
  marketplace.json                 # Marketplace manifest
.cursor-plugin/
  plugin.json                      # Plugin manifest (Cursor) — kept in lockstep
.devin-plugin/
  plugin.json                      # Plugin manifest (Devin) — kept in lockstep
.opencode/
  INSTALL.md                       # Agent-followable install instructions (opencode)
.agents/
  INSTALL.md                       # Agent-followable install instructions (any AGENTS.md/SKILL.md agent)
commands/                          # Twelve thin slash-command dispatchers (see table above)
.claude/
  settings.json                    # Repo-development permissions (not shipped to plugin installs)
.claudeignore                      # Files excluded from context (repo development only)
.gitignore                         # Excludes test run artifacts (iteration-*/) from VCS
data/
  asvs/                            # OWASP ASVS 5.0 requirement chapters (V1–V17)
  fiasse/                          # FIASSE v1.1 reference sections (S1.x–S8.x + Appendix A as SA.x)
skills/                            # Eleven skills (see AGENTS.md § Skills)
plays/
  code-generation/                 # Step-by-step code generation workflows
  code-analysis/                   # Step-by-step analysis procedures
  requirements-analysis/           # Step-by-step PRD enhancement workflows
templates/
  finding.md                       # Individual finding format
  report.md                        # Full assessment report format
  threat-model.md                  # Threat model output format
  triage.md                        # Triage output format
  postmortem.md                    # Postmortem output format
template/
  SKILL.md                         # Template for creating new skills
scripts/
  build_bindings.py                # Kernel -> bindings generator (--check = CI drift guard)
  build_agents.py                  # Persona -> per-harness bindings generator (--check = CI drift guard)
  validate_securable.py            # Securable-contract validator (shape + semantics + ASVS existence)
  securable_status.py              # Contract status summary (planned/implemented/verified)
  check_refs.py                    # ASVS/FIASSE reference integrity checker
  check_manifests.py               # Per-agent manifest lockstep checker (name/version/license)
  install_skills.sh                # Layout-preserving installer for opencode / other agent tools
  securability_report.sh           # Merge-time Securability Report via any agent CLI
  test_opengrep_rules.sh           # Rule-pack test runner (skips if opengrep absent)
  run_checks.sh                    # Everything CI runs, in one command
  build_plugin_zip.sh              # Release zip builder
  generate_marketplace_json.sh     # Release marketplace manifest builder
  extract_fiasse_sections.py       # Utility to extract sections from FIASSE v1.1 framework markdown
examples/
  prd-enhancement/                 # Before/after PRD securability enhancement example
  securable/                       # Worked securable-contract example (requirements + boundaries + policy + dependencies)
docs/
  critical-review-2026-08.md       # Critical assessment + enhancement plan for this plugin
  securable-contract.md            # The securable contract: files, lifecycle, validation
  personas.md                      # Persona roster, design rules, orchestration
  platforms/                       # Per-harness platform guides (nine harnesses)
  plan-five-layers-2026-09.md      # Five-layer coverage plan and checklist
tests/                             # Regression tests (see Testing below)
  run_tests.py                     # Claude Code CLI test runner (skill workspaces)
  kernel_ab.py                     # Kernel A/B runner + detector self-tests
  README.md                        # Test workspace conventions
  <skill>-workspace/               # Per-skill eval workspaces (eleven skills)
  kernel-ab-workspace/             # Kernel A/B evals (naturalistic prompts, deterministic grading)
  securable-contract/              # Contract validator tests
  opengrep-fixtures/               # Paired fail/pass fixtures for the rule pack
```

## Testing

```bash
scripts/run_checks.sh                 # everything CI runs: refs, contract, bindings, agents, manifests, schemas, hooks
python3 scripts/check_refs.py         # ASVS/FIASSE references resolve against data/
python3 scripts/build_agents.py --check  # persona binding drift guard
python3 scripts/check_manifests.py    # manifest lockstep
python3 scripts/securable_status.py --dir examples/securable
OPENGREP_BIN=opengrep scripts/test_opengrep_rules.sh # needs opengrep installed
```

Each skill has a regression workspace under [`tests/`](tests/) that exercises it
on three realistic prompts and grades the output via LLM-as-judge against an
asserted expectation set. Workspaces share a common shape:

```text
tests/<skill>-workspace/
  evals/
    evals.json            # prompts + assertions for each eval
    inputs/               # input fixtures (PRDs / source files)
  skill-snapshot/         # frozen pre-optimization SKILL.md (the baseline)
  iteration-N/            # generated outputs (gitignored)
```

To run a workspace end-to-end against the live skill plus the snapshot
baseline, with grading:

```bash
# Requires the `claude` CLI on PATH and Python 3.9+
python tests/run_tests.py tests/securability-engineering-workspace --grade

# Just the live skill, just one eval
python tests/run_tests.py tests/securability-engineering-review-workspace \
    --config with_skill --eval-id 1 --grade
```

See [`tests/README.md`](tests/README.md) for full conventions, the per-iteration
output layout, and how the runner integrates with the skill-creator
aggregator and viewer.

## Versioning

The plugin carries its own semantic version, independent of the FIASSE version it targets.

- **Plugin version** (`.claude-plugin/plugin.json`) — semver for this plugin's own behaviour. A major bump means the review output changed incompatibly. `2.0.0` is the first release of the ten-attribute, equal-weight scoring model with a weakest-link floor. The per-agent manifests (`.cursor-plugin/`, `.devin-plugin/`, and `plugins[0]` in `marketplace.json`) carry the same version; `scripts/check_manifests.py` fails CI if they drift, and `scripts/build_plugin_zip.sh` stamps all of them at release time.
- **FIASSE target version** — the framework release the reference data is extracted from. Recorded machine-readably in the `fiasse_version` frontmatter of every file under `data/fiasse/`, and in prose here and in `CLAUDE.md`.

The two moved together through `1.0.4` and no longer do. Tracking a new FIASSE release is not automatically a major plugin bump, and a scoring change is a major bump whether or not FIASSE moved.

Release tags are `v<semver>` (e.g. `v2.0.0`). `scripts/build_plugin_zip.sh` and `scripts/generate_marketplace_json.sh` both derive the published version by stripping the leading `v`; the git ref keeps it.

## References

- [FIASSE Framework v1.1](https://github.com/OWASP/FIASSE/blob/v1.1/docs/securable_framework.md)  referenced version
- [OWASP/FIASSE](https://github.com/OWASP/FIASSE) — Source repository
- [OWASP/FIASSE](https://owaspfiasse.org) — Official Home
- [OWASP secure-agent-playbook](https://github.com/OWASP/secure-agent-playbook) — Larger combined project for agent-oriented guidance
- [Securability-Engineering](https://github.com/Securability-Engineering) — Organization hosting IDE-specific versions of this plugin
- [loose-notes_claude_aspnet_pva](https://github.com/Securability-Engineering-Plugin-Tests/loose-notes_claude_aspnet_pva) — Worst-case experiment test project

## License

CC-BY-4.0 — See [LICENSE](LICENSE)

 <a href="https://www.buymeacoffee.com/xcaciv"> <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="25"> </a>
