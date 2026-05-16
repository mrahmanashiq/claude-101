# Evaluation ও Testing

Eval ছাড়া — আপনার LLM system-এ প্রতিটা change guesswork। Eval সহ — fast iterate ও confidently ship করতে পারেন। এই দুই state-এর মাঝে gap বিশাল, এবং বেশিরভাগ project কখনো close করে না কারণ তারা ভাবে eval exotic। না। দুপুরের মধ্যে একটা useful eval suite হতে পারে।

## একটা eval আসলে কী

Eval হলো আপনার LLM-using code-এর জন্য একটা test case-এর set। প্রতিটা case-এ:

- **একটা input** — production-এ system-কে যে prompt বা request দিতেন।
- **একটা expected outcome** — "good" কেমন দেখায়। কখনো exact, কখনো একটা rubric, কখনো "X include করে না"।
- **Score করার একটা উপায়** — actual output expectation-এর সাথে।

মূলত deterministic না এমন জিনিসের unit testing। Scoring-এ যা আলাদা।

## Effort-এর order-এ scoring strategy

**Exact match।** যেখানে পারেন। Classifier, extractor, structured output-এর জন্য — expected output `"billing"` ও model বলে `"billing"`, pass। Cheapest, sharpest signal। যেখানে possible এটাই ব্যবহার করুন।

**Substring / regex match।** Output-এ known marker থাকলে। "Reply-এ order ID থাকতে হবে।" "Reply-এ user-এর email থাকবে না।" Coarse কিন্তু useful।

**Structural check।** JSON output-এর জন্য: parse হলো? Required field ছিল? Field value constraint-এর মধ্যে? Easy code, generation regression-এর বেশিরভাগ catch।

**আরেকটা LLM দিয়ে rubric scoring।** Right answer fuzzy হলে। দ্বিতীয় Claude call-কে input, actual output, ও rubric দিন: "এই dimension-গুলোতে 1–5 rate করো, ব্যাখ্যা দাও।" Slower এবং noisier, কিন্তু "এই reply কি polite" বা "এই code আমাদের style follow করে" এমন কিছু eval করতে দেয়।

**Human review।** Gold standard, most expensive। High-stakes 10% case-এর জন্য বা periodic spot check-এর জন্য রাখুন।

পাঁচটাই mix করবেন। বেশিরভাগ well-run eval 70% structural / exact match ও 30% rubric, occasionally human sample সহ।

## প্রথম eval বানানো

Small শুরু করুন। বিশটা case ship করার জন্য যথেষ্ট। পঞ্চাশটা confident feel-এর জন্য। একশো অনেক।

```python
cases = [
    {"input": "Order 4382-এর refund চাই", "expect": "billing"},
    {"input": "আমার data কীভাবে export করব?", "expect": "general"},
    {"input": "Invoice $99 কিন্তু আমার plan-এ $89 দেখাচ্ছে", "expect": "billing"},
    # ... আরো 17টা ...
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

এটা একটা real eval। আজই বলে দেবে — আপনার classifier গত সপ্তাহের তুলনায় regress করেছে কিনা। বেশিরভাগ project এটাই কখনো লেখে না।

## Case কোথা থেকে আসে

Best source: real production data। Failed session, edge case, customer complaint sample করুন। Anonymize করে suite-এ add করুন। কয়েক মাস পর — actual user reflect করে এমন eval set হবে, আপনার imagine করা না।

Worst source: case যেগুলো সব easy দেখায় ও বানিয়ে নিচ্ছেন। Model pass করে এবং confidently brick wall-এ ship করেন।

## প্রতিটা change-এ run

Eval-এর whole point — often run করা। Wire করুন:

- **A pre-merge check** — কেউ prompt বা model code touch করলে suite run, pass rate meaningfully drop হলে merge block।
- **A nightly job** — drift detection। একই prompt নতুন model version-এ আলাদা behave করতে পারে।
- **A one-line CLI** — `make eval`। Demand-এ চিন্তা না করে invoke করতে পারা উচিত।

Fastest project তাদের eval দিনে কয়েক ডজনবার run করে iterate করে। Slowest-দের কিছুই নেই — "test by feel"।

## Leaderboard chasing-এ সাবধান

Pass rate একটা number; এটা chase করলে পথ হারাতে পারেন। দুটো failure mode:

- **Eval-এ overfit।** শুধু 50 case-এ tune করলে — সেগুলোতে ভালো করবেন এবং next 50-এ খারাপ। Case periodically rotate করুন। একটা fresh set hold out রাখুন যা tune করেন না।
- **Easy win hard loss mask।** Pass rate 92% থেকে 94% — কিন্তু 6% যা এখনো fail সেগুলো সব high-value case। *কোন* case fail হচ্ছে দেখুন, *কতগুলো* না।

## Pass/fail-এর বাইরে

Basic suite থাকলে layer in করুন:

- **Per case cost।** Token track করুন। নতুন prompt একই case half cost-এ pass — real win, pass rate flat থাকলেও।
- **Latency।** Mean ও P95।
- **Failure clustering।** Failure category-তে group। "অর্ধেক failure যখন user-এর question Spanish-এ" — "pass rate 87%" এর চেয়ে অনেক বেশি actionable insight।

A well-instrumented eval suite আপনাকে বলে — system কাজ করে কিনা না শুধু, কোথায় ও কীভাবে করে না। এটাই steer করতে দেয়।
