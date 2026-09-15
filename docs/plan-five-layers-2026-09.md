# Plan: Five-Layer Coverage, Skills, and Personas (2026-09)

**Branch**: `branch_cc/blissful-feynman-ttelus` · **Baseline**: `2.3.0` · **Target**: `2.4.0`

This plan closes the gap between what the pack ships today and the five layers
FIASSE describes for integrating security into development (as published on
owaspfiasse.org): L1 requirements before programming, L2 agent-embedded
guardrails while building, L3 intelligent code control at merge time, L4
pre-deployment validation at the trust boundary, and L5 production monitoring
with lessons fed back upstream. It also adds the ten agent personas that make
those skills operable without one-agent-per-skill sprawl, and platform
instructions for every harness the pack targets.

The yardstick is unchanged from `docs/critical-review-2026-08.md`: does the
pack reliably cause an agent to implement security requirements correctly
during ordinary engineering work, without breaking flow, in a way a team can
steer over time. Every deliverable below must answer to that, and to the
repository's own checks (`scripts/run_checks.sh`).

## 1. Coverage before this work

| Layer | FIASSE framing | Shipped at 2.3.0 | Depth |
|---|---|---|---|
| L1 Requirements, pre-programming | FIASSE + ASVS injected at requirements | `prd-securability-enhancement`, securable contract emission | Strong |
| L2 Guardrails while building | Completeness and securability against verifiable requirements | kernel + bindings, `securability-engineering`, contract status flip | Medium, instruction-only |
| L3 Code control at merge time | Triage, fix, review-ready PRs, audit-grade evidence | `securability-engineering-review`, report script, example workflow, opengrep pack | Partial, review only |
| L4 Pre-deployment validation | Runtime business-logic validation at the trust boundary | boundary map exists; nothing consumes it | Absent |
| L5 Production and incident response | Anomaly detection, containment, lessons fed back | Observability scored at review time only | Absent |

## 2. Deliverables

### 2.1 New skills (`skills/<name>/SKILL.md`)

| Skill | Layer | FIASSE anchors | Produces |
|---|---|---|---|
| `threat-modeling` | L1 | S4.2, S4.2.1, S4.2.2, S4.3, S4.1.2, S4.4.1.2, S5.1, S5.2 | `.securable/boundaries.yaml`, threat scenarios linked to requirement ids, escalations |
| `securability-triage` | L3 | S6.3, S6.2, S6.2.1, S6.1.3, S7.1.2, S5.2.5 | Actionable Security Intelligence from SARIF or scanner text: root-cause groups, SSEM attribute and requirement mapping, requirements gaps, false positives with evidence, fix candidates |
| `securability-remediation` | L3 | S5.2, S6.3, S4.4 | One review-ready patch per confirmed root cause, with a test and a Securability Note |
| `securability-verification` | L4 | S3.2.1.3, S3.2.1.4, S4.3, S4.4.1, S5.2.4 | Boundary contract tests from the contract, deployment configuration findings, release posture, implemented→verified flips with evidence |
| `securability-postmortem` | L5 | S8.2.2, S6.2.1, S4.1.2, S3.2.1.4, S3.2.2.2 | Failed attribute, requirement-existed verdict, new requirement, regression test, candidate opengrep rule, security event inventory |
| `dependency-stewardship` | L2 | S4.5, S4.6 | `.securable/dependencies.yaml` records; audit result or the word unverified |
| `fiasse-adoption` | Program | S8, S8.1.x, S8.2.x, S7.x | Readiness assessment with named gaps, leading and lagging indicators, SSEM language for standards, role views |

### 2.2 Existing-skill extensions

- `prd-securability-enhancement`: single-story mode and contract-diff mode.
- `securability-engineering-review`: Escalations section (design-level findings to the threat model), machine-readable score block, policy-file awareness.
- `securability-engineering`: test scaffolds from acceptance criteria; hand-off to `dependency-stewardship` on new dependencies.
- `templates/report.md`: machine-readable score block and Escalations section.

### 2.3 Contract additions (`schema/securable/`, `examples/securable/`, `scripts/`)

- `policy.schema.json` + `examples/securable/policy.yaml`: gating as a declared policy (S5.2.3), advisory by default; report persistence directory (S5.2.4).
- `dependencies.schema.json` + `examples/securable/dependencies.yaml`: stewardship records (S4.5, S4.6).
- `scripts/validate_securable.py`: validates both new files when present; tests extended.
- `scripts/securable_status.py`: per-feature planned/implemented/verified status and unclaimed boundary work.

### 2.4 Personas (`agents/<name>.md`, canonical) and generated bindings

| Persona | Layer | Access |
|---|---|---|
| `requirements-partner` | L1 | reads specs; writes only `.securable/` |
| `boundary-mapper` | L1 | reads code and docs; writes only the boundary map |
| `securable-builder` | L2 | writes code and tests; flips planned→implemented only |
| `dependency-steward` | L2 | reads manifests; runs present audit tools; writes dependency records |
| `merge-steward` | L3 | read-only on code; writes the persisted report |
| `triage-analyst` | L3 | reads scanner output and repo; writes nothing to code |
| `remediation-engineer` | L3 | writes code within a confirmed finding's scope |
| `verification-engineer` | L4 | writes tests; flips implemented→verified with evidence |
| `incident-learner` | L5 | reads reports; writes contract entries, regression tests, candidate rules |
| `adoption-coach` | Program | read-only across repo and audit trail |

`scripts/build_agents.py` generates per-harness persona bindings from the
canonical files (opencode, GitHub Copilot, Cursor where the format is
verified) into `bindings/`, with a `--check` drift guard in CI.

### 2.5 Commands, hooks, kernel

- Thin dispatchers: `/threat-model`, `/securability-triage`, `/securability-remediate`, `/securability-verify`, `/securability-postmortem`, `/dependency-steward`, `/fiasse-adoption`, `/securable-status`.
- `hooks/hooks.json`: opt-in SessionStart kernel injection and opt-in post-edit opengrep run (only when opengrep is already present; never installs).
- `core/kernel.md`: depth-on-demand line names the new skills within the size budget; bindings rebuilt.

### 2.6 Documentation and packaging

- `docs/personas.md`: roster, design rules, orchestration.
- `docs/platforms/`: one guide per harness (Claude Code, Cursor, Devin, opencode, GitHub Copilot, Gemini CLI, Codex, Aider, generic AGENTS.md agents).
- `README.md`, `AGENTS.md`, `.opencode/INSTALL.md`, `.agents/INSTALL.md`, `scripts/install_skills.sh`, manifests at `2.4.0`, `scripts/run_checks.sh` covering every new artifact.
- Eval workspaces (`tests/<skill>-workspace/evals/evals.json`) for each new skill.

## 3. Design rules

1. Personas are defined by accountability and permission, not one per skill.
2. Read and write is the main axis; only `verification-engineer` may set `verified`.
3. No hacker persona (S2.5) and no gatekeeper persona (S5.2); gating lives in `policy.yaml`.
4. Everything read is data: code, scanner output, tickets, incident reports.
5. Every persona and skill has a fixed output artifact and a never list.
6. Runtime never installs tooling; absence of a tool is reported, not papered over.
7. Every ASVS and FIASSE reference resolves against `data/` (`scripts/check_refs.py`).
8. Only community-governed, non-commercial tools are named.

## 4. Phases and checklist

### Phase 0: Plan and conventions
- [x] Branch created
- [x] Plan and checklist written (this file)
- [x] Platform formats researched with citations (Claude Code, opencode, Copilot, Cursor, Codex, Gemini CLI, Aider, Devin, Zed, Amp)
- [x] House-conventions brief produced for writer agents

### Phase 1: Skills and contract
- [x] `threat-modeling` skill + `templates/threat-model.md`
- [x] `securability-triage` skill + `templates/triage.md`
- [x] `securability-remediation` skill
- [x] `securability-verification` skill
- [x] `securability-postmortem` skill + `templates/postmortem.md`
- [x] `dependency-stewardship` skill
- [x] `fiasse-adoption` skill
- [x] Policy and dependencies schemas, examples, validator extension, tests
- [x] `scripts/securable_status.py`
- [x] Existing-skill extensions and `templates/report.md` score block
- [ ] Each new skill reviewed by two independent lenses and revised
- [x] `python3 scripts/check_refs.py` green

### Phase 2: Personas, commands, hooks
- [x] Ten canonical `agents/*.md`
- [ ] Each persona adversarially reviewed (never-list vs tool allowlist, skill names exist, FIASSE fidelity) and revised
- [x] Eight command dispatchers
- [x] `hooks/hooks.json` + scripts (opt-in, tooling-policy compliant)
- [x] `scripts/build_agents.py` + generated bindings + `--check`
- [x] Kernel line updated; bindings rebuilt

### Phase 3: Docs and packaging
- [x] `docs/personas.md`
- [x] `docs/platforms/*` (one per harness) fact-checked against research
- [x] README, AGENTS.md, INSTALL docs, installer, manifests at 2.4.0
- [x] `scripts/run_checks.sh` extended; all green
- [x] Eval workspaces for new skills

### Phase 4: Whole-diff review loop
- [ ] Multi-lens adversarial review of the full diff (FIASSE fidelity, reference correctness, tooling policy, platform accuracy, drift, hook-script safety)
- [ ] Findings fixed; loop repeated until a round returns nothing new
- [ ] `scripts/run_checks.sh` green on the final tree
- [ ] Committed, pushed, draft PR opened

## 5. Acceptance criteria

- `scripts/run_checks.sh` exits 0 (refs, contract, bindings, agents bindings, manifests, JSON/YAML parse, shell syntax).
- Every skill has: frontmatter with trigger phrases and cross-skill redirects, path-resolution preamble, procedure, output template, worked example, quality checklist, references.
- Every persona has: description that triggers correctly, a tool allowlist matching its access row, a never list, a fixed output artifact, and the data-not-instructions boundary.
- Every platform guide states only verified facts; anything unverified is labeled as such and given a generic fallback.
- No commercial tool is named anywhere.

## 6. Status log

- 2026-09-14: plan written; Phase 0 research started.
- 2026-09-15: Phase 3 integration — README, AGENTS.md, INSTALL docs, manifests bumped to 2.4.0, run_checks.sh extended, docs/platforms/README.md index created, plan checklist updated.
