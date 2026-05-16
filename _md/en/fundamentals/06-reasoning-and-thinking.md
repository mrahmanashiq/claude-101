# Reasoning, Thinking, and Effort

Claude can answer in two modes, very roughly. It can produce a fast, direct answer — token after token, no scratchpad. Or it can *think first* — work through the problem internally, then commit to a final answer. The second mode is slower and more expensive, but on hard problems it makes a real difference.

## "Just answer" vs "think first"

The default is direct answering. The model reads your prompt and starts producing the response on the next token. For most tasks this is fine and is what you want — anything else would be wasteful.

But for harder tasks — multi-step math, tricky code reasoning, weighing trade-offs across constraints — a direct answer often shows holes. The model didn't have room to check itself. Encouraging it to think first fixes a lot of these holes.

There are two ways to do this.

## Way one: extended thinking

Anthropic exposes a built-in feature on recent Claude models called **extended thinking**. When you turn it on (a parameter on the API call), Claude generates a private "thinking" block before its final answer. You can budget how many tokens that block is allowed.

In code, it looks roughly like:

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    thinking={"type": "enabled", "budget_tokens": 2048},
    messages=[{"role": "user", "content": "..."}],
)
```

The thinking content is returned in a separate block of the response. You generally don't show it to end users, but you can log it for debugging.

## Way two: explicit scratchpad

You can also ask the model to think in the open, by including instructions in your prompt:

```
Before giving your final answer, work through the problem inside
<thinking></thinking> tags. Then put the final answer inside
<answer></answer> tags.
```

This is older and lower-tech than extended thinking, but it works on every model and lets you inspect (or hide) the scratchpad explicitly.

## When thinking helps — and when it doesn't

Thinking pays off when:

- The problem has multiple steps and the answer depends on getting each step right.
- There's a verifiable answer (math, code, logic) that the model can self-check against.
- The task involves comparing options or weighing trade-offs.

Thinking doesn't help much when:

- The task is mostly creative (writing a poem, brainstorming names).
- The output is short and direct (classification, single-fact extraction).
- You're already at the right tier and the model gets it right consistently.

The rule of thumb: if you're seeing the model make confident-but-wrong answers on hard tasks, try thinking before you upgrade the model tier. Often that's enough.

## Effort levels

Some surfaces (Claude Code in particular) expose a higher-level "effort" knob — low, medium, high — that bundles thinking, retries, and tool use. Same intuition: dial up effort when the task is hard and time is cheap; dial it down when the task is simple and latency matters.

!!! tip
    Don't enable thinking by default everywhere. It costs tokens and adds latency. Enable it where you've measured a quality lift, not where you hope there is one.
