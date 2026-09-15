# Cursor

Platform guide for the Securable Engineering skill pack on [Cursor](https://cursor.com).

## What this pack gives you on Cursor

| Capability | Delivery | Notes |
|---|---|---|
| Kernel (always-on) | **Native** | Generated `.mdc` rule with `alwaysApply: true` |
| Skills (11) | **Native** | Agent Skills format; auto-invoked or via `/skill-name` |
| Commands (12) | **Manual** | Cursor commands are plain Markdown in `.cursor/commands/`; copy from `commands/` |
| Personas (10) | **Generated binding** | Cursor subagent format under `bindings/cursor/agents/` |
| Hooks | **Not available** | Cursor does not expose lifecycle hooks in the same way; run opengrep in CI instead |
| Merge-time report | **Manual** | `scripts/securability_report.sh` with your agent CLI |

## Install

### Option A: install_skills.sh (project-local)

From a full checkout of this repository, run the installer targeting `.cursor`:

```bash
scripts/install_skills.sh --target /path/to/your-project/.cursor
```

This copies `skills/`, `data/`, `plays/`, `templates/`, `schema/`, `core/`, `rules/`, `agents/`, and `bindings/` into `.cursor/`, preserving the relative-path layout the skills depend on.

### Option B: manual layout

Copy the trees yourself, keeping them as siblings under one root:

```
.cursor/
  skills/           # from skills/
  data/             # from data/
  plays/            # from plays/
  templates/        # from templates/
  agents/           # copy from bindings/cursor/agents/
  rules/
    securable.mdc   # copy from bindings/cursor/securable.mdc
```

Cursor discovers skills from `.cursor/skills/<name>/SKILL.md` at startup, loading only `name` and `description` from frontmatter until a skill is invoked.

## Always-on kernel

The generated kernel rule lives at:

```
bindings/cursor/securable.mdc
```

Copy it to `.cursor/rules/securable.mdc` in your project. Its frontmatter sets `alwaysApply: true`, so Cursor includes the five securable engineering rules in every chat session regardless of the active file.

The rule is generated from `core/kernel.md` by `scripts/build_bindings.py`. Never edit the `.mdc` file directly; edit `core/kernel.md` and rebuild:

```bash
python3 scripts/build_bindings.py
```

Cursor rule precedence (highest to lowest): Team Rules > Project Rules > User Rules > Legacy `.cursorrules` > `AGENTS.md`. The `.mdc` rule sits at project level. Cursor also reads `AGENTS.md` at lowest precedence, so the kernel instructions in `AGENTS.md` provide a fallback even without the rule file, but at the bottom of the priority stack.

## Skills

Cursor discovers skills from `.cursor/skills/<name>/SKILL.md` (project-level) and `~/.cursor/skills/<name>/SKILL.md` (user-level). It also discovers from `.claude/skills/` and `.codex/skills/` paths.

The eleven skills in this pack:

- `securability-engineering-review`
- `securability-engineering`
- `prd-securability-enhancement`
- `fiasse-lookup`
- `threat-modeling`
- `dependency-stewardship`
- `securability-triage`
- `securability-remediation`
- `securability-verification`
- `securability-postmortem`
- `fiasse-adoption`

**Invocation**: Cursor invokes skills automatically when the agent determines the task matches the skill's `description` frontmatter, or manually by typing `/skill-name` in chat. Setting `disable-model-invocation: true` in a skill's frontmatter restricts it to manual invocation only.

**Verify the install** with a one-line prompt:

```
Review this file for securability
```

The agent should load `securability-engineering-review` and produce an SSEM scorecard.

## Commands

Cursor custom commands are plain Markdown files (no YAML frontmatter) stored in `.cursor/commands/` (project-level) or `~/.cursor/commands/` (global). The filename without `.md` becomes the command name, invoked by typing `/` in chat.

This pack ships twelve command dispatchers in `commands/`:

`securability-review`, `secure-generate`, `prd-securability-enhance`, `fiasse-lookup`, `threat-model`, `dependency-steward`, `securability-triage`, `securability-remediate`, `securability-verify`, `securability-postmortem`, `fiasse-adoption`, `securable-status`

These are thin dispatchers that delegate to their corresponding skill. To use them in Cursor, copy the files from `commands/` into `.cursor/commands/` in your project. Note that Cursor commands are plain Markdown with no frontmatter, while the pack's command files may contain frontmatter for Claude Code; the body content (the dispatch instruction) still works as a Cursor command prompt.

## Personas

The pack includes ten task-scoped agent personas. Pre-generated Cursor subagent bindings live at:

```
bindings/cursor/agents/<name>.md
```

Copy them to `.cursor/agents/` in your project to register them as Cursor subagents. Each binding file has Cursor-native YAML frontmatter (`name`, `description`, `tools`) and a system-prompt body.

The ten personas:

| Persona | Layer | Role |
|---|---|---|
| `requirements-partner` | L1 | Security teammate in refinement |
| `boundary-mapper` | L1 | Trust-boundary and threat-model mapping |
| `securable-builder` | L2 | Pair programmer for securable code |
| `dependency-steward` | L2 | Third-party code stewardship |
| `merge-steward` | L3 | Advisory Securability Report |
| `triage-analyst` | L3 | Scanner-output triage |
| `remediation-engineer` | L3 | Review-ready security fixes |
| `verification-engineer` | L4 | Contract verification and release posture |
| `incident-learner` | L5 | Post-incident lessons and corrective requirements |
| `adoption-coach` | Program | Organizational FIASSE adoption guidance |

**Invocation**: Cursor subagents are invoked by automatic delegation based on the task and description, by explicit request by name in a prompt (e.g. "Use the merge-steward subagent"), or by `@`-mention syntax (e.g. `@"merge-steward (agent)"`).

**Example -- review a PR for securability**:

```
@"merge-steward (agent)" Review the diff on this branch for securability
```

**Example -- enhance a PRD**:

```
Use the requirements-partner to add ASVS L1 coverage to docs/prd.md
```

The bindings are generated from `agents/*.md` by `scripts/build_agents.py`. Never edit the bindings directly; edit the source agent files and rebuild:

```bash
python3 scripts/build_agents.py
```

Verify with `python3 scripts/build_agents.py --check`.

If the generated bindings do not work as expected, the generic fallback is to paste the persona body from `bindings/generic/agents/<name>.md` as the system prompt in a Cursor subagent file you create manually.

## Hooks and held checks

Cursor does not expose the lifecycle hook mechanism (SessionStart, PostToolUse) that Claude Code uses. The pack's two opt-in hooks (session kernel injection and post-edit opengrep held checks) are not available natively.

**Manual equivalent for held checks**: run opengrep with the pack's rule set in your CI pipeline:

```bash
opengrep --config rules/opengrep/ --target <paths>
```

`opengrep` must already be installed in your CI environment. The pack never installs tooling at runtime (see Tooling Policy below). If opengrep is absent, state that the held checks were not run rather than implying they passed.

## Merge-time Securability Report

`scripts/securability_report.sh` produces a FIASSE v1.1 S5.2.1 Securability Report for a diff. It reads the prompt from stdin and sends it to whatever agent CLI `AGENT_CLI` names:

```bash
AGENT_CLI="cursor --agent merge-steward" scripts/securability_report.sh \
  --base origin/main --head HEAD --out report.md
```

> **Note**: The `AGENT_CLI` value shown above is not verified against vendor documentation at the time of writing. If Cursor does not support a non-interactive CLI mode, the alternative is to invoke the merge-steward persona interactively: open Cursor, `@"merge-steward (agent)"`, and paste the diff or branch range.

The report is advisory by default (S5.2.2): it directs attention. Gating on the report is a separate, explicit policy decision (S5.2.3).

## Tooling policy reminder

Nothing is installed at runtime. Skills, personas, and the kernel use only the tools already present in the project. When a check cannot run because tooling is absent (e.g. no `opengrep` on PATH), the skill reports that absence as evidence rather than implying verification happened. CI provisioning (agent CLI, opengrep, etc.) is the consuming team's explicit decision.

## Limitations and unverified items

1. **Cursor plugin manifest** (`.cursor-plugin/plugin.json`): the claim that Cursor discovers plugins from `.cursor-plugin/plugin.json` with a `skills` field pointing at the skills tree is not verified against vendor documentation at the time of writing. The instructions above use the verified `.cursor/skills/` discovery path instead.
2. **Cursor CLI non-interactive mode**: whether Cursor exposes a non-interactive CLI invocation (for use as `AGENT_CLI` in `securability_report.sh`) is not verified against vendor documentation at the time of writing. The fallback is to run the merge-steward persona interactively.
3. **Subagent frontmatter fields**: some optional fields documented by community sources (`hooks`, `isolation`, `memory`, `initialPrompt`, `background`) may be community conventions rather than officially supported Cursor features. The generated bindings use only the core verified fields: `name`, `description`, and `tools`.
4. **Lifecycle hooks**: Cursor's hook support (if any) for pre/post tool-use events is not verified. The guide recommends CI-based opengrep instead.
5. **Commands frontmatter stripping**: this pack's `commands/*.md` files may carry YAML frontmatter intended for Claude Code. Cursor commands are plain Markdown with no frontmatter. If pasting directly, strip the `---` fenced frontmatter block; the body content works as-is.
