# MCP Server

MCP — Model Context Protocol — হলো একটা AI agent-এ external tool ও data plug করার জন্য open standard। একটা **MCP server** হলো একটা ছোট program যা capability (এই database পড়, এই issue tracker search করো, এই browser control করো) defined protocol-এর উপর expose করে। Claude Code একটা MCP *client*; আপনি server-এ point করেন, আর তাদের tool Claude-এর toolset-এ চলে আসে।

Browser extension install করে থাকলে mental model আছে। প্রতিটা MCP server একটা self-contained add-on। Protocol হলো contract।

## কেন আছে

MCP-এর আগে প্রতিটা agent প্রতিটা external service one-off integrate করতে হতো — একটা Postgres tool, একটা Slack tool, একটা Linear tool, প্রতিটা agent-এর জন্য scratch থেকে। এটা scale করে না। MCP-এর সাথে server একবার লেখা হয়, এবং যেকোনো compliant client (Claude Code, Cursor, Cline, Continue, custom agent) এটা ব্যবহার করতে পারে।

Practically এটার মানে:

- যে service-এ আগ্রহ — তার জন্য একটা community-maintained MCP server install করতে পারেন এবং সরাসরি কাজ করে।
- নিজের internal tool-এর জন্য *একটা ছোট MCP server লিখতে পারেন* এবং সাথে সাথে agent-এ available করতে পারেন।

## একটা server দেখতে কেমন

একটা MCP server সাধারণত তিন ধরনের জিনিস expose করে:

- **Tools** — function যা agent call করতে পারে (`query_database`, `create_issue`, `take_screenshot`)।
- **Resources** — read-only data source (একটা file, database table, docs page) যা agent fetch করতে পারে।
- **Prompts** — pre-canned prompt template যা agent request করতে পারে।

Tool সবচেয়ে common; resource ও prompt কম universally adopted।

## যে server-গুলো add করতে পারেন

কী আছে — কয়েকটা example:

- **Database server** — Postgres, MySQL, বা SQLite direct query করুন client code না লিখে।
- **Browser server** (যেমন Playwright) — Claude একটা real browser-এ click করতে, type করতে, screenshot নিতে, network traffic পড়তে পারে।
- **Issue tracker** — Linear, JIRA, GitHub Issues। Ticket পড়া, create, comment।
- **Note system** — Notion, Obsidian, Confluence।
- **Cloud SDK** — specific operation-এর জন্য AWS / GCP / Vercel API-এর wrapper।

MCP server-এর একটা public registry আছে, এবং বেশিরভাগ এক-line install।

## Server configure করা

Server থাকে `claude_desktop_config.json` (desktop app) বা `.claude/mcp_servers.json` (CLI)-এ, surface অনুযায়ী। একটা minimal entry:

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

Agent restart করুন (বা reload, surface-এর উপর depend করে) — server-এর tool Claude-এর toolset-এ দেখা দেয়।

## Permission ও risk

MCP tool external system-এ call করে। একটা database tool arbitrary SQL run করতে পারে। একটা browser tool যেকোনো URL-এ যেতে পারে। প্রতিটা server-কে এমনভাবে treat করুন যেভাবে একটা CLI agent-কে দিচ্ছেন — minimum credential দিন, এবং harness-এর permission setting দিয়ে কোন tool auto-approve ও কোন prompt-এর জন্য — control করুন।

বিশেষ করে **write** capability নিয়ে সাবধান (ticket তৈরি, message send, mutation run)। বেশিরভাগ early experiment-এর জন্য, server-কে read-only mode-এ configure করুন এবং agent-এর behavior কিছুদিন watch করার পরই write enable করুন।

## নিজের লেখা

Team-এর একটা internal service যদি এখনো MCP server না পেয়ে থাকে — লিখুন। Protocol well-documented এবং Python ও TypeScript SDK আছে। বেশিরভাগ internal server 300 line-এর নিচে code, এবং প্রথমবার "যে customer..." বলে Claude সেটা করে দিলে — নিজেকে ধন্যবাদ দেবেন।

Advanced Patterns course-এ MCP server বানানো cover করি।
