// Learn Claude — shared client behavior

(function () {
  "use strict";

  // ---------- Language preference ----------
  const LANG_KEY = "lc-lang";
  document.addEventListener("click", (e) => {
    const a = e.target.closest('[data-action="set-lang"]');
    if (!a) return;
    const href = a.getAttribute("href") || "";
    const next = /(^|\/)bn\//.test(href) ? "bn" : "en";
    try { localStorage.setItem(LANG_KEY, next); } catch (_) {}
  });

  // ---------- Theme ----------
  const THEME_KEY = "lc-theme";
  const root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
  }

  function preferredTheme() {
    const stored = localStorage.getItem(THEME_KEY);
    if (stored === "light" || stored === "dark") return stored;
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  }

  applyTheme(preferredTheme());

  document.addEventListener("click", (e) => {
    const btn = e.target.closest('[data-action="toggle-theme"]');
    if (!btn) return;
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(next);
    localStorage.setItem(THEME_KEY, next);
  });

  // ---------- Sidebar drawer (mobile) ----------
  const sidebar = document.querySelector("[data-sidebar]");
  const backdrop = document.querySelector(".sidebar-backdrop");

  function openSidebar() {
    sidebar && sidebar.classList.add("open");
    backdrop && backdrop.classList.add("open");
  }
  function closeSidebar() {
    sidebar && sidebar.classList.remove("open");
    backdrop && backdrop.classList.remove("open");
  }

  document.addEventListener("click", (e) => {
    if (e.target.closest('[data-action="toggle-sidebar"]')) {
      sidebar && sidebar.classList.contains("open") ? closeSidebar() : openSidebar();
      return;
    }
    if (e.target.closest('[data-action="close-sidebar"]')) {
      closeSidebar();
    }
  });

  const activeItem = document.querySelector(".sidebar-nav li.active");
  if (activeItem) {
    requestAnimationFrame(() => {
      activeItem.scrollIntoView({ block: "center", inline: "nearest" });
    });
  }

  // ---------- Right-rail TOC scroll-spy ----------
  const tocLinks = Array.from(document.querySelectorAll(".toc a[href^='#']"));
  if (tocLinks.length) {
    const idToLink = new Map();
    const targets = [];
    tocLinks.forEach((a) => {
      const id = a.getAttribute("href").slice(1);
      const el = document.getElementById(id);
      if (el) {
        idToLink.set(id, a);
        targets.push(el);
      }
    });

    if ("IntersectionObserver" in window && targets.length) {
      let lastActiveId = null;
      const visible = new Set();

      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          const id = entry.target.id;
          if (entry.isIntersecting) visible.add(id);
          else visible.delete(id);
        });

        let activeId = null;
        for (const t of targets) {
          if (visible.has(t.id)) { activeId = t.id; break; }
        }
        if (!activeId) {
          for (const t of targets) {
            if (t.getBoundingClientRect().top < 120) activeId = t.id;
            else break;
          }
        }
        if (activeId && activeId !== lastActiveId) {
          tocLinks.forEach((l) => l.classList.remove("active"));
          const link = idToLink.get(activeId);
          if (link) link.classList.add("active");
          lastActiveId = activeId;
        }
      }, { rootMargin: "-15% 0px -70% 0px", threshold: 0 });

      targets.forEach((t) => observer.observe(t));
    }
  }

  // ---------- Progress (mark chapter complete) ----------
  const PROGRESS_KEY = "lc-progress";

  function readProgress() {
    try { return JSON.parse(localStorage.getItem(PROGRESS_KEY) || "{}"); }
    catch { return {}; }
  }
  function writeProgress(p) {
    localStorage.setItem(PROGRESS_KEY, JSON.stringify(p));
  }

  function pageContext() {
    const path = location.pathname.replace(/\\/g, "/");
    const m = path.match(/\/courses\/([^/]+)\/([^/]+)\.html$/);
    if (m) {
      const courseSlug = m[1];
      const file = m[2];
      if (file === "index") return { kind: "course", courseSlug };
      return { kind: "chapter", courseSlug, chapterSlug: file, chapterId: courseSlug + "/" + file };
    }
    return { kind: "home" };
  }

  function chapterIdFromHref(href, courseSlug) {
    if (!href) return null;
    const m = href.match(/([^/]+)\.html(?:[?#]|$)/);
    if (!m || m[1] === "index") return null;
    return courseSlug + "/" + m[1];
  }

  function updateProgressDisplay(root, done, total) {
    if (!root) return;
    const pct = total > 0 ? Math.round((done / total) * 100) : 0;
    const fill = root.querySelector(".progress-fill");
    if (fill) fill.style.width = pct + "%";
    const doneEl = root.querySelector(".progress-done");
    if (doneEl) doneEl.textContent = String(done);
    const totalEl = root.querySelector(".progress-total");
    if (totalEl) totalEl.textContent = String(total);
    const pctEl = root.querySelector(".progress-pct");
    if (pctEl) pctEl.textContent = pct + "%";
  }

  function paintChapterPage(progress) {
    const ctx = pageContext();
    if (ctx.kind !== "chapter") return;
    const btn = document.querySelector("[data-action='toggle-chapter-complete']");
    if (btn) {
      const done = !!progress[ctx.chapterId];
      btn.classList.toggle("is-complete", done);
      btn.setAttribute("aria-pressed", String(done));
      const label = btn.querySelector(".label");
      if (label) label.textContent = done ? "Completed" : "Mark as complete";
    }
    let total = 0;
    let doneCount = 0;
    document.querySelectorAll(".sidebar-nav li").forEach((li) => {
      const a = li.querySelector("a");
      if (!a) return;
      const id = chapterIdFromHref(a.getAttribute("href"), ctx.courseSlug);
      const isDone = !!(id && progress[id]);
      li.classList.toggle("is-complete", isDone);
      if (id) {
        total += 1;
        if (isDone) doneCount += 1;
      }
    });
    updateProgressDisplay(document.querySelector(".sidebar-progress"), doneCount, total);
  }

  function paintCoursePage(progress) {
    const ctx = pageContext();
    if (ctx.kind !== "course") return;
    const cards = Array.from(document.querySelectorAll(".chapter-card"));
    let done = 0;
    cards.forEach((card) => {
      const id = chapterIdFromHref(card.getAttribute("href"), ctx.courseSlug);
      const isDone = !!(id && progress[id]);
      card.classList.toggle("is-complete", isDone);
      if (isDone) done++;
    });
    updateProgressDisplay(document.querySelector(".course-progress"), done, cards.length);
  }

  function paintHomePage(progress) {
    const ctx = pageContext();
    if (ctx.kind !== "home") return;
    let totalDone = 0;
    let totalCount = 0;
    document.querySelectorAll(".course-card").forEach((card) => {
      const slug = card.getAttribute("data-course-slug");
      const count = parseInt(card.getAttribute("data-chapter-count") || "0", 10);
      if (!slug || !count) return;
      const prefix = slug + "/";
      let done = 0;
      for (const k of Object.keys(progress)) {
        if (k.indexOf(prefix) === 0 && progress[k]) done++;
      }
      totalDone += done;
      totalCount += count;
      card.classList.toggle("is-complete", count > 0 && done === count);
      const mini = card.querySelector(".course-card-progress");
      if (mini) updateProgressDisplay(mini, done, count);
    });
    updateProgressDisplay(document.querySelector(".home-progress"), totalDone, totalCount);
  }

  function paintAll(progress) {
    paintChapterPage(progress);
    paintCoursePage(progress);
    paintHomePage(progress);
  }

  paintAll(readProgress());

  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action='toggle-chapter-complete']");
    if (!btn) return;
    const ctx = pageContext();
    if (ctx.kind !== "chapter") return;
    const progress = readProgress();
    if (progress[ctx.chapterId]) {
      delete progress[ctx.chapterId];
    } else {
      progress[ctx.chapterId] = new Date().toISOString();
    }
    writeProgress(progress);
    paintAll(progress);
  });
})();
