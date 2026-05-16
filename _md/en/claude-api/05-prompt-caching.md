# Prompt Caching

Prompt caching is the single highest-impact cost optimization the API offers. When you reuse the same long prefix across many calls — a stable system prompt, an attached document, a set of example shots — the API can store it on the server side and reuse it across calls at a fraction of the per-token rate. The numbers are big enough that ignoring caching, in any application that makes more than a handful of calls, is leaving real money on the table.

## How it works

You mark a section of your input as cacheable. The API:

1. The first time it sees that exact prefix, charges a **cache write** (slightly more than normal input cost, because it's also storing the result).
2. On subsequent calls within the cache TTL, charges a **cache read** (much cheaper — typically around a tenth of the normal input rate).
3. If anything before the cache breakpoint changes, the cache miss-fires and you pay full price.

The cache is keyed by *exact bytes* up to the breakpoint. Anything below the breakpoint can be different per call.

## Setting it up

You add a `cache_control` field to the content blocks you want to mark as cacheable. The blocks at and before that point form the cached prefix.

```python
resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }
    ],
    messages=[
        {"role": "user", "content": current_user_question},
    ],
)
```

The system prompt above will be cached. Any subsequent request that sends the same exact `LONG_SYSTEM_PROMPT` will read from cache.

## What's cacheable

System prompt, message blocks, and tool definitions can all be marked. You get up to a few breakpoints per request, so you can cache *layers*: tools first, then a long shared doc, then the per-request user turn at the end.

## The structure trick

The order of your prompt matters. The cache benefits the **prefix**. Anything that changes per call must come *after* anything that's stable.

A common, useful layout:

```
[Tools - stable, cached]
[System prompt - stable, cached]
[Long reference document - stable, cached]
[Conversation history so far - mostly stable, last few turns cached]
[New user turn - not cached]
```

If you accidentally put the user's per-turn data in the middle of your prompt, you've broken the cache for everything after it. This is the most common mistake.

## TTL and warm-up

The default cache TTL is short — typically a few minutes. There's also a longer (1-hour) tier for production workloads with sustained traffic. If your traffic is bursty, the first request after a quiet period pays the cache-write again.

For latency-critical paths, "warm up" the cache: send a single dummy request shortly before you expect real traffic, and the subsequent requests hit cache cheaply.

## Reading the usage

The response object reports caching activity:

```python
resp.usage
# Usage(
#     input_tokens=120,             # uncached input this call
#     cache_creation_input_tokens=0,
#     cache_read_input_tokens=8400, # served from cache
#     output_tokens=210,
# )
```

In a healthy production setup, `cache_read_input_tokens` will dwarf `input_tokens` after warm-up. If it doesn't, your cache is missing — investigate.

## When to bother

Caching pays off when:

- You make repeat calls with a long stable prefix.
- That prefix is over ~1,000 tokens (smaller prefixes don't recoup the write overhead).
- Your traffic pattern is dense enough that the TTL doesn't expire between calls.

Skip it for one-off calls or short prompts. Definitely set it up for: chat apps with system prompts, RAG over a long doc, agent loops with stable tool definitions.

## The mental model

Think of caching as *building an inverse function for your call*. You stop paying for the same context over and over and start paying mostly for the part that's new. In a well-designed system, the marginal cost per call drops by 5–10× once the cache is warm. That's not a micro-optimization — that's the difference between a feature that ships and a feature that's too expensive to run.
