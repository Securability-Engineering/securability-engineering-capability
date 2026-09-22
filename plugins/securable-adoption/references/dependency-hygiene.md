# Dependency Hygiene & Stewardship (generation constraint 8)

Shared reference for the generation skill (`securability-engineering`, Foundational Constraint 8) and the `dependency-stewardship` skill, which audits and records against it. This file is the single source of truth for the constraint's wording.

**Dependency Hygiene & Stewardship** (FIASSE v1.1 S4.5, S4.6) — Default to the latest stable release compatible with the runtime. Prefer packages with low CVE/CWE exposure, active maintenance, and strong release signals. Treat each dependency as an ongoing relationship.

When generating code, apply this constraint to every new import. When auditing, `dependency-stewardship` turns it into a recorded decision in `.securable/dependencies.yaml`.
