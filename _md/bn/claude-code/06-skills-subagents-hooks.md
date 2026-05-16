# Skill, Subagent ও Hook

প্রথম দেখায় তিনটে concept similar মনে হয় কিন্তু আলাদা problem solve করে। Claude Code casually ব্যবহার করে থাকলে কোথায় কী fit করে — না জেনে এদের সাথে ধাক্কা খেতে পারেন। চলুন line স্পষ্ট আঁকি।

## Skill: চাহিদামতো focused expertise

**Skill** হলো একটা self-contained instruction set — একটা markdown file plus optional helper script — যা relevant task দেখলে Claude invoke করতে পারে। Skill auto-discovered। Explicitly call করতে হয় না; harness available skill load করে এবং Claude যেগুলো apply সেগুলো pick করে।

Example: একটা `pdf-extract` skill যেটা জানে কীভাবে একটা particular tool ব্যবহার করে PDF থেকে text বের করতে হয়। "এই PDF থেকে text extract করো" বললে — Claude notice করে skill আছে, এবং guess না করে সেটা ব্যবহার করে।

Skill থাকে `~/.claude/skills/<name>/`-তে বা একটা plugin-এ। প্রতিটার একটা `SKILL.md` যা describe করে — এটা কী করে এবং কখন ব্যবহার, plus যেকোনো code বা data যা skill-এর দরকার।

Skill ব্যবহার করুন যখন:

- একটা specific kind-এর task আছে যেটা specific instruction বা helper code থেকে benefit হয়।
- Task যথেষ্ট আসে যে প্রতিবার re-explain করা wasteful।
- আপনি এটা ভাবা ছাড়া অনেক session ও conversation-এ available চান।

## Subagent: কাজের একটা chunk হাতে দেওয়া

**Subagent** হলো একটা আলাদা Claude session — main one দ্বারা spawned — যা isolation-এ একটা specific subtask handle করে। নিজের context window-এ, নিজের (প্রায়ই narrow) tool set-এ run করে, এবং parent-কে একটা single result return করে।

Pattern:

```
Main agent: "30-file module refactor করতে হবে। প্রথমে current state audit করি।"

Subagent spawn → "src/legacy/-এর প্রতিটা file পড়ো, public API surface 
summarize করো, export-এর list এবং তাদের caller return করো।"

Subagent fresh context-এ run করে, 200-line report produce করে।

Main agent report পড়ে, next step decide করে, original context-এ 
30 file read না *পুড়িয়ে*।
```

Subagent ব্যবহার করুন যখন:

- Subtask well-scoped ও self-contained।
- Main context clean ও focused রাখতে চান।
- Subtask যথেষ্ট independent যে parallelize করা যায় (একসাথে কয়েকটা spawn করতে পারেন)।

Subagent magic problem-solver না। এটা একটা context-management technique।

## Hook: tool call-এর চারপাশে চলা code

**Hook** হলো একটা shell command যা Claude Code harness একটা specific মুহূর্তে run করে — tool call-এর আগে, session শেষ হওয়ার পর, file edit-এর পর, ইত্যাদি। Hook configure হয় `.claude/settings.json`-এ (বা global settings-এ)।

Common use:

- **প্রতিটা edit-এর পর lint।** একটা `PostToolUse` hook যা `Edit` tool call-এর পর `npm run lint --fix` run করে।
- **Bad command block।** একটা `PreToolUse` hook যা dangerous pattern match করা `Bash` call refuse করে।
- **Long task শেষ হলে notification।** একটা `Stop` hook যা Slack-এ ping করে বা bell বাজায়।

Hook model-এর problem না — আপনার, harness দ্বারা enforced। Model decide করে না যে এটা run করবে; harness করে, প্রতিবার।

## এদের আলাদা করা

| চাইলে... | ব্যবহার করুন... |
|---|---|
| Claude জানুক X কীভাবে করতে হয় যখন X আসে | একটা skill |
| Claude একটা কাজের chunk delegate করুক context clean রাখতে | একটা subagent |
| প্রতিটা tool call-এর চারপাশে কিছু automatically হোক | একটা hook |

একটা useful sanity check: skill বদলায় *Claude কী করতে পারে*। Subagent বদলায় *Claude কীভাবে context allocate করে*। Hook বদলায় *Claude-এর চারপাশে harness কী করে*। তিনটা আলাদা layer।

## কোথা থেকে শুরু

Skill দিয়ে শুরু করুন। সবচেয়ে user-visible ও সবচেয়ে সহজ payoff। কয়েকটা থাকলে hook আসে — সাধারণত একটা nagging behavior enforce করতে। Serious agentic কাজ করার সময় subagent useful হয়; ততক্ষণ ignore করতে পারেন।
