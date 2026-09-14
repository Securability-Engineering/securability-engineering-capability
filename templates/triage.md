# Securability Triage Report Template

Use this scaffold to assemble the output of the `securability-triage` skill. The skill at [skills/securability-triage/SKILL.md](../skills/securability-triage/SKILL.md) is the source of truth for the procedure, verdict definitions, and grouping discipline.

This report converts raw security tool output into Actionable Security Intelligence (FIASSE v1.1 S6.3). It groups by root cause, not by rule or file, and routes each group to the skill or persona that owns the fix.

````markdown
# Securability Triage Report

**Date**: YYYY-MM-DD
**Scope**: [What was triaged — repo / service / PR #N / changeset]
**Tools**: [tool name @ version, tool name @ version, ...]
**Input files**: [SARIF / JSON / text file paths]
**Not scanned**: [Excluded paths, unsupported languages, absent tool categories — state explicitly so posture is not overstated (FIASSE v1.1 S5.2.5)]

---

## Summary Funnel

| Stage | Count |
|-------|-------|
| Raw hits (all tools) | N |
| Root-cause groups | N |
| Confirmed | N |
| False positive | N |
| Needs human | N |

---

## Group Table

| ID | Tag | SSEM Attribute(s) | Verdict | Hits | Requirement / Gap | Effort | Route |
|----|-----|--------------------|---------|------|-------------------|--------|-------|
| TG-01 | [anti-pattern tag] | [attribute] | Confirmed | N | [F-xx-Ry / RG-01] | S/M/L | [skill or persona] |
| TG-02 | [anti-pattern tag] | [attribute] | False positive | N | — | — | — |
| TG-03 | [anti-pattern tag] | [attribute] | Needs human | N | — | — | [who must answer] |

---

## Per-Group Detail

### TG-01: [Tag] (Verdict — Systemic | Local)

**SSEM attribute(s)**: [attribute name(s)]
**FIASSE reference**: [S-section]
**Rule IDs**: [tool:ruleId, tool:ruleId, ...]

**Locations**:
- `file:line` — [brief context: what the code does at this site]
- `file:line` — [brief context]
- [... representative sites; for systemic groups, cite 2-3 and state total count]

**Evidence**: [Why this is confirmed / false positive / needs human. For Confirmed: trace from trust boundary to sink. For False positive: the specific reason (sanitized upstream, test fixture, unreachable, wrong language mode). For Needs human: the exact question.]

**Requirement mapping**: [Requirement ID from `.securable/requirements.yaml` whose acceptance criteria this violates, or "Requirements gap RG-xx" with the gap described in contract shape]

**Fix candidate**: [Correct shape, referencing the generation skill's Anti-Pattern Tag Reference. Effort: S/M/L. In scope of current change: yes/no.]

**Route**: [securability-remediation / prd-securability-enhancement / threat-modeling escalation]

[Repeat for each group.]

---

## Requirements Gaps

Gaps found during triage where no matching requirement exists in `.securable/requirements.yaml`. Each is emitted in contract shape (FIASSE v1.1 S6.1.3) for adoption by `prd-securability-enhancement` or a human. These are not invented controls (FIASSE v1.1 S6.1.1); they are observed engineering deficits that need a requirement.

```yaml
# Requirements gap RG-01
- id: [F-xx-Ry or CC-Ry]
  text: [What the code must observably do]
  asvs: [Vx.y.z]
  acceptance:
    - [Testable criterion]
  status: planned
  source: securability-triage TG-xx
```

[Repeat for each gap. If no gaps: "No requirements gaps found — all confirmed groups map to existing requirements."]

---

## False-Positive Register

Document every false positive with evidence so the decision is reviewable and so the same finding is not re-triaged next cycle.

| Group | Rule ID | Location | Reason |
|-------|---------|----------|--------|
| TG-xx | [ruleId] | `file:line` | [Specific reason: sanitized upstream / test fixture / unreachable / wrong language mode] |

---

## Handoffs

| Recipient | Groups | Action |
|-----------|--------|--------|
| securability-remediation | TG-01, TG-02 | Fix confirmed code-level findings |
| prd-securability-enhancement | RG-01 | Add missing requirement to contract |
| threat-modeling | — | [Design-level escalations, if any] |
| [human / team] | TG-03 | Answer the questions in "Needs human" groups |

---

## Machine-Readable Triage Block

```yaml
securability_triage:
  version: 1
  date: YYYY-MM-DD
  scope: <string>
  tools:
    - name: <tool>
      version: <version or unknown>
      hits: <N>
  not_scanned: [<path or category>, ...]
  raw_hits: <N>
  groups:
    - id: TG-01
      tag: "<anti-pattern tag>"
      attribute: [<SSEM attribute>, ...]
      verdict: confirmed          # confirmed | false_positive | needs_human
      scope: systemic             # systemic | local
      rule_ids: [<tool:ruleId>, ...]
      locations:
        - file: <path>
          line: <N>
      requirement: <F-xx-Ry>     # or null
      gap: null                   # or RG-xx
      effort: M                   # S | M | L
      route: securability-remediation
    # ... repeat for each group
  summary:
    confirmed: <N>
    false_positive: <N>
    needs_human: <N>
  gaps: [RG-01, ...]
```

---

## Securability Notes

- **SSEM attributes enforced**: [attributes this triage touched]
- **Trust boundaries**: [boundaries where confirmed findings concentrate]
- **ASVS references**: [requirement IDs confirmed or gap IDs recorded]
- **Trade-offs**: [any reordering vs scanner severity, coverage gaps that limit confidence]
````

## Authoring Guidance

- **Group by cause, not by rule.** Twelve hits from one missing convention is one systemic group, not twelve local findings. Filing them separately inflates the count and points remediation at symptoms (FIASSE v1.1 S6.2).
- **Evidence, not assertion.** Every verdict must cite `file:line` and state *why* — an unsupported "Confirmed" is as useless as the raw finding it replaced.
- **Name the gap, not the control.** When a requirement is missing, describe the observable behavior that is needed (FIASSE v1.1 S6.1.3), not the catalog control that would cover it (FIASSE v1.1 S6.1.1).
- **No code edits.** This template produces a report. Code changes belong to `securability-remediation` or `securability-engineering`.
- **No commercial tools.** Never name a commercially licensed scanner in the output.
