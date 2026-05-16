# MCP Server বানানো

আপনার দরকারি MCP server না থাকলে — লিখুন। Protocol well-specified, SDK friendly, এবং একটা useful server সাধারণত কয়েকশ line code। একটা লিখলে — clean tool design-এর forcing function হয়, এবং একটা লিখার পর পুরো agent ecosystem better বুঝবেন।

## কী বানাচ্ছেন

একটা MCP server হলো একটা ছোট program। MCP protocol-এ কথা বলে — stdio-এর উপর (most common) বা HTTP+SSE। Expose করে:

- **Tools** — callable function, schema সহ, যা agent invoke করে।
- **Resources** — read-only data source যা agent URI দিয়ে fetch করতে পারে।
- **Prompts** — optional prompt template যা agent request করতে পারে।

বেশিরভাগ server-এর জন্য tool 90% value। সেখান থেকে শুরু; resource ও prompt যদি fit করে তবেই add করুন।

## Python-এ একটা minimum server

Python SDK `mcp`। একটা minimal stdio server:

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as t

server = Server("my-server")

@server.list_tools()
async def list_tools() -> list[t.Tool]:
    return [
        t.Tool(
            name="add",
            description="Add two numbers and return the sum.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
            },
        )
    ]

@server.call_tool()
async def call_tool(name, arguments):
    if name == "add":
        return [t.TextContent(type="text", text=str(arguments["a"] + arguments["b"]))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

এটা একটা fully working MCP server। Script path একটা Claude Code config-এ drop করুন — সাথে সাথে available।

## Tool design principle

Useful tool — good function signature-এর মতো rule follow করে:

- **Name ও description।** Unambiguous হোন। `query_db` fine; `q` না। Description-ই Claude পড়ে decide করতে — tool apply কিনা। Code-review audience-এর জন্য না, model-এর জন্য লিখুন।
- **Tight schema।** Value constrain করতে `enum` ব্যবহার করুন। Mandatory field-এ `required`। Schema যত narrow — Claude তত কম wrong call করে।
- **Small surface।** পাঁচটা well-designed tool পনেরোটা mediocre-কে হারায়। Server-এ 30টা tool থাকলে — agent confuse করবে কোনটা pick করবে।
- **Idempotence যেখানে possible।** Easy retry, fewer surprise।
- **Structured return।** Model parse করতে পারে এমন JSON বা compact text return করুন। Free-form paragraph এড়ান — যদি না একটা generate করাই *whole point*।

## Error

একটা tool fail করলে — exception trace না, একটা *structured error* return করুন। Model একটা clear error message-এর উপর reason করতে পারে ও different কিছু try করতে পারে; একটা Python stack dump-এর উপর পারে না।

```python
return [t.TextContent(
    type="text",
    text=json.dumps({
        "error": "row_not_found",
        "detail": f"No row matched id={row_id}",
        "hint": "Use list_ids() to see valid options.",
    }),
)]
```

`hint` field gold — retry loop না লিখে model-কে productive recovery-এর দিকে nudge করে।

## Permission ও side effect

MCP server-কে production code হিসেবে treat করুন। Side effect-যুক্ত যেকোনো কিছু (database write, API mutation, file system change) দরকার:

- Default-এ একটা **read-only mode**। Write explicitly opt in হলেই add।
- Destructive operation-এর জন্য **confirmation hook**। Client (Claude Code) user-কে confirmation surface করবে।
- **Scoped credential।** "Just in case" admin-level access দেবেন না। যে narrowest permission কাজ করে দেন।

## Distribution

Kaj করলে distribute করুন। Option:

- **Local-only script।** Personal tooling-এর জন্য fine। Config-এ path, ব্যস।
- **npm বা PyPI package।** Others-কে one command-এ install করতে দেয়।
- **Public registry।** MCP server-এর একটা directory আছে; general-purpose হলে submit করুন।

Well-designed server যে client-এর জন্য built — তাকে outlive করে, কারণ protocol portable। আজ Claude Code-এর জন্য লেখা server দু বছর পর এমন কিছু ব্যবহার করতে পারে যেটা এখনো exist করে না।

## Watch করার জিনিস

- **Schema drift।** একটা tool-এর schema change করলে — যেসব agent পুরোনো shape শিখেছে তারা misbehave করবে। Tool name version করুন (`query_v2`) বা একটা deprecation window-এর জন্য পুরোনো shape accept করুন।
- **Long operation।** 30 second-এর tool call agent block করে। Long কাজের জন্য — সাথে সাথে একটা job ID return করুন এবং একটা `poll_job` tool offer করুন status check করতে।
- **Streaming।** কিছু server long-running tool expose করে যা partial result stream করে। Protocol support করে; SDK helper-ও করে। Large dataset scan করা tool-এর জন্য useful।

প্রথম server লেখা hardest। চতুর্থটা fun। ততক্ষণে আপনি আপনার codebase, service, এমনকি team-এর process — সব potential MCP surface হিসেবে দেখবেন — এবং right হবেন।
