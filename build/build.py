"""Build the Learn Claude offline reader from markdown sources.

Multilingual: each course is built once per language declared in courses.yml.
English (default) is output to the project root; other languages go under
their language code (e.g. /bn/).

Run from the project root:
    python build/build.py
"""
from __future__ import annotations

import io
import re
import sys
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

import markdown
import yaml
from markdown.extensions.toc import TocExtension

# Force UTF-8 stdout on Windows so we can print non-ASCII titles.
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"

SLUG_RE = re.compile(r"[^a-z0-9ঀ-৿]+")
NUM_PREFIX_RE = re.compile(r"^\s*(\d+)")
# "01-what-is-claude.md" -> ("01", "what-is-claude")
FILENAME_PARTS_RE = re.compile(r"^(\d+)[-_](.+)\.md$", re.IGNORECASE)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

DEFAULT_LANG = "en"  # output to root


@dataclass
class Chapter:
    source_path: Path
    number: int
    slug: str
    title: str
    body_html: str
    headings: list[tuple[str, str]] = field(default_factory=list)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = SLUG_RE.sub("-", text)
    return text.strip("-")


def chapter_number_from_filename(name: str) -> int:
    m = NUM_PREFIX_RE.match(name)
    return int(m.group(1)) if m else 9999


def make_md() -> markdown.Markdown:
    return markdown.Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "sane_lists",
            "admonition",
            "attr_list",
            TocExtension(toc_depth="2-3", permalink=False),
            "codehilite",
        ],
        extension_configs={
            "codehilite": {"guess_lang": False, "css_class": "codehilite"},
        },
    )


def extract(path: Path, number: int) -> Chapter:
    raw = path.read_text(encoding="utf-8")
    m = H1_RE.search(raw)
    if not m:
        raise ValueError(f"no H1 in {path.name}")
    title = m.group(1).strip()
    body_md = (raw[: m.start()] + raw[m.end():]).lstrip("\n")

    body_html = make_md().convert(body_md)

    headings: list[tuple[str, str]] = []
    for i, hm in enumerate(H2_RE.finditer(body_md)):
        text = hm.group(1).strip()
        anchor = slugify(text) or f"section-{i+1}"
        headings.append((anchor, text))

    # Derive slug from filename so translated versions share the same URL
    fm = FILENAME_PARTS_RE.match(path.name)
    slug = fm.group(2).lower() if fm else (slugify(title) or f"chapter-{number}")

    return Chapter(
        source_path=path,
        number=number,
        slug=slug,
        title=title,
        body_html=body_html,
        headings=headings,
    )


def extract_folder(folder: Path) -> list[Chapter]:
    chapters: list[Chapter] = []
    if not folder.exists():
        return chapters
    for path in sorted(folder.glob("*.md"), key=lambda p: chapter_number_from_filename(p.name)):
        number = chapter_number_from_filename(path.name)
        if number == 9999:
            print(f"  skip (no number): {path.name}")
            continue
        try:
            ch = extract(path, number)
        except Exception as exc:
            print(f"  FAIL {path.name}: {exc}")
            continue
        chapters.append(ch)
        print(f"  ok   {number:>3} {ch.title}")
    return chapters


def read_template(name: str) -> str:
    return (BUILD / name).read_text(encoding="utf-8")


def chapter_filename(ch: Chapter) -> str:
    return f"{ch.number:02d}-{ch.slug}.html"


def lang_root(lang: str) -> Path:
    """Output root for this language."""
    return ROOT if lang == DEFAULT_LANG else ROOT / lang


def lang_url_prefix(lang: str) -> str:
    """Site-relative URL prefix for this language (used in toggle links)."""
    return "" if lang == DEFAULT_LANG else f"{lang}/"


def base_path_for_chapter(lang: str) -> str:
    """Relative path from a chapter page back to the project root."""
    # Chapter at <root>/courses/<slug>/file.html  -> ../../
    # Chapter at <root>/bn/courses/<slug>/file.html -> ../../../
    return "../../" if lang == DEFAULT_LANG else "../../../"


def base_path_for_course_landing(lang: str) -> str:
    """Relative path from a course landing back to the project root."""
    return "../../" if lang == DEFAULT_LANG else "../../../"


def base_path_for_home(lang: str) -> str:
    return "" if lang == DEFAULT_LANG else "../"


def render_sidebar_links(chapters: list[Chapter], current: Chapter | None,
                          strings: dict, base: str, course_slug: str) -> str:
    out: list[str] = []
    for ch in chapters:
        href = chapter_filename(ch)
        is_active = current is not None and ch.source_path == current.source_path
        cls = "active" if is_active else ""
        aria = ' aria-current="page"' if is_active else ""
        out.append(
            f'            <li class="{cls}"><a href="{href}"{aria}>'
            f'<span class="ch-num">{ch.number:02d}</span>'
            f'<span class="ch-title">{escape(ch.title)}</span></a></li>'
        )
    return "\n".join(out)


def render_toc_links(headings: list[tuple[str, str]], strings: dict) -> str:
    if not headings:
        return f'            <li class="toc-empty">{escape(strings["no_sections"])}</li>'
    return "\n".join(
        f'            <li><a href="#{anchor}">{escape(text)}</a></li>'
        for anchor, text in headings
    )


def render_prev_next(chapters: list[Chapter], current: Chapter, strings: dict) -> tuple[str, str]:
    idx = next(i for i, c in enumerate(chapters) if c.source_path == current.source_path)
    if idx > 0:
        p = chapters[idx - 1]
        prev_html = (
            f'          <a class="chapter-nav-prev" href="{chapter_filename(p)}">'
            f'<span class="dir">{escape(strings["previous"])}</span>'
            f'<span class="title">{escape(p.title)}</span></a>'
        )
    else:
        prev_html = '          <span class="chapter-nav-prev placeholder"></span>'
    if idx < len(chapters) - 1:
        n = chapters[idx + 1]
        next_html = (
            f'          <a class="chapter-nav-next" href="{chapter_filename(n)}">'
            f'<span class="dir">{escape(strings["next"])}</span>'
            f'<span class="title">{escape(n.title)}</span></a>'
        )
    else:
        next_html = '          <span class="chapter-nav-next placeholder"></span>'
    return prev_html, next_html


def render_chapter_cards(chapters: list[Chapter], strings: dict) -> str:
    cards: list[str] = []
    for ch in chapters:
        href = chapter_filename(ch)
        cards.append(
            f'      <a class="chapter-card" href="{href}">'
            f'<span class="num">{escape(strings["chapter_label"])} {ch.number:02d}</span>'
            f'<span class="title">{escape(ch.title)}</span>'
            f'<span class="hint">{len(ch.headings)} {escape(strings["sections_label"])}</span></a>'
        )
    return "\n".join(cards)


def render_course_cards(courses: list[dict], chapter_counts: dict[str, int],
                          lang: str, strings: dict, base: str) -> str:
    cards: list[str] = []
    for c in courses:
        slug = c["slug"]
        count = chapter_counts.get(slug, 0)
        title = c["titles"].get(lang, c["titles"]["en"])
        desc = c["descriptions"].get(lang, c["descriptions"]["en"])
        # Home is at <root>/index.html or <root>/<lang>/index.html
        # Course landing: courses/<slug>/index.html relative to home
        cards.append(
            f'      <a class="course-card" href="courses/{slug}/index.html"'
            f' data-course-slug="{slug}" data-chapter-count="{count}">'
            f'<span class="course-eyebrow">{escape(strings["course_label"])}</span>'
            f'<h2>{escape(title)}</h2>'
            f'<p>{escape(desc)}</p>'
            f'<span class="course-meta">{count} {escape(strings["chapters"])} · {escape(strings["start_course"]).split("→")[0].strip()} →</span>'
            f'<div class="course-card-progress" aria-hidden="true">'
            f'<div class="progress-track"><span class="progress-fill"></span></div>'
            f'<div class="progress-meta">'
            f'<span class="progress-count"><span class="progress-done">0</span> / <span class="progress-total">{count}</span> {escape(strings["completed_count"])}</span>'
            f'<span class="progress-pct">0%</span>'
            f'</div></div></a>'
        )
    return "\n".join(cards)


def render_template(template: str, replacements: dict[str, str]) -> str:
    out = template
    for key, value in replacements.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def alt_lang(lang: str, languages: list[dict]) -> dict:
    """Return the metadata for the language to switch *to* from this one."""
    others = [l for l in languages if l["code"] != lang]
    return others[0] if others else languages[0]


def build_course(course: dict, lang: str, strings: dict,
                  template_chapter: str, template_course: str,
                  languages: list[dict]) -> int:
    slug = course["slug"]
    title = course["titles"].get(lang, course["titles"]["en"])
    description = course["descriptions"].get(lang, course["descriptions"]["en"])
    source_dir = ROOT / "_md" / lang / slug

    print(f"\n[{lang}/{slug}] reading {source_dir}")
    chapters = extract_folder(source_dir)
    if not chapters:
        print(f"  no chapters found, skipping {lang}/{slug}")
        return 0

    out_dir = lang_root(lang) / "courses" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    other = alt_lang(lang, languages)
    base = base_path_for_chapter(lang)
    home_href = f"{base}index.html"
    course_index_href = "index.html"

    # For the language toggle: from a chapter page, link to the same chapter
    # in the other language. Same {slug}/{filename}.
    def chapter_toggle_href(ch: Chapter) -> str:
        # From <lang_root>/courses/<slug>/<file>.html, switch to <other_lang_root>/courses/<slug>/<file>.html
        # Go up to project root, then descend into other lang.
        up = base  # ../../  or ../../../
        if other["code"] == DEFAULT_LANG:
            return f"{up}courses/{slug}/{chapter_filename(ch)}"
        return f"{up}{other['code']}/courses/{slug}/{chapter_filename(ch)}"

    course_toggle_href = (
        f"{base}courses/{slug}/index.html" if other["code"] == DEFAULT_LANG
        else f"{base}{other['code']}/courses/{slug}/index.html"
    )

    for ch in chapters:
        prev_html, next_html = render_prev_next(chapters, ch, strings)
        replacements = {
            "lang": lang,
            "dir": next(l["dir"] for l in languages if l["code"] == lang),
            "base_path": base,
            "site_name": escape(strings["site_name"]),
            "promo_strip_text": f'{escape(strings["promo_open"])} · {escape(title)}',
            "home_label": escape(strings["home_label"]),
            "course_title": escape(title),
            "course_slug": slug,
            "chapter_title": escape(ch.title),
            "chapter_body": ch.body_html,
            "sidebar_links": render_sidebar_links(chapters, ch, strings, base, slug),
            "toc_links": render_toc_links(ch.headings, strings),
            "prev_link": prev_html,
            "next_link": next_html,
            "mark_complete_label": escape(strings["mark_complete"]),
            "on_this_page_label": escape(strings["on_this_page"]),
            "completed_label": escape(strings["completed_count"]),
            "course_label": escape(strings["course_label"]),
            "lang_toggle_href": chapter_toggle_href(ch),
            "lang_toggle_label": escape(strings["toggle_lang"]),
        }
        page = render_template(template_chapter, replacements)
        (out_dir / chapter_filename(ch)).write_text(page, encoding="utf-8")

    first = chapters[0]
    landing = render_template(template_course, {
        "lang": lang,
        "dir": next(l["dir"] for l in languages if l["code"] == lang),
        "base_path": base_path_for_course_landing(lang),
        "site_name": escape(strings["site_name"]),
        "promo_strip_text": f'{escape(strings["promo_open"])} · {escape(title)}',
        "home_label": escape(strings["home_label"]),
        "course_label": escape(strings["course_label"]),
        "course_title": escape(title),
        "course_slug": slug,
        "course_description": escape(description),
        "chapter_count": str(len(chapters)),
        "chapters_label": escape(strings["chapters"]),
        "start_course_label": escape(strings["start_course"]),
        "first_chapter_href": chapter_filename(first),
        "chapter_cards": render_chapter_cards(chapters, strings),
        "chapters_complete_label": escape(strings["chapters_complete"]),
        "lang_toggle_href": course_toggle_href,
        "lang_toggle_label": escape(strings["toggle_lang"]),
    })
    (out_dir / "index.html").write_text(landing, encoding="utf-8")
    print(f"  wrote {len(chapters)} chapters + index to {lang_root(lang).relative_to(ROOT) if lang_root(lang) != ROOT else '.'}/courses/{slug}/")
    return len(chapters)


def build_home(courses: list[dict], chapter_counts: dict[str, int],
                lang: str, strings: dict, template_home: str,
                languages: list[dict]) -> None:
    total_courses = sum(1 for c in courses if chapter_counts.get(c["slug"], 0) > 0)
    total_chapters = sum(chapter_counts.values())
    lede = strings["home_lede_template"].format(courses=total_courses, chapters=total_chapters)

    other = alt_lang(lang, languages)
    if other["code"] == DEFAULT_LANG:
        toggle_href = "../index.html"
    else:
        # From English home (root/index.html), toggle to bn/index.html
        toggle_href = f"{other['code']}/index.html"

    home = render_template(template_home, {
        "lang": lang,
        "dir": next(l["dir"] for l in languages if l["code"] == lang),
        "base_path": base_path_for_home(lang),
        "site_name": escape(strings["site_name"]),
        "promo_strip_text": f'{escape(strings["promo_open"])} · {total_courses} courses · {total_chapters} chapters · {escape(strings["promo_free"])}'
            if lang == "en" else
            f'{escape(strings["promo_open"])} · {total_courses}টি কোর্স · {total_chapters}টি অধ্যায় · {escape(strings["promo_free"])}',
        "home_label": escape(strings["home_label"]),
        "home_h1": escape(strings["home_h1"]),
        "home_lede": escape(lede),
        "total_courses": str(total_courses),
        "total_chapters": str(total_chapters),
        "chapters_complete_label": escape(strings["chapters_complete"]),
        "footer": strings["footer"],  # raw HTML allowed (curated, not user input)
        "course_cards": render_course_cards(
            [c for c in courses if chapter_counts.get(c["slug"], 0) > 0],
            chapter_counts, lang, strings, base_path_for_home(lang),
        ),
        "lang_toggle_href": toggle_href,
        "lang_toggle_label": escape(strings["toggle_lang"]),
    })
    (lang_root(lang) / "index.html").write_text(home, encoding="utf-8")
    print(f"\nwrote {('index.html' if lang == DEFAULT_LANG else lang+'/index.html')} ({total_courses} courses, {total_chapters} chapters)")


def main() -> int:
    manifest = yaml.safe_load((BUILD / "courses.yml").read_text(encoding="utf-8"))
    courses = sorted(manifest["courses"], key=lambda c: c.get("order", 999))
    languages = manifest["languages"]
    all_strings = manifest["strings"]

    template_chapter = read_template("template_chapter.html")
    template_course = read_template("template_course.html")
    template_home = read_template("template_home.html")

    for lang_meta in languages:
        lang = lang_meta["code"]
        strings = all_strings.get(lang, all_strings["en"])
        # Make sure target root exists
        lang_root(lang).mkdir(parents=True, exist_ok=True)

        chapter_counts: dict[str, int] = {}
        for c in courses:
            n = build_course(c, lang, strings, template_chapter, template_course, languages)
            chapter_counts[c["slug"]] = n

        build_home(courses, chapter_counts, lang, strings, template_home, languages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
