# Streaming Response

Default-এ `messages.create(...)` পুরো response generate হওয়া পর্যন্ত wait করে। Short reply-এর জন্য ঠিক আছে, কিন্তু কয়েক second-এর বেশি কোনো কিছুর জন্য খারাপ — user spinner দেখে, এবং generate হওয়ার সাথে সাথে react করার কোনো সুযোগ নেই।

Streaming দুটোই fix করে। Token-গুলো produce হতেই আপনি পান, live render করতে পারেন, এবং পুরোটা না লাগলে আগে cancel করতে পারেন।

## এটা চালু করা

শুধু `stream=True` pass করুন:

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "CSS নিয়ে একটা haiku লেখো।"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

`text_stream` শুধু text delta yield করে — UI-তে wire করা সহজ। Finer-grained access দরকার হলে (flying tool call, usage update, raw event) — `stream` নিজের উপর iterate করতে পারেন এবং typed event পাবেন।

## Event type

Underneath API একটা series-এর typed event emit করে:

- **`message_start`** — response-এর শুরু। Model ID, role, initial usage।
- **`content_block_start`** — একটা নতুন content block-এর শুরু (text, tool_use, thinking)।
- **`content_block_delta`** — একটা block-এর incremental chunk। Text-এর জন্য একটা ছোট string। Tool_use-এর জন্য একটা JSON fragment।
- **`content_block_stop`** — block-এর শেষ।
- **`message_delta`** — top-level metadata update (stop reason, final usage)।
- **`message_stop`** — শেষ।

Exotic কিছু না করলে নিজে এই সব handle করতে হয় না। SDK helper (`text_stream`, `accumulate_messages`, ইত্যাদি) common case cover করে।

## একটা common UI pattern

Chat UI-এর জন্য contract সাধারণত: text delta render করুন আসার সাথে সাথে, তারপর stream শেষ হলে finalize করুন।

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

Streamed token user-এর view-তে incrementally আসে; final event authoritative usage ও stop_reason বহন করে।

## Cancellation

Stream cancellable। User navigate করে চলে গেলে বা stop চাপলে — connection drop করুন (বা `with` block-এর `for` loop থেকে break করুন)। Token যা generate হয়নি — তার জন্য bill হবে না।

```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        if user_aborted:
            break
        write(text)
```

User live output না দেখলেও stream করার একটা practical কারণ এটাই — কিছু ভুল হলে একটা clean exit।

## Tool use-এর সাথে streaming

Streaming ও tool use compose করে। Model একটা tool call generate করার সাথে সাথে — JSON fragment সহ `content_block_delta` event পান। SDK accumulate করে যাতে tool call finalize হলে act করতে পারেন।

Agent code-এ একটা common pattern: response stream করুন, এবং একটা tool_use block finalize হলেই (message-এর বাকি অংশ আসার আগেই) — parallel-এ tool call kick off করুন। Tool call-এর পরও model হয়তো text emit করছে; কাজ শুরু করতে wait করতে হয় না।

## কখন stream করবেন না

Batch job, eval, যেকোনো non-user-facing — streaming complexity add করে কোনো benefit ছাড়া। Just non-streaming call করুন এবং response পড়ুন। Streaming UX feature, engineering feature না primarily।

## একটা ছোট gotcha

প্রতিটা delta একটা giant string-এ concatenate করে accidentally memory-তে response ধরে রাখবেন না — যদি না দরকার। প্রতিটা delta যেখানে possible render-then-discard করুন। Long output-এর জন্য এটা real memory বাঁচায় এবং প্রতিটা tick-এ পুরো transcript re-render এড়ায়।
