# Securable Engineering on opencode

## What this pack gives you on opencode

| Capability | Status | Mechanism |
|---|---|---|
| Always-on kernel | Native | `AGENTS.md` (this repo's AGENTS.md is read automatically) |
| Skills (11) | Native | Discovered from `.opencode/skills/`, `.claude/skills/`, or `.agents/skills/` |
| Commands (12) | Manual | Copy command files into `.opencode/commands/` |
| Personas (10) | Generated binding | `bindings/opencode/agents/<name>.md` copied to `.opencode/agents/` |
| Hooks | Not available | opencode has no native hook lifecycle; run the opengrep rule pack in CI instead |
| Merge-time report | Manual | `scripts/securability_report.sh` with `AGENT_CLI="opencode run"` |

## Install

1. Clone this repository:

   ```bash
   git clone --depth 1 https://github.com/Securability-Engineering/securable-claude-plugin.git /tmp/securable-claude-plugin
   ```

2. Run the layout-preserving installer at the scope you want:

   ```bash
   # Project-level (from the project root):
   /tmp/securable-claude-plugin/scripts/install_skills.sh --target .opencode

   # Global (all projects):
   /tmp/securable-claude-plugin/scripts/install_skills.sh --target "$HOME/.config/opencode"
   ```

   The script copies `skills/`, `data/`, `plays/`, `templates/`, `schema/`,
   `core/`, `rules/`, `agents/`, and `bindings/` together under the target root.
   The sibling layout is load-bearing: relative references inside each `SKILL.md`
   (`../../data/...`, `../../plays/...`) depend on it.

3. Copy the generated persona bindings into place:

   ```bash
   cp -R /tmp/securable-claude-plugin/bindings/opencode/agents/* .opencode/agents/
   ```

4. Optionally copy the slash-command files:

   ```bash
   mkdir -p .opencode/commands
   cp /tmp/securable-claude-plugin/commands/*.md .opencode/commands/
   ```

5. Remove the clone:

   ```bash
   rm -rf /tmp/securable-claude-plugin
   ```

## Always-on kernel

opencode reads `AGENTS.md` by walking up from the current directory to the git
worktree root. When this repository (or an installed copy) is in scope, the
kernel rules in `AGENTS.md` are loaded automatically as always-on instructions.

If you install into a consuming project, the project's own `AGENTS.md` takes
priority. In that case, add the kernel rules to your project's `AGENTS.md`
or use the `instructions` array in `opencode.json` to load the installed
kernel file:

```json
{
  "instructions": [
    ".opencode/core/kernel.md"
  ]
}
```

opencode also falls back to `CLAUDE.md` when `AGENTS.md` is absent (unless
`OPENCODE_DISABLE_CLAUDE_CODE_PROMPT` is set).

## Skills

opencode discovers skills from multiple paths:

- `.opencode/skills/**/SKILL.md` (project)
- `~/.config/opencode/skills/**/SKILL.md` (global)
- `.claude/skills/**/SKILL.md` and `.agents/skills/**/SKILL.md` (project, via Claude Code compatibility)

After installation, the agent discovers skills through its native `skill` tool.
Available skills appear in the `<available_skills>` section shown to the agent.
Verify by asking:

```
Use the fiasse-lookup skill to explain Canonical Parsing.
```

The eleven skills installed are: `securability-engineering-review`, `securability-engineering`, `prd-securability-enhancement`, `fiasse-lookup`, `threat-modeling`, `dependency-stewardship`, `securability-triage`, `securability-remediation`, `securability-verification`, `securability-postmortem`, `fiasse-adoption`.

Skill access is controlled by the `permission` field on each agent (`skill: allow` is the default for built-in agents).

## Commands

opencode custom commands are markdown files in `.opencode/commands/` (project)
or `~/.config/opencode/commands/` (global). The filename without `.md` becomes
the command name, invoked as `/name`.

After copying the command files (step 4 above), twelve slash commands are available: `/securability-review`, `/secure-generate`, `/prd-securability-enhance`, `/fiasse-lookup`, `/threat-model`, `/dependency-steward`, `/securability-triage`, `/securability-remediate`, `/securability-verify`, `/securability-postmortem`, `/fiasse-adoption`, `/securable-status`.

Commands support `$ARGUMENTS` for passed arguments, `$1`/`$2` for positional parameters, `` !`command` `` for shell output injection, and `@filepath` for file content inclusion.

## Personas

Ten task-scoped agent personas are provided as generated bindings under
`bindings/opencode/agents/`. Each file is an opencode-native markdown agent
with YAML frontmatter (`description`, `mode: subagent`, `permission`).

Copy them into `.opencode/agents/` (done in step 3 above). The personas are:

| Persona | Layer | Accountability |
|---|---|---|
| `requirements-partner` | L1 | Security teammate in refinement |
| `boundary-mapper` | L1 | Trust-boundary mapping |
| `securable-builder` | L2 | Pair programmer for securable code |
| `dependency-steward` | L2 | Third-party code stewardship |
| `merge-steward` | L3 | Advisory Securability Report |
| `triage-analyst` | L3 | Scanner output triage |
| `remediation-engineer` | L3 | Review-ready fixes |
| `verification-engineer` | L4 | Executed verification evidence |
| `incident-learner` | L5 | Postmortem lessons to requirements |
| `adoption-coach` | Program | Organizational adoption assessment |

**Invoking personas:**

- **By mention:** type `@merge-steward review this PR` in the chat to invoke
  a specific persona as a subagent.
- **Automatic delegation:** primary agents invoke subagents for specialized
  tasks via the `task` tool, selecting by the subagent's `description`.
- **Via command:** combine a command with a persona by setting the `agent`
  field in the command frontmatter (e.g. `agent: merge-steward`).

Example invocations:

```
# Review layer — invoke the merge steward
@merge-steward Review the current branch against main.

# Build layer — invoke the secure builder
@securable-builder Implement the password-reset endpoint against the contract.

# Triage layer — invoke the triage analyst
@triage-analyst Triage the SARIF output in reports/sast.sarif.
```

**Enforcement note:** tool allowlists in the `permission` frontmatter are
enforced by opencode. Path restrictions (e.g. "writes only
`.securable/requirements.yaml`") are stated in the persona prompt and followed
behaviorally, but not sandboxed by the harness.

## Hooks and held checks

opencode does not have a native hook lifecycle (SessionStart, PostToolUse, etc.). Run the pack's opengrep rule pack manually or in CI instead:

```bash
opengrep scan --config rules/opengrep/securable.yaml .
```

The pack never installs opengrep or any other tool. If opengrep is absent, report that the held checks were not run rather than implying verification happened.

## Merge-time Securability Report

Use `scripts/securability_report.sh` with opencode's non-interactive mode:

```bash
AGENT_CLI="opencode run" scripts/securability_report.sh --base origin/main --head HEAD
```

This produces the FIASSE v1.1 S5.2.1 Securability Report. The report is advisory by default (S5.2.2); gating on it is a separate policy decision (S5.2.3). Alternatively, invoke the merge-steward persona directly: `@merge-steward Produce a securability report for the diff between origin/main and HEAD.`

## Tooling policy reminder

The skills never install scanners or other tools into your project at runtime. If a check cannot run because tooling is absent, the skill reports what was not assessed rather than implying verification happened. CI provisioning (e.g. installing opengrep on a runner) is the consumer's explicit decision.

## Limitations and unverified items

1. **No native hooks.** opencode does not support lifecycle hooks (SessionStart,
   PostToolUse). The session kernel injection and post-edit opengrep checks
   available on Claude Code are not available natively. Workaround: load the
   kernel via the `instructions` config array; run opengrep in CI.

2. **`opencode run` as `AGENT_CLI`.** The non-interactive invocation
   `opencode run` for `scripts/securability_report.sh` was not verified against
   vendor documentation at the time of writing. If it does not work, run the
   merge-steward persona interactively instead.

3. **Command `subtask` field.** The `subtask` field on commands (forces subagent
   invocation) is documented but its availability in markdown frontmatter versus
   JSON config was not fully verified. If commands do not delegate as expected,
   define them in `opencode.json` under the `command` key instead.

4. **Path restrictions are behavioral.** Persona path restrictions (e.g.
   "writes only `.securable/requirements.yaml`") are stated in the system prompt,
   not enforced by the harness. A persona with `edit: allow` can technically
   write anywhere the tool permits.
