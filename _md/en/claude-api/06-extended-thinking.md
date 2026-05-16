# Extended Thinking

Extended thinking is Claude's built-in scratchpad. When enabled, the model produces an internal reasoning block — invisible to end users by default — before committing to its final answer. On hard problems, this consistently improves quality. On easy problems, it's wasted tokens. The whole game is knowing when to turn it on.

## Turning it on

It's a parameter on the call:

```python
resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    thinking={"type": "enabled", "budget_tokens": 2048},
    messages=[
        {"role": "user", "content": "Solve this multi-step problem..."},
    ],
)
```

Two fields:

- **`type`** — `"enabled"` or `"disabled"`. Default is disabled.
- **`budget_tokens`** — how many tokens the thinking block is allowed to consume. The model may use less. This is part of `max_tokens` — set `max_tokens` high enough to include both the thinking and the visible answer.

## What you get back

The response's `content` will include a `thinking` block in addition to the text:

```python
resp.content
# [
#   ThinkingBlock(type='thinking', thinking='Let me break this down...'),
#   TextBlock(type='text', text='The answer is...'),
# ]
```

You typically don't render the thinking to end users. It's useful for:

- **Debugging.** When the model gets something wrong, the thinking shows where its logic went sideways.
- **Logging.** Saving the thinking lets you analyze hard cases later.
- **Multi-turn continuity.** If you're continuing a conversation, you can pass the previous turn's thinking back (or not) — covered below.

## When it helps

The model's quality on these task types tends to improve with thinking enabled:

- Multi-step arithmetic or symbolic reasoning.
- Code with non-obvious correctness criteria.
- Logical puzzles, constraint satisfaction.
- Trade-off analysis ("which approach is better given these requirements?").
- Anything where you've seen the model give confident-but-wrong answers without thinking.

It rarely helps on:

- Short factual lookups.
- Writing tasks where flow matters more than logic.
- Tasks where the model already nails it without thinking.

A simple test: pick 20 representative hard prompts. Run them with and without thinking. Compare. If the lift is real, enable it for the production path. If it isn't, you've saved yourself 30% of the cost.

## Budget sizing

Higher budget = more reasoning room, slower response, more cost. Useful ranges:

- **Up to ~1,024 tokens** — light reasoning. Costs almost nothing extra, helps marginally.
- **2,048 to 4,096** — meaningful reasoning. Good default for hard tasks.
- **8,192+** — heavy reasoning. Multi-step proofs, complex analysis. Only for the hardest tail.

Set it once based on your task and don't churn it. The model is allowed to use less than the budget, so being generous is mostly safe.

## Interaction with tools

Thinking works alongside tool use. The model thinks, decides which tool to call, calls it, receives the result, and continues. Each "think" segment is a fresh reasoning step.

In the response you may see thinking blocks interleaved with tool_use blocks. The agent loop is the same as the basic tool-use loop — just be aware of which blocks to preserve in subsequent turns.

## Passing thinking back

For multi-turn conversations, the API will accept the assistant's previous thinking blocks in the next call. Whether to send them back depends on your goals:

- **Send them.** The model can continue reasoning where it left off. Better continuity. More expensive (those tokens count as input).
- **Drop them.** Cheaper, but the model starts fresh. Fine for unrelated next questions.

Default is to keep thinking blocks scoped to the turn that produced them; send back only if you have a reason to.

## A philosophical note

Thinking isn't truly hidden reasoning the way human thought is hidden. It's just *more output tokens, generated before the official answer*. The model has more room to commit to wrong paths and correct itself, which is exactly the benefit. Treat it like a scratchpad: useful, but not magic.
