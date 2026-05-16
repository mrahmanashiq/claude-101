# Workflow Pattern

Claude Code-এর part গুলো জানা এক জিনিস। সেগুলোকে এমন workflow-এ string করা যা actually সময় বাঁচায় — অন্য জিনিস। প্রতিদিন মাসের পর মাস ব্যবহারের পর যেগুলো টিকে থাকে — সেই pattern।

## Plan-execute-verify loop

সবচেয়ে reliable single pattern। তিনটা explicit phase:

1. **Plan.** কোনো code লেখার আগে Claude-কে একটা plan draft করতে বলুন। কোন file বদলাবে, কী test add হবে, কোন edge case matter করে, কী ভুল হতে পারে।
2. **Execute.** Plan approve করুন, তারপর Claude-কে step by step কাজ করতে দিন।
3. **Verify.** Claude (বা আপনি বা একটা subagent) test run করুক, type-check করুক, lint করুক, এবং diff-কে plan-এর সাথে মিলিয়ে পড়ুক।

Trap হলো step 1 skip করা কারণ task "simple feel" করছে। দু-এক file-এর বেশি touch করা যেকোনো কিছুতে, plan লেখা প্রায় সবসময় দুই মিনিট worth।

## Small, scoped task

বড় task বড় way-তে fail করে না — একসাথে অনেক small way-তে fail করে, যা debug করা harder। কাজকে 30–60 মিনিট agent time-এর chunk-এ ভাঙুন। প্রতিটার পর commit করুন। এখন আপনার history small reviewable diff-এর series, একটা sprawling change না।

একটা good chunk-এ থাকে:

- Goal describe করা এক বাক্য।
- পরিষ্কার "done" condition (test pass করে, behavior X কাজ করে, screenshot Y ঠিক দেখায়)।
- File-এর একটা estimated scope (Claude 5 file পড়া fine; 50 — আলাদা ধরনের task)।

## সবসময় একটা branch-এ থাকুন

যেকোনো non-trivial change-এর আগে `git checkout -b feature/<thing>`। এর কোনো cost নেই এবং যেদিন Claude এমন কিছু করে যা রাখতে চান না — সেদিন বাঁচায়। Branch-এর undo button শুধু `git checkout main`। Main-এ — `git reflog`-এ একটা সন্ধ্যা।

## CLAUDE.md পড়ুন, CLAUDE.md লিখুন

Project-wide convention-এ Claude-কে correct করার সময় প্রতিবার নিজেকে জিজ্ঞেস করুন: এই correction কি CLAUDE.md material? যদি হয় — add করুন। আপনার future-self এই same project-এ Claude run করবে; এই correction-এর সাথে তাদের জন্য debt pay down করছেন।

## Read-heavy কাজে sub-agent ব্যবহার করুন

কোনো কিছু *summarize* করতে অনেক code পড়া দরকার এমন task — "এই module কী করে?", "এই API-কে যেখানে যেখানে call করি খুঁজে দাও," "আমাদের error handling audit করো" — সেটা textbook subagent job। Main agent-কে সব code context-এ load করতে হয় না; subagent reading করে এবং summary report করে। Context ও money বাঁচান।

## Habit হিসেবে না, hook হিসেবে test run করুন

প্রতিটা change-এর পর "এখন test run করো" type করতে থাকলে — একটা PostToolUse hook setup করুন যা প্রতিটা Edit-এর পর test command run করে। Mechanical step থেকে human-কে loop-এর বাইরে রাখুন। এখন Claude test failure-কে observation cycle-এর অংশ হিসেবে দেখে, এবং interesting কিছু থাকলেই intervene করেন।

## Conversation-কে code হিসেবে treat করুন

একটা long Claude session একটা real artifact। সেখানে নেওয়া decision, considered trade-off, follow করা plan — একটা গল্প বলে। দুটো habit সাহায্য করে:

- একটা session non-trivial design decision দিলে — PR description-এ বা design doc-এ summary paste করুন।
- অস্বাভাবিকভাবে ভালো কাজ করেছে এমন একটা prompt পেলে — slash command হিসেবে save করুন।

Compounding real। ছয় মাসে আপনার এমন slash command ও skill-এর পাহাড় থাকবে যা নতুন task 5× দ্রুত করে।

## কখন bail out করবেন

কিছু task simply Claude Code-এর জন্য না:

- **Massive cross-cutting refactor** এমন codebase-এ যেখানে test coverage poor। Risk surface বড় বেশি।
- **Pure visual design কাজ।** Text agent না — একটা design tool ব্যবহার করুন।
- **One-line change যেটা ইতিমধ্যে জানেন কীভাবে করতে হবে।** Type করাই দ্রুত।

কখন editor-এ directly drop করবেন — সেটা recognize করা practice করার skill। Tool good; সব কিছুর answer না।
