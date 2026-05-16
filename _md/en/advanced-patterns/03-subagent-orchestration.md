# Subagent Orchestration

A **subagent** is a Claude session spawned by another Claude session to handle a specific chunk of work. The parent gets back a summary of what happened — not the full transcript. This is the most underrated tool in the kit, because it solves a problem that nothing else does well: **context management at scale**.

## The problem subagents solve

Your main agent has to do five things to finish a task. Each thing requires reading several files. If the main agent does all five sequentially, by the time it's done it's loaded fifty files into context. Now everything after that is slow and expensive, and quality drops because the prompt is bloated.

Solution: delegate each "thing" to a subagent. The subagent reads its own files, does its own work, returns a 200-word summary. The main agent absorbs five summaries — clean, focused, cheap.

## When to use one

A task is a good subagent candidate when it's:

- **Self-contained.** A subagent has its own context — it can't easily reference what the parent knows mid-flight.
- **Read-heavy.** Audits, summaries, "find all X" tasks. Anything where most of the work is consuming information.
- **Independent.** Doesn't depend on what other subagents are doing right now.
- **Parallelizable.** Bonus — you can spawn several at once.

Bad subagent candidates: small one-off tasks (overhead isn't worth it), tightly coupled subtasks (you spend more time passing state than working), anything where the parent really needs the full output not a summary.

## Spawning one

In Claude Code, the Task / Agent tool spawns a subagent. In your own API code, it's just another `messages.create()` call with its own system prompt, its own tools, and its own message history.

A skeleton:

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
    return resp.content[-1].text   # the final text block
```

The system prompt does a lot of work here. You want a subagent that *finishes* and returns a clean answer — not one that asks for clarification or rambles.

## Briefing matters

The single biggest determinant of subagent quality is the brief. A subagent has none of the parent's context — it doesn't know your project, your goals, your codebase. Write the brief as if for a stranger who walked in and has to deliver in 20 minutes:

- **What** is the task. Be concrete and bounded.
- **Why** it matters (one sentence — gives the subagent a sense of what good looks like).
- **What you've already ruled out** (saves it from re-doing work).
- **Where to look** (paths, search terms, URLs).
- **What format** the answer should be in.
- **What's out of scope.**

A good brief is a paragraph or two. Half a sentence and you'll get vague results.

## Parallel subagents

When you have several independent sub-tasks, run them in parallel:

```python
import asyncio

async def fan_out(briefs):
    return await asyncio.gather(*(
        spawn_subagent_async(b["task"], b["tools"]) for b in briefs
    ))
```

This is where the win compounds. Five subagents in parallel finish in roughly one subagent's time. Especially nice for "explore N hypotheses, report which one looks best."

## Don't over-decompose

The temptation is to break every task into ten subagents. Resist. Subagents have:

- Overhead — spawning, briefing, summarizing all cost tokens.
- Risk — each adds a way to lose the thread.

A useful rule: spawn a subagent when the cost of the task (in context, tokens, or attention) is *more* than the cost of the brief and summary. If the task is short, do it inline.

## A common pattern: explore + execute

A surprisingly powerful template:

1. **Main agent reads the problem and identifies the work.**
2. **Main agent spawns one or more "explore" subagents** to investigate the codebase / docs / data. Each returns a short report.
3. **Main agent synthesizes the reports and writes a plan.**
4. **Main agent executes the plan** (or spawns execution subagents per chunk).

You keep the main agent's context focused on the high-level plan and synthesis, while the deep reading happens in throwaway children. This is, more or less, how a senior engineer delegates to a team.

## Watch the outputs

Subagent summaries are great until they're not. A subagent that confidently summarizes "I checked everything, looks fine" is a subagent you should spot-check. For high-stakes work, sample subagent traces (the harness usually saves them) and read the actual interactions, not just the summary. Trust, but verify.
