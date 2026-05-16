# Extended Thinking

Extended thinking হলো Claude-এর built-in scratchpad। Enable করলে model final answer-এ commit করার আগে একটা internal reasoning block produce করে — default-এ end user-দের কাছে invisible। কঠিন problem-এ এটা ধারাবাহিকভাবে quality improve করে। সহজ problem-এ — wasted token। পুরো game হলো কখন on করবেন জানা।

## চালু করা

Call-এ একটা parameter:

```python
resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    thinking={"type": "enabled", "budget_tokens": 2048},
    messages=[
        {"role": "user", "content": "এই multi-step problem solve করো..."},
    ],
)
```

দুটো field:

- **`type`** — `"enabled"` বা `"disabled"`। Default disabled।
- **`budget_tokens`** — thinking block কত token consume করতে পারবে। Model কম use করতে পারে। এটা `max_tokens`-এর অংশ — `max_tokens` যথেষ্ট উঁচু set করুন যাতে thinking ও visible answer দুটোই include হয়।

## যা ফেরত পাবেন

Response-এর `content`-এ text-এর পাশাপাশি একটা `thinking` block থাকবে:

```python
resp.content
# [
#   ThinkingBlock(type='thinking', thinking='Let me break this down...'),
#   TextBlock(type='text', text='The answer is...'),
# ]
```

End user-কে thinking সাধারণত render করেন না। Useful যেসব ক্ষেত্রে:

- **Debugging।** Model কিছু ভুল করলে thinking দেখায় logic কোথায় sideways গেছে।
- **Logging।** Thinking save করলে পরে hard case analyze করতে পারেন।
- **Multi-turn continuity।** Conversation continue করলে — আগের turn-এর thinking pass back করতে পারেন (বা না) — নিচে cover।

## কখন সাহায্য করে

এই ধরনের task-এ thinking enabled থাকলে quality improve হয়:

- Multi-step arithmetic বা symbolic reasoning।
- Non-obvious correctness criteria-সহ code।
- Logical puzzle, constraint satisfaction।
- Trade-off analysis ("এই requirement-এ কোন approach better?")।
- যেখানে thinking ছাড়া model confident-but-wrong answer দিচ্ছে।

খুব একটা সাহায্য করে না:

- Short factual lookup।
- Writing task যেখানে logic-এর চেয়ে flow matter করে।
- যে task-এ thinking ছাড়াই model nail করছে।

A simple test: 20টা representative hard prompt pick করুন। Thinking on ও off — দুটোতে run করুন। Compare করুন। Lift real হলে — production path-এ enable করুন। না হলে — 30% cost বাঁচালেন।

## Budget sizing

বেশি budget = বেশি reasoning room, slower response, বেশি cost। Useful range:

- **~1,024 token পর্যন্ত** — light reasoning। কিছুই extra cost না, marginally সাহায্য।
- **2,048 থেকে 4,096** — meaningful reasoning। Hard task-এর জন্য good default।
- **8,192+** — heavy reasoning। Multi-step proof, complex analysis। শুধু hardest tail-এর জন্য।

Task অনুযায়ী একবার set করুন, churn করবেন না। Model budget-এর চেয়ে কম use করতে পারে — তাই generous হওয়া mostly safe।

## Tool-এর সাথে interaction

Thinking tool use-এর পাশাপাশি কাজ করে। Model thinks, কোন tool call করবে decide করে, call করে, result পায়, continue করে। প্রতিটা "think" segment একটা fresh reasoning step।

Response-এ thinking block tool_use block-এর সাথে interleaved দেখতে পারেন। Agent loop basic tool-use loop-এর মতোই — শুধু কোন block পরবর্তী turn-এ preserve করবেন aware থাকুন।

## Thinking back pass করা

Multi-turn conversation-এ API পরবর্তী call-এ assistant-এর previous thinking block accept করবে। Back পাঠাবেন কিনা — আপনার goal-এর উপর depend করে:

- **পাঠান।** Model যেখানে ছেড়েছিল continue করতে পারে। Better continuity। বেশি expensive (সেই token input হিসেবে count করে)।
- **Drop করুন।** Cheaper, কিন্তু model fresh শুরু করে। Unrelated next question-এর জন্য fine।

Default — thinking block যে turn produce করেছে সেই turn-এ scope করে রাখুন; reason থাকলেই back পাঠান।

## একটা philosophical note

Thinking মানুষের চিন্তার মতো truly hidden reasoning না। এটা শুধু *আরও output token, official answer-এর আগে generate করা*। Model-এর ভুল path-এ commit করে নিজেকে correct করার বেশি room আছে — এটাই exact benefit। Scratchpad-এর মতো treat করুন: useful, magic না।
