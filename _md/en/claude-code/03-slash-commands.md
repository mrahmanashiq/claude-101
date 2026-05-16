# Slash Commands

Slash commands are how you steer a Claude Code session without retyping the same instructions every time. You type `/` and a command name, hit enter, and Claude runs a pre-defined routine — your own or one Anthropic ships.

Think of them as macros: a name plus a chunk of behavior. Once you start writing your own, your sessions get a lot shorter and a lot more consistent.

## Built-in commands

A few are useful from day one:

- `/help` — list available commands.
- `/clear` — drop the current conversation and start fresh. Cheap and useful.
- `/compact` — summarize the conversation so far to free up context.
- `/cost` — see how many tokens you've burned and what it cost.
- `/model` — switch which Claude model the session uses.
- `/permissions` — adjust what tools are allowed without prompting.

The full list depends on your version and any plugins you've installed.

## Why you'll want custom ones

Suppose you find yourself typing this every Monday morning:

> Read the changelog, identify what shipped last week, and write a one-paragraph internal summary in our team's tone (concise, focused on user impact). Save it to `docs/weekly/<date>.md`.

That's a slash command waiting to happen.

## Creating one

Custom slash commands live as markdown files. The convention is:

- Project-level: `.claude/commands/<name>.md` — only available in this repo.
- User-level: `~/.claude/commands/<name>.md` — available everywhere.

The file is just markdown with a YAML front matter and a body. The body becomes the prompt; the front matter declares metadata.

```markdown
---
name: weekly-summary
description: Generate the weekly engineering update from the changelog.
---

Read CHANGELOG.md and identify entries from the last 7 days.

Write a single paragraph (4-6 sentences) summarizing what shipped,
focused on user-visible impact. Match the tone of the existing
docs/weekly/ entries.

Save the result to docs/weekly/<today's date>.md
```

Now `/weekly-summary` does the whole routine in one keystroke.

## Arguments

Most commands take arguments. Convention is to reference them with `$ARGUMENTS` or `$1`, `$2`, etc. in the body. So a `/review-pr 4738` would expand `$ARGUMENTS` to `4738`.

```markdown
---
name: review-pr
description: Review the specified PR by number.
---

Check out PR #$ARGUMENTS and review it for correctness, style,
and tests. Output your review as a markdown summary.
```

## When to use a slash command vs CLAUDE.md

Standing rules ("always run prettier before committing", "this codebase uses tabs not spaces") go in `CLAUDE.md` — they apply to every interaction. Reusable *routines* ("do this specific workflow") go in slash commands. The line: if you'd say it in every conversation, it's a CLAUDE.md rule; if you'd say it occasionally as a discrete task, it's a slash command.

## Building a library

Your slash command folder is a real personal artifact. Treat it like one — version it, share useful ones with teammates, prune the ones that didn't pan out. After a few months you'll have a kit of small, reliable tools you can compose. That's where the productivity gains compound.
