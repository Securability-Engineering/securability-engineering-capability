# Play: End-to-End Securable Code Generation (FIASSE v1.1 / SSEM)

Five-step runbook for generating code with a measured securability improvement loop: **enhance requirements → generate → review → improve → report**.

> **This play is opt-in.** It does *not* run by default for code-generation requests. The default path is the `securability-engineering` skill alone (single-shot generation). Activate this play only when the user passes `--full-loop` (or `--end-to-end`) or says **"end-to-end securable"** / **"full securability loop"** / explicitly references this play. Without that signal, do not invent a PRD or run the loop.
>
> **Source of truth**: [skills/securability-engineering/SKILL.md](../../skills/securability-engineering/SKILL.md) defines the SSEM constraints, anti-pattern table, and Securability Notes format. [skills/securability-engineering-review/SKILL.md](../../skills/securability-engineering-review/SKILL.md) defines the scoring rubric. This play sequences the work; it does not redefine those.

## Trigger Conditions (opt-in only)

Run this play when:

- The user passes `--full-loop` or `--end-to-end`
- The user says "end-to-end securable", "full securability loop", or "follow the securable-generation play"
- The user explicitly asks for a baseline-vs-post-enhancement scorecard tied to generated code

Do **not** run this play just because the user asked for "secure code" — that's the single-shot generation skill's job.

## Inputs

- PRD, feature specification, or user story set
- Target language / framework / runtime
- Architecture constraints and trust boundaries (if available)
- Existing codebase context (for refactors)

If no PRD or feature specification exists, ask whether the user wants:

- (a) A compact feature specification synthesized from the conversation, then the loop, or
- (b) Single-shot generation via the skill instead.

Do not silently invent a PRD.

## Prerequisites (check before Step 1)

This play spans three FIASSE layers, and the persona plugins split them: `securability-engineering` ships in `securable-build`, `prd-securability-enhancement` (Step 1) in `securable-requirements`, and `securability-engineering-review` (Steps 3–4) in `securable-review`. The all-in-one `securable-claude-plugin` ships all three.

Before Step 1, confirm both `skills/prd-securability-enhancement/SKILL.md` and `skills/securability-engineering-review/SKILL.md` are available (at the plugin root, or as installed skills). If either is missing, **do not start the loop** and do not improvise its procedure inline. Tell the user which plugin to install (`securable-requirements`, `securable-review`, or the all-in-one), and offer Default Mode single-shot generation via the `securability-engineering` skill instead. A partial loop — generation without the baseline review, or review without enhanced requirements — cannot produce the baseline/delta report this play promises.

## Steps

### Step 1 — Enhance requirements with ASVS

Invoke the `prd-securability-enhancement` skill.

Required outputs from Step 1:

- Enhanced requirements with ASVS-aligned coverage and a chosen ASVS level
- Feature-level securability notes
- Open assumptions and requirement gaps
- Coverage matrix

### Step 2 — Generate or refactor code

Invoke the `securability-engineering` skill in default mode against the enhanced requirements.

Required outputs from Step 2:

- Implementation code aligned to enhanced requirements
- Tests for valid, invalid, boundary, and error paths
- Securability Notes block per the skill's format

### Step 3 — Review and build enhancement plan

Invoke the `securability-engineering-review` skill against the generated code. Capture the **baseline scores**.

Required outputs from Step 3:

- Baseline 10-attribute scores (per attribute, per pillar, overall)
- Severity-classified findings with FIASSE v1.1 pattern tags
- Prioritized enhancement plan ordered by score-impact and effort

### Step 4 — Execute enhancements

Apply the prioritized plan from Step 3, highest-impact first. Re-invoke `securability-engineering-review` to capture the **post-enhancement scores**.

**Iteration cap**: at most two improvement passes. If scores have not crossed the user's target (or 8.0 overall as a default goal) after two passes, stop and surface the residual findings with their effort estimate. Do not loop indefinitely.

Required outputs from Step 4:

- Updated code implementing review-driven improvements
- Post-enhancement 10-attribute scores
- Score delta per attribute, per pillar, and overall

### Step 5 — Save the securability report

Persist the final report to `securability_report.md` at the path the user specifies. If they do not specify, ask before writing — do not assume the repo root.

The report must include:

1. Project / feature scope and evaluation date
2. ASVS level chosen (from Step 1)
3. Baseline 10-attribute scores (Step 3)
4. Implemented enhancement summary (Step 4)
5. Post-enhancement 10-attribute scores (Step 4)
6. Delta section showing score changes per attribute, per pillar, and overall
7. Final grade and concise next recommendations
8. Residual findings (if any) with effort estimates

Use [templates/report.md](../../templates/report.md) as the structural scaffold; extend with the baseline / delta / post-enhancement sections.

## Workflow Guards

- Do not enter this play without an explicit opt-in signal.
- Do not start Step 1 until the Prerequisites check passes; if it fails, name the missing plugin and offer Default Mode.
- Do not skip Step 1 once the play is active.
- Do not generate implementation code before requirement enhancement is complete.
- Do not skip Step 3 review before applying enhancements.
- Iterate Step 4 at most twice.
- Do not finalize without writing the report file.
- If required context is missing, ask for the minimum needed inputs.

## Quality Checklist

- [ ] Opt-in signal received (`--full-loop`, "end-to-end securable", or explicit play reference)
- [ ] Prerequisites confirmed: requirements and review skills available (`securable-requirements` + `securable-review`, or the all-in-one)
- [ ] Requirements ASVS-enhanced before coding
- [ ] Code generated with `securability-engineering` skill constraints
- [ ] Code reviewed with `securability-engineering-review` (baseline captured)
- [ ] Enhancements executed; iteration cap respected
- [ ] Post-enhancement scores captured
- [ ] Report written with baseline, delta, and post-enhancement scores
- [ ] Report path confirmed with user (no silent placement)

## References

- [skills/prd-securability-enhancement/SKILL.md](../../skills/prd-securability-enhancement/SKILL.md) (`securable-requirements`)
- [skills/securability-engineering/SKILL.md](../../skills/securability-engineering/SKILL.md) (`securable-build`)
- [skills/securability-engineering-review/SKILL.md](../../skills/securability-engineering-review/SKILL.md) (`securable-review`)
- [plays/requirements-analysis/prd-fiasse-asvs-enhancement.md](../requirements-analysis/prd-fiasse-asvs-enhancement.md) (`securable-requirements`)
- [plays/code-analysis/securability-engineering-review.md](../code-analysis/securability-engineering-review.md) (`securable-review`)
- [templates/finding.md](../../templates/finding.md)
- [templates/report.md](../../templates/report.md)
