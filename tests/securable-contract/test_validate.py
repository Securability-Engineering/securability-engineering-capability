#!/usr/bin/env python3
"""Tests for scripts/validate_securable.py.

Runs the validator over the shipped valid example and over a set of invalid
fixtures, asserting each invalid fixture fails for the expected reason.
No test framework required: python3 tests/securable-contract/test_validate.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
VALIDATOR = REPO / "scripts" / "validate_securable.py"
EXAMPLES = REPO / "examples" / "securable"

VALID_REQUIREMENTS = (EXAMPLES / "requirements.yaml").read_text(encoding="utf-8")
VALID_BOUNDARIES = (EXAMPLES / "boundaries.yaml").read_text(encoding="utf-8")
VALID_POLICY = (EXAMPLES / "policy.yaml").read_text(encoding="utf-8")
VALID_DEPENDENCIES = (EXAMPLES / "dependencies.yaml").read_text(encoding="utf-8")

# (name, mutate(requirements_text) -> text, expected error substring)
INVALID_CASES = [
    (
        "wrong-contract-version",
        lambda t: t.replace("securable_contract: 1", "securable_contract: 2", 1),
        "'securable_contract: 1' is required",
    ),
    (
        "bad-asvs-level",
        lambda t: t.replace("asvs_level: 2", "asvs_level: 5"),
        "'asvs_level' must be 1, 2, or 3",
    ),
    (
        "nonexistent-asvs-requirement",
        lambda t: t.replace("V6.3.8", "V6.3.99"),
        "6.3.99 not found",
    ),
    (
        "pre-5.0-style-chapter",
        lambda t: t.replace("V16.3.1", "V19.1.1"),
        "chapter V19 not found",
    ),
    (
        "escalation-missing",
        lambda t: t.replace("        escalation: true\n", ""),
        "set 'escalation: true'",
    ),
    (
        "verified-without-evidence",
        lambda t: t.replace("status: planned", "status: verified", 1),
        "requires non-empty 'evidence'",
    ),
    (
        "requirement-id-wrong-feature",
        lambda t: t.replace("id: F-03-R5", "id: F-04-R5"),
        "does not belong to feature F-03",
    ),
    (
        "duplicate-requirement-id",
        lambda t: t.replace("id: F-03-R4", "id: F-03-R1", 1),
        "duplicate id F-03-R1",
    ),
    (
        "unknown-boundary",
        lambda t: t.replace("browser-api, api-email", "browser-api, api-smtp"),
        "boundary 'api-smtp' not defined",
    ),
    (
        "missing-acceptance",
        lambda t: t.replace(
            "        acceptance:\n"
            "          - More than 5 requests for one email within 10 minutes are rejected with HTTP 429 and logged.\n",
            "",
        ),
        "'acceptance' must be a non-empty string or list",
    ),
    (
        "bad-status",
        lambda t: t.replace("status: planned", "status: done", 1),
        "'status' must be one of",
    ),
    (
        "unknown-key",
        lambda t: t.replace("generated_by:", "generated_from:"),
        "unknown top-level key 'generated_from'",
    ),
]


def run_validator(workdir: Path, extra: list[str] | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(VALIDATOR), "--dir", str(workdir)]
    return subprocess.run(cmd + (extra or []), capture_output=True, text=True)


def main() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "requirements.yaml").write_text(VALID_REQUIREMENTS, encoding="utf-8")
        (d / "boundaries.yaml").write_text(VALID_BOUNDARIES, encoding="utf-8")
        proc = run_validator(d)
        if proc.returncode != 0:
            failures.append(f"valid example rejected:\n{proc.stdout}{proc.stderr}")
        else:
            print("ok  valid-example accepted")

    for name, mutate, expected in INVALID_CASES:
        mutated = mutate(VALID_REQUIREMENTS)
        if mutated == VALID_REQUIREMENTS:
            failures.append(f"{name}: mutation did not change the fixture (test bug)")
            continue
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "requirements.yaml").write_text(mutated, encoding="utf-8")
            (d / "boundaries.yaml").write_text(VALID_BOUNDARIES, encoding="utf-8")
            proc = run_validator(d)
            out = proc.stdout + proc.stderr
            if proc.returncode == 0:
                failures.append(f"{name}: expected rejection, validator passed")
            elif expected not in out:
                failures.append(f"{name}: rejected, but without expected message {expected!r}:\n{out}")
            else:
                print(f"ok  {name} rejected as expected")

    # --- Policy: valid example ---
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "policy.yaml").write_text(VALID_POLICY, encoding="utf-8")
        proc = run_validator(d)
        if proc.returncode != 0:
            failures.append(f"valid policy rejected:\n{proc.stdout}{proc.stderr}")
        else:
            print("ok  valid-policy accepted")

    # --- Dependencies: valid example ---
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "requirements.yaml").write_text(VALID_REQUIREMENTS, encoding="utf-8")
        (d / "dependencies.yaml").write_text(VALID_DEPENDENCIES, encoding="utf-8")
        proc = run_validator(d)
        if proc.returncode != 0:
            failures.append(f"valid dependencies rejected:\n{proc.stdout}{proc.stderr}")
        else:
            print("ok  valid-dependencies accepted")

    # --- Policy invalid mutations ---
    POLICY_INVALID = [
        (
            "policy-bad-mode",
            lambda t: t.replace("mode: advisory", "mode: enforce"),
            "'mode' must be one of",
        ),
        (
            "policy-duplicate-gate-id",
            lambda t: t + "\nmode: gate\ngates:\n  - id: G-01\n    description: First gate.\n    when:\n      severity: [HIGH]\n  - id: G-01\n    description: Duplicate.\n    when:\n      severity: [LOW]\n",
            "duplicate gate id G-01",
        ),
        (
            "policy-bad-gate-id",
            lambda t: t + "\nmode: gate\ngates:\n  - id: GATE-1\n    description: Bad id.\n    when:\n      severity: [HIGH]\n",
            "must match G-<n>",
        ),
        (
            "policy-bad-severity",
            lambda t: t + "\nmode: gate\ngates:\n  - id: G-01\n    description: Bad sev.\n    when:\n      severity: [EXTREME]\n",
            "severity 'EXTREME' not in",
        ),
        (
            "policy-bad-attribute",
            lambda t: t + "\nmode: gate\ngates:\n  - id: G-01\n    description: Bad attr.\n    when:\n      attribute_below:\n        authorization: 3\n",
            "not in the ten SSEM attributes",
        ),
        (
            "policy-report-dir-dotdot",
            lambda t: t.replace("report_dir: .securable/reports", "report_dir: ../outside/reports"),
            "must not contain '..' segments",
        ),
    ]

    for name, mutate, expected in POLICY_INVALID:
        mutated = mutate(VALID_POLICY)
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "policy.yaml").write_text(mutated, encoding="utf-8")
            proc = run_validator(d)
            out = proc.stdout + proc.stderr
            if proc.returncode == 0:
                failures.append(f"{name}: expected rejection, validator passed")
            elif expected not in out:
                failures.append(f"{name}: rejected, but without expected message {expected!r}:\n{out}")
            else:
                print(f"ok  {name} rejected as expected")

    # --- Dependencies invalid mutations ---
    DEPS_INVALID = [
        (
            "deps-bad-ecosystem",
            lambda t: t.replace("ecosystem: pypi", "ecosystem: pip", 1),
            "'ecosystem' must be one of",
        ),
        (
            "deps-duplicate-name",
            lambda t: t.replace("name: structlog", "name: pyjwt"),
            "duplicate dependency name 'pyjwt'",
        ),
        (
            "deps-audit-clean-no-tool",
            lambda t: t.replace("tool: pip-audit", "tool: none").replace("result: clean", "result: clean", 1),
            "requires a tool",
        ),
        (
            "deps-tool-none-not-unverified",
            lambda t: t.replace("tool: none\n      result: unverified", "tool: none\n      result: clean"),
            "result must be 'unverified'",
        ),
        (
            "deps-bad-date",
            lambda t: t.replace('checked: "2026-06-15"', 'checked: "not-a-date"', 1),
            "must be a YYYY-MM-DD date",
        ),
        (
            "deps-missing-rationale",
            lambda t: t.replace("rationale: JWT creation and verification for password-reset tokens; stdlib has no JWT support.", "rationale: "),
            "'rationale' is required and must be non-empty",
        ),
        (
            "deps-bad-scope",
            lambda t: t.replace("scope: runtime", "scope: production", 1),
            "'scope' must be one of",
        ),
        (
            "deps-bad-verdict",
            lambda t: t.replace("verdict: healthy", "verdict: good", 1),
            "maintenance.verdict must be one of",
        ),
    ]

    for name, mutate, expected in DEPS_INVALID:
        mutated = mutate(VALID_DEPENDENCIES)
        if mutated == VALID_DEPENDENCIES:
            failures.append(f"{name}: mutation did not change the fixture (test bug)")
            continue
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "dependencies.yaml").write_text(mutated, encoding="utf-8")
            proc = run_validator(d)
            out = proc.stdout + proc.stderr
            if proc.returncode == 0:
                failures.append(f"{name}: expected rejection, validator passed")
            elif expected not in out:
                failures.append(f"{name}: rejected, but without expected message {expected!r}:\n{out}")
            else:
                print(f"ok  {name} rejected as expected")

    # Boundaries-only and requirements-only runs must both work.
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "boundaries.yaml").write_text(VALID_BOUNDARIES, encoding="utf-8")
        if run_validator(d).returncode != 0:
            failures.append("boundaries-only run failed")
        else:
            print("ok  boundaries-only accepted")

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "requirements.yaml").write_text(VALID_REQUIREMENTS, encoding="utf-8")
        proc = run_validator(d)
        # Without boundaries.yaml, unknown-boundary checks are skipped: still valid.
        if proc.returncode != 0:
            failures.append(f"requirements-only run failed:\n{proc.stdout}{proc.stderr}")
        else:
            print("ok  requirements-only accepted")

    # Missing ASVS catalog degrades to a warning, not an error.
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "requirements.yaml").write_text(VALID_REQUIREMENTS, encoding="utf-8")
        proc = run_validator(d, ["--asvs-dir", str(d / "no-catalog")])
        if proc.returncode != 0 or "existence not verified" not in proc.stdout:
            failures.append(f"missing-catalog should warn and pass:\n{proc.stdout}{proc.stderr}")
        else:
            print("ok  missing-catalog degrades to warning")

    if failures:
        print(f"\n{len(failures)} test failure(s):")
        for f in failures:
            print(f"  FAIL {f}")
        return 1
    print("\nAll securable-contract validator tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
