# Cost Optimization

Cost AI feature-এর silent killer। একটা demo per call $0.05 cost cheap শোনায় — যতক্ষণ না দশ লক্ষ user দিয়ে multiply করেন এবং বুঝতে পারেন — feature প্রতিটা interaction-এ টাকা হারাচ্ছে। বেশিরভাগ cost problem raw model pricing থেকে আসে না — sloppy usage pattern থেকে আসে যা compound করে।

Quality না হারিয়ে cost কমানোর playbook এখানে।

## টাকা কোথায় যাচ্ছে জানুন

যা measure করতে পারেন না — সেটা optimize করতে পারেন না। Minimum track করুন:

- **Per call cost** — feature ও model অনুযায়ী breakdown।
- **Per user per day cost।**
- **Business term-এ per output cost** — per support ticket resolved, per code review, per onboarding completed।

এই number না থাকলে — chapter-এর বাকি theoretical। আগে measurement bring করুন, তারপর optimize।

## যে smallest model কাজ করে — pick করুন

Rule out করেননি এমন প্রতিটা tier-এ আপনার eval re-run করুন। Classification, extraction, short generation-এ প্রায়ই Haiku Sonnet-এর 90% করে। Pass rate acceptable থাকলে — cost drop বিশাল, সাধারণত 5–10×।

ধরে নেবেন না bigger model = better outcome। Measure করুন।

## Aggressively cache

Single highest-impact lever, নিজের API chapter-এ cover। Production discipline-এ recap:

- Stable prefix (system prompt, tool definition, reference doc) cacheable mark।
- Per-request data cached content-এর *পরে* রাখুন, interleave করবেন না।
- Cache hit rate monitor — production-এ >70% target।
- Long-lived (1-hour) cache tier sustained workload-এ enable।

Cached prefix full input rate-এর ~10% charge করে। বেশিরভাগ feature-এর জন্য — profit ও loss-এর পার্থক্য।

## max_tokens tighten করুন

`max_tokens` cap, target না। কিন্তু প্রায়ই "just in case" উঁচু set করা থাকে, এবং Claude happily সেই পর্যন্ত generate করে। Actual output token distribution দেখুন। 99% response 300 token-এর নিচে হলে — `max_tokens=2048` দরকার নেই।

এটার সাথে brevity-চাওয়া prompt pair করুন। "2-3 বাক্যে reply" — quality না হারিয়ে routinely output cost 30%+ কমায়।

## Repeatable task-এর জন্য temperature drop

Classifier, extractor, যেখানে consistency চান — `temperature=0`। আরও cache-friendly behavior পাবেন (similar input → similar output → better caching) এবং variability eliminate করেন — যা handle করতে কখনো retry cost pay করছিলেন।

## History compress

Long conversation দুইভাবে expensive: per call বেশি input token, এবং worse model focus। Periodically compress করুন:

- Older turn-কে একটা short paragraph-এ summarize।
- Relevant info subsequent turn-এ থাকলে — tool-call/tool-result pair drop।
- Conversation long হয়ে আসলে — clean system prompt + recent context সহ restart।

Agent loop-এর জন্য particularly: প্রতি K iteration-এ — model-কে summarize করতে বলুন "যা শিখেছি ও কী বাকি"। Long history সেই summary দিয়ে replace করুন। Agent কিছু fine-grained memory হারাবে কিন্তু অনেক cheaper থাকবে।

## Cost cap-এর জন্য streaming

Streaming আপনাকে response আসতে দেখতে দেয়। Model rails-এর বাইরে যেতে শুরু করলে — ভুল কিছু generate, নিজেকে repeat, planned length cross — মাঝপথে abort করতে পারেন। যে token generate হয়নি — pay করেননি।

Interactive tool-এর জন্য smart cancellation সহ streaming effective output cost noticeably কমাতে পারে।

## Latency matter না করলে batch

High-volume, non-real-time workload-এর জন্য — analytics, content moderation pipeline, eval run — Batch API ব্যবহার করুন। ~50% discount, same quality। যা যা একটা giant `asyncio.gather` দিয়ে run করতেন — সব Batch candidate।

## Cheaper tool, cheaper outcome

Tool-use loop-এ tool *call* cheap, কিন্তু *result* পরবর্তী turn-এ পড়া হয়। 50KB blob return করা tool এখন prompt-এর অংশ চিরকালের জন্য (compress না করা পর্যন্ত)। দুটো implication:

- **Tool-গুলো model-এর জন্য দরকারি minimum data return করুক।** "পুরো table" না — "তিনটা row যা match"। "পুরো HTML page" না — "relevant section"।
- **Server filter ও pagination support করুক।** Model যা actually দরকার চাইতে দিন।

Agent system-এর সবচেয়ে বড় hidden cost source-গুলোর একটা।

## Rarely re-prompt

একটা common cost trap: প্রতিটা UI tweak full inference re-trigger করছে। Call site দেখুন — semantically কিছু না বদলালেও re-prompt করছেন কিনা? Client-side result cache। Debounce। দরকার না হলে প্রতিটা keystroke-এ re-call না।

## Loop right-size

Agent loop-এর জন্য iteration count cost linearly drive করে। আপনার agent regularly একটা task শেষ করতে 20 iteration নিচ্ছে — কেন দেখুন:

- Tool যথেষ্ট info return করছে?
- Task একটা agent-এর জন্য too big? (Subagent দিয়ে decompose।)
- Model বারবার wrong tool pick করছে? (Description tighten।)
- `max_iters` too generous, একটা real bug mask করছে?

Loop tighten দুইবার pay off — fewer call, ও faster response।

## Eval-এর connection

প্রতিটা cost optimization quality risk করে। প্রতিটা change-এর আগে ও পরে eval suite run করুন। Quality hold ও cost drop হলে — ship। Quality drop-ও হলে — too far গেছেন।

## একটা reality check

Most cost-effective Claude feature, এই order-এ:

1. Right model tier (most expensive না) pick।
2. প্রতিটা stable prefix cache।
3. Output length trim।
4. Where appropriate batch / async।
5. Structurally simple থাকা — unnecessary tool, subagent, iteration কিছুই না।

Boring optimization skip করে "agentic যাওয়া" — feature better না হয়ে expensive হওয়ার উপায়। Boring stuff করুন। তারপর fancy stuff layer in করুন যেখানে এটার keep earn করে।
