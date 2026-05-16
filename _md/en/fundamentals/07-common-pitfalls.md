# Common Pitfalls and How to Avoid Them

A short list of mistakes that show up over and over again, in the order they typically bite. Each one is easy to fix once you know to look for it.

## 1. Assuming Claude remembers

Claude has no memory between API calls. None. If you don't send the previous turns back, they don't exist. This sounds obvious but trips up newcomers constantly — they ask "why did Claude forget my earlier instruction?" and the answer is always: because you didn't include it in this call.

If you want continuity, you (or the harness around you) must pass the conversation history every time. Claude.ai does this for you. Claude Code does this for you. Your own app has to do it explicitly.

## 2. Confusing the surfaces

A behavior in Claude.ai isn't necessarily available in the API. A Claude Code feature isn't a model feature — it's a feature of the *tool around* the model. When you read a blog post or a tweet, ask which surface it's talking about. The distinction matters more than people admit.

## 3. Trusting confident output

A confident-sounding answer is not a correct answer. Language models are trained to be coherent and helpful, and that includes being coherent when they're wrong. The cure is verification: for anything that matters, check the output against a source of truth — run the code, query the database, ask a second model, ask a human.

The dangerous version of this pitfall is invented facts, sometimes called hallucinations. They show up most often when:

- The question is about a specific, narrow fact (a number, a date, a name).
- The question is in a domain where the model has shallow knowledge.
- The prompt is leading (you implied the answer exists when it doesn't).

Mitigation: ground the model with real data via tools or retrieval, and tell it explicitly that it's allowed to say "I don't know."

## 4. Stuffing the context

Long context windows tempt people to paste everything they have. Don't. Quality degrades when the model has to wade through pages of barely-relevant material. Be selective. The right reflex is: *what is the smallest amount of context this task actually needs?*

## 5. Ignoring temperature for the wrong tasks

Many SDKs default `temperature` to around 1.0. For deterministic tasks — extraction, classification, code generation where you want consistency — drop it to 0 or near it. You'll get more stable outputs across runs.

For creative tasks — brainstorming, writing — leave it higher. Different jobs, different settings.

## 6. Not pinning the model version

Calling `claude-latest` or letting your SDK default to a moving alias is fine for experimentation. In production, pin to an exact model ID. Otherwise the day a new model ships, your output behavior changes — sometimes for the better, sometimes not, but always without warning.

## 7. No evals, all vibes

The number-one predictor of an LLM project succeeding is whether the builder has a small evaluation suite — twenty to a hundred input/expected-output pairs they can run automatically. Without that, every change is guesswork. With it, you can iterate fast and ship confidently.

## 8. Treating prompts like one-time write-only assets

A prompt that works today won't necessarily work next quarter. Models change. Use cases evolve. Treat prompts as code: version them, review them, test them. The folder full of `.md` prompts in your repo is a real artifact, not a scratchpad.

---

That's the short list. If you internalize these eight, you'll skip most of the early stumbles and get to interesting problems faster.
