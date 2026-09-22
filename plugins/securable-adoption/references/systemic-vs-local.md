# Systemic versus Local

Shared definition used by the review, triage, remediation, and postmortem skills to classify findings and root-cause groups. This file is the single source of truth — skills reference it by path and never restate it.

SA.4 requires that scoring distinguish "between a systemic weakness and a local exception so teams do not optimize for the score at the expense of the architecture." Tag every finding one way or the other:

- **Systemic** — the pattern is the codebase's default. Fixing one instance does not move the attribute score. Remediation is a convention, a shared helper, or an architectural boundary.
- **Local** — a specific deviation from an otherwise sound practice. Fixing the instance moves the score.

A report full of local findings against a systemic root cause is Shoveling Left (FIASSE v1.1 S6.2) with a scorecard attached.
