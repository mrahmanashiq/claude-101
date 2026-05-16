# What is Claude Code?

Claude Code is Anthropic's coding agent. You run it in your terminal (or inside your IDE), and it operates on your codebase the way a careful collaborator would — reading files, editing them, running commands, checking results, and continuing until the task is done.

If you've used a chat-based coding assistant, the mental model is different. A chat assistant gives you suggestions; you copy-paste and run things yourself. Claude Code closes that loop. It can read the files, make the change, run the tests, and report back.

## Why it matters

The big shift is from *snippet-by-snippet help* to *task-by-task execution*. You don't ask "how would I refactor this function?" — you ask "refactor this function to take a context manager," and Claude does it. Then you review the diff.

This changes how you spend your time. Less typing, more reviewing. Less mechanical work, more architectural decisions. The unit of human attention moves up a level.

## Where it lives

- **Terminal:** the CLI. Open a project folder, run `claude`, and you're talking to it.
- **IDE:** VS Code and JetBrains have extensions that embed it in the editor.
- **Desktop and web apps:** there's a desktop UI and a hosted version at claude.ai/code.

All of them are the same agent underneath; only the surface differs.

## What it can actually do

Out of the box, Claude Code can:

- Read any file in the project directory.
- Edit files (preview the diff first, then apply).
- Run shell commands (with your permission).
- Search the codebase (grep, glob).
- Open URLs and fetch documentation.
- Use tools from MCP servers you've configured.
- Spawn sub-agents to parallelize work.

You're in control of what it's allowed to do. Risky commands prompt for confirmation; you can configure rules about what runs automatically and what doesn't.

## What it isn't

Claude Code is not a magic "build my app" button. It's a powerful assistant that still benefits — a lot — from a clear specification, a clean codebase, and a human in the loop. If you give it a vague task, you'll get a vague result. If you give it a precise task, with the right context, you'll get something close to what you wanted, fast.

It also isn't the model itself. Claude Code is the *harness*: the layer that gives Claude (the model) tools, file access, memory, and the ability to act in a loop. Underneath, it's calling the same API anyone else can call. The harness is what makes it agentic.

## What you'll learn next

In the rest of this course we'll cover: starting and managing a session, the slash commands that steer it, the tools available, how `CLAUDE.md` files give Claude project context, and the higher-level concepts — skills, subagents, hooks, and MCP servers — that let you tailor Claude Code to your workflow.

By the end you'll have the vocabulary and instincts to actually ship with it.
