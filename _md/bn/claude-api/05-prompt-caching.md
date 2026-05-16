# Prompt Caching

Prompt caching API-এর single highest-impact cost optimization। অনেক call-এ একই long prefix re-use করার সময় — একটা stable system prompt, একটা attached document, কিছু example shot — API এটা server-side-এ store করতে পারে এবং per-token rate-এর একটা ভগ্নাংশে call জুড়ে reuse করতে পারে। Number-গুলো এত বড় যে — কয়েকটার বেশি call করা যেকোনো application-এ caching ignore করা মানে real টাকা পড়ে থাকতে দেওয়া।

## কীভাবে কাজ করে

আপনি input-এর একটা section cacheable হিসেবে mark করেন। API:

1. প্রথমবার সেই exact prefix দেখলে — একটা **cache write** charge করে (normal input cost-এর চেয়ে একটু বেশি, কারণ result-ও store করছে)।
2. পরের call-গুলোতে cache TTL-এর মধ্যে — একটা **cache read** charge করে (অনেক cheaper — সাধারণত normal input rate-এর প্রায় এক-দশমাংশ)।
3. Cache breakpoint-এর আগে কিছু বদলালে — cache miss-fire করে এবং full price pay করেন।

Cache key হলো breakpoint পর্যন্ত *exact byte*। Breakpoint-এর নিচে যা — per call আলাদা হতে পারে।

## Setup

যে content block cacheable mark করতে চান — সেগুলোতে একটা `cache_control` field add করেন। সেই point-এ ও আগের block-গুলো cached prefix form করে।

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

উপরের system prompt cache হবে। পরবর্তী যেকোনো request যা একই exact `LONG_SYSTEM_PROMPT` পাঠায় — cache থেকে read করবে।

## কী cacheable

System prompt, message block, এবং tool definition — সব mark করা যায়। প্রতিটা request-এ কয়েকটা breakpoint পান — তাই *layer* cache করতে পারেন: প্রথমে tool, তারপর একটা long shared doc, তারপর per-request user turn শেষে।

## Structure trick

Prompt-এর order matters। Cache **prefix** কে benefit করে। Per call যা বদলায় — সব stable জিনিসের *পরে* আসতে হবে।

একটা common, useful layout:

```
[Tools - stable, cached]
[System prompt - stable, cached]
[Long reference document - stable, cached]
[Conversation history so far - mostly stable, last few turns cached]
[New user turn - not cached]
```

User-এর per-turn data accidentally prompt-এর মাঝে রাখলে — তারপরের সব কিছুর জন্য cache ভেঙে দিয়েছেন। এটাই most common mistake।

## TTL ও warm-up

Default cache TTL short — সাধারণত কয়েক মিনিট। একটা longer (1-hour) tier আছে — sustained traffic-এর production workload-এর জন্য। Traffic bursty হলে quiet period-এর পর প্রথম request আবার cache-write pay করে।

Latency-critical path-এর জন্য cache "warm up" করুন: real traffic শুরুর কিছু আগে একটা single dummy request পাঠান — পরের request-গুলো cheap-ভাবে cache hit করে।

## Usage পড়া

Response object caching activity report করে:

```python
resp.usage
# Usage(
#     input_tokens=120,             # এই call-এ uncached input
#     cache_creation_input_tokens=0,
#     cache_read_input_tokens=8400, # cache থেকে served
#     output_tokens=210,
# )
```

একটা healthy production setup-এ warm-up-এর পর `cache_read_input_tokens` `input_tokens`-কে dwarf করবে। না করলে — cache miss হচ্ছে — investigate করুন।

## কখন bother করবেন

Caching pay off হয় যখন:

- Long stable prefix-এর সাথে repeat call করছেন।
- সেই prefix ~1,000 token-এর বেশি (smaller prefix write overhead recoup করে না)।
- আপনার traffic pattern এত dense যে TTL call-এর মাঝে expire করে না।

One-off call বা short prompt-এর জন্য skip করুন। সাবধানে setup করুন: system prompt সহ chat app, long doc-এর উপর RAG, stable tool definition সহ agent loop।

## Mental model

Caching-কে *আপনার call-এর একটা inverse function build করা* হিসেবে ভাবুন। একই context-এর জন্য বারবার pay করা বন্ধ করেন, এবং নতুন অংশটার জন্যই mostly pay করেন। Well-designed system-এ cache warm হলে per call marginal cost 5–10× drop করে। এটা micro-optimization না — এটা ship হওয়া feature এবং run করার জন্য বেশি expensive feature-এর মধ্যে পার্থক্য।
