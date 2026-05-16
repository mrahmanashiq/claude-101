# আপনার প্রথম Session

চলুন একটা real task-এ end-to-end Claude Code run করি। কিছু exotic না — একটা small refactor, সপ্তাহে দুবার আপনি যা করেন এমন। উদ্দেশ্য — loop-এর feel পাওয়া।

## Install ও authenticate

CLI install করুন (exact command platform-এর উপর — সাধারণত `npm install -g @anthropic-ai/claude-code` বা একটা installer script)। তারপর যেকোনো directory-তে `claude` run করুন। প্রথমবার এটা sign-in walk-through করায়। তারপর প্রতিটা project folder একটা candidate workspace।

## একটা project pick করুন

আপনার একটা real project-এ `cd` করুন। Desktop-এ পড়ে থাকা throwaway folder নয় — actual code, test ও `README` আছে এমন একটা pick করুন। Context থাকলে Claude বেশি useful।

## Agent শুরু করুন

```
claude
```

ব্যস। আপনি interactive session-এ। Prompt open, cursor blink করে, plain English-এ task type করতে পারেন।

## একটা concrete কিছু চান

প্রথম দিনে সবচেয়ে বড় ভুল মানুষ করে — abstract কিছু চাওয়া। *"Codebase improve করো"* meandering response দেয়। *"`cli/deploy.py`-তে একটা `--dry-run` flag add করো যেটা planned change print করবে execute না করে, এবং help text update করো"* দুই মিনিটে clean diff দেয়।

Specific হোন। File-এর নাম বলুন। Behavior-এর নাম বলুন। Result describe করুন।

## Diff পড়ুন

Claude previewable form-এ edit propose করবে। Autopilot-এ ফেলবেন না। প্রতিটা skim করুন — typo-এর জন্য না (এটা typo করে না), কিন্তু:

- Request বুঝেছে, নাকি একটু আলাদা problem solve করেছে?
- যে file ছোঁয়ার কথা না, ছুঁয়েছে?
- Existing style-এর সাথে codebase consistent রেখেছে?

কিছু off দেখলে diff reject করুন বা revision চান। Loop fast — clarification-এ seconds লাগে।

## Command run করতে দিন

Claude shell command (`npm test`, `pytest`, `go build`) run করতে চাইলে আগে জিজ্ঞেস করে। Safe-গুলো approve করুন। কয়েকবার পর কোন ধরনের command pre-approved সেটা শেখাতে পারেন (`.claude/settings.json`-এ বা permission UI-এর মাধ্যমে)।

## Session intentionally শেষ করুন

Task শেষ হলে `exit` type করুন বা terminal close করুন। আপনার change real file-এ real edit — disk-এ আছে, commit-এর জন্য ready। Claude কোনো magical জায়গায় "save" করে না। Diff-গুলোই *output*।

## প্রথম session checklist

এই সব করলে real session করেছেন:

- [ ] Real project directory-তে agent start করেছেন।
- [ ] একটা concrete, scoped task জিজ্ঞেস করেছেন।
- [ ] Approve করার আগে প্রতিটা proposed diff পড়েছেন।
- [ ] কমপক্ষে একটা shell command run করতে দিয়েছেন।
- [ ] Exit করার পর `git diff` review করেছেন এবং যেটা রাখতে চান সেটা commit করেছেন।

এখন আপনি Claude Code সম্পর্কে এমন 80% মানুষের চেয়ে বেশি জানেন যারা এটা সম্পর্কে পড়েছে।
