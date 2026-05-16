# Production Readiness

"আমার laptop-এ কাজ করে" থেকে "production-এ user নির্ভর করতে পারে"-তে যাওয়া — নিজেই একটা project। Model easy অংশ। চারপাশের boring infrastructure-ই determine করে আপনার AI feature real traffic-এর সাথে contact-এ survive করবে কিনা।

এটা একটা checklist, মোটামুটিভাবে যেক্রমে প্রতিটা item নিয়ে ভাবতে হবে।

## সব কিছু pin করুন

- **Model version pin করুন।** `claude-latest` না। Alias না। Exact ID, একটা config file-এ, কখন update করেছেন তার record সহ।
- **SDK version pin করুন।** একই reasoning। Auto-update surprise নামায়।
- **Prompt version pin করুন।** Prompt-কে code-এর মতো treat করুন। Versioned file, code-reviewed change, application-এর সাথে deployed।

"এই request-এর সময় ঠিক কী চলছিল?" — ambiguity ছাড়া answer দিতে পারলে — debug করার একটা chance আছে। নাহলে প্রতিটা incident একটা mystery।

## Timeout, retry ও limit

- **Per-request timeout set করুন।** Default "চিরকাল wait"। প্রায় প্রতিটা production path-এ ভুল। Synchronous call-এর জন্য 30–60s sensible upper bound।
- **Transient failure retry করুন।** 429, 5xx, network blip। SDK-এর reasonable default আছে; আপনার দরকারে tune ও trust করুন।
- **চিরকাল retry করবেন না।** Retry cap (সাধারণত 3–5) — যাতে একটা bad day runaway cost event না হয়।
- **Per request token budget।** `max_tokens` set করুন যাতে একটা single response blow up না করতে পারে। Agentic loop-এর জন্য whole loop-এর total token-ও cap করুন।

## Observability

পরে ব্যবহার করতে পারেন এমন level-এ log করুন। Minimum:

- Request ID (আপনার, শুধু API-এর না)।
- User ID (বা anonymized session ID)।
- Model used, prompt version, tool list version।
- Input ও output token count। (Default-এ full prompt/response log করবেন না — বড় এবং PII থাকতে পারে।)
- Latency।
- Stop reason, error থাকলে।
- Token count থেকে computed USD cost।

Dashboard-এ aggregate করুন: P50/P95/P99 latency, error type অনুযায়ী error rate, per user cost, per feature cost, daily volume। কিছু break হলে — মিনিটের মধ্যে জানা উচিত, একদিন পর user complain থেকে না।

## Cost guardrail

তিন layer-এর protection:

- **Per-user rate limit।** একটা misbehaving user আপনাকে bankrupt করবে না। তাদের daily / hourly volume cap করুন।
- **Per-request cost cap।** একটা request-এর total token usage budget cross করলে gracefully abort।
- **Global circuit breaker।** Total daily spend threshold-এ পৌঁছলে — কাউকে page করুন এবং low-priority traffic refuse করতে শুরু করুন।

এগুলো often fire করে না। যখন করে — অনেক বাঁচায়।

## Safety ও content control

User-facing feature-এর জন্য:

- **Input validation।** Obviously hostile input (prompt injection, malformed payload) edge-এ reject।
- **Output filter।** Expose করতে চান না এমন PII strip করুন। Known-bad output pattern block করুন।
- **Refusal handling।** Model answer দিতে refuse করলে (কখনো করবে) — একটা graceful fallback রাখুন। Claude-এর refusal text raw expose করবেন না; একটা UI message render করুন।
- **Audit-এর জন্য logging।** Regulated industry-এর জন্য — compliance meet করে এমন একটা retention policy লাগতে পারে — পরে bolt on করবেন না।

## Caching strategy

Production-এ prompt caching mandatory, optional না। Stable prefix-যুক্ত যেকোনো feature-এর জন্য:

- Cacheable block mark করুন।
- Usage stat-এ cache hit rate monitor করুন।
- Startup-এ বা traffic spike-এর আগে cache warm করুন।

Caching থেকে 5–10× cost reduction — feature ship হওয়া বনাম axe পাওয়ার পার্থক্য।

## Graceful degradation

কী হয় যখন:

- API down? (Last good response cache করুন যেখানে possible; নাহলে একটা clear "পরে চেষ্টা করুন" দেখান।)
- Model slow? (একটা streaming response দেখান যাতে user *কিছু* দেখে; একটা hard timeout রাখুন যা static reply বা simpler model-এ fall back করে।)
- Tool fail? (Agent loop-এ recover; recovery fail হলে — clean error surface করুন।)

Launch-এর আগে এই failure mode design করুন। Test করুন। Black Friday-তে discover করবেন না।

## CI-তে eval gate

আপনার eval suite (আগের chapter) প্রতিটা PR-এ run হোক যেটা prompt বা model touch করে। Pass rate threshold-এর চেয়ে বেশি drop হলে — PR fail। Silent quality regression-এর বিরুদ্ধে এটাই single best defense।

## Rollout

Model, prompt বা tool change করার সময়:

- **প্রথমে traffic-এর একটা ছোট percentage-এ roll out।** Metric — quality, cost, latency — বাকির সাথে compare।
- **একটা rollback plan রাখুন।** এটা একটা one-line config change হওয়া উচিত, deploy না।
- **User-visible metric দেখুন**, শুধু synthetic না। Conversion rate, support volume, satisfaction score।

## On-call playbook

আপনি যত failure mode ভাবতে পারেন — প্রতিটার জন্য একটা one-page playbook লিখুন: কী check করতে হবে, কী rollback করতে হবে, কাকে wake up করতে হবে। প্রথমবার একটা LLM-related incident hit করলে — লিখে রেখেছেন বলে খুশি হবেন।

---

এটা AI engineering-এর boring অংশ। এটাই demo-কে product থেকে আলাদা করে।
