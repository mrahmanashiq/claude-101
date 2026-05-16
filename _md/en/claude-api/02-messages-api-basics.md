# Messages API Basics

The Messages API is the heart of the Claude API. Almost everything you do — single-shot prompts, multi-turn chat, tool use, vision, batch — runs through `client.messages.create(...)`. Once you understand its shape, the rest is parameters.

## The request

The minimum fields:

```python
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello"}
    ],
)
```

Optional but common:

- **`system`** — a string (or a list of typed blocks) for the system prompt.
- **`temperature`** — float, 0.0 to 1.0. Lower = more deterministic.
- **`top_p`** — float, alternative sampling control. Usually leave this alone.
- **`stop_sequences`** — list of strings; the model stops if it generates any of them.
- **`tools`** — list of tool definitions (next chapter).
- **`stream`** — bool; stream tokens as they generate (also its own chapter).

## The messages list

`messages` is the conversation so far. Each item has a `role` and a `content`.

`role` is either `"user"` or `"assistant"`. There is no third role here — the system prompt is its own field. Messages must alternate: user, assistant, user, assistant, and so on. The first message must be from `user`. You can't have two user messages in a row in a single request (you'd merge them client-side first).

`content` can be a string *or* a list of typed blocks. The string form is shorthand:

```python
{"role": "user", "content": "What's 2+2?"}
```

Equivalent in block form:

```python
{"role": "user", "content": [
    {"type": "text", "text": "What's 2+2?"}
]}
```

Block form is required for anything beyond plain text — images, PDFs, tool results.

## The response

```python
resp = client.messages.create(...)
```

What you get back:

- **`resp.content`** — list of content blocks. For a simple text reply, one block of `type: "text"` with a `text` field.
- **`resp.stop_reason`** — why the model stopped. Common values: `"end_turn"` (normal completion), `"max_tokens"` (you hit the limit), `"tool_use"` (the model wants to call a tool), `"stop_sequence"` (matched one of your stop strings).
- **`resp.usage`** — token counts. `input_tokens`, `output_tokens`, and (when caching) `cache_creation_input_tokens` and `cache_read_input_tokens`.
- **`resp.id`**, **`resp.model`**, **`resp.role`** — metadata.

A robust client reads `stop_reason` rather than assuming the response is "done." `max_tokens` in particular is a common silent truncation source — you ask for a long answer, set `max_tokens=512`, and the response gets cut mid-sentence. Always check.

## Multi-turn

To have a conversation, append each turn to the `messages` list and resend:

```python
history = [
    {"role": "user", "content": "What's the capital of France?"},
]

resp = client.messages.create(model="claude-sonnet-4-6",
                              max_tokens=256, messages=history)
history.append({"role": "assistant", "content": resp.content})

history.append({"role": "user", "content": "And of Germany?"})
resp = client.messages.create(model="claude-sonnet-4-6",
                              max_tokens=256, messages=history)
```

That's how chat is built — you maintain the history yourself, and Claude has no memory between calls.

## Token economics, quickly

Two rules of thumb:

- A token is roughly 4 English characters. A short paragraph is ~80 tokens; a typical page is ~500–800.
- Input tokens are cheaper than output tokens, sometimes by 3× or more. Long inputs / short outputs are cheaper than the reverse.

If you find yourself getting expensive responses, look at output. Either set a tighter `max_tokens` cap or ask Claude to be more concise.

## What you can build with just this

Honestly, a lot. A surprising amount of "AI feature" work in real products is just clever use of the Messages API with a well-crafted system prompt. Don't reach for tool use and agents until you've squeezed value out of plain Messages.
