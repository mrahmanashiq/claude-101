# Models: Opus, Sonnet, Haiku

Claude একটাই model না — এটা একটা পরিবার। ঠিক model বেছে নেওয়া হলো আপনার সবচেয়ে বড় leverage-এর সিদ্ধান্ত। ভুল tier ব্যবহার করলে হয় টাকা পুড়িয়ে এমন problem solve করবেন যেটার দরকার ছিল না, অথবা এমন problem-এ quality wall-এ আটকাবেন যেটার দরকার ছিল।

## তিনটা tier

Anthropic তিনটা model size ship করে:

- **Haiku** — সবচেয়ে ছোট ও দ্রুত। সবচেয়ে কম cost, সবচেয়ে কম latency। Classification, extraction, ছোট summary, simple tool-calling loop ও high-throughput backend কাজে ভালো।
- **Sonnet** — মাঝের tier। Quality আর cost-এর মাঝে balance। বেশিরভাগ product surface-এর default workhorse — chat assistant, code review, content generation, agentic workflow যেখানে শক্ত reasoning দরকার কিন্তু সবচেয়ে গভীর না।
- **Opus** — সবচেয়ে capable। কঠিন reasoning, জটিল code, multi-step planning, এবং যেসব কাজে small quality difference অনেক বেশি matter করে — সেগুলোর জন্য সেরা। তিনটার মধ্যে সবচেয়ে slow ও সবচেয়ে expensive।

Haiku ও Opus-এর per-token price gap সাধারণত 10–20× — তাই reflexively Opus-এর দিকে হাত বাড়াবেন না। যে প্রশ্নটা করবেন: *marginal quality কি marginal cost-এর সমান value দিচ্ছে?*

## একটা rule of thumb

Sonnet দিয়ে শুরু করুন। বেশিরভাগ প্রশ্নের সঠিক উত্তর সেটাই। যদি scale-এ simple কাজ করছেন এবং কম latency বা cost দরকার — Haiku-তে নামুন। Opus-এ যান শুধু তখনই যখন Sonnet-এ একটা concrete failure দেখতে পান যেটা Opus fix করছে — অনুমানের উপর না।

Agentic কাজের জন্য (Claude Code, custom agent loop) Sonnet ও Opus practical choice। Haiku সাধারণত দীর্ঘ multi-tool workflow-এ track হারিয়ে ফেলে।

## Version ও ID

প্রতিটা tier-এর versioned release আছে — Sonnet 4.5, Sonnet 4.6, Opus 4.7, এভাবে। Dot-এর পরের number iteration, "minor" version না; quality লক্ষণীয়ভাবে jump করতে পারে এদের মধ্যে। API call করার সময় `claude-sonnet-4-6` বা `claude-opus-4-7`-এর মতো একটা model ID string পাঠান। Production-এ specific version-এ pin করুন; SDK-এর "latest" alias ব্যবহার করলে নতুন model ship হলেই আপনার behavior বদলে যাবে।

## Practical-ভাবে কীভাবে choose করবেন

তিনটা প্রশ্ন:

1. **এই model-কে সবচেয়ে কঠিন কোন একক কাজ করতে হবে?** Average-এর জন্য না, hardest task-এর জন্য pick করুন। Average সহজ। 10% hard tail-এ গিয়ে আপনি আটকান।
2. **প্রতিটা call-এর cost কত, আর প্রতি user-এ কতবার করেন?** Multiply করুন। যদি cheap per call এবং rare per user, তাহলে অনেক room আছে। Frequent হলে tier matter করে।
3. **Critical path-এ latency কি গুরুত্বপূর্ণ?** Spinner দেখে অপেক্ষা করা একজন user-এর চাহিদা nightly batch job-এর থেকে সম্পূর্ণ আলাদা।

সন্দেহ হলে দুটোই evaluate করুন। আপনার আসল 30–50টা prompt প্রতিটা tier-এ চালান, output score করুন, compare করুন। Hunch বেশি ভুল হয় eval-এর চেয়ে।
