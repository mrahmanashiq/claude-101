# Messages API-এর Basic

Messages API হলো Claude API-এর হৃদয়। প্রায় সব কিছু — single-shot prompt, multi-turn chat, tool use, vision, batch — `client.messages.create(...)`-এর মধ্য দিয়ে চলে। এর shape বুঝলে বাকি — parameter।

## Request

Minimum field:

```python
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello"}
    ],
)
```

Optional কিন্তু common:

- **`system`** — system prompt-এর জন্য একটা string (বা typed block-এর list)।
- **`temperature`** — float, 0.0 থেকে 1.0। Lower = more deterministic।
- **`top_p`** — float, alternative sampling control। সাধারণত এটা ছুঁবেন না।
- **`stop_sequences`** — string-এর list; model কোনোটা generate করলে থেমে যায়।
- **`tools`** — tool definition-এর list (পরের chapter)।
- **`stream`** — bool; token generate হওয়ার সাথে সাথে stream (নিজের chapter ও)।

## Messages list

`messages` এ পর্যন্তর conversation। প্রতিটা item-এর একটা `role` ও একটা `content`।

`role` হয় `"user"` বা `"assistant"`। এখানে তৃতীয় কোনো role নেই — system prompt নিজের field। Message alternate করতে হবে: user, assistant, user, assistant, এভাবে। প্রথম message `user` থেকে হতে হবে। একটা request-এ পরপর দুটো user message থাকতে পারে না (client-side merge করতে হবে)।

`content` হতে পারে একটা string *অথবা* typed block-এর একটা list। String form shorthand:

```python
{"role": "user", "content": "2+2 কত?"}
```

Block form-এ equivalent:

```python
{"role": "user", "content": [
    {"type": "text", "text": "2+2 কত?"}
]}
```

Plain text-এর বাইরে যা কিছু — image, PDF, tool result — block form লাগে।

## Response

```python
resp = client.messages.create(...)
```

যা ফেরত পাবেন:

- **`resp.content`** — content block-এর list। Simple text reply-এর জন্য, `type: "text"` ও একটা `text` field সহ একটা block।
- **`resp.stop_reason`** — model কেন থামলো। Common value: `"end_turn"` (normal completion), `"max_tokens"` (limit hit), `"tool_use"` (model একটা tool call করতে চায়), `"stop_sequence"` (আপনার একটা stop string match হয়েছে)।
- **`resp.usage`** — token count। `input_tokens`, `output_tokens`, এবং (caching-এর সময়) `cache_creation_input_tokens` ও `cache_read_input_tokens`।
- **`resp.id`**, **`resp.model`**, **`resp.role`** — metadata।

একটা robust client response "done" ধরে নেওয়ার বদলে `stop_reason` পড়ে। বিশেষ করে `max_tokens` একটা common silent truncation source — আপনি long answer চান, `max_tokens=512` set করেন, এবং response মাঝপথে cut হয়। সবসময় check করুন।

## Multi-turn

Conversation চালাতে — প্রতিটা turn `messages` list-এ append করে resend করুন:

```python
history = [
    {"role": "user", "content": "ফ্রান্সের রাজধানী কী?"},
]

resp = client.messages.create(model="claude-sonnet-4-6",
                              max_tokens=256, messages=history)
history.append({"role": "assistant", "content": resp.content})

history.append({"role": "user", "content": "আর জার্মানির?"})
resp = client.messages.create(model="claude-sonnet-4-6",
                              max_tokens=256, messages=history)
```

Chat এভাবে build হয় — history নিজেই maintain করেন, এবং call-এর মাঝে Claude-এর কোনো memory নেই।

## Token economics, দ্রুত

দুটো rule of thumb:

- একটা token মোটামুটি 4 character English। একটা short paragraph ~80 token; একটা typical page ~500–800।
- Input token output-এর চেয়ে cheaper, কখনো 3× বা তার বেশি। Long input / short output উল্টোটার চেয়ে cheaper।

Expensive response পেতে থাকলে output-এ দেখুন। হয় tighter `max_tokens` cap set করুন, না হয় Claude-কে আরও concise হতে বলুন।

## এতটুকু দিয়ে কী বানাতে পারেন

সত্যিই — অনেক। Real product-এ "AI feature" কাজের একটা surprising পরিমাণ হলো clever-ভাবে Messages API ব্যবহার, ভালোভাবে craft করা system prompt-এর সাথে। Plain Messages থেকে value squeeze করার আগে tool use ও agent-এর জন্য reach করবেন না।
