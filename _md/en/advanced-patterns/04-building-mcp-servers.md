# Building MCP Servers

If the MCP server you need doesn't exist, you write it. The protocol is well-specified, the SDKs are friendly, and a useful server is usually a few hundred lines of code. Writing one is a forcing function for clean tool design — once you've built one, you understand the whole agent ecosystem better.

## What you're building

An MCP server is a small program. It speaks the MCP protocol over stdio (most common) or HTTP+SSE. It exposes:

- **Tools** — callable functions, with schemas, that the agent invokes.
- **Resources** — read-only data sources the agent can fetch by URI.
- **Prompts** — optional prompt templates the agent can request.

For most servers, tools are 90% of the value. Start there; add resources and prompts only if they fit.

## A minimum server in Python

The Python SDK is `mcp`. A minimal stdio server:

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

That's a fully working MCP server. Drop the script path into a Claude Code config and it becomes available immediately.

## Tool design principles

A useful tool follows the same rules as a good function signature:

- **Names and descriptions.** Be unambiguous. `query_db` is fine; `q` is not. The description is what Claude reads to decide whether the tool applies — write it for the model, not for a code-review audience.
- **Tight schemas.** Use `enum` to constrain values. Use `required` to lock in mandatory fields. The narrower the schema, the fewer wrong calls Claude makes.
- **Small surface.** Five well-designed tools beat fifteen mediocre ones. If your server has 30 tools, agents will get confused about which to pick.
- **Idempotence where possible.** Easy retries, fewer surprises.
- **Structured returns.** Return JSON or compact text the model can parse. Avoid free-form paragraphs except when generating one is the *whole point*.

## Errors

When a tool fails, return a *structured error* not an exception trace. The model can reason over a clear error message and try something different; it can't reason over a Python stack dump.

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

The `hint` field is gold — it nudges the model toward a productive recovery without you writing a retry loop.

## Permissions and side effects

Treat MCP servers as production code. Anything with side effects (database writes, API mutations, file system changes) needs:

- A **read-only mode** as the default. Add writes only when explicitly opted in.
- **Confirmation hooks** for destructive operations. The client (Claude Code) will surface confirmations to the user.
- **Scoped credentials.** Don't give the server admin-level access "just in case." Give it the narrowest permissions that work.

## Distribution

Once it works, distribute it. Options:

- **Local-only script.** Fine for personal tooling. Path in the config, that's it.
- **npm or PyPI package.** Lets others install with one command.
- **Public registry.** There's a directory of MCP servers; submit yours if it's general-purpose.

A well-designed server outlives the client it was built for, because the protocol is portable. The server you write today for Claude Code might be used in two years by something that doesn't exist yet.

## Things to watch

- **Schema drift.** If you change a tool's schema, agents that learned the old shape will misbehave. Version your tool names (`query_v2`) or accept the old shape for a deprecation window.
- **Long operations.** A tool call that takes 30 seconds blocks the agent. For long work, return a job ID immediately and offer a `poll_job` tool to check status.
- **Streaming.** Some servers expose long-running tools that stream partial results. The protocol supports it; the SDK helpers do too. Useful for tools that scan large datasets.

The first server you write is the hardest. The fourth is fun. By then you'll see your codebase, your services, even your team's processes, as potential MCP surfaces — and you'll be right.
