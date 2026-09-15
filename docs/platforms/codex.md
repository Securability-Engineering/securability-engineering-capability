# Securable Engineering on OpenAI Codex

Platform guide for the securable engineering skill pack on
[OpenAI Codex](https://github.com/openai/codex) (the open-source CLI agent).

---

## 1. What this pack gives you on Codex

| Layer | Capability | Codex support |
|-------|-----------|---------------|
| Always-on kernel | Five securable engineering rules in every prompt | Native — `AGENTS.md` in the repo root |
| Skills (11) | FIASSE/SSEM review, generation, PRD enhancement, triage, remediation, verification, postmortem, threat modeling, dependency stewardship, adoption, lookup | Native — `.agents/skills/` discovery |
| Commands / prompts | Twelve slash-style dispatchers | Manual — invoke the underlying skill by description |
| Personas (10) | Task-scoped agent definitions with accountability boundaries | Generic fallback — paste from `bindings/generic/agents/<name>.md` |
| Hooks | Session kernel injection, post-edit opengrep held checks | Not available — use CI instead |
| Merge-time report | FIASSE S5.2.1 Securability Report on a diff | `scripts/securability_report.sh` with `AGENT_CLI="codex exec"` |

## 2. Install

```bash
git clone --depth 1 \
  https://github.com/Securability-Engineering/securable-claude-plugin.git \
  /tmp/securable-clone

/tmp/securable-clone/scripts/install_skills.sh --target .agents

rm -rf /tmp/securable-clone
```

The installer copies `skills/`, `data/`, `plays/`, `templates/`, `schema/`,
`core/`, `rules/`, `agents/`, `bindings/`, and `docs/` under `.agents/`. That sibling
layout is load-bearing: relative references inside each `SKILL.md` depend on it.

Optionally append the kernel to the project's `AGENTS.md`:

```bash
cat .agents/core/kernel.md >> AGENTS.md
```

Verify by asking Codex to list its skills. You should see all eleven
(see section 4).

## 3. Always-on kernel

The securability kernel (~300 tokens) covers: parse-don't-trust, server-side
authority, banned patterns, observable security, and securability notes.

Codex discovers `AGENTS.md` using a cascading hierarchy: global
(`~/.codex/AGENTS.md` or `$CODEX_HOME/AGENTS.md`), then from repository root
down to the current directory. `AGENTS.override.md` in the same directory
takes priority. Files are concatenated root-down.

Append `core/kernel.md` to the project's `AGENTS.md` (see Install above).

## 4. Skills

Codex discovers skills from `.agents/skills/` in every directory from the
current working directory up to the repository root, plus `~/.agents/skills/`
(user-wide). Legacy path `~/.codex/skills/` also works. Each skill is a
directory containing a `SKILL.md` with YAML frontmatter (`name` and
`description` only -- other fields are not part of the Codex spec).

Installed skills:

| Skill | Trigger on |
|-------|-----------|
| `securability-engineering-review` | "review securability", "SSEM scorecard" |
| `securability-engineering` | "generate secure code", "securable scaffold" |
| `prd-securability-enhancement` | "harden this PRD", "ASVS coverage" |
| `fiasse-lookup` | "what does FIASSE say about …" |
| `threat-modeling` | "threat model", "trust boundaries" |
| `dependency-stewardship` | "audit dependencies", "dependency review" |
| `securability-triage` | "triage scanner output", "prioritize findings" |
| `securability-remediation` | "fix this finding", "remediate vulnerability" |
| `securability-verification` | "verify requirement", "contract test" |
| `securability-postmortem` | "incident postmortem", "lessons learned" |
| `fiasse-adoption` | "adoption assessment", "FIASSE maturity" |

**Quick test:** `Review the securability of src/auth/ against the SSEM model.`

## 5. Commands / prompt equivalents

Codex does not have a verified native mechanism for user-defined slash
commands (custom prompts in `~/.codex/prompts/` are not verified against
vendor documentation at the time of writing).

The pack ships twelve dispatchers as `commands/*.md`:
`securability-review`, `secure-generate`, `prd-securability-enhance`,
`fiasse-lookup`, `threat-model`, `dependency-steward`,
`securability-triage`, `securability-remediate`, `securability-verify`,
`securability-postmortem`, `fiasse-adoption`, `securable-status`.

Each delegates to a skill, so the simplest approach on Codex is to invoke
the skill directly by describing the task. Codex matches the description
and activates the appropriate skill.

## 6. Personas

Codex does not have a first-class named-persona system (not verified
against vendor documentation at the time of writing).

**Generic fallback** -- use the pre-generated persona definitions under
`bindings/generic/agents/`:

| Persona | File | Layer |
|---------|------|-------|
| requirements-partner | `bindings/generic/agents/requirements-partner.md` | L1 |
| boundary-mapper | `bindings/generic/agents/boundary-mapper.md` | L1 |
| securable-builder | `bindings/generic/agents/securable-builder.md` | L2 |
| dependency-steward | `bindings/generic/agents/dependency-steward.md` | L2 |
| merge-steward | `bindings/generic/agents/merge-steward.md` | L3 |
| triage-analyst | `bindings/generic/agents/triage-analyst.md` | L3 |
| remediation-engineer | `bindings/generic/agents/remediation-engineer.md` | L3 |
| verification-engineer | `bindings/generic/agents/verification-engineer.md` | L4 |
| incident-learner | `bindings/generic/agents/incident-learner.md` | L5 |
| adoption-coach | `bindings/generic/agents/adoption-coach.md` | Program |

Paste the persona file contents into the conversation before the task:

```
<paste contents of bindings/generic/agents/merge-steward.md>

Review the diff on the current branch and produce a Securability Report.
```

Tool allowlists and path restrictions in each persona file are promised
(the agent is instructed to follow them) but not enforced by the Codex
runtime.

## 7. Hooks and held checks

Codex does not expose lifecycle hooks. The pack's hooks
(`hooks/scripts/session_kernel.sh`, `hooks/scripts/post_edit_opengrep.sh`)
cannot run automatically.

**Manual equivalent:** run opengrep with the pack's rule file in CI:

```bash
opengrep scan --config .agents/rules/opengrep/securable.yaml src/
```

This requires `opengrep` to already be installed. The pack never installs
tooling at runtime.

## 8. Merge-time Securability Report

```bash
AGENT_CLI="codex exec" scripts/securability_report.sh \
  --base origin/main --head HEAD --out report.md
```

If `codex exec` does not accept a prompt on stdin in your version (not
verified -- see section 10), run the merge-steward persona on the diff
interactively instead.

## 9. Tooling policy reminder

This pack never installs tooling at runtime. Skills use only the tools
already present. When a check cannot run because a tool is absent, the
skill reports the gap as `Not assessed`. CI provisioning is the consumer's
explicit decision.

## 10. Limitations and unverified items

The following are **not verified against vendor documentation at the time
of writing**:

1. **Custom prompts / slash commands** -- `~/.codex/prompts/*.md` (deprecated
   in favor of skills). Fallback: invoke skills by description.
2. **Named personas / subagents** -- no documented custom agent definition
   format with model or tool restriction fields. Fallback: paste from
   `bindings/generic/agents/`.
3. **System instructions override** -- `--config experimental_instructions_file`
   flag. Fallback: use `AGENTS.md`.
4. **Config.toml fallback filenames** -- `project_doc_fallback_filenames` in
   `~/.codex/config.toml`.
5. **Lifecycle hooks** -- no pre/post tool-use hooks documented. Use CI or a
   wrapper script.
6. **`codex exec` stdin mode** -- whether it reads a prompt from stdin for
   `securability_report.sh`. Test locally before relying on it in CI.
7. **Tool allowlists** -- persona files promise restrictions but the Codex
   runtime does not enforce them.
