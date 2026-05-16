# Tool Use

Tool use-ই Claude-কে question-answerer থেকে act করতে পারে এমন কিছুতে পরিণত করে। আপনি function declare করেন; Claude কখন call করবে decide করে; আপনি run করেন; result return করেন। Task শেষ না হওয়া পর্যন্ত loop।

এটাই Claude Code underneath ব্যবহার করে। বুঝলে — agent বানাতে পারবেন।

## এর shape

Plain Messages call থেকে তিনটা জিনিস বদলায়:

1. একটা **`tools`** array pass করেন — model কী call করার অনুমতি পাচ্ছে describe করে।
2. Model **`tool_use`** block দিয়ে respond করতে পারে — text-এর বদলে বা পাশাপাশি।
3. Tool run করুন, তারপর একটা **`tool_result`** message return পাঠিয়ে আবার call করুন।

## একটা tool declare করা

একটা tool হলো একটা name, description, এবং একটা input schema (JSON Schema):

```python
tools = [
    {
        "name": "get_weather",
        "description": "Return the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "units": {"type": "string", "enum": ["c", "f"], "default": "c"},
            },
            "required": ["city"],
        },
    }
]
```

Description-এই Claude-কে শেখান tool কীসের জন্য। *Explicit হোন।* "কখন ব্যবহার করতে হবে," "প্রতিটা parameter-এর মানে," "edge case।" কোন tool call করবে decide করতে — model এই text-ই reasoning-এর উপাদান হিসেবে দেখে।

## প্রথম call

```python
resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Tokyo-এর আবহাওয়া কেমন?"}],
)
```

Claude tool ব্যবহার করতে decide করলে — response-এ একটা `tool_use` block থাকবে এবং `stop_reason` হবে `"tool_use"`:

```python
resp.content
# [ToolUseBlock(type='tool_use', id='toolu_01ABC...', name='get_weather',
#               input={'city': 'Tokyo', 'units': 'c'})]
```

## Run করা ও continue

আপনি নিজে function execute করেন, তারপর result return পাঠান:

```python
def get_weather(city: str, units: str = "c"):
    # ... real implementation ...
    return {"temp": 22, "conditions": "clear"}

# tool_use block বের করুন
tool_use = next(b for b in resp.content if b.type == "tool_use")
result = get_weather(**tool_use.input)

# Conversation continue করুন — assistant-এর tool call AND result সহ
history = [
    {"role": "user", "content": "Tokyo-এর আবহাওয়া কেমন?"},
    {"role": "assistant", "content": resp.content},
    {"role": "user", "content": [
        {
            "type": "tool_result",
            "tool_use_id": tool_use.id,
            "content": str(result),
        }
    ]},
]

final = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=history,
)
print(final.content[0].text)
# "Tokyo-তে এখন 22°C এবং clear।"
```

Pattern-টা notice করুন: assistant message tool call বহন করে; পরের user message tool result বহন করে। Model কখনো আপনাকে function "run" করতে দেখে না — শুধু call এবং তার পরে result দেখে।

## Agent loop

এটাকে generalize করুন:

```python
def run_agent(client, system, tools, user_message, max_iters=10):
    history = [{"role": "user", "content": user_message}]
    for _ in range(max_iters):
        resp = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=2048,
            system=system, tools=tools, messages=history,
        )
        history.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return resp
        # Response-এর প্রতিটা tool call execute করুন
        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":
                result = TOOL_REGISTRY[block.name](**block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
        history.append({"role": "user", "content": tool_results})
    raise RuntimeError("Agent didn't finish within iteration cap.")
```

20 line-এ একটা agent। বাকি সব — memory, planning, eval — এর উপরে layer।

## Tool design-এর tip

- **Schema ছোট রাখুন।** পাঁচটা parameter অনেক। পনেরোটা unmanageable।
- **Schema-এ strong typing।** যেখানে সম্ভব enum, integer constrain, field explicitly require করুন। Schema tight হলে model সেটা better honor করে।
- **Default-এ idempotent ও safe।** যে tool-এর side effect আছে (DB-তে write, message send) — extra care দিন। একটা `dry_run` parameter বা confirmation step ভাবুন।
- **পারলে structured data return করুন।** Prose-এর paragraph-এর চেয়ে dict-এ reasoning easier।
