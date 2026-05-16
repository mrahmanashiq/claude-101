# Context Window-এর ব্যাখ্যা

**Context window** হলো একটা single call-এ Claude কতটুকু text consider করতে পারে। এটা token-এ মাপা হয় — মোটামুটি ৪ character English text per token। সাম্প্রতিক Claude model-গুলো hundreds of thousands token-এর context support করে, কিছু extended variant এক million পর্যন্ত যায়।

এটা অনেক। কিন্তু "অনেক" মানে "অসীম" না, এবং context-কে infinite ভাবা সবচেয়ে common rookie ভুলগুলোর একটা।

## কী কী context হিসেবে count হয়

একটা call-এ model-কে যা যা পাঠান সবই context:

- **System prompt** (role, tone, rule সম্পর্কে high-level instruction)
- **Conversation history** (আগের সব turn, user ও assistant দুজনেরই)
- যেকোনো **attached document** (pasted file, PDF, image)
- **Tool definition** ও আগের turn-এর **tool result**

সবগুলোই একই budget-এর জন্য compete করে। 200k token window থাকলে এবং এর মধ্যে 180k conversation-এ চলে গেলে, পরের exchange ও response-এর জন্য 20k বাকি।

## "Lost in the middle"

বড় window থাকলেও, model context-এর শুরু আর শেষে সবচেয়ে strongly attend করে। একটা long prompt-এর মাঝে চাপা পড়া information miss হওয়ার বা de-emphasize হওয়ার সম্ভাবনা বেশি। দুটো practical implication:

- **সবচেয়ে important instruction-গুলো একদম শুরুতে বা একদম শেষে রাখুন।**
- **Long document-এর জন্য, question চাপা ফেলবেন না।** আগে task state করুন, তারপর document, তারপর শেষে task আবার restate করুন।

## আপনি প্রতি token-এর জন্য, প্রতিবার pay করেন

API ব্যবহার করলে, প্রতিটা call-এ আপনাকে per input token bill করা হয়। 100k-token history জমা হওয়া একটা long-running chat *প্রতিটা নতুন user turn-এ* সেই পুরো history-এর জন্য charge করবে। এখানেই prompt caching একটা বড় lever হয়ে ওঠে (API course-এ পরে cover করব) — এটা আপনাকে full price re-pay না করে একটা long stable prefix reuse করতে দেয়।

## কখন compact করবেন

Conversation দীর্ঘ হয়ে গেলে তিনটা option:

- **Summarize and continue.** পুরোনো turn-গুলোকে একটা short summary দিয়ে replace করুন, সাম্প্রতিক turn-গুলো verbatim রাখুন। Fidelity হারায় কিন্তু cheap থাকে।
- **Trim by relevance.** যেসব turn current question-এর জন্য useful না সেগুলো drop করুন। কোন turn relevant সেটা detect করতে পারলে best।
- **Start fresh.** কখনো সবচেয়ে clean answer। Relevant fact system prompt-এ দিয়ে একটা নতুন conversation শুরু করুন।

Claude Code নিজের context ভরে গেলে কিছুটা automatically করে দেয়, কিন্তু নিজের application-এ আপনাকে নিজেই manage করতে হবে।

## একটা mental model

Context-কে memory ভাবার বদলে workbench ভাবুন। Model শুধু এই মুহূর্তে bench-এ যা আছে সেটাই দেখে। Bench-এর বাইরে কিছু থাকলে যেন সেটার অস্তিত্বই নেই। Builder হিসেবে আপনার কাজ — current task-এর জন্য সঠিক জিনিস bench-এ রাখা — বেশিও না, কমও না।

!!! note
    Long context window একটা capability, strategy না। 500k token dump করতে *পারেন* মানে এই না যে *দরকার*। Context যখন আসলে যা দরকার তাতেই focused, model-এর quality তখনই best।
