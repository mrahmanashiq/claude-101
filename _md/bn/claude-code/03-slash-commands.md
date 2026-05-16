# Slash Command

Slash command হলো প্রতিবার একই instruction re-type না করে Claude Code session-কে steer করার উপায়। `/` type করেন আর একটা command name, enter চাপেন, Claude একটা pre-defined routine run করে — আপনার নিজের বা Anthropic-এর ship করা।

Macro হিসেবে ভাবুন: একটা নাম + কিছু behavior। নিজের লিখতে শুরু করলে session অনেক ছোট ও consistent হয়ে যায়।

## Built-in command

দিন এক থেকেই কয়েকটা useful:

- `/help` — available command list।
- `/clear` — current conversation drop করে নতুন শুরু। Cheap ও useful।
- `/compact` — এ পর্যন্তর conversation summarize করে context free করে।
- `/cost` — কত token খরচ হলো, কত cost — দেখুন।
- `/model` — session কোন Claude model ব্যবহার করছে switch করুন।
- `/permissions` — prompt ছাড়া কোন tool allowed adjust করুন।

পুরো list version ও installed plugin-এর উপর depend করে।

## নিজের কেন চাইবেন

ধরুন প্রতি Monday সকালে আপনি এটা type করেন:

> Changelog পড়ো, গত সপ্তাহে কী ship হলো identify করো, এবং আমাদের team-এর tone-এ (concise, user impact-focused) এক paragraph internal summary লেখো। `docs/weekly/<date>.md`-এ save করো।

এটা একটা slash command হওয়ার অপেক্ষায়।

## তৈরি করা

Custom slash command markdown file হিসেবে থাকে। Convention:

- Project-level: `.claude/commands/<name>.md` — শুধু এই repo-তে available।
- User-level: `~/.claude/commands/<name>.md` — সবজায়গায় available।

File হলো একটা YAML front matter সহ markdown। Body prompt হয়; front matter metadata declare করে।

```markdown
---
name: weekly-summary
description: Generate the weekly engineering update from the changelog.
---

CHANGELOG.md পড়ো এবং গত 7 দিনের entry identify করো।

User-visible impact-এ focused একটা single paragraph (4-6 বাক্য) summary লেখো,
যেটা docs/weekly/-এর existing entry-এর tone match করে।

Result docs/weekly/<আজকের তারিখ>.md-তে save করো
```

এখন `/weekly-summary` এক keystroke-এ পুরো routine করে।

## Argument

বেশিরভাগ command argument নেয়। Convention হলো body-তে `$ARGUMENTS` বা `$1`, `$2`, ইত্যাদি দিয়ে reference করা। তাই `/review-pr 4738` `$ARGUMENTS`-কে `4738`-এ expand করবে।

```markdown
---
name: review-pr
description: Review the specified PR by number.
---

PR #$ARGUMENTS check out করো এবং correctness, style ও test-এর জন্য
review করো। তোমার review একটা markdown summary হিসেবে output করো।
```

## Slash command বনাম CLAUDE.md কখন

Standing rule ("commit-এর আগে সবসময় prettier run করো", "এই codebase tab ব্যবহার করে spaces না") — `CLAUDE.md`-এ যায় — প্রতিটা interaction-এ apply হয়। Reusable *routine* ("এই specific workflow করো") — slash command-এ যায়। Line: প্রতিটা conversation-এ বলতেন — CLAUDE.md rule; occasionally discrete task হিসেবে বলতেন — slash command।

## একটা library তৈরি

আপনার slash command folder একটা real personal artifact। সেভাবেই treat করুন — version করুন, useful-গুলো teammate-দের সাথে share করুন, যেগুলো কাজ করেনি prune করুন। কয়েক মাসে — small, reliable tool-এর একটা kit হবে যা compose করতে পারেন। সেখানেই productivity gain compound করতে শুরু করে।
