# Platform Guides

Per-harness instructions for installing and using the Securable Engineering skill pack. Each guide covers what ships natively, what requires a generated binding, and what remains manual or unavailable.

## Guides

| Harness | Guide |
|---------|-------|
| Claude Code | [claude-code.md](claude-code.md) |
| Cursor | [cursor.md](cursor.md) |
| Devin | [devin.md](devin.md) |
| opencode | [opencode.md](opencode.md) |
| GitHub Copilot | [github-copilot.md](github-copilot.md) |
| Gemini CLI | [gemini-cli.md](gemini-cli.md) |
| Codex | [codex.md](codex.md) |
| Aider | [aider.md](aider.md) |
| Generic AGENTS.md (Zed, Amp, ...) | [generic-agents-md.md](generic-agents-md.md) |

## Capability Matrix

| Capability | Claude Code | Cursor | Devin | opencode | Copilot | Gemini CLI | Codex | Aider | Generic |
|---|---|---|---|---|---|---|---|---|---|
| **Kernel** | Native | Native | Native | Native | Generated | Generated | Native | Generated | Manual |
| **Skills (11)** | Native | Native | Native | Native | Manual | Native | Native | N/A | Native |
| **Commands (12)** | Native | Manual | Manual | Manual | Manual | Manual | Manual | N/A | Manual |
| **Personas (10)** | Native | Generated | Unverified | Generated | Generated | Manual | Generic | Manual | Generated |
| **Hooks** | Native | N/A | Unverified | N/A | N/A | N/A | N/A | N/A | N/A |
| **Merge-time report** | Native | Manual | Manual | Manual | Manual | Manual | Manual | Manual | Manual |

**Legend**: Native = works out of the box with the pack's own files; Generated = a binding under `bindings/` provides the format the harness expects; Manual = paste or adapt from the generic binding; Unverified = the harness may support the feature but it has not been verified against vendor documentation; N/A = the harness does not expose this capability.
