# CIDRA Documentation Viewer

A single-file, dependency-free (CDN-loaded) HTML viewer for CIDRA-authored
Markdown documentation. Implements the rendering contract defined in
[`Agents/shared/multilingual_rendering_protocol.yaml`](../../Agents/shared/multilingual_rendering_protocol.yaml)
(MRP) v1.1.0.

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
| `Dir: Auto / RTL / LTR` | Override document direction. `Auto` uses front-matter or first-strong heuristic. |
| `Theme: Light / Dark` | Swaps page CSS variables AND the highlight.js stylesheet. |
| `Mirror HE Comments: Off / On` | When on, Hebrew runs inside `hljs-comment` spans get a `<bdi dir="rtl">` wrapper so they read RTL inside an LTR code block. This is a **view-time preference** — it does not modify the source file. |
| `Clear` | Empties the current document. |

The file-info panel shows the loaded filename, size, and detected
encoding (UTF-8, UTF-16 LE, UTF-16 BE). A warning badge appears if the
file is not UTF-8 without BOM.

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
| RPG, CL, DDS, ABAP | inline | n/a | Minimal stub grammars registered in the viewer script (no external CDN). | Registered only after hljs core loads. |

### Progressive degradation matrix

| Scenario | UI controls work? | Markdown renders? | Syntax colored? | Notes |
|----------|-------------------|-------------------|-----------------|-------|
| All deps load | yes | yes | yes | Happy path, no banners. |
| `highlight.js` blocked | yes | yes | no | Warning banner: "Syntax highlighter unavailable". |
| One grammar blocked (e.g. cobol) | yes | yes | partial | Aggregate "Some syntax grammars unavailable" banner. |
| `DOMPurify` blocked | yes | refused by default | n/a | Error banner with **Render anyway (unsafe)** action, scoped to the currently-loaded file. |
| `marked` blocked | yes | no | no | Error banner with link to README; UI buttons still respond. |
| **All CDN blocked** | yes | no (until vendor) | no | Banners chained: info "Trying ./vendor/..." → final status. Toolbar remains clickable. |

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
**three files** (file names are load-bearing — the viewer expects
exactly these names):

| Save as | Download from |
|---------|---------------|
| `vendor/marked.min.js`     | `https://cdn.jsdelivr.net/npm/marked@5.1.2/marked.min.js` |
| `vendor/purify.min.js`     | `https://cdn.jsdelivr.net/npm/dompurify@3.0.11/dist/purify.min.js` |
| `vendor/highlight.min.js`  | `https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11.9.0/highlight.min.js` |

PowerShell one-liner (the default shell on Windows per CLAUDE.md):

```powershell
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path vendor | Out-Null
$dl = @{
  'marked.min.js'    = 'https://cdn.jsdelivr.net/npm/marked@5.1.2/marked.min.js'
  'purify.min.js'    = 'https://cdn.jsdelivr.net/npm/dompurify@3.0.11/dist/purify.min.js'
  'highlight.min.js' = 'https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11.9.0/highlight.min.js'
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
| 1.2.0 | 2026-05-31 | Resilience redesign: SRI hashes on every CDN URL, defer + capture-phase error listener, per-library failure registry, `./vendor/` fallback for `marked` / `dompurify` / `highlight.js`, structured Banner DOM (no innerHTML), per-file `Render anyway` opt-in (scoped to current file, cleared on every load), 8s boot watchdog, CSP meta tag, DOMPurify `afterSanitizeAttributes` hook stripping `javascript:`/`data:` on `<a href>` and `<iframe src>`, footer `dir="ltr"` (UAX#9 N1 trailing-period fix), toolbar `dir="ltr" lang="en"`, banner host `dir="ltr"` + sticky, bilingual banner messages (en + he), title `lang="en" dir="ltr"`. |
| 1.1.0 | 2026-05-31 | Critical+high adversarial fixes folded in: pinned marked to v5 (positional API), browser-bundle highlight.js, valid stub grammars, autolink disabled, BOM detection, front-matter parsing, blockquote dir fix, ul/ol re-declaration, DOMPurify v3 `ALLOWED_URI_REGEXP`, structural tablecell detection, Hebrew mono fallbacks, inline-style empty state removed. |
| 1.0.0 | 2026-05-30 | Initial viewer aligned with MRP v1.0. |

---

## License / attribution

Part of the B+CIDRA framework. Maintained as `Protocols/viewer/`.
For questions about rendering decisions, see the MRP
(`Agents/shared/multilingual_rendering_protocol.yaml`) — it is the
source of truth.
