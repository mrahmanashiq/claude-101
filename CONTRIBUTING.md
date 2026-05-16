# Contributing to Learn Claude

Thanks for being here. Learn Claude is an open guide — pull requests are welcome whether you're fixing a typo, adding a new chapter, translating, or polishing the design. This doc is the short version of how everything fits together and what makes a good contribution.

## What you can contribute

A non-exhaustive list, in roughly increasing order of effort:

- **Typos and small wording fixes** — any chapter, either language.
- **Better code examples** in existing chapters — clearer, more idiomatic, more current.
- **Updated technical details** — Claude moves fast; if something here is out of date or just wrong, fix it.
- **New chapters** within an existing course (Fundamentals, Claude Code, Claude API, Advanced Patterns).
- **Translations** — finish a partial language, fix a Bangla phrasing, or add an entirely new language.
- **Tooling fixes** — build script, templates, CSS, deploy config.
- **A whole new course** — biggest scope. Open an issue first to align on the topic and outline before you write.

## Project layout

```
.
├─ _md/<lang>/<course>/NN-slug.md   source markdown (this is what you edit)
├─ build/
│  ├─ build.py                      converts _md/ to courses/*.html
│  ├─ courses.yml                   manifest: languages, courses, UI strings
│  ├─ template_{home,course,chapter}.html
│  ├─ make_icons.py                 regenerates favicon PNGs from the SVG
│  └─ requirements.txt
├─ assets/
│  ├─ styles.css                    one CSS file for everything
│  ├─ script.js                     theme toggle, sidebar, progress tracking
│  └─ favicon.svg + variants
├─ index.html                       English home   (built output)
├─ courses/<slug>/*.html            English chapters (built output)
└─ bn/index.html, bn/courses/...    বাংলা home + chapters (built output)
```

**Source vs. output.** You edit files in `_md/` and `build/`. The build script regenerates everything in `courses/`, `bn/`, and `index.html`. Don't hand-edit the built HTML — your changes will be wiped on the next build.

## Setting up locally

You need Python 3.10+. Anything newer than that is fine.

```bash
# Clone
git clone https://github.com/mrahmanashiq/claude-101.git
cd claude-101

# Install build deps
pip install -r build/requirements.txt

# Build the site (regenerates courses/ and bn/)
python build/build.py

# Preview locally
python -m http.server 8000
# then open http://localhost:8000
```

That's it. No node, no bundler, no framework.

## Editing an existing chapter

1. Find the file under `_md/en/<course>/NN-slug.md` (and the matching `_md/bn/<course>/NN-slug.md` if you also want to update the Bangla version).
2. Make your edit. Standard CommonMark works, plus a few python-markdown extensions you'll find useful:
   - Fenced code blocks with language tags (` ```python ` etc.)
   - Tables with `|` syntax
   - Admonitions: `!!! tip`, `!!! note`, `!!! warning` followed by an indented paragraph
3. Rebuild: `python build/build.py`
4. Refresh your browser and check the change.

If you change the H1 of a chapter, the filename's slug part should still match between languages — don't rename the file unless you rename it in every language folder.

## Adding a new chapter

1. Pick a slot — e.g. you want a new chapter 9 in Claude Code, after "Workflow Patterns".
2. Create the markdown file at `_md/en/claude-code/09-your-slug.md`. The filename must start with a two-digit number; the rest becomes the chapter's URL slug.
3. The first line must be a single `# H1 Title`. That title appears in the sidebar, breadcrumb, and `<title>`.
4. Write the chapter. Aim for clear, practical, opinionated. See existing chapters for the tone.
5. If you can, mirror the file at `_md/bn/claude-code/09-your-slug.md` with a Bangla translation. Same filename, same H2 structure if possible (so anchors line up). If you can't translate it now, that's fine — open the PR with just the English version and note that a translation is welcome.
6. Build and preview before submitting.

## Adding a new language

1. Add a new entry to `courses.yml` under `languages:`:

   ```yaml
   - code: hi          # ISO 639-1
     label: हिन्दी
     alt_label: English
     dir: ltr
   ```

2. Add UI strings under `strings:` for the new code. Copy the `en:` block as a starting point and translate every value.
3. Add per-language `titles:` and `descriptions:` to each course in the same file.
4. Create `_md/<code>/<course>/` folders with translated chapter files. They should use the same filenames as the English versions so URLs and progress state line up.
5. Build. The script will automatically emit to `/<code>/` and the language toggle in the header will cycle through every declared language.

If your language is right-to-left (Arabic, Hebrew, etc.), set `dir: rtl` and let me know in the PR — there may be small CSS tweaks needed beyond what's already there.

## Style notes

A few things that keep the guide coherent:

- **Tone:** plain, direct, opinionated. Short sentences. No hype. Address the reader as "you."
- **Tech terms:** keep them in English even in non-English chapters (`API`, `token`, `agent`, `prompt`). Translate the connecting prose. This matches how developers actually talk in those languages.
- **Code examples:** runnable when possible. Prefer Python or TypeScript unless the chapter is about a specific other tool.
- **Length:** chapters are typically 400–700 words. Longer is fine if the topic genuinely needs it. Shorter is fine if it doesn't.
- **No filler:** if a paragraph could be deleted without losing anything, delete it.

## Pull request workflow

1. **Fork** the repo on GitHub.
2. **Branch** from `master`. Name it after what you're doing: `fix-typo-rate-limits`, `add-vector-db-chapter`, `bn-streaming-fix`.
3. **Commit** with a short, descriptive subject line. One sentence, lowercase, no period. Examples: `fix typo in tool use chapter`, `add chapter on extended thinking`, `improve mark-as-complete on safari`.
4. **Build before pushing.** Run `python build/build.py` and make sure it completes without errors. Commit the regenerated HTML in `courses/` and `bn/` if your change affects content.
5. **Open a PR** against `master`. Describe what you changed and why. Screenshots welcome for visual changes.

If you're not sure something will be accepted, open an issue first and we can talk about it. Small fixes don't need an issue — just send the PR.

## Reporting bugs or suggesting ideas

Open a GitHub issue at <https://github.com/mrahmanashiq/claude-101/issues>. For bugs, include:

- The page URL where you hit the problem.
- What you expected vs. what actually happened.
- Browser and OS, if it might be relevant (e.g. layout issues).

For ideas, just describe the idea and why it would help readers.

## Code of conduct

Be kind. Assume the other person is doing their best. If a review comment feels harsh, it's probably about the code, not you. If your review comment might feel harsh, soften it — we're all volunteers here.

That's it. Thanks for contributing.
