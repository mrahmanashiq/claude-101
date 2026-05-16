# API দিয়ে শুরু

Claude API হলো সেই ভিত্তি যার উপর বাকি সব দাঁড়িয়ে। Claude.ai, Claude Code, desktop app — সবাই এটাকে underneath call করে। নিজে call করতে পারলে এই product-গুলো যা করে সব বানাতে পারেন, এবং সেগুলো যা করে না — তাও অনেক।

## যা দরকার

তিনটা জিনিস:

1. একটা **Anthropic account** — console.anthropic.com-এ sign up করুন।
2. **API credit** বা একটা paid plan। নতুন account experiment করার জন্য small amount free credit পায়।
3. একটা **API key**। Console-এ generate করুন। Environment variable-এ store করুন, কখনো source code-এ না।

## একটা SDK pick করুন

SDK ব্যবহার করতেই হবে এমন না — API plain HTTPS plus JSON — কিন্তু SDK জীবন সহজ করে। দুটো official: Python ও TypeScript:

```bash
# Python
pip install anthropic

# Node / TypeScript
npm install @anthropic-ai/sdk
```

Go, Rust, Java, ও অন্য ভাষায় community SDK আছে। বেশিরভাগই একই endpoint-এর thin wrapper।

## আপনার প্রথম call

Hello-world এমন দেখায়। Python:

```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[
        {"role": "user", "content": "এক বাক্যে: API কী?"}
    ],
)

print(resp.content[0].text)
```

TypeScript প্রায় identical:

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();  // ANTHROPIC_API_KEY env থেকে read করে

const resp = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 512,
  messages: [
    { role: "user", content: "এক বাক্যে: API কী?" },
  ],
});

console.log(resp.content[0].text);
```

ব্যস। Run করলে response পান। স্বাগতম।

## একটা call-এর anatomy

কয়েকটা জিনিস notice করুন:

- **`model`** — exact model ID। Production-এ specific version-এ pin করুন।
- **`max_tokens`** — response length-এর upper bound। Model আগে থামতে পারে; cross করতে পারে না।
- **`messages`** — conversation একটা list হিসেবে। প্রতিটা message-এর একটা `role` (`user` বা `assistant`) ও `content`।
- Response **`content`** ও একটা list — single string না। কারণ Claude একটা response-এ multiple "block" return করতে পারে (text, tool call, thinking, image)। Simple text reply-এর জন্য `text` type-এর একটা block পাবেন।

## Environment hygiene

দিন এক থেকে দুটো অভ্যাস lock করুন:

- **API key environment variable-এ, কখনো code-এ না।** Private repo-ও দুর্ঘটনাবশত public হয়ে যায়।
- **Log-এ full response print করবেন না।** এগুলোতে user data থাকে, scale-এ re-read করা expensive। যে structured field-গুলো actually দরকার সেগুলো log করুন।

## প্রথম দিন থেকে cost সচেতন

প্রতিটা call টাকা লাগে। Console একটা usage dashboard দেখায় — প্রথম সপ্তাহে check করুন। Per-model rate এবং আপনার spend breakdown দেখবেন।

দুটো cost lever জেনে রাখুন:

- **Cheaper model।** Haiku Sonnet-এর চেয়ে অনেক cheaper; Sonnet Opus-এর চেয়ে অনেক cheaper। যে smallest model কাজ করে সেটা ব্যবহার করুন।
- **Prompt caching।** একটা long prefix re-use করলে (system prompt, document, example) — caching enable করলে cached অংশে rate-এর একটা ভগ্নাংশ pay করেন। এটার জন্য আলাদা পুরো chapter আছে।

এতটুকু দিয়ে dangerous হওয়ার মতো জ্ঞান হলো। পরের chapter Messages API ও response-এর shape-এ deeper যাবে।
