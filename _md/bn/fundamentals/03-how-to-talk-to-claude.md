# কীভাবে Claude-এর সাথে কথা বলবেন

Prompt লেখা একটা সত্যিকারের skill, কিন্তু rocket science না। কয়েকটা অভ্যাস ধারাবাহিকভাবে apply করলে Claude অনেক বেশি useful হয়ে যায়। কোনোটাই জাদু না — যেভাবে একজন বুদ্ধিমান কিন্তু নতুন colleague-কে কাজ দিতেন, সেটাই।

## Output সম্পর্কে specific হোন

সবচেয়ে বড় improvement আসে Claude-কে exactly বলা থেকে — answer-এর shape কেমন হবে। "এটা summarize করো" বলার বদলে চেষ্টা করুন: "এটা তিনটা bullet point-এ summarize করো, প্রতিটা verb দিয়ে শুরু, মোট 80 word-এর নিচে।" Specifics model-কে commit করতে দেয়; vague ask-এ এটা hedge করে।

## Model-এর যা দরকার সেই context দিন

Model শুধু সেটাই জানে যা আপনি prompt-এ রাখেন। Codebase সম্পর্কে জিজ্ঞেস করলে relevant file paste করুন। কোনো document নিয়ে জিজ্ঞেস করলে — paste করুন। Tone match করতে বললে — উদাহরণ paste করুন। Context আপনি যা ভাবেন তার চেয়ে cheap — বেশিরভাগ prompt overfeed নয়, underfeed করে।

## কাজ structured হলে structure ব্যবহার করুন

Claude formatting-এ গুরুত্ব দেয়। Multiple input থাকলে tag করুন:

```
<user_message>
Bill টা গত মাসের, এই মাসের না।
</user_message>

<order_details>
order_id: 4382
created: 2026-04-12
status: shipped
</order_details>

User কোন order-এর কথা বলছে বলো।
```

XML-style tag, header, numbered step — যা কিছু structure-কে obvious করে — সব সাহায্য করে। বাধ্যতামূলক না, কিন্তু ambiguity কমায়।

## বলার চেয়ে দেখান

একটা particular style চাইলে সেটার একটা example paste করুন। Particular output format চাইলে একটা sample output paste করুন। একটা concrete example একটা paragraph description-এর চেয়ে বেশি value-এর। দুটো example দুটো paragraph-এর চেয়ে বেশি value-এর।

## Answer দেওয়ার আগে model-কে ভাবতে দিন

Non-trivial reasoning-এর জন্য Claude-কে encourage করুন final answer-এর আগে problem-টা ভেতরে কাজ করে নিতে। একটা simple "answer দেওয়ার আগে step by step ভাবো" অনেক দূর নিয়ে যায়। আরও ভালো — একটা explicit scratchpad দিন:

```
Answer দেওয়ার আগে তোমার reasoning <thinking></thinking> tag-এর ভেতরে লেখো।
তারপর final answer <answer></answer> tag-এর ভেতরে দাও।
```

এটা কোনো magic incantation না — কাজ করে কারণ এটা model-কে reasoning-এর space দেয় first token-এ commit হতে বাধ্য করার বদলে।

## Over-instruction করবেন না

একটা common failure mode হলো rule-এর উপর rule চাপানো: "X করো না, Y-ও না, কিন্তু Z নিশ্চিত করো, এবং W কখনো ভুলো না।" Long rule list track রাখা model-এর জন্য কঠিন, এবং এরা প্রায়ই contradict করে। Instruction ছোট রাখুন। যে তিন-চারটা matter করে সেগুলো pick করুন, বাকিগুলো ছেড়ে দিন।

## Iterate করুন

প্রথম prompt সাধারণত best না। Try করুন, output কোথায় ভুল দেখুন, এবং সেই specific failure address করতে prompt adjust করুন। বেশিরভাগ "prompt engineering" আসলে এই loop — run, inspect, refine — একটু discipline দিয়ে।
