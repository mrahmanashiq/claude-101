# Reasoning, Thinking ও Effort

Claude মোটামুটিভাবে দুটো mode-এ answer দিতে পারে। একটা fast, direct answer produce করতে পারে — token-এর পর token, কোনো scratchpad ছাড়া। অথবা *আগে ভাবতে পারে* — problem-টা internally কাজ করে নিয়ে তারপর final answer-এ commit করতে পারে। দ্বিতীয়টা slower ও বেশি expensive, কিন্তু hard problem-এ সত্যিকারের পার্থক্য তৈরি করে।

## "Just answer" বনাম "think first"

Default direct answering। Model আপনার prompt পড়ে পরের token থেকেই response produce করতে শুরু করে। বেশিরভাগ task-এর জন্য এটাই ঠিক — অন্য কিছু wasteful হবে।

কিন্তু কঠিন task-এ — multi-step math, tricky code reasoning, constraint-এর মধ্যে trade-off — direct answer প্রায়ই hole দেখায়। Model-এর নিজেকে check করার room ছিল না। আগে ভাবতে encourage করলে অনেক hole fix হয়।

দুইভাবে এটা করা যায়।

## Way one: extended thinking

Anthropic সাম্প্রতিক Claude model-এ একটা built-in feature expose করে: **extended thinking**। এটা on করলে (API call-এ একটা parameter), Claude final answer-এর আগে একটা private "thinking" block generate করে। সেই block কত token খরচ করতে পারবে সেটার budget set করতে পারেন।

Code-এ মোটামুটি এমন দেখতে:

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    thinking={"type": "enabled", "budget_tokens": 2048},
    messages=[{"role": "user", "content": "..."}],
)
```

Thinking content response-এর একটা আলাদা block-এ আসে। সাধারণত end user-কে দেখান না, কিন্তু debugging-এর জন্য log করতে পারেন।

## Way two: explicit scratchpad

Prompt-এ instruction দিয়ে model-কে openly ভাবতে বলতে পারেন:

```
Final answer দেওয়ার আগে problem-টা <thinking></thinking> tag-এর ভেতরে
work করো। তারপর final answer <answer></answer> tag-এর ভেতরে দাও।
```

এটা extended thinking-এর চেয়ে পুরোনো ও lower-tech, কিন্তু প্রতিটা model-এ কাজ করে এবং আপনাকে scratchpad explicitly inspect (বা hide) করতে দেয়।

## Thinking কখন সাহায্য করে — এবং কখন না

Thinking pay off হয় যখন:

- Problem-এর multiple step আছে এবং answer প্রতিটা step ঠিক হওয়ার উপর depend করে।
- একটা verifiable answer আছে (math, code, logic) যেটার সাথে model নিজেকে self-check করতে পারে।
- Task option compare করা বা trade-off weigh করা।

Thinking খুব একটা সাহায্য করে না যখন:

- Task মূলত creative (poem লেখা, name brainstorm)।
- Output ছোট ও direct (classification, single-fact extraction)।
- আপনি ইতিমধ্যে ঠিক tier-এ আছেন আর model consistent ঠিক উত্তর দিচ্ছে।

Rule of thumb: কঠিন task-এ model confident-but-wrong answer দিচ্ছে দেখলে, model tier upgrade করার আগে thinking try করুন। প্রায়ই সেটাই যথেষ্ট।

## Effort level

কিছু surface (বিশেষ করে Claude Code) একটা higher-level "effort" knob — low, medium, high — expose করে যা thinking, retry ও tool use bundle করে। একই intuition: task hard ও time cheap হলে effort বাড়ান; task simple ও latency matter করলে কমান।

!!! tip
    সবজায়গায় default-এ thinking enable করবেন না। এটা token খায় ও latency add করে। যেখানে measured quality lift আছে সেখানে enable করুন, যেখানে আশা করেন সেখানে না।
