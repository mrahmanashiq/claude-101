# সাধারণ ভুল ও যেভাবে এড়াবেন

একটা ছোট list — যেসব ভুল বারবার আসে, সাধারণত যেক্রমে কামড় দেয় সেই অনুযায়ী। প্রতিটা সহজেই fix হয় — শুধু খেয়াল রাখা শিখলে।

## ১. Claude মনে রাখবে — এই ভাবা

API call-এর মাঝে Claude-এর কোনো memory নেই। কোনোটাই না। আগের turn আবার না পাঠালে — সেগুলোর অস্তিত্ব নেই। শুনতে obvious কিন্তু নতুনদের constantly trip করায় — "আগের instruction Claude কেন ভুলে গেল?" — উত্তর সবসময় একই: কারণ এই call-এ সেটা include করেননি।

Continuity চাইলে, আপনাকে (বা চারপাশের harness-কে) প্রতিবার conversation history pass করতে হবে। Claude.ai এটা automatically করে দেয়। Claude Code-ও দেয়। নিজের app-কে explicitly করতে হয়।

## ২. Surface-গুলো গুলিয়ে ফেলা

Claude.ai-এর একটা behavior অনিবার্যভাবে API-তে available না। Claude Code-এর feature model-এর feature না — এটা *model-এর চারপাশের tool*-এর feature। কোনো blog post বা tweet পড়ার সময় জিজ্ঞেস করুন: কোন surface-এর কথা বলছে? এই পার্থক্য মানুষ যতটা মানে তার চেয়ে বেশি matter করে।

## ৩. Confident output-কে বিশ্বাস করা

Confident-sounding answer correct answer না। Language model coherent ও helpful হতে train করা, এবং সেটার মধ্যে ভুল থাকলেও coherent থাকা পড়ে। প্রতিকার verification: যা matter করে তার জন্য output সত্যের একটা source-এর সাথে check করুন — code run করুন, database query করুন, দ্বিতীয় model জিজ্ঞেস করুন, মানুষকে জিজ্ঞেস করুন।

এই pitfall-এর dangerous version হলো invented fact, কখনো hallucination বলা হয়। সবচেয়ে বেশি দেখা যায় যখন:

- Question specific, narrow fact সম্পর্কে (একটা number, একটা date, একটা name)।
- Question এমন domain-এ যেখানে model-এর knowledge shallow।
- Prompt leading (আপনি ইঙ্গিত দিয়েছেন answer exists, কিন্তু আসলে নেই)।

Mitigation: real data দিয়ে tool বা retrieval-এর মাধ্যমে model-কে ground করুন, এবং explicitly বলুন যে "জানি না" বলা allowed।

## ৪. Context-এ অতিরিক্ত data ঢালা

Long context window মানুষকে সব কিছু paste করার লোভ দেয়। দেবেন না। Quality degrade হয় যখন model পাতার পর পাতা barely-relevant material পেরিয়ে যেতে হয়। Selective হোন। সঠিক reflex: *এই task-এ আসলে minimum কত context দরকার?*

## ৫. ভুল task-এ temperature ignore করা

অনেক SDK `temperature` default 1.0 দেয়। Deterministic task-এর জন্য — extraction, classification, যে code generation-এ consistency চান — 0 বা তার কাছাকাছি নামান। Run-এর মধ্যে আরো stable output পাবেন।

Creative task-এ — brainstorming, writing — উঁচু রাখুন। আলাদা কাজ, আলাদা setting।

## ৬. Model version pin না করা

`claude-latest` call করা বা SDK-কে moving alias-এ default করতে দেওয়া experiment-এর জন্য fine। Production-এ exact model ID-তে pin করুন। নাহলে যেদিন নতুন model ship হবে, আপনার output behavior বদলাবে — কখনো better-এর জন্য, কখনো না, কিন্তু সবসময় warning ছাড়া।

## ৭. No eval, all vibes

LLM project সফল হওয়ার number-one predictor হলো builder-এর একটা small evaluation suite আছে কিনা — twenty থেকে hundred input/expected-output pair যেগুলো automatically run করতে পারে। ছাড়া, প্রতিটা change guesswork। সাথে, fast iterate করতে পারেন ও confidently ship করতে পারেন।

## ৮. Prompt-কে one-time write-only asset হিসেবে treat করা

আজ যে prompt কাজ করে সেটা পরের quarter-এ কাজ করবে না necessarily। Model বদলায়। Use case বদলায়। Prompt-কে code-এর মতো treat করুন: version করুন, review করুন, test করুন। Repo-এর `.md` prompt folder একটা real artifact, scratchpad না।

---

এটাই short list। এই আটটা internalize করলে বেশিরভাগ প্রাথমিক হোঁচট skip করবেন এবং interesting problem-এ দ্রুত পৌঁছবেন।
