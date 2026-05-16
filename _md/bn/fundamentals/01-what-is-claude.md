# Claude আসলে কী?

Claude হলো Anthropic-এর তৈরি large language model-দের একটা পরিবার। আপনি সাধারণ ভাষায় কথা বলেন; এটাও সাধারণ ভাষায় উত্তর দেয়। ভেতরে এটা একটা neural network — text predict করার জন্য train করা, এবং instruction follow করা, ক্ষতিকর request refuse করা ও tool ব্যবহার করার জন্য fine-tune করা।

আপনি কয়েকভাবে Claude-কে ব্যবহার করতে পারেন, এবং কোনটা matter করে সেটা depend করে আপনি কী বানাচ্ছেন তার উপর।

## তিনটা surface

আজকের দিনে মানুষ Claude-কে মূলত তিনভাবে ব্যবহার করে:

- **Claude.ai** — claude.ai-তে browser-based chat interface। বন্ধুসুলভ, কোনো setup লাগে না। এক-shot প্রশ্ন, writing, research, ও model-এর সক্ষমতা খুঁজে বের করার জন্য ভালো।
- **Claude Code** — Anthropic-এর agentic coding tool। আপনার terminal বা IDE-তে চলে, file পড়তে ও edit করতে পারে, shell command চালাতে পারে, এবং multi-step কাজে মনোনিবেশ রাখতে পারে। Software ship করার সময় এটাই আপনার দরকার।
- **Claude API** — raw HTTP endpoint এবং official SDK (Python, TypeScript, আরও কিছু)। এটাই ভিত্তি। বাকি সব এর উপর তৈরি। নিজের product বানানোর সময় এটা ব্যবহার করুন।

অনেক confusion এই তিনটাকে মিলিয়ে ফেলা থেকে আসে। *"Claude একটা feature add করেছে"* — এই কথাটার তিনটা ভিন্ন মানে হতে পারে: একটা নতুন model version, একটা নতুন Claude Code capability, অথবা একটা নতুন API parameter। শেখার সময় নিজেকে প্রশ্ন করতে শেখান: *কোন surface-এর কথা বলছি?*

## একটা language model আসলে কী করে

Claude-এর মতো একটা model input হিসেবে token-এর একটা sequence (মোটামুটি word-piece) নেয় আর একটা একটা করে output token produce করে। ব্যস। বাকি সব — chat, tool calling, "thinking," memory, agents — সব এই core loop-এর উপর তৈরি।

এটা matter করে কারণ call-গুলোর মাঝে model-এর কোনো internal state নেই। আপনি আগের conversation আবার না পাঠালে এটা মনে রাখে না। আপনি (বা চারপাশের harness) prompt-এ না দিলে আপনার file-এ এর access নেই। যত capability আপনি দেখেন, সব ওই token-in / token-out loop-এর চারপাশে input ও output-এর যত্নশীল arrangement।

!!! tip
    Claude-এর behavior debug করার সবচেয়ে দ্রুত উপায় হলো জিজ্ঞেস করা: *আসলে model input হিসেবে ঠিক কী দেখলো?* বেশিরভাগ surprise আসে আপনি যা ভাবছেন এটা দেখেছে আর context-এ আসলে যা ছিল — এই দুটোর mismatch থেকে।

## এই guide আপনাকে কোথায় নিয়ে যাবে

এই course-এর বাকি অংশে আমরা model নিয়েই কথা বলবো — size, prompting, context, reasoning। তারপর surface-by-surface যাব: Claude Code (terminal agent), Claude API (নিজের app), এবং basics-এর পরে advanced pattern।

পড়ার কোনো বাঁধাধরা order নেই, কিন্তু এটাই যদি প্রথম পরিচয় হয়, course-গুলো ক্রমে পড়ুন। প্রতিটা ধরে নেয় আগেরটা আপনি বুঝেছেন।
