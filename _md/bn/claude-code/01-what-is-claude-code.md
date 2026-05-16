# Claude Code কী?

Claude Code হলো Anthropic-এর coding agent। আপনি terminal-এ (বা IDE-এর ভেতর) এটা run করেন, এবং এটা আপনার codebase-এ এমনভাবে কাজ করে যেভাবে একজন careful collaborator করতেন — file পড়ে, edit করে, command চালায়, result check করে, এবং task শেষ না হওয়া পর্যন্ত continue করে।

Chat-based coding assistant ব্যবহার করে থাকলে — mental model আলাদা। Chat assistant suggestion দেয়; আপনি copy-paste করে নিজেই run করেন। Claude Code সেই loop টা close করে দেয়। file পড়তে পারে, change make করতে পারে, test run করতে পারে, এবং report করতে পারে।

## কেন matter করে

বড় shift হলো *snippet-by-snippet help* থেকে *task-by-task execution*-এ। "এই function-টা কীভাবে refactor করব?" জিজ্ঞেস করেন না — বলেন "এই function-কে refactor করো যাতে এটা context manager নেয়," আর Claude করে দেয়। তারপর আপনি diff review করেন।

এটা আপনার সময় কাটানোর ধরন বদলে দেয়। কম typing, বেশি review। কম mechanical কাজ, বেশি architectural decision। মানুষের attention-এর unit এক level উপরে চলে যায়।

## কোথায় চলে

- **Terminal:** CLI। Project folder open করুন, `claude` run করুন, কথা শুরু।
- **IDE:** VS Code ও JetBrains-এর extension আছে যা editor-এ এটা embed করে।
- **Desktop ও web app:** একটা desktop UI আছে, এবং claude.ai/code-এ একটা hosted version।

সব surface-এই underlying agent একই; শুধু surface আলাদা।

## আসলে কী করতে পারে

Out-of-the-box Claude Code পারে:

- Project directory-এর যেকোনো file পড়তে।
- File edit করতে (আগে diff preview, তারপর apply)।
- Shell command run করতে (আপনার permission নিয়ে)।
- Codebase-এ search করতে (grep, glob)।
- URL open করতে ও documentation fetch করতে।
- আপনার configure করা MCP server থেকে tool ব্যবহার করতে।
- কাজ parallelize করতে sub-agent spawn করতে।

কী allowed সেটা আপনার control-এ। Risky command-এর জন্য confirmation চায়; কী automatically চলবে কী চলবে না — rule configure করতে পারেন।

## যা না

Claude Code কোনো magic "build my app" button না। এটা একটা powerful assistant যেটার এখনো — অনেক — সাহায্য লাগে: একটা clear specification, একটা clean codebase, এবং loop-এ একজন human। Vague task দিলে vague result পাবেন। Precise task সঠিক context-এর সাথে দিলে — দ্রুত, আপনি যা চান তার কাছাকাছি কিছু পাবেন।

এটা model নিজেও না। Claude Code হলো *harness*: যে layer Claude (model)-কে tool, file access, memory, ও একটা loop-এ act করার ক্ষমতা দেয়। ভেতরে এটা একই API call করছে যা যে কেউ call করতে পারে। Harness-ই এটাকে agentic বানায়।

## পরে কী শিখবেন

এই course-এর বাকি অংশে: একটা session শুরু ও manage করা, যে slash command এটাকে steer করে, available tool-গুলো, কীভাবে `CLAUDE.md` file Claude-কে project context দেয়, এবং higher-level concept — skill, subagent, hook, ও MCP server — যা Claude Code-কে আপনার workflow-এর সাথে tailor করতে দেয়।

শেষে আপনার vocabulary ও instinct হবে এটা দিয়ে actually ship করার।
