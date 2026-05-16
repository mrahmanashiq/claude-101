# Agent Loop

LLM-এর ভাষায় একটা "agent" হলো একটা loop: model একটা task পায়, পরে কী করবে decide করে, একটা action নেয়, result observe করে, এবং আবার decide করে। Repeat — শেষ না হওয়া পর্যন্ত। ব্যস — agent-এর অন্য কোনো গোপন secret নেই। Loop বুঝলে — বাকি engineering।

Tool Use chapter-এ bare bones দেখেছি। এটা deeper version: loop কীভাবে design করবেন যাতে robust, observable ও bounded।

## Canonical loop

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

State machine-এর পাঁচটা honest line। বাকি সব — memory, planning, recovery, eval — এর উপর layer।

## যেসব জিনিস ভুল হয়

একটা naive loop predictable-ভাবে fail করে:

- **Infinite loop।** Model একটা tool call করতেই থাকে, error পায়, আবার call করে। সবসময় `max_iters` bound করুন।
- **Context bloat।** প্রতিটা turn history বাড়ায়। Eventually prompt এত বড় যে model focus করতে পারে না।
- **Cascading error।** একটা bad tool result বাকি run poison করে — model wrong কিছু "জানে" এবং তার উপর act করে।
- **Tool flailing।** Model নিশ্চিত না হলে — random-ভাবে tool call করে। Output worse হয়, better না।

প্রতিটা fixable। কোনোটাই accident না — design problem।

## Iteration ও token bound করা

দুটোই সবসময় cap করুন:

- **Iteration** — N tool call-এর পর hard stop। Task অনুযায়ী N choose করুন। Simple task: 5। Complex task: 30। Regularly cap hit করলে — task একটা agent-এর জন্য too big; break করুন।
- **Total token** — cumulative input/output track করুন। Budget cross করলে abort করুন। Production traffic-এ runaway loop-এর বিরুদ্ধে cheap insurance।

## Context manage

History long হলে cheapest fix — **summarization**। Periodically `history`-এর older portion-কে একটা compact summary block দিয়ে replace করুন। Most recent turn verbatim রাখুন — highest signal।

একটা common scheme: প্রতি K turn-এ — model-কে এ পর্যন্তর conversation কয়েকশ word-এ summarize করতে বলুন। Original turn-গুলোকে summary দিয়ে replace করুন। শেষ 3–5 turn verbatim রাখুন।

Next-level fix **selective recall**। Conversation history (বা external data) একটা vector store-এ index করুন; দরকার হলেই relevant piece retrieve করুন। বেশি code কিন্তু আরও scale করে।

## Recovery

একটা tool error করলে — error as-is হাতে দিয়ে আশা করবেন না model figure out করবে। Tool call wrap করুন:

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

Structured error message model-কে reasoning-এর জন্য কিছু দেয় — opaque stack trace-এর বদলে। Model প্রায়ই automatically অন্য approach try করবে — কিন্তু শুধু error legible হলে।

## Observability

প্রতিটা tool call, এর argument, এর result, এবং model-এর response — log করুন। Production-এ এটা দুই কারণে দরকার:

- **Debugging।** User complain করলে trace-ই আপনার একমাত্র source of truth।
- **Improvement।** Agent কোথায় fail বা waste call করে — সেই pattern পরবর্তী prompt revision-এর highest-signal input।

Good log format-এ থাকে: session ID, per-turn step number, tool name, argument hash, result size, এবং model-level metadata যেমন stop_reason। High volume-এ প্রতিটা prompt-এর full content log করবেন না — structured summary log, full trace sample করুন।

## কখন থামবেন জানা

Loop শেষ হয় যখন:

- Model tool_use block ছাড়া text return করে (done বলে মনে করে)।
- Iteration cap fire করে।
- Token budget cap fire করে।
- Harness-এ একটা hard error।

Long-running agent-এর জন্য periodically একটা explicit "are we done?" check ভাবুন। Model-কে জিজ্ঞেস করুন: "Stated task complete করেছ? হ্যাঁ হলে যা করেছ summarize করো। না হলে — কী বাকি?" সেই meta-question কখনো ঘণ্টার useless iteration বাঁচায়।

## Honest secret

বেশিরভাগ "agent failure" model failure না — loop failure। Bad bounding, bad context management, bad error surface, no observability। Harness ঠিক করুন এবং model অনেক দূর যায় নিজে।
