# CLAUDE.md — Project Memory

`CLAUDE.md` হলো project root-এ একটা file যা Claude Code প্রতিটা session-এর শুরুতে পড়ে। এখানে সেই rule ও context রাখেন যা *প্রতিবার* এই codebase-এ Claude দিয়ে যে কেউ কাজ করতে বসলে apply হয়। ভালোভাবে করলে এটা আপনার সবচেয়ে বড় single quality lever।

## কী রাখবেন

পাঁচটা category প্রায় সব কিছু cover করে:

- **Project কী।** Codebase-এর দুই-line summary: stack, purpose, entry point কোথায়।
- **Convention।** Naming, formatting, language choice, file organization। নতুন hire-কে প্রথম সপ্তাহে যেগুলো correct করতেন।
- **Workflow rule।** Test কীভাবে run, dev server কীভাবে start, commit-এর আগে কী, feature branch ব্যবহার করতে হবে কিনা।
- **Gotcha।** যেসব weird দেখায় কিন্তু intentional। `legacy/auth_v1.go`-এর সেই weird file যা এখনো in use। সেই pre-commit hook যা changelog entry না দিলে fail করে।
- **Hard rule।** কখনো না করার জিনিস। *কখনো `main`-এ directly commit না। কখনো `dist/` edit না। কখনো এই path-এ `rm -rf` না।*

কী যাবে *না*: যেকোনো ephemeral। Current task, in-flight feature, আজকের মেজাজ। CLAUDE.md durable context। Temporary জিনিস conversation-এর জন্য রেখে দিন।

## একটা small, good example

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

লক্ষ্য করুন কী নেই: কোনো task description, কোনো "TODO", current feature-এর উপর কোনো commentary। Pure durable context।

## কত লম্বা হবে?

Rule cover করার মতো লম্বা; comfortably context-এ fit করার মতো ছোট। এক পাতা markdown — healthy size। তিন পাতা dilute করতে শুরু করে। 500 line ছাড়ালে — এটাকে wiki হিসেবে ব্যবহার করতে শুরু করেছেন। Wiki-ish অংশ আলাদা doc-এ ভেঙে link করুন।

## লেখা যেভাবে

দুটো path:

1. **Scratch থেকে।** একটা নতুন `CLAUDE.md` open করুন, day one-এ নতুন hire-কে যা বলতেন তাই লিখুন। Claude ভুল করলে correct করতে করতে iterate করুন — প্রতিটা correction file-এর জন্য একটা candidate rule।
2. **Generate করিয়ে।** `/init` (বা আপনার version-এর equivalent) run করুন এবং Claude repo scan করে একটা draft propose করবে। তারপর edit করুন — draft overshoot করবে।

দুটোই — file একটা living document। Convention বদলালে update করুন। যে rule আর apply হয় না delete করুন।

## Personal বনাম project

সাধারণত দুটো layer:

- **Project CLAUDE.md** — repo root-এ। Git-এর মাধ্যমে team-এর সাথে share।
- **User CLAUDE.md** — `~/.claude/CLAUDE.md`-এ। Personal rule যা আপনার সব project-এ apply হয়। *"Default-এ short answer,"* *"settings.json edit করার আগে জিজ্ঞেস করো,"* ইত্যাদি।

দুটোই apply হয়, এবং compose হয়। Conflict হলে project rule user rule-এর উপরে।

## কেন এটা highest leverage

Claude Code-এর প্রতিটা অন্য technique per-task বা per-session। `CLAUDE.md` per-project, *চিরকাল*। এই file ঠিকঠাক করুন — প্রতিটা future session ইতিমধ্যে already-good থেকে শুরু হবে। এক ঘণ্টার কাজ, বছরের পর বছর compounding return।
