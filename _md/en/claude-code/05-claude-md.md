# CLAUDE.md — Project Memory

`CLAUDE.md` is a file in your project root that Claude Code reads at the start of every session. It's where you put the rules and context that apply *every time* anyone (or you, future-you) opens this codebase with Claude. Done well, it's the single biggest quality lever you have.

## What goes in it

Five categories cover almost everything:

- **What the project is.** A two-line summary of the codebase: stack, purpose, where the entry points are.
- **Conventions.** Naming, formatting, language choices, file organization. Anything you'd correct a new hire on in their first week.
- **Workflow rules.** How to run tests, how to start the dev server, what to do before committing, whether to use a feature branch.
- **Gotchas.** Things that look weird but are intentional. The weird file at `legacy/auth_v1.go` that's still in use. The pre-commit hook that fails if you forget the changelog entry.
- **Hard rules.** Things never to do. *Never commit to `main` directly. Never edit `dist/`. Never run `rm -rf` on this path.*

What does *not* go in: anything ephemeral. Current task, in-flight feature, today's mood. CLAUDE.md is durable context. Save the temporary stuff for the conversation itself.

## A small, good example

```markdown
# Project Memory

## What this is
A Next.js + Postgres app. Code is in /app, /lib, /db. Tests in /tests.

## Run
- Dev server: `npm run dev`
- Tests: `npm test`
- Type check: `npm run typecheck` (must pass before commit)

## Conventions
- TypeScript everywhere. No `any`.
- React Server Components by default; only add `"use client"` when needed.
- Files: kebab-case. Components: PascalCase. Hooks: camelCase with `use` prefix.
- Tailwind utility classes only — no custom CSS files except /app/globals.css.

## Gotchas
- /lib/db/migrations runs on app boot. Adding migrations: append-only.
- Auth tokens go through /lib/auth/session.ts, never directly to cookies.

## Never
- Don't commit to main. Always a feature branch.
- Don't edit /app/api/.generated/*.ts (regenerated from OpenAPI spec).
- Don't add new dependencies without listing the alternative considered.
```

Notice what's not there: any task description, any "TODO", any commentary on the current feature. Pure durable context.

## How long should it be?

Long enough to cover the rules; short enough to fit in context comfortably. A page of markdown is a healthy size. Three pages starts to dilute. If yours is over 500 lines, you've started using it as a wiki — split out the wiki-ish parts into separate docs and link to them.

## How to write one

Two paths:

1. **From scratch.** Open a new `CLAUDE.md`, write what you'd tell a new hire on day one. Iterate as you catch Claude doing the wrong thing — every correction is a candidate rule for the file.
2. **Generate it.** Run `/init` (or the equivalent in your version) and Claude will scan the repo and propose a draft. Then edit it — the draft will overshoot.

Either way, the file is a living document. Update it when conventions change. Delete rules that no longer apply.

## Personal vs project

There are typically two layers:

- **Project CLAUDE.md** at the repo root. Shared with the team via git.
- **User CLAUDE.md** at `~/.claude/CLAUDE.md`. Personal rules that apply to all your projects. *"Default to short answers,"* *"never edit settings.json without asking,"* etc.

They both apply, and they compose. Project rules override user rules if they conflict.

## Why this is the highest leverage

Every other technique in Claude Code is per-task or per-session. `CLAUDE.md` is per-project, *forever*. Get this file right and every future session starts already-good. It's an hour of work for years of compounding return.
