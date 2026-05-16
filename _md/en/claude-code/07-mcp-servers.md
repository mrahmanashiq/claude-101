# MCP Servers

MCP — the Model Context Protocol — is the open standard for plugging external tools and data into an AI agent. An **MCP server** is a small program that exposes capabilities (read this database, search this issue tracker, control this browser) over a defined protocol. Claude Code is an MCP *client*; you point it at servers, and their tools show up in Claude's toolset.

If you've ever installed a browser extension, you have the mental model. Each MCP server is a self-contained add-on. The protocol is the contract.

## Why it exists

Before MCP, every agent had to integrate every external service one-off — a Postgres tool, a Slack tool, a Linear tool, each written from scratch for each agent. That doesn't scale. With MCP, the server is written once and any compliant client (Claude Code, Cursor, Cline, Continue, custom agents) can use it.

Practically, this means:

- You can install a community-maintained MCP server for the service you care about and have it just work.
- You can write a small MCP server for your *own* internal tools and immediately make them available to your agent.

## What a server looks like

An MCP server typically exposes three kinds of things:

- **Tools** — functions the agent can call (`query_database`, `create_issue`, `take_screenshot`).
- **Resources** — read-only data sources (a file, a database table, a docs page) the agent can fetch.
- **Prompts** — pre-canned prompt templates the agent can request.

Tools are by far the most common; resources and prompts are less universally adopted.

## Useful servers you might add

A few examples of what's out there:

- **Database servers** — query Postgres, MySQL, or SQLite directly without writing client code.
- **Browser servers** (e.g. Playwright) — Claude can click, type, screenshot, and read network traffic in a real browser.
- **Issue trackers** — Linear, JIRA, GitHub Issues. Read tickets, create them, comment.
- **Note systems** — Notion, Obsidian, Confluence.
- **Cloud SDKs** — wrappers around AWS / GCP / Vercel APIs for specific operations.

There's a public registry of MCP servers, and most are a one-line install.

## Configuring servers

Servers are listed in your `claude_desktop_config.json` (desktop app) or in `.claude/mcp_servers.json` (CLI), depending on the surface. A minimal entry looks like:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
    }
  }
}
```

Restart the agent (or reload, depending on the surface) and the server's tools appear in Claude's toolset.

## Permissions and risk

MCP tools call out to external systems. A database tool can run arbitrary SQL. A browser tool can navigate to any URL. Treat each server as you would a CLI you're handing to an agent — give it the minimum credentials it needs, and use the harness's permission settings to control which tools auto-approve and which prompt first.

In particular: be careful with **write** capabilities (creating tickets, sending messages, running mutations). For most early experiments, configure servers in read-only mode and only enable writes when you've watched the agent's behavior for a while.

## Writing your own

If your team has an internal service that doesn't have an MCP server yet, write one. The protocol is well-documented and there are SDKs in Python and TypeScript. Most internal servers are under 300 lines of code, and you'll thank yourself the first time you say "find the customer that..." and Claude just does it.

We cover building MCP servers in the Advanced Patterns course.
