# Workflow Patterns

Knowing the parts of Claude Code is one thing. Stringing them into a workflow that actually saves you time is another. Here are the patterns that hold up after months of daily use.

## The plan-execute-verify loop

The single most reliable pattern. Three explicit phases:

1. **Plan.** Before writing any code, have Claude draft a plan. What files will change, what tests will be added, what edge cases matter, what could go wrong.
2. **Execute.** Approve the plan, then let Claude work through it step by step.
3. **Verify.** Have Claude (or you, or a subagent) run the tests, type-check, lint, and read the diff against the plan.

The trap is skipping step 1 because the task "feels simple." On anything that touches more than two files, the plan is almost always worth the two minutes it takes to write.

## Small, scoped tasks

Big tasks don't fail in big ways — they fail in many small ways at once, which is harder to debug. Break work into chunks of 30–60 minutes of agent time. Commit after each. Now your history is a series of small reviewable diffs, not a sprawling change you can't unwind.

A good chunk has:

- One sentence that describes the goal.
- A clear "done" condition (tests pass, behavior X works, screenshot Y looks right).
- An estimated scope of files (Claude reading 5 files is fine; reading 50 is a different kind of task).

## Always be in a branch

Before any non-trivial change, `git checkout -b feature/<thing>`. This costs nothing and saves you the day Claude does something you don't want to keep. The undo button on a branch is just `git checkout main`. On main, it's an evening with `git reflog`.

## Read CLAUDE.md, write CLAUDE.md

Every time you correct Claude on a project-wide convention, ask yourself: was this correction CLAUDE.md material? If so, add it. Your future-self runs Claude on this same project; you're paying down debt for them every time.

## Use sub-agents for read-heavy work

If a task requires reading a lot of code to *summarize* something — "what does this module do?", "find every place we call this API," "audit our error handling" — that's a textbook subagent job. The main agent doesn't need to load all that code into context; the subagent does the reading and reports a summary. You save context and money.

## Run tests as a hook, not as a habit

If you find yourself typing "now run the tests" after every change, set up a PostToolUse hook that runs the test command after every Edit. Take the human out of the loop on the mechanical step. Now Claude sees test failures as part of its observation cycle, and you only intervene when there's something interesting.

## Treat the conversation as code

A long Claude session is a real artifact. The decisions made in it, the trade-offs considered, the plan that was followed — they tell a story. Two habits that help:

- When a session yields a non-trivial design decision, paste a summary into the PR description or a design doc.
- When you find a prompt that worked unusually well, save it as a slash command.

The compounding is real. Six months in, you'll have a pile of slash commands and skills that make new tasks 5× faster.

## When to bail out

Some tasks just aren't a good Claude Code fit:

- **Massive cross-cutting refactors** in a codebase with poor test coverage. The risk surface is too big.
- **Pure visual design work.** Use a design tool, not a text agent.
- **One-line changes you already know how to make.** It's faster to type it.

Recognizing when to drop into your editor directly is a skill worth practicing. The tool is good; it's not the answer to everything.
