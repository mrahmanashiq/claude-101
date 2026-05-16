# Your First Session

Let's run Claude Code end-to-end on a real task. Nothing exotic — a small refactor, the kind you'd do twice a week. The point is to feel the loop.

## Install and authenticate

Install the CLI (the exact command depends on your platform — usually `npm install -g @anthropic-ai/claude-code` or an installer script). Then run `claude` in any directory. The first time, it walks you through signing in. After that, every project folder is a candidate workspace.

## Pick a project

`cd` into a real project of yours. Don't pick the throwaway folder you keep on the desktop — pick something with actual code, tests, and a `README`. Claude is more useful when there's context to work from.

## Start the agent

```
claude
```

That's it. You're now in an interactive session. The prompt opens, the cursor blinks, and you can type a task in plain English.

## Ask for something concrete

The biggest mistake people make on day one is asking for something abstract. *"Improve the codebase"* gets you a meandering response. *"Add a `--dry-run` flag to `cli/deploy.py` that prints the planned changes without executing them, and update the help text"* gets you a clean diff in two minutes.

Be specific. Name files. Name behaviors. Describe the result.

## Read the diffs

Claude will propose edits in a previewable form. Don't autopilot through them. Skim each one — not for typos (it doesn't make typos), but for:

- Did it understand the request, or did it solve a slightly different problem?
- Did it touch files it shouldn't have?
- Did it leave the codebase consistent with its existing style?

If something looks off, reject the diff or ask for a revision. The loop is fast — clarifications cost seconds.

## Let it run commands

When Claude wants to run a shell command (`npm test`, `pytest`, `go build`), it asks first. Approve the safe ones. After a few of these you can teach it which kinds of commands are pre-approved (in `.claude/settings.json` or via the permissions UI).

## End the session intentionally

When the task is done, type `exit` or close the terminal. Your changes are real edits to real files — they're on disk, ready to commit. Claude doesn't "save" anywhere magical. The diffs *are* the output.

## A first-session checklist

If you've done all of this, you've done a real session:

- [ ] Started the agent in a real project directory.
- [ ] Asked for one concrete, scoped task.
- [ ] Read each proposed diff before approving.
- [ ] Let it run at least one shell command.
- [ ] Reviewed `git diff` after exiting and committed the parts you kept.

You now know more about Claude Code than 80% of people who've read about it.
