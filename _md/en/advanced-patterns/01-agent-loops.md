# Agent Loops

An "agent" in LLM terms is a loop: the model gets a task, decides what to do next, takes an action, observes the result, and decides again. Repeat until done. That's it — there's no other secret to agents. Once you understand the loop, the rest is engineering.

We saw the bare bones in the Tool Use chapter. This is the deeper version: how to design the loop so it's robust, observable, and bounded.

## The canonical loop

```python
def run_agent(client, system, tools, user_task, max_iters=20):
    history = [{"role": "user", "content": user_task}]
    for step in range(max_iters):
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system,
            tools=tools,
            messages=history,
        )
        history.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return resp, history
        tool_results = run_tool_calls(resp.content)
        history.append({"role": "user", "content": tool_results})
    raise RuntimeError("Hit iteration cap.")
```

Five honest lines of state machine. Everything else — memory, planning, recovery, evals — is layered on.

## Things that go wrong

A naive loop fails in predictable ways:

- **Infinite loops.** The model keeps calling a tool, getting an error, calling the tool again. Always bound `max_iters`.
- **Context bloat.** Every turn grows the history. Eventually the prompt is too big for the model to focus.
- **Cascading errors.** One bad tool result poisons the rest of the run — the model "knows" something wrong and acts on it.
- **Tool flailing.** When the model isn't sure what to do, it calls tools at random. Output gets worse, not better.

Each of these is fixable. None are accidents — they're design problems.

## Bounding iterations and tokens

Always cap both:

- **Iterations** — hard stop after N tool calls. Choose N based on the task. Simple tasks: 5. Complex tasks: 30. If you regularly hit the cap, the task is too big for one agent; break it up.
- **Total tokens** — track cumulative input/output. If you cross a budget, abort. Cheap insurance against a runaway loop on production traffic.

## Managing context

When history grows long, the cheapest fix is **summarization**. Periodically replace the older portion of `history` with a compact summary block. Keep the most recent turns verbatim because they have the highest signal.

A common scheme: every K turns, ask the model to summarize the conversation so far in a few hundred words. Replace the original turns with the summary. Keep the last 3–5 turns verbatim.

The next-level fix is **selective recall**. Index the conversation history (or external data) into a vector store; retrieve only the relevant pieces when needed. This is more code but scales further.

## Recovery

When a tool errors, don't just hand the error back as-is and hope the model figures it out. Wrap your tool calls:

```python
def safe_run(name, fn, args):
    try:
        return {"status": "ok", "result": fn(**args)}
    except ValidationError as e:
        return {"status": "input_error", "hint": str(e)}
    except ExternalServiceError as e:
        return {"status": "service_error", "retry_safe": True, "detail": str(e)}
    except Exception as e:
        return {"status": "internal_error", "detail": repr(e)}
```

Structured error messages give the model something to reason over instead of an opaque stack trace. The model will often try a different approach automatically — but only if the error is legible.

## Observability

Log every tool call, its arguments, its result, and the model's response. In production you need this for two reasons:

- **Debugging.** When a user complains, the trace is your only source of truth.
- **Improvement.** Patterns of where the agent fails or wastes calls are the highest-signal input to your next prompt revision.

A good log format includes: a session ID, a per-turn step number, the tool name, the arguments hash, the result size, and any model-level metadata like stop_reason. Don't log the *full* contents of every prompt at high volume — log structured summaries, sample the full traces.

## Knowing when to stop

The loop ends when:

- The model returns text without a tool_use block (it thinks it's done).
- The iteration cap fires.
- The token budget cap fires.
- A hard error in your harness.

For long-running agents, also consider an explicit "are we done?" check periodically. Ask the model: "Have you completed the task as stated? If yes, summarize what you did. If no, what's left?" Sometimes that meta-question saves hours of useless iteration.

## The honest secret

Most "agent failures" aren't model failures — they're loop failures. Bad bounding, bad context management, bad error surfaces, no observability. Get the harness right and the model goes a long way on its own.
