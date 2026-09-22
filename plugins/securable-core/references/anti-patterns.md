# Anti-Pattern Tag Reference

Shared reference for the securable engineering skills. The generation skill (`securability-engineering`) uses it as the list of shapes never to emit; triage, remediation, and postmortem use its **Tag** column as the anti-pattern vocabulary and its **Correct shape** column as the fix target. This file is the single source of truth — skills reference it by path and never restate it.

> **Path resolution**: this file lives at the plugin root under `references/`. In a Claude Code plugin install that root is `${CLAUDE_PLUGIN_ROOT}`; in a repo checkout, resolve relative to this file's position in the tree.

These are the patterns to **not** emit during generation. Each row pairs the bad shape with the principle it would violate, so when you find yourself about to write one, you know what's going wrong and what the correct shape looks like.

| Pattern to avoid emitting | Principle / attribute violated | Tag | Correct shape instead |
|---|---|---|---|
| String-built SQL / shell / format strings touching user input | Integrity — input handling at boundary (FIASSE v1.1 S4.4.1, S4.3) | "Trust boundary input handling" | Parameterized query / `subprocess` arg list / format with placeholders |
| Trusting `req.body.user_id`, `X-Tenant-ID`, JWT claims for authorization decisions | Integrity — Isolated Integrity (FIASSE v1.1 S4.4.1.2) | "Isolated Integrity violation" | Look up user/tenant from authenticated session; never client-asserted |
| Spreading `req.body` / `**request.json` directly into ORM update | Integrity — Canonical Parsing (FIASSE v1.1 S4.4.1.1) | "Mass assignment" | Explicit allow-list of named fields → typed DTO → mapped update |
| `os.path.join(base, user_input)` / template path concatenation | Integrity — boundary canonicalization (FIASSE v1.1 S4.4.1) | "Path canonicalization gap" | Resolve absolute path, assert it's under `base`, reject otherwise |
| `jwt.decode(token)` with default algorithms / no `aud` / no `iss` | Authenticity (FIASSE v1.1 S3.2.2.3) | "Token verification under-specified" | `jwt.decode(token, key, algorithms=['RS256'], audience=..., issuer=...)` |
| `print(...)` / `console.log(...)` / `fmt.Println(...)` for security events | Accountability + Observability (FIASSE v1.1 S2.6, S3.2.1.4) | "Unstructured audit trail" | Structured logger emitting `{event, actor, target, outcome, request_id}` |
| `try: ... except: pass` / silent failure paths | Observability (FIASSE v1.1 S3.2.1.4); Resilience (FIASSE v1.1 S3.2.3.3) | "Silent failure" | Specific exception types; log with context; re-raise or return typed error |
| Bare `except:` / `catch (e)` returning raw exception text | Resilience; Confidentiality (FIASSE v1.1 S3.2.3.3, S3.2.2.1) | "Specific exception handling missing" | Named exception types, generic public message, internal log with detail |
| Module-level globals (DB connection, app, config) created at import | Modifiability + Testability (FIASSE v1.1 S3.2.1.2, S3.2.1.3) | "Import-time side effects" | Factory function / DI container / fixture-injected dependencies |
| `request.body.read()` / `ioutil.ReadAll(r.Body)` with no size cap | Availability + Resilience (FIASSE v1.1 S3.2.3.1, S3.2.3.3) | "Unbounded resource consumption" | Bounded reader; explicit `max_size`; 413 on overflow |
| `password == request.password` / non-constant-time secret comparison | Authenticity; Confidentiality | "Timing-side-channel comparison" | `hmac.compare_digest` / language equivalent |
| Hardcoded secrets, connection strings, or API keys | Confidentiality (FIASSE v1.1 S3.2.2.1) | "Secret in code" | Env var / secret manager; pass via injected config |
| `any` / `interface{}` / `dynamic` on the trust-boundary surface | Analyzability + Integrity | "Trust-boundary type erasure" | Concrete typed DTO / Pydantic model / typed struct |
| `setTimeout` / `time.sleep` as a substitute for actual rate limiting | Availability (FIASSE v1.1 S3.2.3.1) | "Sleep-based throttling" | Real rate limiter (token bucket / fixed window) keyed by actor |
| External call without timeout (`requests.get(url)`, `http.Client{}`) | Availability + Resilience | "Unbounded external call" | Explicit `timeout=` / configured `Client` with timeouts |
| Logging the full request body / response body / token by default | Confidentiality + Accountability (sensitive data in audit) | "PII in audit log" | Log structured event with IDs only; redact body and credential fields |

If you catch yourself emitting one of these, stop and rewrite.
