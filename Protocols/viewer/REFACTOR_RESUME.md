# Resume: ES-module refactor of viewer.html (Plan upgrade #4)

This branch (`refactor/modules`) is set up and ready to execute the
viewer.html ES-module split. The previous session shipped upgrades
#0–#3 to `main` and prepared this branch with a safety-net Playwright
suite that locks every current behavior.

**Do NOT touch `main`'s viewer.html during this refactor.** The branch
isolation is the rollback story — if the split goes sideways,
`git checkout main; git branch -D refactor/modules` cleans everything.

---

## What's already done

- Branch `refactor/modules` created off `c782035` (`#3` head).
- `Protocols/viewer/_refactor_safety_net.py` — 9 scenarios locking
  current behavior (file load, mark cycle, counter, theme/mirror/dir,
  Export decisions, FSA Save decisions, Forget button, no-FSA gating,
  external-change banner). **9/9 PASS against the unrefactored
  viewer.html.** Must continue to pass after every module extraction.

Run the suite at any point:

```powershell
python C:\My_AI\enterprise_cidra_framework\Protocols\viewer\_refactor_safety_net.py
```

Exit 0 = clean. Exit 1 = something regressed.

---

## What's left

Refactor `viewer.html` from a single 4800-line IIFE into **12 native ES
modules** under `Protocols/viewer/modules/`. No build step — uses
`<script type="module">` + relative `./modules/...` imports. External
libraries (marked, DOMPurify, hljs, mermaid, katex, html-docx-js,
ExcelJS, JSZip) stay loaded via existing `<script>` tags and are
accessed by modules via `window.X` globals.

### Module decomposition (12 files)

| # | Module | Owns | Imports from |
|---|---|---|---|
| 1 | `modules/core/state.js` | `State` object + state mutators | (leaf) |
| 2 | `modules/core/banner.js` | Banner IIFE (current viewer.html lines ~1512–1613) | (leaf) |
| 3 | `modules/render/code.js` | `escapeHtml`, `sanitizeLang`, `wrapHebrewInCommentSpans`, hljs stub grammars | (leaf) |
| 4 | `modules/render/marks.js` | `wrapDecisionMarks`, `cycleMarkState`, `exportDecisionsMd`, CIDRA_MARK constants | (leaf) |
| 5 | `modules/render/direction.js` | `applyDir`, `parseFrontMatter` | (leaf) |
| 6 | `modules/render/markdown.js` | `configureRenderer`, `smokeTestMarked` | `render/code` |
| 7 | `modules/io/file-read.js` | `decodeBuffer`, `loadFile` | `core/state`, `core/banner`, `core/render` |
| 8 | `modules/io/file-write.js` | FSA save (`saveDecisionsToFile`, `hasFsaSupport`, IDB layer, `forgetCurrentFileHandle`, `checkForExternalChange`, `reloadFromHandle`) + all export handlers (`exportMarkdown`/`exportHtml`/`exportDocx`/`exportDecisions`/`exportCsv`/`exportXlsx`) + clone prep + table export helpers | `render/code`, `render/marks`, `core/state`, `core/banner` |
| 9 | `modules/ui/export-menu.js` | ExportMenu IIFE + `refreshExportButtons` + `setItem` | `io/file-write`, `core/state` |
| 10 | `modules/core/render.js` | `render()`, `setEmptyOutput`, `installPurifyHook`, `updateDecisionsCounter` | `render/markdown`, `render/marks`, `render/direction`, `core/state`, `core/banner`, `ui/export-menu` |
| 11 | `modules/ui/toolbar.js` | `wireUI` for toolbar buttons, drag-drop, decision-mark click delegate, visibilitychange/focus listeners | `core/render`, `io/file-read`, `ui/export-menu`, `io/file-write` |
| 12 | `modules/core/boot.js` | Deps probes, `bootOnce`, `boot`, watchdog | `ui/toolbar`, `core/state`, `core/banner` |

### Extraction order (dependency-derived waves)

1. **Wave 1 (parallel-safe):** `code.js`, `marks.js`, `direction.js`, `state.js`, `banner.js`
2. **Wave 2:** `markdown.js` (imports code)
3. **Wave 3 (parallel-safe):** `file-read.js`, `file-write.js`
4. **Wave 4:** `export-menu.js` (imports file-write)
5. **Wave 5:** `render.js` (imports almost everything above)
6. **Wave 6:** `toolbar.js`
7. **Wave 7:** `boot.js`
8. **Wave 8 (final assembly):** rewrite `viewer.html` as ~200-line thin
   shell — `<head>` (CSS, dependency `<script>` tags with SRI), body
   markup (toolbar, banners, output container), and a single
   `<script type="module" src="./modules/core/boot.js">` tag.

After every wave: `python _refactor_safety_net.py` must still return
9/9 PASS. If a wave breaks something, fix or revert that wave alone
before continuing.

### Key line ranges in current viewer.html (Section map from earlier exploration)

- IIFE: lines 1438–4489
- Section 0 (Deps + State): 1441–1505
- Section 1 (Stub grammars): 1673–1726
- Section 2 (Smoke test): 1729–1744
- Section 3 (Renderer helpers): 1747–1896
- Section 4 (Marked config + renderer overrides): 1902–2019
- Section 5 (DOMPurify config): 2030–2060
- Section 6 (Front-matter parser): 2071–2084
- Section 7 (Render pipeline): 2110–2309
- Section 8 (File reading): 2314–2383
- Section 9 (Toolbar handlers): 2388–2408
- Section 9.5 (Export pipeline): 2410–4144 (large — ExportMenu IIFE
  2536–3062, refreshExportButtons 3066, FSA helpers added in #1
  starting around line 3722, change-watcher added in #3 around 3870)
- Section 10 (wireUI): 4255–4720+
- Section 11 (Boot): 4400+
- Section 12 (Watchdog): 4500+

(Run `Grep` against viewer.html for the section banners — the comments
`// 1. SMOKE TEST`, `// 2. RENDERER OVERRIDES`, etc. — to find exact
current line numbers, since post-#0/#2/#1/#3 edits have shifted them.)

### Loading order in the new viewer.html

```html
<head>
  <!-- existing CSS -->
  <!-- existing CDN <script> tags with SRI for marked, DOMPurify,
       hljs, mermaid, katex (and the vendor fallback chain). These
       stay as-is; modules access them via window.X globals. -->
</head>
<body>
  <!-- existing toolbar, banners, output, toast markup -->

  <!-- Single entry point. boot.js imports everything else via the
       module graph. defer is implicit for type=module. -->
  <script type="module" src="./modules/core/boot.js"></script>
</body>
```

### Risks and known sharp edges

1. **External-lib globals.** marked, DOMPurify, hljs, mermaid, katex,
   html-docx-js, ExcelJS, JSZip are NOT imported via ES modules —
   they're loaded by the existing `<script>` tags before `boot.js`
   runs. Modules access them via `window.X`. This is intentional (no
   build step) but means modules must defensively check `window.X` is
   available, mirroring the existing `Deps` probes.

2. **CSS classes referenced by JS** must be tested after split — e.g.
   `.cidra-mark`, `.decisions-counter`, `.link-button`, `.banner`,
   `.banner-action`, `.toast`, `.export-menu-root .menu` all need to
   keep working.

3. **Event delegation lives in `toolbar.js`** but the elements (`#output`,
   `#btnTheme`, etc.) are in the HTML shell. The shell ships
   pre-marked-up; toolbar.js attaches listeners on DOMContentLoaded.

4. **IIFE boundary disappears.** Variables that were "private" inside
   the IIFE (e.g. `CIDRA_MARK_CYCLE`, `purifyConfig`) become module-
   private. Anything that needs to cross modules must be exported
   explicitly. Module privacy is stronger than IIFE privacy — good
   thing — but it means accidental "global access" patterns inside
   the IIFE will surface as missing imports.

5. **Avoid circular imports.** The dependency graph above is acyclic
   by construction. If you find yourself wanting `marks.js` to
   import from `render.js`, that's a sign the split is wrong —
   the shared helper belongs in a lower module (probably
   `core/state.js`).

6. **`State` is shared mutable singleton.** Every module that mutates
   State imports `{ State }` from `core/state.js` and works against
   the same instance. Don't try to "pass State as a parameter" —
   the existing code structure assumes singleton access.

### Final assembly checklist

After Wave 8:

- `viewer.html` reduced from ~4800 lines to ~200.
- `modules/` directory contains all 12 .js files.
- `python _refactor_safety_net.py` → 9/9 PASS.
- `git diff main -- Protocols/viewer/viewer.html | wc -l` shows the
  expected ~4600 line reduction in `viewer.html`.
- Commit the branch in small, reviewable chunks (one wave per commit
  is reasonable — 8 commits total).
- Merge to main only after the full suite passes from a fresh `git
  checkout refactor/modules` + a fresh Playwright run.

---

## Why we stopped here mid-session

The previous session shipped #0, #2, #1, #3 to main. #4 is genuinely a
1-week refactor and trying to compress it into the same session would
risk context-compression bleed (which would manifest as missing
imports, wrong line numbers, or accidental main-branch edits). The
clean handoff was the right call.

When you resume:
1. `git checkout refactor/modules`
2. Read this file
3. Run the safety net to confirm 9/9 baseline
4. Start Wave 1 — extract `state.js` first (smallest, leaf, easiest to
   verify the import-graph approach works)
5. Continue wave-by-wave, running the safety net after each wave

Good luck.

*Refactor branch created: 2026-06-02. Plan source:
`C:\Users\iliya\.claude\plans\validated-conjuring-eich.md`.*
