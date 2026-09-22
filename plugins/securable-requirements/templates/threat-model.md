# Threat Model Template

Use this scaffold to assemble the output of the `threat-modeling` skill. The skill at [skills/threat-modeling/SKILL.md](../skills/threat-modeling/SKILL.md) is the source of truth for the procedure, boundary-map shape, scenario format, and quality checklist. This template supplies the structural shape.

Threat scenarios describe what can go wrong and the SSEM attribute that prevents it — never step-by-step attack instructions (FIASSE v1.1 S2.5, S6.2.2).

````markdown
# Threat Model — [System Name]

**Date**: YYYY-MM-DD
**Scope**: [What was analyzed — full system / feature / escalation target]
**Mode**: Design | Code | Escalation
**Inputs read**: [Documents, files, or findings analyzed — cite each by name or path]

---

## Boundary Map

| ID | Kind | Description | Entry Points | Data | Authority | Notes |
|---|---|---|---|---|---|---|
| [kebab-id] | [http/rpc/queue/file/cli/env/webhook/db/third-party/other] | [What crosses this boundary] | [Routes, handlers, or listeners] | [Data classes] | [Server-side authority source] | [Open questions] |

---

## Threat Scenarios

| ID | Boundary | Data Class | What Can Go Wrong | SSEM Attribute(s) | Resolution | ASVS | Status |
|---|---|---|---|---|---|---|---|
| T-01 | [boundary-id] | [data class] | [One sentence — failure of an SSEM attribute] | [Attribute name(s)] | [Inherent solution (attribute) or requirement id] | [Vx.y section] | [addressed by design / requirement raised / open] |

---

## Requirement Gaps

Requirements raised by this threat model. Each entry follows the `.securable/requirements.yaml` shape. All gaps carry `status: planned`.

```yaml
- id: [F-xx-Rn or CC-Rn]
  text: [What the requirement says]
  asvs: [Vx.y.z references]
  acceptance:
    - [Behaviorally testable criterion]
  status: planned
```

[Repeat for each gap. When the gap set is large, hand it to prd-securability-enhancement for full ASVS treatment.]

---

## Escalations & Assumptions

[Anything requiring a human decision. Each escalation names what is unknown and why the threat model cannot resolve it.]

- **[Topic]**: [Question for the team — e.g., "What is the intended trust level of the webhook source?"]

---

## Securability Notes

- **SSEM attributes enforced**: [2-4 attributes that shaped this analysis]
- **Trust boundaries**: [count and summary]
- **Requirement gaps**: [count raised as planned]
- **Trade-offs**: [decisions or assumptions a reviewer must see]
````

## Notes

- Boundaries that do not exist in the input are never invented. Mark uncertain ones with a question in `notes`.
- Every scenario names an SSEM attribute — never a CWE, CVSS score, or exploit technique.
- Requirement gaps carry at least one testable acceptance criterion; an entry without one is a control citation, not a requirement (FIASSE v1.1 S6.1.1).
- The boundary map is written to `.securable/boundaries.yaml` in the user's project and validated with `python3 scripts/validate_securable.py --dir .securable` when the validator is available.
- This skill creates requirements with `status: planned` only. It never sets `implemented` or `verified`.
