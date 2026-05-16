# Models: Opus, Sonnet, Haiku

Claude isn't one model — it's a family. Picking the right one is the single highest-leverage decision you'll make. Use the wrong tier and you'll either burn money on a problem that didn't need it, or hit a quality wall on a problem that did.

## The three tiers

Anthropic ships three model sizes:

- **Haiku** — the smallest and fastest. Lowest cost, lowest latency. Good at classification, extraction, short summaries, simple tool-calling loops, and high-throughput backend tasks.
- **Sonnet** — the middle tier. Balances quality and cost. The default workhorse for most product surfaces — chat assistants, code review, content generation, agentic workflows that need solid reasoning but not the deepest.
- **Opus** — the most capable. Best at hard reasoning, complex code, multi-step planning, and tasks where small quality differences matter a lot. Slowest and most expensive of the three.

The price gap between Haiku and Opus is roughly 10–20× per token, so don't reach for Opus reflexively. The question to ask is: *is the marginal quality worth the marginal cost?*

## A rule of thumb

Start with Sonnet. It's the right answer to most questions. Move to Haiku if you're doing simple work at scale and need lower latency or cost. Move to Opus only when you can see a concrete failure on Sonnet that Opus fixes — not on a hunch.

For agentic work (Claude Code, custom agent loops), Sonnet and Opus are the practical choices. Haiku tends to lose the thread on long multi-tool workflows.

## Versions and IDs

Each tier has versioned releases — Sonnet 4.5, Sonnet 4.6, Opus 4.7, and so on. The number after the dot is the iteration, not a "minor" version; quality can jump noticeably between them. When you call the API, you pass a model ID string like `claude-sonnet-4-6` or `claude-opus-4-7`. Pin to a specific version in production; let the SDK's "latest" alias slide and your behavior changes the day a new model ships.

## Picking, in practice

Three questions to ask:

1. **What's the hardest single task this model has to do?** Pick for the hardest task, not the average. The average is easy. The 10% hard tail is what trips you up.
2. **How much does each call cost, and how many do you make per user?** Multiply. If it's cheap per call and rare per user, you have a lot of room. If it's frequent, the tier matters.
3. **Is latency on the critical path?** A user staring at a spinner has very different needs than a nightly batch job.

When in doubt, evaluate both. Run 30–50 of your real prompts through each tier, score the outputs, and compare. Hunches are wrong more often than evals.
