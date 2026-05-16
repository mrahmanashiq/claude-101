# Getting Started with the API

The Claude API is the foundation everything else sits on. Claude.ai, Claude Code, the desktop app — all of them call it under the hood. Once you can call it yourself, you can build anything those products do, and a lot they don't.

## What you need

Three things:

1. An **Anthropic account** — sign up at console.anthropic.com.
2. **API credits** or a paid plan. New accounts get a small amount of free credit to experiment with.
3. An **API key**. Generate one in the console. Store it in an environment variable, never in source code.

## Pick an SDK

You don't have to use an SDK — the API is plain HTTPS with JSON — but the SDKs make life easier. The two official ones are Python and TypeScript:

```bash
# Python
pip install anthropic

# Node / TypeScript
npm install @anthropic-ai/sdk
```

There are community SDKs in Go, Rust, Java, and others. They're mostly thin wrappers around the same endpoints.

## Your first call

The hello-world looks like this. Python:

```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[
        {"role": "user", "content": "In one sentence: what is the API?"}
    ],
)

print(resp.content[0].text)
```

TypeScript is nearly identical:

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();  // reads ANTHROPIC_API_KEY from env

const resp = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 512,
  messages: [
    { role: "user", content: "In one sentence: what is the API?" },
  ],
});

console.log(resp.content[0].text);
```

That's it. Run it, you get a response. Welcome.

## Anatomy of a call

A few things to notice:

- **`model`** — exact model ID. Pin to a specific version in production.
- **`max_tokens`** — the upper bound on response length. The model may stop short; it cannot exceed.
- **`messages`** — the conversation as a list. Each message has a `role` (`user` or `assistant`) and `content`.
- The response **`content`** is also a list — not a single string. That's because Claude can return multiple "blocks" in a response (text, tool calls, thinking, images). For a simple text reply you'll have one block of type `text`.

## Environment hygiene

Two early habits to lock in:

- **API keys in environment variables, never in code.** Even private repos accidentally end up public.
- **Don't print full responses in your logs.** They contain user data, and they're expensive to re-read at scale. Log structured fields you actually need.

## Cost awareness from day one

Every call costs money. The console shows a usage dashboard — check it during your first week. You'll see per-model rates and your spend breakdown.

Two cost levers to know about:

- **Cheaper model.** Haiku is much cheaper than Sonnet; Sonnet is much cheaper than Opus. Use the smallest model that does the job.
- **Prompt caching.** If you re-use a long prefix (system prompt, document, examples), enable caching to pay a fraction of the rate on the cached part. We have a whole chapter on this.

That's enough to be dangerous. The next chapter goes deeper into the Messages API and the shape of responses.
