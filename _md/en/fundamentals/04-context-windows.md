# Context Windows Explained

The **context window** is how much text Claude can consider in a single call. It's measured in tokens — roughly four characters of English text per token, give or take. Recent Claude models support context windows in the hundreds of thousands of tokens, with some extended-context variants going to a million.

That's a lot. But "a lot" doesn't mean "infinite," and treating context like infinite is one of the most common rookie mistakes.

## What counts as context

Everything you send to the model on a given call is context:

- The **system prompt** (high-level instructions about role, tone, rules)
- The **conversation history** (previous turns, both user and assistant)
- Any **attached documents** (pasted files, PDFs, images)
- **Tool definitions** and **tool results** from earlier in the conversation

All of these compete for the same budget. If you have a 200k-token window and 180k of it is the conversation so far, you have 20k left for the next exchange and the response.

## "Lost in the middle"

Even with a large window, models attend most strongly to the beginning and end of the context. Information buried in the middle of a long prompt is more likely to be missed or de-emphasized. Two practical consequences:

- **Put the most important instructions at the very start or very end** of the prompt.
- **For long documents, don't bury the question.** State the task first, then the document, then restate the task at the end.

## You pay for every token, every time

If you're using the API, you're billed per input token on every call. A long-running chat that has accumulated a 100k-token history will charge you for that history *on every new user turn*. This is where prompt caching becomes a major lever (covered later in the API course) — it lets you reuse a long stable prefix without re-paying full price.

## When to compact

Once a conversation gets long, three options:

- **Summarize and continue.** Replace the older turns with a short summary, keep recent turns verbatim. Loses fidelity but stays cheap.
- **Trim by relevance.** Drop turns that aren't useful for the current question. Best if you can detect which turns are relevant.
- **Start fresh.** Sometimes the cleanest answer. Begin a new conversation with the relevant facts in the system prompt.

Claude Code does some of this automatically when its own context fills up, but in your own applications you'll need to manage it yourself.

## A mental model

Think of context as a workbench, not a memory. The model only sees what's on the bench right now. Anything off the bench may as well not exist. Your job as the builder is to keep the right things on the bench for the current task — no more, no less.

!!! note
    A long context window is a capability, not a strategy. Just because you *can* dump 500k tokens in does not mean you *should*. The model's quality is best when the context is focused on what's actually needed.
