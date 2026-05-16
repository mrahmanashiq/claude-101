# Batch ও Async

প্রতিটা API call user-facing না। সবচেয়ে highest-value Claude usage-এর কিছু batch-এ — দশ লক্ষ record classify, গত quarter-এর support ticket summarize, প্রতিটা change-এ eval run। এই সবের জন্য দুটো tool matter করে: Batch API ও async client।

## কখন batch

আপনার call যদি:

- **Latency-sensitive না** — minutes-to-hours turnaround fine।
- **Independent** — call N call N-1 এর উপর depend করে না।
- **High volume** — কয়েকশ বা তার বেশি একসাথে।

…তাহলে Batch API right tool। এটা একসাথে request-এর list accept করে, queue করে, relaxed pace-এ run করে, এবং একটা discounted rate charge করে (সাধারণত synchronous price-এর প্রায় 50% off)।

## কীভাবে কাজ করে

আপনি একটা JSON Lines file (বা request object-এর একটা list) submit করেন যেখানে প্রতিটা line একটা Messages call। API একটা batch ID return করে। Status-এর জন্য poll করেন, এবং complete হলে result download করেন — এটাও JSON Lines, একই order-এ।

Python-এ:

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

`custom_id` আপনার set করার — আপনার data-এর সাথে result কীভাবে map করবে।

## Polling বনাম webhook

Status periodically poll করতে পারেন (`client.messages.batches.retrieve(batch_id)`) complete না দেখা পর্যন্ত, বা — platform support করলে — notified হতে একটা webhook register করতে পারেন।

বেশিরভাগ use case-এ minute-এ একবার polling fine। Normal size-এর জন্য বেশিরভাগ batch একটা ঘণ্টার মধ্যে শেষ হয়; কিছু long batch বেশি সময় নেয়।

## Caveat

- **Order preserved**, কিন্তু partial failure হতে পারে। সবসময় প্রতিটা item-এর `result.type` check করুন — "succeeded" বনাম "errored"। ধরে নেবেন না যে প্রতিটা line কাজ করেছে।
- **Per-request limit এখনো apply।** প্রতিটা entry-এর নিজস্ব max_tokens, tools ইত্যাদি। Batch একটা container, bypass না।
- **No streaming।** Batch শুধু final response return করে। Tokens-as-they-arrive দরকার হলে — এটা সেই API না।

## Async client

অন্য dimension async-in-your-app। SDK একটা async client ship করে:

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

`asyncio.gather(...)` দিয়ে কয়েক ডজন call concurrently run করতে ব্যবহার করুন:

```python
import asyncio

async def run_all(items):
    return await asyncio.gather(*(summarize(t) for t in items))

results = asyncio.run(run_all(my_texts))
```

Async right tool যখন **synchronous freshness** চান (request complete হতে হবে আপনার function return করার আগে) কিন্তু **parallel throughput**। ঘণ্টার জন্য wait করছেন না; কয়েক ডজন call handle করতে এক call-এর worth latency-এর জন্য wait করছেন।

## Rate limit

Tier-এর উপর depend করে আপনার per-minute ও per-day rate limit আছে। Parallel-এ অনেক call fire করলে — eventually hit করবেন।

429-গুলোকে অন্য rate-limited API-এর মতো handle করুন:

- `retry-after` header (বা SDK-এর typed error) দেখে back off করুন।
- SDK-এর built-in retry ব্যবহার করুন (transient failure-এর জন্য reasonable default আছে)।
- Batch job-এর জন্য Batch API exactly এই জন্যই যাতে scale-এ এটা handle করতে না হয়।

## সঠিক tool pick

Quick decision table:

| Volume | Latency tolerance | Right tool |
|---|---|---|
| 1 call | < 1s | sync |
| 1 call | wait করতে পারে | sync |
| 10–100 calls | < 1 min | async + asyncio.gather |
| 1,000+ calls | hours | Batch API |
| Mixed | varies | live path-এ async, bulk-এ Batch |

Practical-ভাবে বেশিরভাগ production AI system দুটোই ব্যবহার করে: request path-এ async, nightly job-এ Batch।
