# Gemini CLI

Platform guide for the Securable Engineering skill pack on [Gemini CLI](https://github.com/google-gemini/gemini-cli).

## What this pack gives you on Gemini CLI

| Capability | Status | Mechanism |
|---|---|---|
| Always-on kernel | Generated binding | `bindings/gemini/GEMINI.md` placed in the project root or `~/.gemini/` |
| Skills (11) | Native | Discovered from `.gemini/skills/` or `.agents/skills/` |
| Commands (12) | Manual | Create TOML stubs in `.gemini/commands/` (see Commands section) |
| Personas (10) | Manual | No native persona format; paste from `bindings/generic/agents/<name>.md` as a prompt |
| Hooks | Not available | No native hook lifecycle found in vendor documentation reviewed at time of writing; run the opengrep rule pack in CI instead |
| Merge-time report | Manual | Run the merge-steward persona prompt on the diff |

## Install

1. Clone this repository:

   ```bash
   git clone --depth 1 https://github.com/Securability-Engineering/securable-claude-plugin.git /tmp/securable-clone
   ```

2. Run the layout-preserving installer into the `.agents` tree (Gemini CLI
   discovers skills from `.agents/skills/`):

   ```bash
   /tmp/securable-clone/scripts/install_skills.sh --target .agents
   ```

   The script copies `skills/`, `data/`, `plays/`, `templates/`, `schema/`,
   `core/`, `rules/`, `agents/`, `bindings/`, and `docs/` together. The sibling layout
   is load-bearing: relative references inside each `SKILL.md` depend on it.

3. Copy the always-on kernel binding into your project:

   ```bash
   cp /tmp/securable-clone/bindings/gemini/GEMINI.md ./GEMINI.md
   ```

   Or, if you already have a project `GEMINI.md`, append the kernel to it:

   ```bash
   cat /tmp/securable-clone/bindings/gemini/GEMINI.md >> ./GEMINI.md
   ```

4. Create TOML command stubs for the twelve slash commands (see the
   [Commands](#commands-prompt-equivalents) section below).

5. Remove the clone:

   ```bash
   rm -rf /tmp/securable-clone
   ```

## Always-on kernel

Gemini CLI loads `GEMINI.md` from three tiers: global (`~/.gemini/GEMINI.md`),
workspace directories up to `.git`, and just-in-time when tools access new
directories. All found files are concatenated and sent with every prompt.

The generated kernel binding is at `bindings/gemini/GEMINI.md`. Place it as the
project-root `GEMINI.md` or append it to an existing one. `GEMINI.md` supports
`@file.md` imports, so you can also keep the kernel separate:

```markdown
@.agents/core/kernel.md
```

To make Gemini CLI also discover `AGENTS.md` files natively, set
`context.fileName` in `settings.json`:

```json
{ "context": { "fileName": ["GEMINI.md", "AGENTS.md"] } }
```

Verify with `/memory show`; reload after changes with `/memory reload`.

## Skills

Gemini CLI discovers skills from four tiers (increasing precedence): built-in,
extension, user (`~/.gemini/skills/` or `~/.agents/skills/`), and workspace
(`.gemini/skills/` or `.agents/skills/`). Within a tier, `.agents/skills/`
takes precedence over `.gemini/skills/`.

After installation into `.agents/`, eleven skills are discoverable:
`securability-engineering-review`, `securability-engineering`,
`prd-securability-enhancement`, `fiasse-lookup`, `threat-modeling`,
`dependency-stewardship`, `securability-triage`, `securability-remediation`,
`securability-verification`, `securability-postmortem`, `fiasse-adoption`.

Skills activate via the `activate_skill` tool when the model matches a task to
the skill's description. Verify with:

```
Use the fiasse-lookup skill to explain Canonical Parsing.
```

## Commands (prompt equivalents)

Gemini CLI custom commands are TOML files in `~/.gemini/commands/` (global) or
`<project>/.gemini/commands/` (project). The filename minus `.toml` becomes the
slash command. Subdirectories create namespaced commands (e.g. `sec/review.toml`
becomes `/sec:review`). Fields: `prompt` (required), `description` (optional).
Templates support `{{args}}`, `!{shell}`, and `@{path}` injection.

Create `.gemini/commands/` and add a TOML file for each command. Example:

```toml
# .gemini/commands/securability-review.toml
description = "Run a FIASSE/SSEM securability engineering review"
prompt = """
Activate the securability-engineering-review skill and run a full review.
Focus on: {{args}}
"""
```

The twelve commands to create stubs for:

| Command file | Dispatches to skill |
|---|---|
| `securability-review.toml` | `securability-engineering-review` |
| `secure-generate.toml` | `securability-engineering` |
| `prd-securability-enhance.toml` | `prd-securability-enhancement` |
| `fiasse-lookup.toml` | `fiasse-lookup` |
| `threat-model.toml` | `threat-modeling` |
| `dependency-steward.toml` | `dependency-stewardship` |
| `securability-triage.toml` | `securability-triage` |
| `securability-remediate.toml` | `securability-remediation` |
| `securability-verify.toml` | `securability-verification` |
| `securability-postmortem.toml` | `securability-postmortem` |
| `fiasse-adoption.toml` | `fiasse-adoption` |
| `securable-status.toml` | (contract status check) |

Each stub follows the same pattern: a `description` and a `prompt` that
activates the skill with `{{args}}`. Reload with `/commands reload`.

## Personas

Gemini CLI does not support user-defined named agent personas. Custom commands
are prompt templates, not agent definitions; `agents.overrides` only tweaks
built-in agents.

**Fallback:** use `@{path}` in a custom command to inject the persona body from
`bindings/generic/agents/<name>.md`. The ten personas are:

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

Example: create a command that loads the merge-steward persona:

```toml
# .gemini/commands/merge-steward.toml
description = "Run the merge-steward persona for a securability report"
prompt = """
@{.agents/bindings/generic/agents/merge-steward.md}

Review the diff between origin/main and HEAD. Produce the advisory
Securability Report following the securability-engineering-review skill.
Focus on: {{args}}
"""
```

Example invocations (assuming the TOML stubs above exist):

```
# Review layer
/merge-steward the changes in this PR

# Build layer
/secure-generate Implement the password-reset endpoint against the contract.

# Triage layer
/securability-triage Triage the SARIF output in reports/sast.sarif.
```

**Enforcement note:** tool restrictions in the generic persona files are
behavioral only. Global tool access is controlled via `settings.json` keys:
`tools.core`, `tools.allowed`, `tools.confirmationRequired`, `tools.exclude`.

## Hooks and held checks

No native hook lifecycle (SessionStart, PostToolUse) was found in vendor
documentation reviewed at the time of writing. Run the opengrep rule pack
manually or in CI instead:

```bash
opengrep scan --config rules/opengrep/securable.yaml .
```

The pack never installs opengrep. If it is absent, report that held checks were
not run rather than implying verification happened.

## Merge-time Securability Report

Whether Gemini CLI supports a non-interactive mode suitable for
`scripts/securability_report.sh` was not verified against vendor documentation
at the time of writing. If available, use it as `AGENT_CLI`:

```bash
AGENT_CLI="gemini <non-interactive-flag>" scripts/securability_report.sh \
  --base origin/main --head HEAD
```

Otherwise, invoke the merge-steward persona interactively (`/merge-steward`) or
ask directly to activate the `securability-engineering-review` skill on the diff.

The report is advisory by default (FIASSE S5.2.2); gating on it is a separate
policy decision (S5.2.3).

## Tooling policy reminder

The skills never install scanners or other tools into your project at runtime.
If a check cannot run because tooling is absent, the skill reports what was not
assessed rather than implying verification happened. CI provisioning (e.g.
installing opengrep on a runner) is the consumer's explicit decision.

## Limitations and unverified items

1. **No native personas.** Generic persona bindings (`bindings/generic/agents/*.md`) are prompt text only; tool restrictions and model pinning are not enforced.
2. **No native hooks.** No SessionStart or PostToolUse lifecycle found in vendor documentation reviewed at the time of writing. Workaround: load the kernel via `GEMINI.md`; run opengrep in CI.
3. **Non-interactive CLI mode.** Not verified against vendor documentation at the time of writing. If unavailable, run the merge-steward persona interactively.
4. **Path restrictions are behavioral.** Persona write restrictions are stated in the prompt, not sandboxed by the harness.
5. **TOML command stubs are manual.** The pack does not ship pre-built TOML files; the twelve stubs must be created following the pattern above.
6. **Model pinning per persona.** Model is global (`model.name` in `settings.json`). Per-persona model tiering must be applied globally or ignored.
