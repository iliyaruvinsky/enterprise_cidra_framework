# CIDRA Documentation Viewer

A single-file, dependency-free (CDN-loaded) HTML viewer for CIDRA-authored
Markdown documentation. Implements the rendering contract defined in
[`Agents/shared/multilingual_rendering_protocol.yaml`](../../Agents/shared/multilingual_rendering_protocol.yaml)
(MRP) v1.2.0.

The viewer exists because GitHub, VS Code preview, and other generic
Markdown viewers do not consistently handle bilingual (Hebrew + English)
documents that mix RTL prose with LTR identifiers, code blocks, and
tables. The CIDRA viewer applies the MRP's deterministic direction
policy so every documenter output renders identically.

---

## Quick start

1. **Open** `viewer.html` by double-clicking it. It opens in the default
   browser via `file://`. No server required.
2. **Load a document** in one of three ways:
   - Click **Open .md…** in the toolbar and pick a file.
   - Drag and drop a `.md` / `.markdown` / `.txt` file anywhere on the
     window.
   - Pass via URL query (`viewer.html?file=...`) is **not** supported —
     `file://` security restrictions prevent fetch from disk paths.
3. **Adjust direction / theme / comments** using the toolbar buttons.

---

## Toolbar reference

| Button | Purpose |
|--------|---------|
| `Open .md…` | File picker for `.md`, `.markdown`, or `.txt` files. |
| `Dir: Auto / RTL / LTR` | Override document direction. `Auto` uses front-matter or first-strong heuristic. On boot, the label is synced to the live `html[dir]` (the empty state ships as RTL so the Hebrew prompt reads correctly). |
| `Theme: Light / Dark` | Swaps page CSS variables AND the highlight.js stylesheet. Disabled while an export is in flight to defend the "theme race" adversarial finding. |
| `Mirror HE Comments: Off / On` | When on, Hebrew runs inside `hljs-comment` spans get a `<bdi dir="rtl">` wrapper so they read RTL inside an LTR code block. This is a **view-time preference** — it does not modify the source file. |
| `Clear` | Empties the current document and re-disables the export buttons. |
| `Export .md` | Downloads the **source** Markdown as `.md`. Round-trips losslessly. Disabled until a document is loaded. |
| `Export .html` | Downloads a self-contained `.html` file with all viewer CSS inlined. Opens identically in any browser without the CDN. Disabled until a document is loaded. |
| `Export .docx` | Downloads a Word `.docx` produced by `html-docx-js` v0.3.1 with the Hebrew/RTL and Mermaid mitigations described below. Disabled until a document is loaded AND `html-docx-js` finished loading. |

The file-info panel shows the loaded filename, size, and detected
encoding (UTF-8, UTF-16 LE, UTF-16 BE). A warning badge appears if the
file is not UTF-8 without BOM.

A short-lived **toast** in the lower-end corner confirms each successful
export. Click the toast to dismiss it early; otherwise it auto-fades
after 2.5 s.

---

## Front-matter convention

For bilingual documents, open the `.md` file with a YAML front-matter
block:

```markdown
---
dir: rtl
documentation_language: hebrew
---

# כותרת המסמך

תוכן המסמך...
```

Recognised keys:

- `dir`: one of `rtl`, `ltr`, `auto`. Controls `html[dir]` before render.
- `documentation_language`: one of `hebrew`, `english`, `bilingual`.
  Sets `html[lang]` so font fallbacks pick the right script.

If front-matter is absent, the viewer falls back to `dir="auto"` (first
strong character of each block decides). The user can override either
choice via the toolbar **Dir** button; the override sticks until the
next file load.

---

## What the viewer does for you

- **Inline backticked identifiers** like `` `RK0041C776` `` become
  `<bdi><code>RK0041C776</code></bdi>` — both `<bdi>` and `<code>`
  isolate the identifier so trailing Hebrew punctuation lands on the
  Hebrew side, not next to the identifier.
- **Fenced code blocks** are wrapped `<pre dir="ltr">` with highlight.js
  syntax coloring. Hebrew comments inside code are isolated per-comment
  with `<bdi dir="rtl">` when **Mirror HE Comments** is on.
- **Tables** inherit direction from `html[dir]`. Cells containing only
  code/identifiers/numbers (no Hebrew letters) are detected
  structurally and rendered LTR regardless of the table direction — so
  a row of HTTP codes `` `200`, `404`, `500` `` does not reverse to
  `500, 404, 200` under RTL.
- **Block elements** (paragraphs, headings, list items, lists
  themselves) carry `dir="auto"` so each resolves to its own
  first-strong direction. Blockquotes do NOT carry `dir` on the outer
  block — the inner `<p>`s do, so each line of a multi-line
  blockquote resolves independently.
- **Links** are wrapped in `<bdi>` so trailing punctuation does not
  attach to the URL run.
- **Mermaid SVG** embedded as `<img src="data:image/svg+xml;base64,…">`
  is permitted by the DOMPurify config (via `ALLOWED_URI_REGEXP`, the
  documented v3 mechanism — not the deprecated `ADD_DATA_URI_TAGS`).

---

## Table styling

Tables produced by the viewer (and carried through to `.html` and `.docx`
exports) follow a uniform GitHub-grade visual: dark slate header, subtle
zebra body, crisp slate borders, comfortable 8x14 padding.

### Philosophy

One source of truth, three export targets. The viewer's CSS variables
`--tbl-header-bg`, `--tbl-row-even`, `--tbl-border`, etc. drive on-screen
rendering AND propagate into the exports via two different mechanisms:

| Surface | CSS mechanism | Zebra mechanism | Theme |
|---------|---------------|-----------------|-------|
| Viewer | `var(--tbl-*)` resolving against `:root` or `html[data-theme="dark"]` | `tbody tr:nth-child(odd|even)` | Live light/dark toggle |
| `.html` export | Full viewer `<style>` block embedded in `<head>` | `nth-child` **AND** pre-baked inline `background:` on every other `<tr>` | Mirrors viewer's active theme; dark block included so DevTools toggle works in the exported file |
| `.docx` export | Inline `style="..."` on every `<table>`, `<th>`, `<td>`, `<tr>` with literal hex resolved at export time | Pre-baked inline `background:` only (Word ignores `:nth-child` reliably) | **Always light** — see below |

### Light-theme color values used in DOCX

The DOCX export rewriter resolves all `var(--tbl-*)` to these literals
before serialization. They mirror the viewer's `:root` block exactly.

| Token | Value | Used for |
|-------|-------|----------|
| `--tbl-border-outer` | `#a0aec0` | Frame border (cells only — table-level border dropped to avoid Word's double-frame quirk) |
| `--tbl-border` | `#cbd5e0` | Inner cell borders |
| `--tbl-header-bg` | `#2d3748` | Header row background (slate-700) |
| `--tbl-header-fg` | `#ffffff` | Header row text |
| `--tbl-row-odd` | `#ffffff` | Odd body rows |
| `--tbl-row-even` | `#f7fafc` | Even body rows (slate-50, zebra) |
| `--tbl-cell-fg` | `#1a202c` | Body cell text (slate-900) |
| `--tbl-code-bg` | `#edf2f7` | Inline `<code>` chip background |
| `--tbl-code-fg` | `#1a202c` | Inline `<code>` chip text |

### Why DOCX always bakes light theme

1. **Word lacks theme awareness.** Word documents do not have a
   `data-theme` attribute or a "dark mode" rendering pipeline.
   Recipients see whatever colors are inlined.
2. **Recipients typically print or share.** Light backgrounds match
   printer paper and Maccabi's corporate template defaults.
3. **Eliminates a class of theme-leakage bugs.** The `buildHtmlDocument`
   call with `{forLightTheme: true}` strips the
   `html[data-theme="dark"]` CSS rule from the embedded `<style>` AND
   forces `data-theme="light"` on the root `<html>`. Any non-inlined
   `var()` therefore resolves against `:root` light values, never
   stale dark values left behind by the rewriter.

### `.md` exports remain unstyled

Table styling is a **rendering-time** concern. The source markdown
returned by `Export .md` is the raw pipe-table syntax with no inline
HTML. Styling is re-applied automatically on the next render in any
viewer that opens the file.

### Known browser / Word differences

| Engine | Behavior | Mitigation |
|--------|----------|------------|
| Modern browsers (Chrome 49+, Firefox 31+, Safari 9.1+) | `var()`, `:nth-child`, `:where()`, `:has()` all work natively | None needed — viewer + `.html` export render correctly |
| Word 2016/2019/2021 desktop | Ignores CSS Custom Properties; `:nth-child` unreliable; treats logical padding (`padding-inline`) as unknown | DOCX rewriter pre-bakes literal hex values + pre-bakes zebra inline + emits only physical padding shorthand |
| Word for the Web | Mostly matches desktop; `:nth-child` slightly more reliable | Inline pre-bake is defensive but doesn't hurt |
| Outlook (style-stripping email clients) | Strips `<style>` blocks; preserves inline `style` attributes | `.html` export ALSO pre-bakes zebra inline so the table reads correctly when pasted into email |
| LibreOffice Writer | Honors `border-collapse:collapse` correctly; `background-clip:padding-box` respected | None — same DOCX output works |
| Apple Pages (via `.docx` import) | Tolerates inline styles; `background-clip` respected | None — same DOCX output works |
| `:has()` (Firefox ESR <121) | Cell-level `code-only` detection via `:has()` is unavailable | Renderer's structural detection tags `class="code-only"` — viewer works without `:has()` |

### Limitations

- **Header row repetition across page breaks** in DOCX is not
  enabled. `html-docx-js` does not emit `<w:tblHeader/>` — reviewers
  must turn on "Repeat as header row at the top of each page" in
  Word's Table Properties dialog manually.
- **Very wide tables (>10 columns)** may exceed page margins in
  Word. Future enhancement: detect overwide tables in the rewriter
  and emit `colgroup` widths with `table-layout:fixed`.
- **Nested tables** are passed through but may flatten in older Word
  versions (Word 2016/2019). The rewriter applies `width:auto` and
  skips zebra on inner tables to mitigate visual conflicts; for
  reliable nested-table rendering, use the `.html` export.
- **Merged cells (`rowspan`/`colspan` >1)** carry a neutral white
  background instead of the row zebra, so the merged cell reads
  consistently across all visual rows it spans.

---

## What the viewer enforces

Per the MRP (see `Agents/shared/multilingual_rendering_protocol.yaml`):

| Rule | Enforcement |
|------|-------------|
| **MRP_001** Code always LTR | `<pre>` / `<code>` carry `direction: ltr; unicode-bidi: isolate`. |
| **MRP_002** Explicit paragraph direction | Renderer injects `dir="auto"` on every block. |
| **MRP_003** Identifier isolation | Inline backticks wrap to `<bdi><code>…</code></bdi>`. |
| **MRP_004** No mixed-direction cells | Code-only cells force LTR; mixed cells trigger MRP_VC_003. |
| **MRP_005** No legacy bidi controls | Source-level check (MRP_VC_001); viewer renders them visibly if present. |
| **MRP_006** Markup over controls | No `\u202x` codepoints emitted by the renderer. |
| **MRP_007** Careful language per language | Source-level check (MRP_VC_008); viewer does not enforce. |
| **FP_005** No bare URLs | Marked autolink disabled — URLs must be backticked. |

---

## Export pipeline

The viewer ships three exporters. All three run **entirely in the
browser** — nothing leaves the page, no server round-trip, works
offline once the dependencies have been vendored (see "Vendoring
procedure" below).

| Exporter | Library | Output | Notes |
|----------|---------|--------|-------|
| `.md`   | (none) | UTF-8 source markdown | Round-trips the file you loaded. MIME `text/markdown;charset=utf-8`. |
| `.html` | (none) | Self-contained HTML with all viewer CSS inlined | Pixel-equivalent to the on-screen rendering. Safe to open from `file://` in any browser. |
| `.docx` | [`html-docx-js`](https://github.com/evidenceprime/html-docx-js) v0.3.1 (SRI-pinned) | Word `.docx` (zip of `[Content_Types].xml`, `word/document.xml`, `word/afchunk.mht`, relationships) | Uses Word's altChunk mechanism; pre-export DOM rewriting compensates for the library's known Hebrew/RTL gaps (see "Adversarial mitigations" below). |

### Filename convention

For an input named `RK1_PHARMACY_JOURNAL_README.md`, exports are named
`RK1_PHARMACY_JOURNAL_README.{md,html,docx}` — the source extension is
stripped and the target extension is appended explicitly. We never
trust the browser to derive the extension from the MIME type because:

- **Safari** rewrites `.md` to `.txt` (treats unknown `text/*` as plain
  text for download).
- **Windows hide-known-extensions** can double-extend (`foo.docx.docx`).
- **NTFS** rejects filenames over 255 UTF-16 code units once the
  Downloads-folder prefix is added by the browser.

The filename builder applies a deterministic sanitization pipeline:

1. NFC-normalize so combining Hebrew marks become composed code points.
2. Replace Windows-reserved characters (`\ / : * ? " < > |`) and control
   characters with `_`.
3. Collapse runs of `_`.
4. Trim trailing dots and spaces (Windows path policy).
5. Truncate to 120 UTF-16 code units **before** appending the extension.
6. Fallback to `cidra-document-${Date.now()}` when the title is empty.

Hebrew filenames are preserved verbatim through this pipeline — e.g.
`רוקחות_פרק_1.docx` survives all six steps. Cross-OS testing has
confirmed that Chrome on Windows respects the `download` attribute for
Hebrew filenames; on Safari rename to `.docx` if the browser drops the
extension.

### Adversarial mitigations folded into the export pipeline

The full adversarial review covered twelve issues across the
`export-edge-cases` and `hebrew-in-docx` lenses. The critical and high
findings are addressed inline below; medium and low findings are
documented under "Export limitations" or deferred with explicit
rationale.

| Adversarial finding | Severity | Status | Mitigation |
|---------------------|----------|--------|------------|
| `dir="rtl"` not translated to `<w:bidi/>` by html-docx-js | critical | **mitigated** | Pre-export DOM rewriter inlines `style="direction:rtl;text-align:right"` on every `dir=rtl` block (and resolves `dir=auto` to a concrete value by first-strong-character lookup). Word honors inline CSS more reliably than the `dir` attribute. Verified end-to-end: a 7 KB Hebrew README round-trips to a 38 KB `.docx` with 51 inline `direction:rtl` declarations in the `afchunk.mht` payload. |
| `<bdi>` tags dropped by html-docx-js | high | **mitigated** | Pre-export DOM rewriter wraps the text content of every leaf `<bdi>` with Unicode FIRST STRONG ISOLATE (U+2068) and POP DIRECTIONAL ISOLATE (U+2069). The isolation survives even when the `<bdi>` tag itself is stripped, because the encoding is now at the text-run level. |
| Mermaid SVG dropped by altChunk above ~2 MB | critical | **partially mitigated** | Pre-export DOM rewriter serializes every inline `<svg>` as a `data:image/svg+xml;base64,...` URI on an `<img>` (with explicit `width`/`height`). Full PNG rasterization (which would survive more reliably than SVG) is **deferred** because it requires an async canvas pass that would restructure the export to a Promise pipeline; the comment in `viewer.html` flags the upgrade path. Fallback: when SVG serialization throws, a visible "[Diagram omitted — view HTML export]" marker is inserted so the loss is never silent. |
| Double-click race triggers two concurrent passes | high | **mitigated** | `State.isExporting` boolean held in module state. `beginExport()` returns `false` on re-entry; `endExport()` runs in a `finally` block that resets the flag and revokes the `URL.createObjectURL` blob. Visually, all three export buttons receive `aria-disabled="true"` + `pointer-events:none` for the duration, so even assistive-tech users cannot fire a second pass. |
| Filename construction does not defend Hebrew / NTFS / Safari | high | **mitigated** | See "Filename convention" above. |
| Empty document export produces blank `.docx` | high | **mitigated** | Pre-flight check requires `State.lastRawMd != null` AND `#output` has non-whitespace text AND at least one block-level child. Otherwise the export button is disabled (and a defensive `Banner.warning("export-empty", ...)` fires if a programmatic call somehow reaches the handler). |
| 10 MB document near cap exhausts memory | high | **partially mitigated** | A warning banner ("Large document — export may take 10-30 seconds and use significant memory") fires when source markdown exceeds 5 MB. **Full Web Worker offload is deferred** because the current viewer architecture is a single IIFE; restructuring to a worker pipeline is a larger change. The hard 10 MB intake cap (`HARD_MAX` in `loadFile`) limits worst-case heap pressure. |
| `.md` MIME `text/plain` causes Safari to rename to `.txt` | medium | **mitigated** | Explicit `Blob({type: "text/markdown;charset=utf-8"})`. The Safari-specific data-URI workaround is **deferred** (warn the user via the README; no UA-sniff). |
| Theme toggle mid-export produces half-themed file | low | **mitigated** | The Theme button is disabled during export (`isExporting` flag). Additionally, the export clone gets inline styles applied during `prepareCloneForDocxExport` so the resulting `.docx` is self-contained styling-wise regardless of which theme was live at clone time. |
| `'Render anyway'` content propagates into exported file | low | **mitigated** | `State.renderedUnsanitized` tracks whether the current render bypassed DOMPurify. Before any export, `confirmUnsafeIfNeeded(kind)` calls `window.confirm` and aborts on cancel. The user has to actively re-acknowledge the propagation risk. |
| Embedded `data:` URI images survive HTML export poorly | medium | **deferred** | The single-file HTML export inlines `data:` URIs (current behavior). Split-button "folder ZIP with assets" mode is **deferred** because it requires JSZip as another dependency. |
| Mixed-direction `<bdi>` / `<pre dir=ltr>` containing Hebrew | medium | **partially mitigated** | The DOM rewriter handles `<bdi>` (Unicode isolates) and `<pre>` blocks (inline `style="font-family:Consolas;background:#f6f8fa"`). Per-Hebrew-run `<w:rtl/>` injection inside code blocks would require post-processing the DOCX zip; **deferred** — document the limitation in "Export limitations". |
| Mermaid lazy-load fails offline mid-render | medium | **deferred** | The viewer does not currently lazy-load Mermaid; SVGs in source documents are static. If a future version adds dynamic Mermaid rendering, the `navigator.onLine` detection + static bundle plan in the adversarial review applies. |
| Hebrew filenames lose visual order on Windows title bars | low | **deferred** | The download attribute receives the sanitized Hebrew filename verbatim; OS-level title-bar rendering depends on the locale. No client-side fix is possible from a `Blob` download anchor; documented under "Export limitations". |

### Export limitations

- **Per-run `<w:rtl/>` injection** for Hebrew runs inside code blocks
  is not performed. Hebrew comments inside an LTR code block are
  wrapped in `<bdi dir="rtl">` in the preview, but the DOCX export
  preserves only the inline CSS direction — Word's complex-script font
  binding falls back to its default for Hebrew characters. If you need
  precise code-block Hebrew rendering in Word, prefer the `.html`
  export and open it via Word's "Open in Word" dialog.
- **Mermaid diagrams** are exported as inline SVG data URIs. Word 2016+
  generally renders these via altChunk; older Word versions or Word
  for Mac may render the diagram region as a blank box. Until full
  PNG rasterization lands, fall back to the `.html` export for
  documents whose primary content is diagrammatic.
- **Section-level `<w:bidi/>`** (page gutter, page-number position) is
  NOT injected. The document body is right-aligned via inline CSS, but
  the section properties remain LTR. For print-bound Hebrew documents,
  open the `.docx` and apply Word's "Right-to-left document" toggle
  manually.

---

## Encoding requirements

The viewer detects BOM-marked encodings and decodes them:

| BOM | Encoding | Action |
|-----|----------|--------|
| `EF BB BF` | UTF-8 with BOM | Decoded as UTF-8; BOM stripped. |
| `FF FE` | UTF-16 LE | Decoded; warning shown. |
| `FE FF` | UTF-16 BE | Decoded; warning shown. |
| (none) | UTF-8 (assumed) | Decoded as UTF-8 (the canonical wire format). |

If more than three replacement characters (`�`) appear in the first 4 KB
after decoding, a warning recommends re-saving as UTF-8 without BOM.

**When emitting markdown from PowerShell 5.1** (the default shell on
Windows per CLAUDE.md), use:

```powershell
[System.IO.File]::WriteAllText(
    $path, $content, [System.Text.UTF8Encoding]::new($false))
```

— not `Out-File`, which defaults to UTF-16 LE with BOM. PowerShell 7
users can use `Out-File -Encoding utf8NoBOM`.

---

## CDN dependencies

All loaded over `https://` from jsDelivr with **Subresource Integrity
(SRI) hashes** pinned in the `integrity` attribute. SRI failures are
caught by both per-script `onerror` handlers and a global capture-phase
`error` listener installed before the `<script defer>` chain runs.

| Library | Version | SRI shape | Purpose | Failure mode |
|---------|---------|-----------|---------|--------------|
| `marked` | 5.1.2 | sha384 | Markdown parser. **Pinned** to v5 because the positional renderer API used here was replaced with a token-object API in v6+. | **Floor**: without this, the viewer shows an empty-state banner — UI still works. |
| `dompurify` | 3.0.11 | sha384 | HTML sanitizer. Configured with `ALLOWED_URI_REGEXP` plus an `afterSanitizeAttributes` hook that strips `javascript:` / `data:` from links and iframes. | **Security floor**: missing → rendering is refused unless the user opts in per-file via a banner action. |
| `highlight.js` (core) | 11.9.0 | sha384 | Syntax highlighting (browser bundle, loaded from `@highlightjs/cdn-assets`). | Missing → markdown renders, code blocks become plain `<pre><code>`. Warning banner shown. |
| `highlight.js` grammars: c, cpp, sql, javascript, python, yaml, json, xml | 11.9.0 | sha384 | Per-language tokenizers. | Missing → that language degrades to plaintext silently; aggregate warning banner lists which languages failed. |
| `highlightjs-cobol` | 0.3.1 | sha384 | COBOL grammar. | Same as other grammars. |
| `html-docx-js` | 0.3.1 | sha384 | DOCX export (Word's altChunk-based HTML embed). The library is functionally complete-but-unmaintained; we use it because no maintained alternative produces a single-file vanilla-JS bundle. | Missing → Export `.docx` button stays disabled with an explanatory tooltip + warning banner. Export `.md` and Export `.html` continue to work. |
| RPG, CL, DDS, ABAP | inline | n/a | Minimal stub grammars registered in the viewer script (no external CDN). | Registered only after hljs core loads. |

### Progressive degradation matrix

| Scenario | UI controls work? | Markdown renders? | Syntax colored? | Exports work? | Notes |
|----------|-------------------|-------------------|-----------------|---------------|-------|
| All deps load | yes | yes | yes | all three | Happy path, no banners. |
| `highlight.js` blocked | yes | yes | no | all three | Warning banner: "Syntax highlighter unavailable". |
| One grammar blocked (e.g. cobol) | yes | yes | partial | all three | Aggregate "Some syntax grammars unavailable" banner. |
| `DOMPurify` blocked | yes | refused by default | n/a | depends on "Render anyway" | Error banner with **Render anyway (unsafe)** action, scoped to the currently-loaded file. Export of unsafe content triggers a confirm dialog. |
| `marked` blocked | yes | no | no | none (gated on doc loaded) | Error banner with link to README; UI buttons still respond. |
| `html-docx-js` blocked | yes | yes | yes | `.md` + `.html` only | Warning banner; `.docx` button disabled with tooltip "Use HTML export and open in Word". |
| **All CDN blocked** | yes | no (until vendor) | no | none | Banners chained: info "Trying ./vendor/..." → final status. Toolbar remains clickable. |

If a CDN script does load but executes incorrectly (proxy injection,
SRI mismatch, or a tampered grammar that parse-fails), the global
capture-phase `error` listener flips the failure registry for that
`data-dep` even when the inline `onerror` attribute does not fire.

---

## Offline / corporate firewall (vendoring)

When jsDelivr is blocked by firewall, browser privacy settings, or
Brave/Firefox ETP shields, the viewer auto-detects the failure and
attempts a local `./vendor/` fallback. The banner sequence is:

1. **Info banner**: "Some libraries failed to load from CDN. Trying
   local `./vendor/` copies..." (or "Browser privacy settings or
   extensions may be blocking cdn.jsdelivr.net..." when the script
   load was silent).
2. The viewer attempts to inject `<script src="./vendor/marked.min.js">`,
   `<script src="./vendor/purify.min.js">`, `<script src="./vendor/highlight.min.js">`
   in parallel for any missing library.
3. **Final banner**: success (banners clear) OR error/warning per
   library that is still missing.

### Vendoring procedure

Create a `vendor/` folder next to `viewer.html` and drop these
**four files** (file names are load-bearing — the viewer expects
exactly these names):

| Save as | Download from |
|---------|---------------|
| `vendor/marked.min.js`     | `https://cdn.jsdelivr.net/npm/marked@5.1.2/marked.min.js` |
| `vendor/purify.min.js`     | `https://cdn.jsdelivr.net/npm/dompurify@3.0.11/dist/purify.min.js` |
| `vendor/highlight.min.js`  | `https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11.9.0/highlight.min.js` |
| `vendor/html-docx.min.js`  | `https://cdn.jsdelivr.net/npm/html-docx-js@0.3.1/dist/html-docx.min.js` |

PowerShell one-liner (the default shell on Windows per CLAUDE.md):

```powershell
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path vendor | Out-Null
$dl = @{
  'marked.min.js'    = 'https://cdn.jsdelivr.net/npm/marked@5.1.2/marked.min.js'
  'purify.min.js'    = 'https://cdn.jsdelivr.net/npm/dompurify@3.0.11/dist/purify.min.js'
  'highlight.min.js' = 'https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11.9.0/highlight.min.js'
  'html-docx.min.js' = 'https://cdn.jsdelivr.net/npm/html-docx-js@0.3.1/dist/html-docx.min.js'
}
foreach ($k in $dl.Keys) {
  Invoke-WebRequest -Uri $dl[$k] -OutFile (Join-Path 'vendor' $k)
}
```

Bash equivalent (Git Bash / WSL):

```bash
mkdir -p vendor
curl -L -o vendor/marked.min.js    https://cdn.jsdelivr.net/npm/marked@5.1.2/marked.min.js
curl -L -o vendor/purify.min.js    https://cdn.jsdelivr.net/npm/dompurify@3.0.11/dist/purify.min.js
curl -L -o vendor/highlight.min.js https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11.9.0/highlight.min.js
curl -L -o vendor/html-docx.min.js https://cdn.jsdelivr.net/npm/html-docx-js@0.3.1/dist/html-docx.min.js
```

You do **not** need to vendor the per-language hljs grammars or the
highlight.js CSS themes — they degrade silently to plaintext + UA
default styles. Vendor them only if you frequently view code in those
languages and want the colored output offline.

### Security note on vendor files

The `./vendor/` fallback path loads scripts **without SRI hashes**
because the operator may choose a different upstream mirror. This is a
deliberate trade-off: SRI on the CDN path protects against the
common-case (live network MITM), and the vendor path is only reached
when the CDN path failed, at which point you are choosing to trust the
local file you placed in `./vendor/`. Treat that folder as a
write-controlled location — anyone who can write to it can change what
the viewer renders.

### Watchdog timeout

If the deferred CDN scripts stall (slow network, captive portal, TCP
hang) the viewer's boot watchdog fires at 8 seconds, marks any
not-yet-loaded scripts as failed, and proceeds to the vendor fallback
path. The toolbar buttons are wired before this timer fires — they
always work.

---

## Integration with CIDRA workflow

The viewer is the **canonical preview surface** for CIDRA-authored
documentation. Wire-in points:

- `THE_DOCUMENTER_AGENT` reads
  `Agents/shared/multilingual_rendering_protocol.yaml` as a mandatory
  preprocessing step (see `agent_specification.md` and
  `skills.yaml#DOC_INT_015`).
- `/document:validate` runs the `validation_checks` from the MRP as
  part of the 100-point validation gate.
- When the documenter completes a screen, the README in the screen's
  folder includes a one-line pointer:
  `Open in CIDRA viewer: Protocols/viewer/viewer.html`.

---

## Known limitations

- **`:has()` selector** fallback: Firefox ESR before 121 does not
  support `:has()`. The viewer adds `class="code-only"` to such cells
  via JS regardless, so code-only cell styling still works on older
  Firefox.
- **Word / Outlook paste** does not preserve `<bdi>` tags. Pasting
  rendered documentation into MS Word loses the BiDi isolation and the
  identifiers may collide with adjacent Hebrew punctuation. The viewer
  cannot fix this; document Word-paste as an unsupported consumption
  path. Use the rendered viewer as the primary surface.
- **Mermaid SVG with raw `<text>` nodes** containing Hebrew renders the
  Hebrew reversed character-by-character (LTR by SVG default). The
  documenter agent must pre-render Mermaid with `htmlLabels: true` (see
  MRP `mermaid_diagrams` section and MRP_VC_012). The viewer cannot
  fix this post-hoc because the SVG arrives base64-encoded.
- **`file://` security**: the viewer cannot fetch other files from
  disk — only files opened via picker or drag-drop are loaded. This
  is a browser security policy, not a viewer limitation.

---

## Version history

| Version | Date | Notes |
|---------|------|-------|
| 1.4.0 | 2026-06-01 | Table styling overhaul (MRP v1.2.0): GitHub-grade visual look with dark slate-700 header, subtle slate-50 zebra body, slate-300/400 borders, 8x14 padding. New `--tbl-*` CSS variables driving all three surfaces (viewer / `.html` / `.docx`); `prepareCloneForDocxExport` extended with `inlineTableStylesForDocx` that resolves every var() to a literal hex (Word cannot read `var()`). `.docx` always bakes the light theme (`buildHtmlDocument({forLightTheme:true})` strips the dark-theme block AND forces `data-theme="light"`). Critical+high adversarial fixes folded in: dark-theme code-chip contrast lift, `background-clip:padding-box` to prevent Word/LibreOffice padding divergence, merged-cell zebra neutralization, nested-table double-paint prevention, RTL-text-align specificity raised above `text-align:start`, `unicode-bidi:isolate-override` on code-only cells to defeat Hebrew-in-code re-flipping, dropped table-level border to avoid Word's double-frame quirk, deduplicating `appendInlineStyle`. Playwright Scenario 7 with 31 assertions (viewer light + dark + RTL, HTML export style block + pre-baked zebra, DOCX literal hex + no var() + no dark theme leak). |
| 1.3.0 | 2026-06-01 | Export pipeline added: `Export .md` / `Export .html` / `Export .docx`. SRI-pinned `html-docx-js` v0.3.1 with `./vendor/html-docx.min.js` fallback. Critical+high adversarial fixes folded in: `State.isExporting` double-click guard, NFC + reserved-char + 120-UTF16 filename sanitization with Hebrew preservation, empty-document gating, large-document (>5MB) warning, `<bdi>` content wrapped in U+2068/U+2069 isolates before DOCX serialization, inline `direction:rtl` style on every `dir=rtl` block (Word honors inline CSS where it ignores the `dir` attribute), inline SVG → `data:image/svg+xml` substitution for Mermaid (with visible fallback marker), Theme button disabled during export (mid-export race), `Render anyway` content propagation confirm dialog, toast confirmation, Dir button label synced to live `html[dir]` on boot, Playwright suite extended with Scenarios 5 (all-buttons-respond) + 6 (round-trip exports), 51 new assertions. |
| 1.2.0 | 2026-05-31 | Resilience redesign: SRI hashes on every CDN URL, defer + capture-phase error listener, per-library failure registry, `./vendor/` fallback for `marked` / `dompurify` / `highlight.js`, structured Banner DOM (no innerHTML), per-file `Render anyway` opt-in (scoped to current file, cleared on every load), 8s boot watchdog, CSP meta tag, DOMPurify `afterSanitizeAttributes` hook stripping `javascript:`/`data:` on `<a href>` and `<iframe src>`, footer `dir="ltr"` (UAX#9 N1 trailing-period fix), toolbar `dir="ltr" lang="en"`, banner host `dir="ltr"` + sticky, bilingual banner messages (en + he), title `lang="en" dir="ltr"`. |
| 1.1.0 | 2026-05-31 | Critical+high adversarial fixes folded in: pinned marked to v5 (positional API), browser-bundle highlight.js, valid stub grammars, autolink disabled, BOM detection, front-matter parsing, blockquote dir fix, ul/ol re-declaration, DOMPurify v3 `ALLOWED_URI_REGEXP`, structural tablecell detection, Hebrew mono fallbacks, inline-style empty state removed. |
| 1.0.0 | 2026-05-30 | Initial viewer aligned with MRP v1.0. |

---

## License / attribution

Part of the B+CIDRA framework. Maintained as `Protocols/viewer/`.
For questions about rendering decisions, see the MRP
(`Agents/shared/multilingual_rendering_protocol.yaml`) — it is the
source of truth.
