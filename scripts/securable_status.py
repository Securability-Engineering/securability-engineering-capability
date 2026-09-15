#!/usr/bin/env python3
"""Print a markdown (or JSON) status summary of the securable contract.

Reads a --dir (default .securable) containing requirements.yaml (required),
and optionally boundaries.yaml, dependencies.yaml, and policy.yaml.

Reports per-feature requirement counts (planned/implemented/verified),
unverified requirement ids, cross-cutting totals, dependency review status,
and policy mode.

Options:
  --json                          Machine-readable JSON output.
  --changed-files FILE-OR-LIST    Comma-separated paths (or @file with one
                                  path per line) to report which boundaries
                                  are touched and which requirements on those
                                  boundaries are not verified.
  --fail-on-unverified-touched    Exit 1 if any touched boundary has
                                  unverified requirements (for gate-mode CI).

Boundary-touch heuristic: a boundary is touched when any of its entry_points
strings, or its id, appears in the text of a changed file, or when the file
path contains the boundary id. This is a text-based heuristic, not an AST
analysis; it will over-match on short ids.

Exit 0 = success (or advisory). Exit 1 = --fail-on-unverified-touched and
unverified requirements exist on touched boundaries.

Usage:
  scripts/securable_status.py [--dir .securable]
  scripts/securable_status.py --dir .securable --json
  scripts/securable_status.py --dir .securable --changed-files src/auth.py,src/reset.py
  scripts/securable_status.py --dir .securable --changed-files @changed.txt --fail-on-unverified-touched
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("error: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)


def load_yaml_file(path: Path):
    if not path.is_file():
        return None
    try:
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        print(f"error: failed to parse {path}: {exc}", file=sys.stderr)
        sys.exit(1)


def gather_status(directory: Path) -> dict:
    req_path = directory / "requirements.yaml"
    bnd_path = directory / "boundaries.yaml"
    dep_path = directory / "dependencies.yaml"
    pol_path = directory / "policy.yaml"

    req_data = load_yaml_file(req_path)
    if req_data is None:
        print(f"error: {req_path} not found — the status script requires requirements.yaml even when other contract files exist", file=sys.stderr)
        sys.exit(1)
    if not isinstance(req_data, dict):
        print(f"error: {req_path} top-level value must be a YAML mapping, got {type(req_data).__name__}", file=sys.stderr)
        sys.exit(1)

    bnd_data = load_yaml_file(bnd_path)
    dep_data = load_yaml_file(dep_path)
    pol_data = load_yaml_file(pol_path)

    features = []
    for feat in req_data.get("features") or []:
        if not isinstance(feat, dict):
            print(f"warning: skipping non-dict feature entry: {feat!r}", file=sys.stderr)
            continue
        fid = feat.get("id", "?")
        title = feat.get("title", "")
        reqs = feat.get("requirements") or []
        counts = {"planned": 0, "implemented": 0, "verified": 0}
        unverified_ids = []
        for r in reqs:
            if not isinstance(r, dict):
                print(f"warning: {fid}: skipping non-dict requirement entry: {r!r}", file=sys.stderr)
                continue
            status = r.get("status", "planned")
            if status not in counts:
                print(f"warning: {fid}: unknown status '{status}', counting as planned", file=sys.stderr)
                status = "planned"
            counts[status] = counts.get(status, 0) + 1
            if status != "verified":
                unverified_ids.append(r.get("id", "?"))
        features.append({
            "id": fid,
            "title": title,
            "boundaries": feat.get("boundaries", []),
            "counts": counts,
            "unverified_ids": unverified_ids,
        })

    cc_reqs = req_data.get("cross_cutting") or []
    cc_counts = {"planned": 0, "implemented": 0, "verified": 0}
    cc_unverified = []
    for r in cc_reqs:
        if not isinstance(r, dict):
            print(f"warning: cross_cutting: skipping non-dict requirement entry: {r!r}", file=sys.stderr)
            continue
        status = r.get("status", "planned")
        if status not in cc_counts:
            print(f"warning: cross_cutting: unknown status '{status}', counting as planned", file=sys.stderr)
            status = "planned"
        cc_counts[status] = cc_counts.get(status, 0) + 1
        if status != "verified":
            cc_unverified.append(r.get("id", "?"))

    total_planned = sum(f["counts"]["planned"] for f in features) + cc_counts["planned"]
    total_implemented = sum(f["counts"]["implemented"] for f in features) + cc_counts["implemented"]
    total_verified = sum(f["counts"]["verified"] for f in features) + cc_counts["verified"]
    total = total_planned + total_implemented + total_verified

    # Dependencies
    dep_issues = []
    if dep_data and isinstance(dep_data, dict) and isinstance(dep_data.get("dependencies"), list):
        from datetime import date
        today = date.today().isoformat()
        for dep in dep_data["dependencies"]:
            if not isinstance(dep, dict):
                print(f"warning: skipping non-dict dependency entry: {dep!r}", file=sys.stderr)
                continue
            name = dep.get("name", "?")
            nr = dep.get("next_review")
            audit_result = (dep.get("audit") or {}).get("result", "unverified")
            if nr and nr <= today:
                dep_issues.append({"name": name, "issue": f"past next_review ({nr})"})
            if audit_result == "unverified":
                dep_issues.append({"name": name, "issue": "audit unverified"})

    policy_mode = None
    if pol_data and isinstance(pol_data, dict):
        policy_mode = pol_data.get("mode", "advisory")

    return {
        "system": req_data.get("system", ""),
        "asvs_level": req_data.get("asvs_level"),
        "features": features,
        "cross_cutting": {"counts": cc_counts, "unverified_ids": cc_unverified},
        "totals": {
            "planned": total_planned,
            "implemented": total_implemented,
            "verified": total_verified,
            "total": total,
        },
        "dependency_issues": dep_issues,
        "policy_mode": policy_mode,
        "boundaries": bnd_data.get("boundaries", []) if isinstance(bnd_data, dict) else [],
    }


def resolve_changed_files(arg: str) -> list[str]:
    if arg.startswith("@"):
        fpath = Path(arg[1:])
        if not fpath.is_file():
            print(f"error: file list '{fpath}' not found", file=sys.stderr)
            sys.exit(1)
        return [line.strip() for line in fpath.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [p.strip() for p in arg.split(",") if p.strip()]


def check_touched_boundaries(status: dict, changed_files: list[str]) -> list[dict]:
    """Determine which boundaries are touched by changed files.

    Heuristic: a boundary is touched when any of its entry_points strings,
    or its id, appears in the text of a changed file, or when the file path
    contains the boundary id. This is a text-based heuristic, not an AST
    analysis; it will over-match on short ids.
    """
    boundaries = status["boundaries"]
    if not boundaries:
        return []

    # Read file contents (best-effort)
    file_texts: dict[str, str] = {}
    for fp in changed_files:
        p = Path(fp)
        if p.is_file():
            try:
                file_texts[fp] = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                file_texts[fp] = ""
        else:
            file_texts[fp] = ""

    # Build boundary lookup
    feature_boundary_map: dict[str, list[dict]] = {}
    for feat in status["features"]:
        for bid in feat.get("boundaries", []):
            feature_boundary_map.setdefault(bid, []).append(feat)

    touched = []
    for bnd in boundaries:
        if not isinstance(bnd, dict):
            continue
        bid = bnd.get("id", "")
        entry_points = bnd.get("entry_points", []) or []
        needles = [bid] + entry_points

        is_touched = False
        for fp, text in file_texts.items():
            # Check if file path contains boundary id
            if bid and bid in fp:
                is_touched = True
                break
            # Check if any needle appears in file text
            for needle in needles:
                if needle and needle in text:
                    is_touched = True
                    break
            if is_touched:
                break

        if is_touched:
            unverified_on_boundary = []
            for feat in feature_boundary_map.get(bid, []):
                unverified_on_boundary.extend(feat["unverified_ids"])
            touched.append({
                "boundary_id": bid,
                "unverified_requirement_ids": unverified_on_boundary,
            })

    return touched


def print_markdown(status: dict, touched: list[dict] | None) -> None:
    system = status["system"]
    if system:
        print(f"# Securable Status: {system}\n")
    else:
        print("# Securable Status\n")

    print(f"ASVS level: {status['asvs_level']}\n")

    print("## Features\n")
    print("| Feature | Planned | Implemented | Verified | Unverified IDs |")
    print("|---------|---------|-------------|----------|----------------|")
    for feat in status["features"]:
        c = feat["counts"]
        uv = ", ".join(feat["unverified_ids"]) if feat["unverified_ids"] else "—"
        print(f"| {feat['id']} {feat['title']} | {c['planned']} | {c['implemented']} | {c['verified']} | {uv} |")

    cc = status["cross_cutting"]
    if cc["counts"]["planned"] + cc["counts"]["implemented"] + cc["counts"]["verified"] > 0:
        print(f"\n## Cross-Cutting\n")
        c = cc["counts"]
        uv = ", ".join(cc["unverified_ids"]) if cc["unverified_ids"] else "—"
        print(f"Planned: {c['planned']}  Implemented: {c['implemented']}  Verified: {c['verified']}")
        print(f"Unverified: {uv}")

    t = status["totals"]
    print(f"\n## Totals\n")
    print(f"Total requirements: {t['total']}  "
          f"Planned: {t['planned']}  Implemented: {t['implemented']}  Verified: {t['verified']}")

    if status["dependency_issues"]:
        print(f"\n## Dependency Issues\n")
        for di in status["dependency_issues"]:
            print(f"- **{di['name']}**: {di['issue']}")

    if status["policy_mode"] is not None:
        print(f"\n## Policy\n")
        print(f"Mode: {status['policy_mode']}")

    if touched is not None:
        print(f"\n## Touched Boundaries\n")
        if not touched:
            print("No boundaries touched by changed files.")
        else:
            for tb in touched:
                uv = ", ".join(tb["unverified_requirement_ids"]) if tb["unverified_requirement_ids"] else "—"
                print(f"- **{tb['boundary_id']}**: unverified requirements: {uv}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=".securable", help="directory holding the contract files (default .securable)")
    ap.add_argument("--json", action="store_true", dest="json_output", help="machine-readable JSON output")
    ap.add_argument("--changed-files", help="comma-separated paths or @file to check boundary touches")
    ap.add_argument("--fail-on-unverified-touched", action="store_true",
                    help="exit 1 if touched boundaries have unverified requirements")
    args = ap.parse_args()

    status = gather_status(Path(args.dir))

    touched = None
    if args.changed_files:
        changed = resolve_changed_files(args.changed_files)
        touched = check_touched_boundaries(status, changed)

    if args.json_output:
        output = {
            "system": status["system"],
            "asvs_level": status["asvs_level"],
            "features": status["features"],
            "cross_cutting": status["cross_cutting"],
            "totals": status["totals"],
            "dependency_issues": status["dependency_issues"],
            "policy_mode": status["policy_mode"],
        }
        if touched is not None:
            output["touched_boundaries"] = touched
        print(json.dumps(output, indent=2))
    else:
        print_markdown(status, touched)

    if args.fail_on_unverified_touched and touched:
        has_unverified = any(tb["unverified_requirement_ids"] for tb in touched)
        if has_unverified:
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
