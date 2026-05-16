# What is Claude?

Claude is a family of large language models built by Anthropic. You talk to it in plain language; it talks back in plain language. Under the hood it's a neural network trained to predict text, fine-tuned to follow instructions, refuse harmful requests, and use tools when given the option.

You can reach Claude in a few different ways, and which one matters depends on what you're building.

## The three surfaces

There are three main ways people use Claude today:

- **Claude.ai** — the chat interface at claude.ai. Friendly, browser-based, no setup. Good for one-off questions, writing, research, and exploring what the model can do.
- **Claude Code** — Anthropic's agentic coding tool. Runs in your terminal or IDE, can read and edit your files, run shell commands, and stay focused on a multi-step task. This is what you want when you're shipping software.
- **The Claude API** — the raw HTTP endpoint plus official SDKs (Python, TypeScript, others). This is the foundation. Everything else is built on top of it. Use this when you're building your own product.

A lot of confusion comes from mixing these up. *"Claude added a feature"* can mean any of three different things — a new model version, a new Claude Code capability, or a new API parameter. As you learn, train yourself to ask: *which surface?*

## What a language model actually does

A model like Claude takes a sequence of tokens (roughly: word pieces) as input and produces tokens as output, one at a time. That's it. Everything else — chat, tool calling, "thinking," memory, agents — is built on top of that core loop.

This matters because the model has no internal state between calls. It does not remember your last conversation unless you send the conversation back to it. It does not have access to your files unless you (or the harness around it) put their contents in the prompt. Every capability you see is a careful arrangement of inputs and outputs around that core token-in / token-out loop.

!!! tip
    The fastest way to debug Claude's behavior is to ask: *what exactly did the model see as input?* Most surprises come from a mismatch between what you think it saw and what was actually in the context.

## Where this guide will take you

The rest of this course covers the model itself — sizes, prompting, context, reasoning. Then we'll go surface by surface: Claude Code (terminal agent), the Claude API (your own apps), and advanced patterns once you're past the basics.

There is no required order, but if this is your first exposure, read the courses in order. Each one assumes you understand the previous.
