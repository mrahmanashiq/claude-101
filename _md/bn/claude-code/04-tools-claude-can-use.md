# Claude যেসব Tool ব্যবহার করতে পারে

Agent দুনিয়ায় "tool" মানে — model-এর call করার অনুমতি আছে এমন একটা function। Claude Code একটা built-in toolkit নিয়ে আসে — file পড়া, file edit করা, shell command run করা, search, URL fetch, ইত্যাদি — এবং সেই toolkit-ই এটাকে chatty-এর বদলে agentic বানায়।

সাধারণত আপনি নিজে tool invoke করেন না। English-এ task describe করেন; Claude কোন tool call করবে decide করে। কিন্তু toolset বোঝা আপনার 10 মিনিটের সমান value, কারণ এটা বলে — agent কী পারে এবং কী পারে না, এবং কীভাবে request phrase করলে এটা সঠিক tool pick করে।

## Core file tool

- **Read** — একটা file open করে conversation-এ load করে। প্রায় সব সময় ব্যবহার।
- **Write** — দেওয়া content দিয়ে একটা নতুন file create করে। Scratch থেকে শুরু করার সময় explicitly চাওয়া হয়।
- **Edit** — existing file-এ একটা specific string নতুন content দিয়ে replace করে। Change-এর workhorse; Write-এর চেয়ে safer কারণ এটা surrounding context specify করতে বলে।
- **Glob** — name pattern দিয়ে file খুঁজে দেয় (যেমন `src/**/*.ts`)।
- **Grep** — regex দিয়ে file content search করে।

বেশিরভাগ session: Glob/Grep দিয়ে locate, Read দিয়ে confirm, Edit দিয়ে change।

## Shell tool

- **Bash** (বা Windows-এ **PowerShell**) — project directory-তে একটা command run করে।

Shell access-ই Claude-কে actually কাজ verify করতে দেয় — test run, type-check, lint, dev server start। By default risky command approval চায়। Safe-গুলো pre-approve করতে পারেন।

## Web tool

- **WebFetch** — একটা URL load করে content পড়ে (HTML text-এ strip করা)।
- **WebSearch** — relevant page-এর জন্য web search করে।

যখন Claude-এর training data-এ নেই এমন documentation দরকার — গত সপ্তাহে ship হওয়া library version, vendor page-এ একটা API spec — তখন useful।

## Agent tool

- **Task** (বা **Agent**) — isolation-এ কাজের একটা chunk handle করতে sub-agent spawn করে।

এটা একটা force multiplier। একটা conversation-এ ছয়টা কাজ করে context ভরে ফেলার বদলে, Claude একটা discrete subtask sub-agent-কে দিতে পারে, সেটা run করতে দিতে পারে, এবং শুধু result absorb করতে পারে। Advanced Patterns course-এ depth-এ cover করা হয়েছে।

## MCP server থেকে tool

Built-in set-এর বাইরে **MCP server** plug করতে পারেন — external program যা নিজস্ব tool expose করে। Database-এর জন্য server আছে, browser-এর জন্য, JIRA, Notion, GitHub, design tool — সব কিছুর। একবার একটা server configured হলে, এর tool Claude-এর toolset-এ দেখা দেয় এবং একই loop-এ এটা ব্যবহার করতে পারে।

MCP-এর জন্য আলাদা chapter আছে; আপাতত এটুকু জানুন যে toolset extensible।

## Claude কীভাবে tool pick করে

Model prompt-এর অংশ হিসেবে available tool ও তাদের schema-এর list পায়। যখন decide করে একটা tool দরকার, একটা structured tool-call emit করে (কোন tool, কোন argument-এ)। Harness call run করে এবং result return করে, যা model পরবর্তী turn-এ পড়ে।

Claude-কে সঠিক tool pick করানোর skill মূলত clear prompting-এর skill-এর মতোই:

- **File-এর নাম বলুন।** "`src/auth.py` edit করো যাতে..." unambiguous। "Auth-এর জিনিসটা edit করো" Claude-কে আগে search করায়, কখনো ভুল জিনিস।
- **Verb state করুন।** "Read", "list", "run", "check" — verb tool-এর সাথে cleanly map করে।
- **Scope limit করুন।** "`tests/` folder-এ deprecated mock ব্যবহার করছে এমন কোনো test খুঁজে বের করো" — Claude-কে exactly কোথায় দেখতে হবে ও কোন tool ব্যবহার করতে হবে বলে দেয়।

আপনার request যত concrete, Claude তত কম ভুল tool call করে — এবং তত দ্রুত একটা ভালো answer পান।
