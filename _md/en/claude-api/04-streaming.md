# Streaming Responses

By default, `messages.create(...)` waits for the entire response before returning. That's fine for short replies, but bad for anything longer than a few seconds — users stare at a spinner, and you have no chance to react to the response as it's generated.

Streaming fixes both. You get tokens as they're produced, you can render them live, and you can cancel early if you don't need the whole thing.

## Turning it on

Just pass `stream=True`:

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a haiku about CSS."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

`text_stream` yields just the text deltas — easy to wire to a UI. If you need finer-grained access (tool calls in flight, usage updates, raw events), you can iterate over `stream` itself and get typed events.

## Event types

Under the hood the API emits a series of typed events:

- **`message_start`** — beginning of the response. Has the model ID, role, initial usage.
- **`content_block_start`** — start of a new content block (text, tool_use, thinking).
- **`content_block_delta`** — incremental chunk of a block. For text, a small string. For tool_use, a JSON fragment.
- **`content_block_stop`** — end of a block.
- **`message_delta`** — top-level metadata updates (stop reason, final usage).
- **`message_stop`** — done.

You don't need to handle all of these yourself unless you're doing something exotic. The SDK helpers (`text_stream`, `accumulate_messages`, etc.) cover the common cases.

## A common UI pattern

For a chat UI, the contract is usually: render text deltas as they arrive, then finalize when the stream ends.

```python
async def chat_handler(websocket, prompt):
    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for text in stream.text_stream:
            await websocket.send_text(text)
        final = await stream.get_final_message()
        await websocket.send_json({"done": True, "usage": final.usage.model_dump()})
```

Streamed tokens land in the user's view incrementally; the final event carries authoritative usage and stop_reason.

## Cancellation

Streams are cancellable. If the user navigates away or hits stop, drop the connection (or break out of your `for` loop in the `with` block). You won't be billed for tokens that weren't generated.

```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        if user_aborted:
            break
        write(text)
```

This is one of the practical reasons to stream even when the user isn't watching the output live — it gives you a clean exit if anything goes wrong.

## Streaming with tool use

Streaming and tool use compose. As the model generates a tool call, you get `content_block_delta` events with JSON fragments. The SDK accumulates them so you can act on the complete tool call when it finalizes.

A common pattern in agent code: stream the response, and as soon as a tool_use block finalizes (before the rest of the message even arrives), kick off the tool call in parallel. The model may be still emitting text after the tool call; you don't have to wait for it to start the actual work.

## When not to stream

For batch jobs, evals, anything not user-facing — streaming adds complexity for no benefit. Just call non-streaming and read the response. Streaming is a UX feature first, an engineering feature second.

## A small gotcha

Don't accidentally hold the response in memory by concatenating every delta into a giant string when you don't need it. Render-then-discard each delta where possible. For long outputs this saves real memory and avoids re-rendering the entire transcript on every tick.
