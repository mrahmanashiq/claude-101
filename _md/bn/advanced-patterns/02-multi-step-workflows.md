# Multi-step Workflow

একটা single agent loop সেই task-গুলোর জন্য great যা একটা model-এর মাথায় fit করে। Real workflow প্রায়ই করে না। একটা বড় agent সব করার বদলে — multiple step compose করেন — প্রতিটার narrow scope, প্রতিটার right tool — এবং orchestrate করেন।

এখানেই AI engineering prompt-writing-এর চেয়ে কম, ordinary distributed systems-এর কাজের মতো দেখতে শুরু করে।

## Compose কেন

তিনটা কারণ এক বড় agent সবসময় কাজ করে না:

- **আলাদা step-এ আলাদা tool দরকার।** একটা research step-এ web access; একটা coding step-এ file access; একটা notification step-এ Slack। সব একটা mega-toolset-এ bundle করলে — model confuse করে এবং schema bloat হয়।
- **আলাদা step-এ আলাদা model দরকার।** Classification Haiku-তে cheap। Code-writing Sonnet-এ best। Hard reasoning Opus-এ land করে। Workflow প্রতিটা step right tier-এ route করতে পারে।
- **Failure isolation।** Workflow-এর clear boundary থাকলে — প্রতিটা step independently retry, cache, observe করতে পারেন। একটা messy agent run debug করা hard; ছয়টা tidy step না।

## একটা simple linear pipeline

Minimum-viable workflow — শুধু function একে অপরকে call করছে:

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

প্রতিটা function নিজস্ব prompt ও নিজস্ব tool (থাকলে) সহ একটা narrow Claude call। কোনো magic না — just code।

Production AI-এর জন্য এটা surprisingly প্রায়ই right shape। প্রতিটা workflow-এর agent লাগে না।

## Branch কখন

Step-গুলো আগের step-এর return-এর উপর depend করলে — branching add করেন। Plain `if`/`switch` logic ব্যবহার করুন — model-কে next step decide করতে বলবেন না যখন একটা regex কাজ করে।

একটা useful rule: **যা structurally decide করতে পারেন — করুন, যা পারেন না — model-এ ছেড়ে দিন।** Input language-এর উপর next step depend করলে — একটা language classifier লিখুন এবং switch করুন। Subjective judgment-এর উপর depend করলে ("এই customer কি রেগে আছে?") — model-কে জিজ্ঞেস করুন।

## Map ও Reduce

অনেক workflow fan out এবং back in হয়:

```python
def summarize_repo(file_paths):
    # Map: প্রতিটা file independently summarize
    per_file = [summarize_file(p) for p in file_paths]
    # Reduce: একটা repo-level summary-তে combine
    return combine_summaries(per_file)
```

Speed-এর জন্য map parallel-এ run করুন (`asyncio.gather`)। প্রতিটা map call-এর নিজস্ব focused context; reduce step original file-এর বদলে অনেক ছোট summary।

"অনেক কিছু process" job-এর জন্য এটা workhorse pattern — যেকোনো analysis tool আপনি দেখেছেন — সম্ভবত কোনো না কোনো form-এ এটা ব্যবহার করে।

## Workflow-এর node হিসেবে agent

কিছু step নিজেই agent loop। Fine। Workflow-এর কাজ:

- Agent-কে একটা *clearly scoped task* দেওয়া।
- *Minimum tool* যা দরকার দেওয়া।
- এর output নেওয়া এবং আরও *route* করা।

দেখবেন একটা deterministic outer workflow থেকে call করা — একটা কাজ ভালোভাবে করা agent — সব করার চেষ্টা করা একটা giant agent-এর চেয়ে operate করা far easier।

## Idempotency ও retry

Workflow step-এর side effect থাকলে — DB-তে write, email send — retry-এর জন্য design করুন। দুটো rule:

- **Idempotency key।** Step retry করতে পারলে — একটা unique key attach করুন যাতে duplicate collapse করে। send-email হয়ে যায় send-email-once-per-key।
- **Checkpoint state।** প্রতিটা সফল step-এর পর enough state persist করুন যাতে সেখান থেকে restart করতে পারেন। 7-step pipeline-কে atomic করবেন না; কখনো হবে না।

## Mental model

একটা multi-step workflow হলো (mostly deterministic) node-এর একটা directed graph — যার কিছু LLM call। Graph branch করতে পারে, loop করতে পারে, fan out করতে পারে। Agent এমন node থাকতে পারে। কিন্তু underneath এটা একটা ordinary program — ordinary failure সহ।

আপনার "agent" reason করা hard হয়ে আসলে — সেটা signal — structure prompt থেকে code-এ lift করুন। Model judgment-এর জিনিসে ভালো; বাকি সব-এ আপনার code better।
