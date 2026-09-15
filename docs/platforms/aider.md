# Aider

Platform guide for using the Securable Engineering skill pack with
[Aider](https://aider.chat).

## What this pack gives you on Aider

| Layer | Feature | Aider support |
|-------|---------|---------------|
| Always-on | Securability kernel | **Generated binding** — `bindings/aider/CONVENTIONS.md` loaded via `read:` config |
| Depth | Skills (11) | **Not available** — Aider has no skill discovery system |
| Invocation | Commands / prompts | **Not available** — user-defined custom slash commands were not found in verified vendor documentation (see Limitations) |
| Role | Personas (10) | **Manual** — paste the generic persona prompt from `bindings/generic/agents/<name>.md` into the session |
| Guard | Hooks / held checks | **Not available** — Aider has no hook system; run opengrep in CI instead |
| Report | Merge-time Securability Report | **Manual** — run the merge-steward persona on the diff, or use `scripts/securability_report.sh` with a compatible `AGENT_CLI` |

## Install

Aider reads always-on context from files listed in its `read:` configuration
key. There is no plugin or skill installer to run; you add the generated
kernel binding to your project and point Aider at it.

1. Copy the generated binding into your project:

   ```bash
   # From a clone of the skill pack repository
   cp bindings/aider/CONVENTIONS.md <your-project>/CONVENTIONS.md
   ```

2. Tell Aider to load it. In your project's `.aider.conf.yml`:

   ```yaml
   read: CONVENTIONS.md
   ```

   Alternatively, pass it on the command line:

   ```bash
   aider --read CONVENTIONS.md
   ```

   Files loaded via `read:` are added as read-only context in every session
   and enable prompt caching.

3. The `.aider.conf.yml` file is discovered in the home directory, project
   root, or current directory (in that order). The extension must be `.yml`,
   not `.yaml`.

## Always-on kernel

The file `bindings/aider/CONVENTIONS.md` is a generated binding of the
securability kernel (`core/kernel.md`, roughly 300 tokens). It contains the
five securable engineering rules that apply to every code change:

1. Parse, don't trust (canonical parsing at trust boundaries)
2. Authority is server-side (isolated integrity)
3. Never-emit list (string-built queries, weak JWT verification, mass
   assignment, silent failures, unbounded reads, missing timeouts, leaked
   secrets, non-constant-time compares)
4. Observable security (structured audit events, logged failures, safe errors)
5. Securability Notes (close security-relevant work with boundary and decision
   summary)

The binding also references the securable contract
(`.securable/requirements.yaml`) when present in the target project.
Do not edit the generated file; regenerate with `python3 scripts/build_bindings.py`.

## Skills

Aider has no agent, persona, subagent, or skill system. The eleven skills
shipped in `skills/` cannot be auto-discovered or invoked by name.

To use a skill's procedure manually, paste the relevant `SKILL.md` content
into your Aider session as context. For example, to run a securability review:

```bash
aider --read skills/securability-engineering-review/SKILL.md
```

Available skills:

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

Each skill's `SKILL.md` contains relative references to `data/`, `plays/`,
and `templates/` that expect the repository layout. When loading a skill
manually, ensure the skill pack tree is accessible (clone it alongside your
project or use `--read` with the full path).

## Commands or prompt equivalents

Aider has built-in slash commands (`/read`, `/add`, `/drop`, `/ask`, etc.).
Whether Aider supports user-defined custom slash commands or reusable prompt
templates was not verified against vendor documentation at the time of writing
(see Limitations).

The twelve commands in the skill pack (`commands/*.md`) are Claude Code
dispatchers and cannot be used directly. To approximate them, paste the
corresponding skill procedure into your session:

| Pack command | Equivalent in Aider |
|---|---|
| `/securability-review` | `--read skills/securability-engineering-review/SKILL.md` then ask for a review |
| `/secure-generate` | `--read skills/securability-engineering/SKILL.md` then request code |
| `/prd-securability-enhance` | `--read skills/prd-securability-enhancement/SKILL.md` then provide a PRD |
| `/fiasse-lookup` | `--read skills/fiasse-lookup/SKILL.md` then ask a FIASSE question |
| `/threat-model` | `--read skills/threat-modeling/SKILL.md` then request a threat model |

## Personas

Aider has no agent persona or subagent system. The ten personas defined in
`agents/*.md` cannot be loaded as named agents with tool restrictions and
model selection.

**Generic fallback**: paste the full persona prompt from
`bindings/generic/agents/<name>.md` into your Aider session as read-only
context. These are generated, harness-neutral versions of each persona.

Available persona bindings under `bindings/generic/agents/`:

- `adoption-coach.md`
- `boundary-mapper.md`
- `dependency-steward.md`
- `incident-learner.md`
- `merge-steward.md`
- `remediation-engineer.md`
- `requirements-partner.md`
- `securable-builder.md`
- `triage-analyst.md`
- `verification-engineer.md`

**Example — running a merge-steward review**:

```bash
aider --read bindings/generic/agents/merge-steward.md \
      --read bindings/aider/CONVENTIONS.md
# Then ask: "Review the current diff as the merge steward"
```

Note: Aider does not enforce tool allowlists or path restrictions. The
persona prompt requests these constraints, but they are advisory only.

## Hooks and held checks

Aider has no lifecycle hook system. The plugin's `SessionStart` kernel
injection and `PostToolUse` opengrep held-check hooks
(`SECURABLE_KERNEL_HOOK`, `SECURABLE_HELD_CHECKS` environment variables)
are Claude Code features and do not apply here.

**Manual equivalent**: run the pack's opengrep rules in CI or locally:

```bash
opengrep scan --config rules/opengrep/securable.yaml .
```

This requires `opengrep` to be installed and on `PATH`. The skill pack
never installs tooling at runtime; if opengrep is absent, skip this step
and note the gap.

## Merge-time Securability Report

`scripts/securability_report.sh` produces a FIASSE v1.1 S5.2.1 Securability
Report by piping the diff and the review skill to an agent CLI.

Aider's non-interactive mode was not verified against vendor documentation
at the time of writing. If Aider supports a non-interactive prompt mode,
set `AGENT_CLI` accordingly:

```bash
AGENT_CLI="aider --yes --message" scripts/securability_report.sh --base origin/main
```

Otherwise, run the merge-steward persona on the diff manually (see the
Personas section above), or use a different agent CLI that has a verified
non-interactive mode (e.g., `claude -p --output-format text`).

## Tooling policy reminder

The skill pack never installs packages, scanners, or frameworks at runtime.
Skills report what they found with the tools already present; absence of a
tool is reported as `Not assessed`, never papered over with a fabricated
result. Consumer teams provision their own CI tooling.

## Limitations and unverified items

- **No skill discovery**: Aider cannot auto-discover or invoke skills by
  name. Skills must be loaded manually via `--read`.
- **No custom commands**: user-defined custom slash commands were not found
  in verified vendor documentation at the time of writing; pack commands
  must be approximated by loading the corresponding skill.
- **No persona enforcement**: tool allowlists and path restrictions in
  persona prompts are advisory; Aider does not enforce them.
- **No hooks**: lifecycle hooks for kernel injection and held checks are
  not available; use CI integration instead.
- **Non-interactive mode**: whether `aider --yes --message` or an equivalent
  flag provides a non-interactive mode suitable for `AGENT_CLI` in
  `scripts/securability_report.sh` was not verified against vendor
  documentation at the time of writing. The generic fallback is to run the
  merge-steward persona manually or use a different agent CLI.
- **Architect mode**: Aider has an `--architect` flag / `architect: true`
  config for structured edit workflows, but this is not a persona system
  and is not used by the skill pack.
