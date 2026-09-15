#!/usr/bin/env python3
"""Generate per-harness agent bindings from agents/*.md definitions.

Each agent file in agents/ uses the Claude Code subagent format (YAML
frontmatter with name, description, tools; body = system prompt).  This
script compiles every agent into each supported harness's native subagent
format and keeps them in sync.  Agent definitions are generated, never
edited — hand-forked copies are how content rot happens.

Outputs:
  bindings/opencode/agents/<name>.md         opencode markdown agent
  bindings/copilot/agents/<name>.agent.md    GitHub Copilot custom agent
  bindings/cursor/agents/<name>.md           Cursor subagent
  bindings/generic/agents/<name>.md          harness-neutral persona prompt

Modes:
  (default)   write all bindings
  --check     verify committed bindings match the source agents; exit 1 on
              any drift or missing file (used by CI)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO / "agents"

# ── Tool mappings (Claude Code → target harness) ──────────────────────────
#
# Sources:
#   opencode permission field: https://opencode.ai/docs/agents#permissions
#   Copilot custom agents tools: https://docs.github.com/en/copilot/customizing-copilot/extending-the-functionality-of-github-copilot-in-vs-code/creating-a-copilot-agent-in-vs-code
#   Cursor agents tools: https://docs.cursor.com/more/agents
# When multiple Claude Code tools collapse into one target tool, the
# generated header notes the mapping.

# opencode: uses the `permission` field (the `tools` field is deprecated).
# Both Write and Edit map to the `edit` permission key.
OPENCODE_PERM: dict[str, str] = {
    "Read": "read", "Grep": "grep", "Glob": "glob",
    "Bash": "bash", "Write": "edit", "Edit": "edit",
}

# GitHub Copilot: tools list (read, edit, search, execute).
# Grep+Glob → search; Write+Edit → edit; Bash → execute.
COPILOT_TOOLS: dict[str, str] = {
    "Read": "read", "Grep": "search", "Glob": "search",
    "Bash": "execute", "Write": "edit", "Edit": "edit",
}

# Cursor: comma-separated tools (read, search, edit, Bash).
# Grep+Glob → search; Write+Edit → edit.
CURSOR_TOOLS: dict[str, str] = {
    "Read": "read", "Grep": "search", "Glob": "search",
    "Bash": "Bash", "Write": "edit", "Edit": "edit",
}


def generated_header(name: str) -> str:
    return (
        f"<!-- GENERATED from agents/{name}.md by scripts/build_agents.py"
        " — do not edit -->\n"
    )


def parse_agents() -> list[dict]:
    """Parse every agents/*.md file, returning a sorted list of dicts."""
    agents: list[dict] = []
    for p in sorted(AGENTS_DIR.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?\n)---\n(.*)", text, re.S)
        if not m:
            print(f"warning: {p.name} has no YAML frontmatter, skipping",
                  file=sys.stderr)
            continue
        fm = yaml.safe_load(m.group(1))
        body = m.group(2).strip() + "\n"
        tools = [t.strip() for t in fm.get("tools", "").split(",") if t.strip()]
        agents.append({
            "name": fm["name"],
            "description": fm["description"].strip(),
            "tools": tools,
            "model": fm.get("model"),  # reserved for future renderer use
            "body": body,
            "source": p.name,
        })
    return agents


def collapse_tools(tool_map: dict[str, str],
                   source_tools: list[str]) -> list[str]:
    """Map Claude Code tools → target tools, preserving order, deduplicating."""
    seen: list[str] = []
    for t in source_tools:
        mapped = tool_map.get(t)
        if mapped and mapped not in seen:
            seen.append(mapped)
    return seen


def tool_mapping_notes(tool_map: dict[str, str],
                       source_tools: list[str]) -> list[str]:
    """Describe collapsed or omitted tool mappings for the header comment."""
    notes: list[str] = []
    reverse: dict[str, list[str]] = {}
    for t in source_tools:
        mapped = tool_map.get(t)
        if mapped is None:
            notes.append(f"{t}: no equivalent (omitted)")
        else:
            reverse.setdefault(mapped, []).append(t)
    for target, sources in reverse.items():
        if len(sources) > 1:
            notes.append(f"{'+'.join(sources)} → {target}")
    # Flag Write→edit escalation when Edit is not in the source tools.
    # The target harness cannot distinguish create-only from edit; the
    # constraint is promised by the prompt, not held by the harness.
    if "Write" in source_tools and "Edit" not in source_tools:
        mapped = tool_map.get("Write")
        if mapped and mapped == tool_map.get("Edit"):
            notes.append(
                f"Write → {mapped} (create-only intent; platform"
                f" cannot enforce Write-vs-Edit distinction)"
            )
    return notes


def write_only_escalation(tool_map: dict[str, str],
                          source_tools: list[str]) -> bool:
    """True when Write maps to the same target as Edit but Edit is absent.

    When this returns True the generated binding grants broader capability
    than the canonical definition intends: the persona should create new
    report files, not modify existing ones.  Renderers inject a behavioral
    constraint so the agent knows the restriction.
    """
    if "Write" not in source_tools or "Edit" in source_tools:
        return False
    mapped = tool_map.get("Write")
    return mapped is not None and mapped == tool_map.get("Edit")


# The constraint line injected into the prompt body when
# write_only_escalation is True.
_WRITE_ONLY_CONSTRAINT = (
    "\n> **Platform constraint — create only, never edit.** This platform"
    " maps Write to the same tool as Edit. The canonical tool allowlist"
    " grants Write but not Edit: use the edit capability only to create"
    " new report files, never to modify existing files.\n"
)


# ── Renderers ──────────────────────────────────────────────────────────────

def render_opencode(agent: dict) -> str:
    """Render an opencode markdown agent (permission-based, subagent mode)."""
    name = agent["name"]
    header = generated_header(name)
    notes = tool_mapping_notes(OPENCODE_PERM, agent["tools"])

    # Build permission map (deduplicated, order-preserving)
    perms: dict[str, str] = {}
    for t in agent["tools"]:
        key = OPENCODE_PERM.get(t)
        if key and key not in perms:
            perms[key] = "allow"

    # Rewrite ${CLAUDE_PLUGIN_ROOT}/ → .opencode/ for installed-tree paths
    body = agent["body"].replace("${CLAUDE_PLUGIN_ROOT}/", ".opencode/")

    fm: dict = {
        "description": agent["description"],
        "mode": "subagent",
        "permission": perms,
    }
    fm_str = yaml.dump(fm, default_flow_style=False, sort_keys=False,
                       allow_unicode=True, width=120)

    note_comment = ""
    if notes:
        note_comment = ("<!-- Tool mapping: "
                        + "; ".join(notes) + " -->\n")

    constraint = ""
    if write_only_escalation(OPENCODE_PERM, agent["tools"]):
        constraint = _WRITE_ONLY_CONSTRAINT + "\n"

    # Frontmatter must be the first bytes of the file for the harness to parse
    # it; the generated header goes right after the closing delimiter.
    return f"---\n{fm_str}---\n{header}{note_comment}\n{constraint}{body}"


def render_copilot(agent: dict) -> str:
    """Render a GitHub Copilot custom agent (.agent.md)."""
    name = agent["name"]
    header = generated_header(name)
    notes = tool_mapping_notes(COPILOT_TOOLS, agent["tools"])

    tools = collapse_tools(COPILOT_TOOLS, agent["tools"])

    # Copilot has no native skill-discovery path; ${CLAUDE_PLUGIN_ROOT}
    # paths in the prompt require the plugin tree in the repository.
    fm: dict = {"description": agent["description"]}
    if tools:
        fm["tools"] = tools
    fm_str = yaml.dump(fm, default_flow_style=False, sort_keys=False,
                       allow_unicode=True, width=120)

    note_comment = ""
    if notes:
        note_comment = ("<!-- Tool mapping: "
                        + "; ".join(notes) + " -->\n")
    path_note = ("<!-- ${CLAUDE_PLUGIN_ROOT} paths require the plugin tree"
                 " to be present in the repository -->\n")

    constraint = ""
    if write_only_escalation(COPILOT_TOOLS, agent["tools"]):
        constraint = _WRITE_ONLY_CONSTRAINT + "\n"

    return f"---\n{fm_str}---\n{header}{note_comment}{path_note}\n{constraint}{agent['body']}"


def render_cursor(agent: dict) -> str:
    """Render a Cursor subagent (.cursor/agents/*.md format)."""
    name = agent["name"]
    header = generated_header(name)
    notes = tool_mapping_notes(CURSOR_TOOLS, agent["tools"])

    tools = collapse_tools(CURSOR_TOOLS, agent["tools"])

    fm: dict = {
        "name": name,
        "description": agent["description"],
        "tools": ", ".join(tools),
    }
    fm_str = yaml.dump(fm, default_flow_style=False, sort_keys=False,
                       allow_unicode=True, width=120)

    note_comment = ""
    if notes:
        note_comment = ("<!-- Tool mapping: "
                        + "; ".join(notes) + " -->\n")
    path_note = ("<!-- ${CLAUDE_PLUGIN_ROOT} paths require the plugin tree"
                 " to be present in the repository -->\n")

    constraint = ""
    if write_only_escalation(CURSOR_TOOLS, agent["tools"]):
        constraint = _WRITE_ONLY_CONSTRAINT + "\n"

    return f"---\n{fm_str}---\n{header}{note_comment}{path_note}\n{constraint}{agent['body']}"


def render_generic(agent: dict) -> str:
    """Render a harness-neutral persona prompt (no frontmatter)."""
    name = agent["name"]
    header = generated_header(name)
    paste_hint = (
        "<!-- Harness-neutral persona prompt for AGENTS.md-only tools"
        " (Codex, Gemini CLI, Zed, Amp, Aider)."
        " Paste into your tool's agent or prompt configuration. -->\n\n"
    )
    title = name.replace("-", " ").title()
    # Rewrite ${CLAUDE_PLUGIN_ROOT}/ to relative skills/ paths so the prompt
    # works without Claude Code's variable expansion.
    body = agent["body"].replace("${CLAUDE_PLUGIN_ROOT}/", "")
    return f"{header}{paste_hint}# {title}\n\n{body}"


# ── Orchestration ──────────────────────────────────────────────────────────

def render_all(agents: list[dict]) -> dict[Path, str]:
    targets: dict[Path, str] = {}
    for a in agents:
        name = a["name"]
        targets[REPO / "bindings" / "opencode" / "agents" / f"{name}.md"] = \
            render_opencode(a)
        targets[REPO / "bindings" / "copilot" / "agents" / f"{name}.agent.md"] = \
            render_copilot(a)
        targets[REPO / "bindings" / "cursor" / "agents" / f"{name}.md"] = \
            render_cursor(a)
        targets[REPO / "bindings" / "generic" / "agents" / f"{name}.md"] = \
            render_generic(a)
    return targets


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--check", action="store_true",
                    help="verify instead of write; exit 1 on drift or missing")
    args = ap.parse_args()

    agents = parse_agents()
    if not agents:
        print("No agent definitions found in agents/", file=sys.stderr)
        return 1

    targets = render_all(agents)

    if args.check:
        drift: list[str] = []
        for path, content in targets.items():
            rel = path.relative_to(REPO)
            if not path.is_file():
                drift.append(f"{rel}: missing")
            elif path.read_text(encoding="utf-8") != content:
                drift.append(f"{rel}: differs from generated content")

        # Detect orphaned bindings (files with no source agent)
        expected_by_dir: dict[Path, set[Path]] = {}
        for path in targets:
            expected_by_dir.setdefault(path.parent, set()).add(path)
        for out_dir, expected_paths in expected_by_dir.items():
            if out_dir.is_dir():
                for existing in out_dir.iterdir():
                    if existing.is_file() and existing not in expected_paths:
                        rel = existing.relative_to(REPO)
                        drift.append(f"{rel}: stale (no source agent)")

        if drift:
            print(f"{len(drift)} agent binding(s) out of sync"
                  " — run scripts/build_agents.py:")
            for d in drift:
                print(f"  {d}")
            return 1
        print(f"OK — {len(agents)} agents × 4 targets"
              f" = {len(targets)} bindings in sync.")
        return 0

    for path, content in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(REPO)}")

    print(f"\n{len(agents)} agents × 4 targets"
          f" = {len(targets)} bindings written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
