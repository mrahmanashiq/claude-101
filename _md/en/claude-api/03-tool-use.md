# Tool Use

Tool use is what turns Claude from a question-answerer into something that can act. You declare functions; Claude decides when to call them; you run them; you give the results back. Loop until the task is done.

This is the same machinery Claude Code uses under the hood. Once you understand it, you can build agents.

## The shape of it

Three things change from a plain Messages call:

1. You pass a **`tools`** array describing what the model is allowed to call.
2. The model may respond with **`tool_use`** blocks instead of (or alongside) text.
3. You run the tool, then send back a **`tool_result`** message and call again.

## Declaring a tool

A tool is a name, a description, and an input schema (JSON Schema):

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

The description is where you teach Claude what the tool is for. *Be explicit.* "When to use this," "what each parameter means," "edge cases." This text is what the model reasons over when deciding whether to call.

## The first call

```python
resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
)
```

If Claude decides to use the tool, the response will contain a `tool_use` block and `stop_reason` will be `"tool_use"`:

```python
resp.content
# [ToolUseBlock(type='tool_use', id='toolu_01ABC...', name='get_weather',
#               input={'city': 'Tokyo', 'units': 'c'})]
```

## Running it and continuing

You execute the function yourself, then send the result back:

```python
def get_weather(city: str, units: str = "c"):
    # ... your real implementation ...
    return {"temp": 22, "conditions": "clear"}

# Find the tool_use block
tool_use = next(b for b in resp.content if b.type == "tool_use")
result = get_weather(**tool_use.input)

# Continue the conversation with the assistant's tool call AND the result
history = [
    {"role": "user", "content": "What's the weather in Tokyo?"},
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
# "It's currently 22°C and clear in Tokyo."
```

Notice the pattern: the assistant message carries the tool call; the next user message carries the tool result. The model never sees you "run" the function — it just sees the call followed by the result.

## The agent loop

Generalize this:

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
        # Execute every tool call in the response
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

That's an agent in 20 lines. Everything else — memory, planning, evals — is layered on top.

## Tips for tool design

- **Keep the schema small.** Five parameters is a lot. Fifteen is unmanageable.
- **Strong typing in the schema.** Use enums where possible; constrain integers; require fields explicitly. The model honors the schema better when it's tight.
- **Idempotent and safe by default.** Tools that have side effects (write to a DB, send a message) deserve extra care. Consider a `dry_run` parameter or a confirmation step.
- **Return structured data when you can.** A dict is easier for the model to reason over than a paragraph of prose.
