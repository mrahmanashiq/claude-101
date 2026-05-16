# Tools Claude Can Use

A "tool," in agent land, is a function the model is allowed to call. Claude Code ships with a built-in toolkit — read a file, edit a file, run a shell command, search, fetch a URL, and so on — and that toolkit is what makes it agentic instead of just chatty.

You don't usually invoke tools yourself. You describe a task in English; Claude decides which tools to call to accomplish it. But understanding the toolset is worth ten minutes of your time, because it tells you what the agent can and can't do, and how to phrase requests so it picks the right one.

## The core file tools

- **Read** — open a file and load it into the conversation. Used constantly.
- **Write** — create a new file with given content. Asked for explicitly when starting from scratch.
- **Edit** — replace a specific string in an existing file with new content. The workhorse for changes; safer than Write because it requires you to specify the surrounding context.
- **Glob** — find files by name pattern (e.g. `src/**/*.ts`).
- **Grep** — search file contents for a regex.

Most of your sessions are: Glob/Grep to locate, Read to confirm, Edit to change.

## The shell tool

- **Bash** (or **PowerShell** on Windows) — run a command in the project directory.

Shell access is what lets Claude actually verify its work — run tests, type-check, lint, start a dev server. By default risky commands prompt for approval. You can pre-approve safe ones.

## The web tools

- **WebFetch** — load a URL and read its contents (HTML stripped to text).
- **WebSearch** — search the web for relevant pages.

Useful when Claude needs documentation it doesn't have in its training data — a library version that shipped last week, an API spec on a vendor page.

## The agent tool

- **Task** (or **Agent**) — spawn a sub-agent to handle a chunk of work in isolation.

This is a force multiplier. Instead of doing six things in one conversation and filling up context, Claude can hand a discrete subtask to a sub-agent, let it run, and absorb just the result. Covered in depth in the Advanced Patterns course.

## Tools from MCP servers

Beyond the built-in set, you can plug in **MCP servers** — external programs that expose their own tools. There are servers for databases, browsers, JIRA, Notion, GitHub, design tools, you name it. Once a server is configured, its tools appear in Claude's toolset and it can use them in the same loop.

We cover MCP in its own chapter; for now, just know the toolset is extensible.

## How Claude picks a tool

The model receives a list of available tools and their schemas as part of the prompt. When it decides a tool is needed, it emits a structured tool-call (which tool, with which arguments). The harness runs the call and returns the result, which the model then reads on the next turn.

The skill of getting Claude to pick the right tool is mostly the same as the skill of clear prompting:

- **Name the file.** "Edit `src/auth.py` to..." is unambiguous. "Edit the auth thing" makes Claude search first, sometimes for the wrong thing.
- **State the verb.** "Read", "list", "run", "check" — verbs map cleanly onto tools.
- **Limit scope.** "In the `tests/` folder, find any test using the deprecated mock" tells Claude exactly where to look and which tool to use.

The more concrete your request, the fewer wrong tool calls Claude makes — and the faster you get to a good answer.
