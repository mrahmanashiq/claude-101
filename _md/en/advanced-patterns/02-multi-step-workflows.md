# Multi-step Workflows

A single agent loop is great for tasks that fit in one model's head. Real workflows often don't. Instead of one agent doing everything, you compose multiple steps — each with a narrow scope, each with the right tools — and orchestrate them.

This is where AI engineering starts looking less like prompt-writing and more like ordinary distributed systems work.

## Why compose

Three reasons one big agent doesn't always cut it:

- **Different steps need different tools.** A research step needs web access; a coding step needs file access; a notification step needs Slack. Bundling everything into one mega-toolset confuses the model and bloats the schema.
- **Different steps need different models.** Classification is cheap on Haiku. Code-writing is best on Sonnet. Hard reasoning lands on Opus. A workflow can route each step to the right tier.
- **Failure isolation.** When the workflow has clear boundaries, you can retry, cache, and observe each step independently. One messy agent run is hard to debug; six tidy steps are not.

## A simple linear pipeline

The minimum-viable workflow is just functions calling each other:

```python
def analyze_ticket(ticket_text):
    category = classify_intent(ticket_text)        # Haiku call
    if category == "billing":
        details = extract_billing_data(ticket_text)  # Haiku call
        response = draft_billing_reply(details)      # Sonnet call
    else:
        response = draft_general_reply(ticket_text)  # Sonnet call
    return response
```

Each function is its own narrow Claude call with its own prompt and its own tools (if any). There's no magic — just code.

This is, surprisingly often, the right shape for production AI. Not every workflow needs an agent.

## When to branch

You add branching when the steps depend on what previous steps returned. Use plain `if`/`switch` logic — don't make the model decide what to do next when a regex would do.

A useful rule: **decide structurally what you can, leave to the model what you can't.** If the next step depends on the language of the input, write a language classifier and switch on it. If the next step depends on subjective judgment ("does this customer sound angry?"), ask the model.

## Maps and reduces

Many workflows fan out and back in:

```python
def summarize_repo(file_paths):
    # Map: summarize each file independently
    per_file = [summarize_file(p) for p in file_paths]
    # Reduce: combine into a repo-level summary
    return combine_summaries(per_file)
```

Run the map in parallel (`asyncio.gather`) for speed. Each map call has its own focused context; the reduce step has the much smaller summaries instead of the original files.

This is a workhorse pattern for "process a lot of stuff" jobs — every analysis tool you've seen probably uses some form of it.

## Agents as nodes in the workflow

Some steps are themselves agent loops. That's fine. The workflow's job is to:

- Give the agent a *clearly scoped task*.
- Give it the *minimum tools* it needs.
- Take its output and *route* it further.

You'll find that an agent doing one thing well, called from a deterministic outer workflow, is far easier to operate than one giant agent trying to do everything.

## Idempotency and retries

When workflow steps have side effects — writing to a DB, sending an email — design for retries. Two rules:

- **Idempotency keys.** If you may retry a step, attach a unique key so duplicates collapse. Send-email becomes send-email-once-per-key.
- **Checkpoint state.** After each successful step, persist enough state that you can restart from there. Don't make a 7-step pipeline atomic; it'll never be.

## The mental model

A multi-step workflow is just a directed graph of (mostly deterministic) nodes, some of which happen to be LLM calls. The graph might branch, loop, fan out. It might have nodes that are agents. But underneath it's an ordinary program with ordinary failures.

If your "agent" is becoming hard to reason about, that's a signal to lift structure out of the prompt and into code. The model is good at the parts that need judgment; your code is better at everything else.
