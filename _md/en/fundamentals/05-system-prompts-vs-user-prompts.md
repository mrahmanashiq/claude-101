# System Prompts vs User Prompts

When you call the Claude API (or talk to Claude through almost any harness), there are two distinct slots you can fill: the **system prompt** and the **user message**. They look similar — both are just text — but they play different roles, and using them well is one of the easier wins available to a builder.

## What goes where

A useful way to draw the line:

- **System prompt**: the *standing orders*. Who Claude is in this app, how it should behave, what rules it must always follow, what tools it has, what tone it speaks in. This is the same on every call within a feature.
- **User message**: the *current request*. The specific question, file, or task for this turn. This changes every time.

If you think of Claude as an employee, the system prompt is the job description plus the company handbook. The user message is the email that just landed in their inbox.

## Why the split matters

Three reasons:

1. **Claude treats the system prompt with more weight.** Instructions there are harder for the user to override. This is exactly what you want for safety rules, persona, and structural constraints.
2. **It's cacheable.** A stable system prompt is the perfect target for prompt caching — you write it once, and the cache reuses it across thousands of calls at a fraction of the cost.
3. **It separates concerns in your code.** The system prompt lives in your codebase as a stable template. User messages flow through as variables. You can change the persona without touching the request-handling code, and vice versa.

## Example

A simple support-assistant skeleton:

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

user_message = "Why was I charged $49 on May 3rd?"
```

The system prompt would stay constant across every conversation. The user message is whatever the current customer wrote.

## Anti-patterns

A few things to avoid:

- **Stuffing the system prompt with current-turn details.** If the data changes per call (the user's account ID, today's date, the invoice they're asking about), that belongs in the user message or a tool result — not the system prompt. Otherwise you fragment your cache and pay more.
- **Leaving the system prompt empty.** You can, but you give up the strongest lever for shaping behavior. Even three sentences are better than nothing.
- **Hiding instructions only in the user message.** Anything the user can see, the user can fight with. Safety-critical rules go in the system prompt.

## Rule of thumb

Anything that's true *every time* this feature runs goes in the system prompt. Anything that's true *only for this specific request* goes in the user message. When you're tempted to break that rule, ask yourself why, and you'll usually find a cleaner split.
