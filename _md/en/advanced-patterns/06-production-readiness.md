# Production Readiness

Going from "it works on my laptop" to "users can rely on it in production" is a project of its own. The model is the easy part. The boring infrastructure around it is what determines whether your AI feature survives contact with real traffic.

This is a checklist, in roughly the order you'll need to think about each item.

## Pin everything

- **Pin the model version.** Not `claude-latest`. Not the alias. The exact ID, in a config file, with a record of when you updated it.
- **Pin the SDK version.** Same reasoning. Auto-updates land surprises.
- **Pin prompt versions.** Treat prompts as code. Versioned files, code-reviewed changes, deployed alongside the application.

If you can answer "what exactly was running when this request was made?" without ambiguity, you have a chance at debugging. Otherwise, every incident is a mystery.

## Timeouts, retries, and limits

- **Set per-request timeouts.** The default is "wait forever." That's wrong for almost every production path. 30–60s is a sensible upper bound for synchronous calls.
- **Retry transient failures.** 429s, 5xxs, network blips. The SDK has reasonable defaults; tune them to your needs and trust them.
- **Don't retry forever.** Cap retries (typically 3–5) so a bad day doesn't become a runaway cost event.
- **Token budgets per request.** Set `max_tokens` so a single response can't blow up. For agentic loops, also cap the total tokens across the whole loop.

## Observability

Log at the level you can use later. Minimum:

- Request ID (yours, not just the API's).
- User ID (or anonymized session ID).
- Model used, prompt version, tool list version.
- Input and output token counts. (Don't log full prompts/responses by default — they're large and may contain PII.)
- Latency.
- Stop reason, error if any.
- Cost in USD computed from token counts.

Aggregate these into dashboards: P50/P95/P99 latency, error rate by error type, cost per user, cost per feature, daily volume. When something breaks, you should know within minutes — not from a user complaining a day later.

## Cost guardrails

Three layers of protection:

- **Per-user rate limits.** A single misbehaving user shouldn't bankrupt you. Cap their daily / hourly volume.
- **Per-request cost cap.** If a request's total token usage exceeds your budget, abort gracefully.
- **Global circuit breaker.** When the total daily spend hits a threshold, page someone and start refusing low-priority traffic.

These don't fire often. When they do, they save you a lot.

## Safety and content controls

For user-facing features:

- **Input validation.** Reject obviously hostile inputs (prompt injections, malformed payloads) at the edge.
- **Output filters.** Strip personally identifiable information you don't want to expose. Block known-bad output patterns.
- **Refusal handling.** When the model declines to answer (it sometimes will), have a graceful fallback. Don't expose Claude's refusal text raw; render a UI message.
- **Logging for audit.** For regulated industries, you may need a retention policy that meets compliance — don't bolt this on later.

## Caching strategy

In production, prompt caching is mandatory not optional. For any feature with stable prefixes:

- Mark cacheable blocks.
- Monitor cache hit rate in usage stats.
- Warm the cache on startup or before traffic spikes.

A 5–10× cost reduction from caching is the difference between a feature that ships and one that gets the axe.

## Graceful degradation

What happens when:

- The API is down? (Cache last good responses where possible; show a clear "try again later" otherwise.)
- The model is slow? (Show a streaming response so users see *something*; have a hard timeout that falls back to a static reply or a simpler model.)
- A tool fails? (Recover within the agent loop; if recovery fails, surface a clean error.)

Design these failure modes before launch. Test them. Don't discover them on Black Friday.

## Eval gates in CI

Your eval suite (previous chapter) should run on every PR that touches a prompt or model. If pass rate drops by more than a threshold, the PR fails. This is the single best defense against silent quality regressions.

## Rollouts

When you change the model, the prompt, or a tool:

- **Roll out to a small percentage of traffic first.** Compare metrics — quality, cost, latency — against the rest.
- **Have a rollback plan.** It should be a one-line config change, not a deploy.
- **Watch user-visible metrics**, not just synthetic ones. Conversion rate, support volume, satisfaction scores.

## On-call playbooks

For every failure mode you can think of, write a one-page playbook: what to check, what to roll back, who to wake up. The first time an LLM-related incident hits, you'll be glad you wrote them.

---

This is the boring part of AI engineering. It's also what separates the demos from the products.
