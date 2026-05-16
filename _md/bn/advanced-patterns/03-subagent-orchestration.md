# Subagent Orchestration

একটা **subagent** হলো অন্য Claude session দ্বারা spawn করা একটা Claude session — কাজের একটা specific chunk handle করতে। Parent ফেরত পায় কী হয়েছে তার একটা summary — পুরো transcript না। এটা kit-এর সবচেয়ে underrated tool, কারণ এটা এমন একটা problem solve করে যা অন্য কিছু ভালোভাবে করে না: **scale-এ context management**।

## Subagent যে problem solve করে

আপনার main agent-কে একটা task finish করতে পাঁচটা কাজ করতে হবে। প্রতিটার জন্য কয়েকটা file পড়তে হবে। Main agent পাঁচটা sequentially করলে — শেষে পঞ্চাশটা file context-এ load হয়ে গেছে। এখন তারপরের সব slow ও expensive, এবং prompt bloated বলে quality drop।

Solution: প্রতিটা "thing" subagent-কে delegate করুন। Subagent নিজের file পড়ে, নিজের কাজ করে, একটা 200-word summary return করে। Main agent পাঁচটা summary absorb করে — clean, focused, cheap।

## কখন ব্যবহার করবেন

একটা task ভালো subagent candidate যখন এটা:

- **Self-contained।** Subagent-এর নিজস্ব context — mid-flight-এ parent যা জানে সহজে reference করতে পারে না।
- **Read-heavy।** Audit, summary, "সব X খুঁজে দাও" task। Where most কাজ information consume করা।
- **Independent।** এই মুহূর্তে অন্য subagent কী করছে তার উপর depend করে না।
- **Parallelizable।** Bonus — একসাথে কয়েকটা spawn করতে পারেন।

খারাপ subagent candidate: small one-off task (overhead worth না), tightly coupled subtask (state pass-এ কাজের চেয়ে বেশি সময়), যেখানে parent-কে summary না full output সত্যিই দরকার।

## একটা spawn করা

Claude Code-এ Task / Agent tool subagent spawn করে। আপনার নিজের API code-এ এটা শুধু আরেকটা `messages.create()` call — নিজস্ব system prompt, নিজস্ব tool, নিজস্ব message history সহ।

একটা skeleton:

```python
def spawn_subagent(task_brief, allowed_tools, model="claude-sonnet-4-6"):
    system = f"""
You are a focused subagent. Your job is to complete the task below.
Return ONLY your final result — no chatter, no commentary on your process.

Task:
{task_brief}
"""
    resp = run_agent(
        client, system, allowed_tools,
        user_task="Complete the task and return your result.",
        max_iters=15,
    )
    return resp.content[-1].text   # final text block
```

System prompt এখানে অনেক কাজ করে। আপনি এমন একটা subagent চান যা *শেষ* করে এবং একটা clean answer return করে — clarification চায় না বা ramble করে না।

## Briefing matters

Subagent quality-র single biggest determinant brief। একটা subagent-এর parent-এর কোনো context নেই — এটা আপনার project, goal, codebase জানে না। Brief এমনভাবে লিখুন যেন একজন stranger walk in করে 20 মিনিটে deliver করতে হবে:

- **কী** task। Concrete ও bounded।
- **কেন** matter করে (এক বাক্য — subagent-কে কী good সেটার একটা sense দেয়)।
- আপনি **কী rule out করেছেন** (re-work বাঁচায়)।
- **কোথায় দেখবে** (path, search term, URL)।
- **কী format-এ** answer।
- **কী out of scope।**

Good brief একটা paragraph বা দুটো। Half a sentence — vague result পাবেন।

## Parallel subagent

কয়েকটা independent sub-task থাকলে — parallel-এ run করুন:

```python
import asyncio

async def fan_out(briefs):
    return await asyncio.gather(*(
        spawn_subagent_async(b["task"], b["tools"]) for b in briefs
    ))
```

Win এখানে compound করে। পাঁচটা subagent parallel-এ মোটামুটি এক subagent-এর সময়ে শেষ। Especially nice "N hypothesis explore, কোনটা best দেখাচ্ছে report করো"-এর জন্য।

## Over-decompose করবেন না

প্রতিটা task দশটা subagent-এ ভাঙার লোভ হয়। Resist করুন। Subagent-এর আছে:

- Overhead — spawn, brief, summarize সব token খরচ।
- Risk — প্রতিটা thread হারানোর একটা path add করে।

Useful rule: spawn করুন যখন task-এর cost (context, token বা attention-এ) brief ও summary-এর cost-এর *বেশি*। Task short হলে — inline করুন।

## একটা common pattern: explore + execute

একটা surprisingly powerful template:

1. **Main agent problem পড়ে কাজ identify করে।**
2. **Main agent এক বা একাধিক "explore" subagent spawn করে** — codebase / docs / data investigate করতে। প্রতিটা একটা short report return করে।
3. **Main agent report synthesize করে এবং একটা plan লেখে।**
4. **Main agent plan execute করে** (বা per chunk execution subagent spawn করে)।

Main agent-এর context high-level plan ও synthesis-এ focused রাখেন, deep reading throwaway children-এ। এটা মোটামুটি — একজন senior engineer team-কে যেভাবে delegate করেন।

## Output watch করুন

Subagent summary great — যতক্ষণ না। যে subagent confidently summarize করে "সব check করেছি, looks fine" — সেই subagent-কে spot-check করবেন। High-stakes কাজের জন্য, subagent trace sample করুন (harness সাধারণত save করে) এবং actual interaction পড়ুন, summary না। Trust, but verify।
