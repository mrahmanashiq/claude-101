# System Prompt বনাম User Prompt

Claude API call করার সময় (বা প্রায় যেকোনো harness দিয়ে Claude-এর সাথে কথা বলার সময়) আপনার দুটো আলাদা slot পূরণ করতে হয়: **system prompt** ও **user message**। দেখতে similar — দুটোই plain text — কিন্তু এদের role আলাদা, এবং এদের ভালোভাবে ব্যবহার করা builder-এর জন্য সহজতম জয়গুলোর একটা।

## কোথায় কী যায়

একটা useful line:

- **System prompt**: *standing orders*। এই app-এ Claude কে, কীভাবে behave করবে, কোন rule সবসময় follow করবে, কী কী tool আছে, কী tone-এ কথা বলবে। প্রতিটা call-এ একই থাকে।
- **User message**: *current request*। এই turn-এর specific question, file, বা task। প্রতিবার বদলায়।

Claude-কে একজন কর্মচারী ভাবলে, system prompt হলো job description plus company handbook। User message হলো এইমাত্র inbox-এ এসে পৌঁছানো email।

## এই split কেন matter করে

তিনটা কারণ:

1. **Claude system prompt-কে বেশি ওজন দেয়।** ওখানকার instruction user-এর override করা কঠিন। Safety rule, persona ও structural constraint-এর জন্য এটাই আপনি চান।
2. **এটা cacheable।** একটা stable system prompt prompt caching-এর perfect target — একবার লেখেন, cache হাজার হাজার call-এ অনেক কম cost-এ reuse করে।
3. **আপনার code-এ separation of concerns আনে।** System prompt codebase-এ একটা stable template হিসেবে থাকে। User message variable হয়ে flow করে। Request-handling code না ছুঁয়ে persona change করতে পারেন, এবং উল্টোটাও।

## Example

একটা simple support-assistant skeleton:

```python
system_prompt = """
You are a support assistant for AcmeBilling, a SaaS billing tool.

Your job:
- Answer the user's billing question accurately.
- If you don't know, say so and offer to escalate to a human.
- Never invent invoice numbers, dates, or amounts.
- Keep replies under 200 words unless the user asks for detail.

You have access to a get_invoice(invoice_id) tool. Use it whenever
you need actual invoice data — do not guess.
"""

user_message = "৩ মে $49 charge হলো কেন?"
```

System prompt প্রতিটা conversation জুড়ে constant থাকবে। User message হবে current customer-এর লেখা যা।

## Anti-pattern

কয়েকটা এড়ানোর জিনিস:

- **Current-turn detail দিয়ে system prompt ভরে ফেলা।** Per-call data বদলালে (user-এর account ID, আজকের date, যে invoice সম্পর্কে জিজ্ঞেস করছে) — সেটা user message-এ বা tool result-এ যায়, system prompt-এ না। নাহলে cache fragment হয়ে যায় এবং বেশি pay করতে হয়।
- **System prompt empty রাখা।** পারেন, কিন্তু behavior shape করার strongest lever ছেড়ে দিচ্ছেন। তিনটা বাক্যও কিছুই না-থাকার চেয়ে better।
- **Instruction শুধু user message-এ লুকানো।** User যা দেখতে পারে, user তার সাথে লড়াই করতে পারে। Safety-critical rule system prompt-এ যায়।

## Rule of thumb

এই feature run হলে যা *প্রতিবার* সত্যি — system prompt-এ। যা শুধু *এই specific request-এ* সত্যি — user message-এ। এই rule ভাঙার লোভ হলে নিজেকে why জিজ্ঞেস করুন — সাধারণত একটা cleaner split পাবেন।
