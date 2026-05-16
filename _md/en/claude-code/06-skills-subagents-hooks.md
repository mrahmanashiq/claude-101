# Skills, Subagents, and Hooks

Three concepts that look similar at first glance but solve different problems. If you've used Claude Code casually, you may have bumped into them without knowing where each fits. Let's draw the lines clearly.

## Skills: focused expertise on demand

A **skill** is a self-contained instruction set — a markdown file plus optional helper scripts — that Claude can invoke when it sees a relevant task. Skills are auto-discovered. You don't have to explicitly call them; the harness loads available skills and Claude picks the ones that apply.

Example: a `pdf-extract` skill that knows how to use a particular tool to pull text out of PDFs. When you say "extract the text from this PDF," Claude notices the skill exists and uses it instead of guessing.

Skills live in `~/.claude/skills/<name>/` or in a plugin. Each has a `SKILL.md` describing what it does and when to use it, plus any code or data the skill needs.

Use a skill when:

- You have a specific kind of task that benefits from specific instructions or helper code.
- The task comes up often enough that re-explaining it each time is wasteful.
- You want it available across many sessions and conversations without thinking about it.

## Subagents: handing off a chunk of work

A **subagent** is a separate Claude session, spawned by the main one, to handle a specific subtask in isolation. It runs in its own context window, with its own (often narrower) tool set, and reports back a single result to the parent.

The pattern:

```
Main agent: "I need to refactor this 30-file module. First let me
audit the current state."

Spawns subagent → "Read every file in src/legacy/, summarize the
public API surface, return a list of exports and their callers."

Subagent runs in fresh context, produces a 200-line report.

Main agent reads the report, decides next steps, *without* burning
the original context on 30 file reads.
```

Use a subagent when:

- The subtask is well-scoped and self-contained.
- You want to keep the main context clean and focused.
- The subtask is independent enough to be parallelized (you can spawn several at once).

Subagents are not magic problem-solvers. They're a context-management technique.

## Hooks: code that runs around tool calls

A **hook** is a shell command the Claude Code harness runs at a specific moment — before a tool call, after a session ends, after a file edit, and so on. Hooks are configured in `.claude/settings.json` (or your global settings).

Common uses:

- **Lint after every edit.** A `PostToolUse` hook that runs `npm run lint --fix` after `Edit` tool calls.
- **Block bad commands.** A `PreToolUse` hook that refuses `Bash` calls matching a dangerous pattern.
- **Send a notification when a long task finishes.** A `Stop` hook that pings Slack or rings a bell.

Hooks are not the model's problem — they're yours, enforced by the harness. The model doesn't choose to run them; the harness does, every time.

## Telling them apart

| If you want... | Use... |
|---|---|
| Claude to know how to do X when X comes up | A skill |
| Claude to delegate a chunk of work to keep context clean | A subagent |
| Something to happen automatically around every tool call | A hook |

A useful sanity check: skills change *what Claude can do*. Subagents change *how Claude allocates context*. Hooks change *what the harness does around Claude*. Three different layers.

## Where to start

Start with skills. They're the most user-visible and the easiest payoff. Once you've got a few of those, hooks come next — usually for a single nagging behavior you want enforced. Subagents become useful when you're doing serious agentic work; until then you can ignore them.
