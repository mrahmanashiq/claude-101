# Batch and Async

Not every API call is user-facing. Some of the highest-value Claude usage is in batch — classify a million records, summarize last quarter's support tickets, run an eval over every change. For these, two tools matter: the Batch API and async clients.

## When to batch

If your calls are:

- **Not latency-sensitive** — minutes-to-hours turnaround is fine.
- **Independent** — call N doesn't depend on call N-1.
- **High volume** — hundreds or more at a time.

…then the Batch API is the right tool. It accepts a list of requests at once, queues them, runs them at a relaxed pace, and charges a discounted rate (typically ~50% off the synchronous price).

## How it works

You submit a JSON Lines file (or a list of request objects) where each line is one Messages call. The API returns a batch ID. You poll for status, and when complete, download the results — also as JSON Lines, in the same order.

In Python:

```python
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"item-{i}",
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 512,
                "messages": [{"role": "user", "content": text}],
            },
        }
        for i, text in enumerate(my_inputs)
    ],
)

# ... wait / poll ...

results = client.messages.batches.results(batch.id)
for r in results:
    print(r.custom_id, r.result)
```

The `custom_id` is yours to set — it's how you map results back to your data.

## Polling vs webhooks

You can poll the status periodically (`client.messages.batches.retrieve(batch_id)`) until it shows complete, or — depending on what the platform supports — register a webhook to be notified.

For most use cases, polling once a minute is fine. Most batches finish well within an hour for normal sizes; some long batches take longer.

## Caveats

- **Order is preserved**, but partial failures can occur. Always check `result.type` for each item — "succeeded" vs "errored." Don't assume every line worked.
- **Per-request limits still apply.** Each entry has its own max_tokens, tools, etc. The batch is a container, not a bypass.
- **No streaming.** Batch returns final responses only. If you need tokens-as-they-arrive, this isn't the API for that.

## Async clients

The other dimension is async-in-your-app. The SDK ships an async client:

```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

async def summarize(text):
    resp = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": f"Summarize: {text}"}],
    )
    return resp.content[0].text
```

Use it with `asyncio.gather(...)` to run a few dozen calls concurrently:

```python
import asyncio

async def run_all(items):
    return await asyncio.gather(*(summarize(t) for t in items))

results = asyncio.run(run_all(my_texts))
```

Async is the right tool when you want **synchronous freshness** (the request needs to complete before your function returns) but **parallel throughput**. You're not waiting for hours; you're waiting for one call's worth of latency to handle dozens of calls.

## Rate limits

You have per-minute and per-day rate limits depending on your tier. When you fire many calls in parallel, you'll hit them eventually.

Handle the 429s like any rate-limited API:

- Look at the `retry-after` header (or the SDK's typed error) and back off.
- Use the SDK's built-in retry (it has reasonable defaults for transient failures).
- For batch jobs, the Batch API exists exactly so you don't have to deal with this at scale.

## Picking the right tool

Quick decision table:

| Volume | Latency tolerance | Right tool |
|---|---|---|
| 1 call | < 1s | sync |
| 1 call | OK to wait | sync |
| 10–100 calls | < 1 min | async + asyncio.gather |
| 1,000+ calls | hours | Batch API |
| Mixed | varies | async for the live path, Batch for the bulk |

In practice, most production AI systems end up using both: async for the request path, Batch for the nightly jobs.
