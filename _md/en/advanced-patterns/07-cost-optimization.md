# Cost Optimization

Cost is the silent killer of AI features. A demo that costs $0.05 per call sounds cheap, until you multiply by a million users and realize the feature is losing money on every interaction. Most cost problems aren't from raw model pricing — they're from sloppy usage patterns that compound.

Here's the playbook for getting costs down without sacrificing quality.

## Know where your money goes

You can't optimize what you don't measure. Track at minimum:

- **Cost per call** broken down by feature and model.
- **Cost per user per day.**
- **Cost per output** in business terms — per support ticket resolved, per code review, per onboarding completed.

If you don't have these numbers, the rest of this chapter is theoretical. Get measurement in first, then optimize.

## Pick the smallest model that works

Re-run your evals on every tier you haven't ruled out. Often a Haiku does 90% of what a Sonnet does on classification, extraction, and short generation. If pass rate stays acceptable, the cost drop is huge — usually 5–10×.

Don't assume bigger model = better outcomes. Measure.

## Cache aggressively

The single highest-impact lever, covered in its own API chapter. To recap the production discipline:

- Stable prefixes (system prompts, tool definitions, reference docs) marked as cacheable.
- Per-request data placed *after* cached content, never interleaved.
- Cache hit rate monitored — target >70% in production.
- Long-lived (1-hour) cache tier enabled for sustained workloads.

A cached prefix charges ~10% of full input rate. For most features, that's the difference between profit and loss.

## Tighten max_tokens

`max_tokens` is the cap, not the target. But it's often set too high "just in case," and Claude happily generates up to it. Look at your actual output token distribution. If 99% of responses are under 300 tokens, you don't need `max_tokens=2048`.

Pair this with prompts that ask for brevity. "Reply in 2-3 sentences" routinely cuts output cost by 30%+ with no quality loss.

## Drop temperature for repeatable tasks

For classifiers, extractors, anything where you want consistency: `temperature=0`. You get more cache-friendly behavior (similar inputs → similar outputs → better caching) and you eliminate variability that you're sometimes paying retry costs to handle.

## Compress your history

Long conversations are expensive in two ways: more input tokens per call, and worse model focus. Periodically compress:

- Summarize older turns into a short paragraph.
- Drop tool-call/tool-result pairs once the relevant info is in subsequent turns.
- Restart the conversation with a clean system prompt + recent context when it's getting long.

For agent loops in particular: at every K iterations, ask the model to summarize "what we've learned and what's left." Replace the long history with that summary. The agent will lose some fine-grained memory but stay much cheaper.

## Use streaming to cap costs

Streaming lets you watch the response come in. If the model starts going off the rails — generating something wrong, repeating itself, exceeding a planned length — you can abort partway. The tokens you didn't generate, you didn't pay for.

For interactive tools, streaming with smart cancellation can cut effective output cost noticeably.

## Batch when latency doesn't matter

For high-volume, non-real-time workloads — analytics, content moderation pipelines, eval runs — use the Batch API. ~50% discount, same quality. Anything you'd otherwise run with a giant `asyncio.gather` is a Batch candidate.

## Cheaper tools, cheaper outcomes

In tool-use loops, the tool *call* itself is cheap, but the *result* gets read into the next turn. A tool that returns a 50KB blob is now part of your prompt forever (until you compress). Two implications:

- **Tools should return the minimum data the model needs.** Not "the whole table" — "the three rows that matched." Not "the entire HTML page" — "the relevant section."
- **Servers should support filtering and pagination.** Let the model ask for what it actually needs.

This is one of the biggest hidden cost sources in agent systems.

## Re-prompt rarely

A common cost trap: every UI tweak re-triggers a full inference. Look at your call sites — are you re-prompting when nothing semantically changed? Cache results on the client. Debounce. Don't re-call on every keystroke if you don't have to.

## Right-size the loop

For agent loops, iteration count drives cost linearly. If your agent regularly needs 20 iterations to finish a task, look at why:

- Are tools returning enough info?
- Is the task too big for one agent? (Decompose with subagents.)
- Is the model picking the wrong tool repeatedly? (Tighten descriptions.)
- Is `max_iters` too generous, masking a real bug?

Tightening the loop pays off twice — fewer calls, and faster responses.

## The eval connection

Every cost optimization risks quality. Run your eval suite before and after each change. If quality holds and cost drops, ship. If quality drops too, you went too far.

## A reality check

The most cost-effective Claude features have, in this order:

1. Picked the right model tier (not the most expensive one).
2. Cached every stable prefix.
3. Trimmed output length.
4. Used batch / async where appropriate.
5. Stayed structurally simple — no unnecessary tools, no unnecessary subagents, no unnecessary iteration.

Skipping the boring optimizations to "go agentic" first is how features get expensive without getting better. Do the boring stuff. Then layer in the fancy stuff where it earns its keep.
