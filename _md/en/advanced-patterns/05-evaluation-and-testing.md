# Evaluation and Testing

Without evals, every change to your LLM system is guesswork. With evals, you can iterate fast and ship confidently. The gap between these two states is enormous, and most projects never close it because they think evals are exotic. They aren't. You can have a useful eval suite in an afternoon.

## What an eval actually is

An eval is a set of test cases for your LLM-using code. Each case has:

- **An input** — the prompt or request you'd give the system in production.
- **An expected outcome** — what "good" looks like. Sometimes exact, sometimes a rubric, sometimes "doesn't include X."
- **A way to score** the actual output against the expectation.

It's basically unit testing for things that aren't deterministic. The scoring is what's different.

## Scoring strategies, in order of effort

**Exact match.** When you can. For classifiers, extractors, structured outputs — if the expected output is `"billing"` and the model says `"billing"`, that's a pass. Cheapest, sharpest signal. Use this whenever possible.

**Substring / regex match.** When the output has a known marker. "The reply must contain the order ID." "The reply must not contain the user's email." Coarse but useful.

**Structural checks.** For JSON outputs: did it parse? Did it have the required fields? Are field values within constraints? Easy code to write; catches most generation regressions.

**Rubric scoring with another LLM.** When the right answer is fuzzy. Hand the input, the actual output, and a rubric to a second Claude call: "rate this 1–5 on these dimensions, and explain." Slower and noisier, but lets you eval things like "is this reply polite" or "does this code follow our style."

**Human review.** The gold standard, the most expensive. Reserve for the high-stakes 10% of cases or for periodic spot-checks.

You'll mix all five. Most well-run evals are 70% structural / exact match and 30% rubric, with humans sampling occasionally.

## Building your first eval

Start small. Twenty cases is enough to ship. Fifty is enough to feel confident. A hundred is a lot.

```python
cases = [
    {"input": "I want a refund for order 4382", "expect": "billing"},
    {"input": "How do I export my data?", "expect": "general"},
    {"input": "My invoice says $99 but I only see $89 in my plan", "expect": "billing"},
    # ... 17 more ...
]

def run_eval(case):
    actual = classify_intent(case["input"])
    return {
        "input": case["input"],
        "expected": case["expect"],
        "actual": actual,
        "passed": actual == case["expect"],
    }

results = [run_eval(c) for c in cases]
pass_rate = sum(r["passed"] for r in results) / len(results)
print(f"Pass rate: {pass_rate:.0%}")
for r in results:
    if not r["passed"]:
        print(f"FAIL: {r['input']!r} -> {r['actual']!r} (expected {r['expected']!r})")
```

That's a real eval. It would tell you, today, whether your classifier regressed since last week. Most projects never write this.

## Where the cases come from

Best source: real production data. Sample failed sessions, edge cases, customer complaints. Anonymize and add to the suite. After a few months you'll have an eval set that reflects your actual users, not just what you imagined.

Worst source: cases you make up that all look easy. Models pass them and you ship confidently into a brick wall.

## Running on every change

The whole point of evals is to run them often. Wire them into:

- **A pre-merge check** — run the suite when someone touches the prompt or model code, block merging if the pass rate dropped meaningfully.
- **A nightly job** — drift detection. The same prompt may behave differently on a new model version.
- **A one-line CLI** — `make eval`. You should be able to invoke it on demand without thinking.

The fastest projects iterate by running their evals dozens of times a day. The slowest don't have any and "test by feel."

## Beware leaderboard chasing

Pass rate is a number; chasing it can lead you astray. Two failure modes:

- **Overfitting to the eval.** If you tune the prompt only against your 50 cases, you'll do well on them and badly on the next 50 you encounter. Rotate cases in periodically. Hold out a fresh set you don't tune against.
- **Easy wins masking hard losses.** Your pass rate went from 92% to 94% — but the 6% it still fails are all the high-value cases. Look at *which* cases fail, not just *how many*.

## Beyond pass/fail

Once you have a basic suite, layer in:

- **Cost per case.** Track tokens. A new prompt that passes the same cases at half the cost is a real win, even if pass rate is flat.
- **Latency.** Mean and P95.
- **Failure clustering.** Group failures by category. "Half my failures are when the user's question is in Spanish" is a much more actionable insight than "pass rate is 87%."

A well-instrumented eval suite tells you not just whether the system works, but where and how it doesn't. That's what lets you steer.
