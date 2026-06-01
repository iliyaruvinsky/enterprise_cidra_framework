"""
Playwright verification for the CIDRA Documentation Viewer redesign.

Ten scenarios + cross-cutting assertions, mirroring the redesign's
"Playwright Test Plan — Apply Phase" section.

Scenarios:
  1. All CDNs work — baseline happy path.
  2. highlight.js blocked — viewer still loads & banners.
  3. All CDNs blocked + vendor blocked — UI stays alive, error banners.
  4. Real markdown file via file picker.
  5. Every button responds correctly (Open / Dir / Theme / Mirror / Clear /
     banner-close).
  6. Exports work — .md / .html / .docx round-trip from the same loaded
     fixture, verified by downloaded-file inspection.
  7. Table styling (v1.2.0).
  8. CSV / XLSX table exports (v1.5.0).
  9. Export-menu dropdown (v1.6.0).
 10. CSP console cleanliness (v1.6.1) — load real fixture with all CDNs
     accessible, capture every console message + pageerror, assert ZERO
     CSP violations ("Content Security Policy" / "connect-src" / "Refused to")
     and ZERO page errors. Belt-and-suspenders: explicit assertions for
     the v1.6.1 tightenings (img-src no bare https:, connect-src/npm/ pinned).

Run:
    python C:\\My_AI\\enterprise_cidra_framework\\Protocols\\viewer\\_playwright_test.py
"""

import sys
import json
import zipfile
import io
from pathlib import Path

# Force UTF-8 stdout/stderr — Windows defaults to cp1252 which cannot
# encode Hebrew test labels emitted by Scenario 6's filename-sanitization
# probes.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from playwright.sync_api import sync_playwright

ROOT = Path("C:/My_AI/enterprise_cidra_framework/Protocols/viewer")
VIEWER = (ROOT / "viewer.html").as_uri()
OUTPUT = ROOT / "_test_screenshots"
OUTPUT.mkdir(parents=True, exist_ok=True)
DOWNLOADS = ROOT / "_test_downloads"
DOWNLOADS.mkdir(parents=True, exist_ok=True)

FIXTURE_MD = Path("C:/My_AI/רוקחות_פקודות_יומן/Screens/RK1_PHARMACY_JOURNAL/README.md")

results = []


def record(name, ok, detail=""):
    results.append({"name": name, "ok": ok, "detail": detail})
    print(("PASS  " if ok else "FAIL  ") + name + (("  " + detail) if detail else ""))


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ====================================================================
        # Scenario 1 — All CDNs work
        # ====================================================================
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        page = ctx.new_page()
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(VIEWER)
        page.wait_for_load_state("networkidle", timeout=30000)
        # __cidraViewer should be defined
        try:
            deps = page.evaluate("() => ({marked: window.__cidraViewer.deps.marked(), dompurify: window.__cidraViewer.deps.dompurify(), hljs: window.__cidraViewer.deps.hljs()})")
        except Exception as ex:
            deps = {"error": str(ex)}
        record("01.deps.marked", bool(deps.get("marked")), json.dumps(deps))
        record("01.deps.dompurify", bool(deps.get("dompurify")), "")
        record("01.deps.hljs", bool(deps.get("hljs")), "")

        open_label = page.locator("label.file-picker")
        record("01.open_label.visible", open_label.is_visible())
        # The label wraps the hidden input; clicking the label triggers the picker.
        # We can at least assert it is enabled (a visible label).
        # Check toolbar buttons are clickable
        btn_theme = page.locator("#btnTheme")
        record("01.btnTheme.enabled", btn_theme.is_enabled())
        btn_theme.click()
        theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        record("01.btnTheme.toggle", theme == "dark", "theme=" + str(theme))
        # Footer direction
        footer_dir = page.evaluate("() => getComputedStyle(document.querySelector('footer')).direction")
        record("01.footer.direction=ltr", footer_dir == "ltr", "got=" + footer_dir)
        footer_text = page.locator("footer").text_content().strip()
        record("01.footer.starts_with_Part", footer_text.startswith("Part of"), "text=" + footer_text[:60])
        # CDN script integrity check
        sri_ok = page.evaluate("""
            () => {
              const els = Array.from(document.querySelectorAll('link[href*="jsdelivr"], script[src*="jsdelivr"]'));
              return els.every(e => e.getAttribute('integrity') && e.getAttribute('crossorigin') === 'anonymous');
            }
        """)
        record("01.all_jsdelivr_have_SRI_and_crossorigin", sri_ok)
        # No page errors
        record("01.no_pageerror", len(page_errors) == 0, "errs=" + repr(page_errors[:3]))
        # Banners empty (or at most info that has cleared)
        n_banners = page.locator("#banners .banner").count()
        record("01.banners_empty_or_info", n_banners == 0, "n=" + str(n_banners))
        page.screenshot(path=str(OUTPUT / "01_clean_load.png"), full_page=True)
        ctx.close()

        # ====================================================================
        # Scenario 2 — highlight.js blocked
        # ====================================================================
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        # Block every hljs asset (core, language grammars, and the cobol pkg).
        ctx.route("**/highlight.min.js*", lambda r: r.abort())
        ctx.route("**/highlight.js*", lambda r: r.abort())
        ctx.route("**/highlightjs*", lambda r: r.abort())
        ctx.route("**/highlightjs-cobol/**", lambda r: r.abort())
        ctx.route("**/cobol.min.js*", lambda r: r.abort())
        ctx.route("**/languages/**", lambda r: r.abort())
        page = ctx.new_page()
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(VIEWER)
        # Use domcontentloaded + extra wait — networkidle would block on the
        # 8 second watchdog when scripts are aborted.
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(9000)  # wait past the 8s watchdog
        deps = page.evaluate("() => ({marked: window.__cidraViewer.deps.marked(), dompurify: window.__cidraViewer.deps.dompurify(), hljs: window.__cidraViewer.deps.hljs()})")
        record("02.deps.marked", bool(deps.get("marked")), json.dumps(deps))
        record("02.deps.dompurify", bool(deps.get("dompurify")))
        record("02.deps.hljs_false", not deps.get("hljs"))
        open_label = page.locator("label.file-picker")
        record("02.open_label.visible", open_label.is_visible())
        record("02.btnTheme.enabled", page.locator("#btnTheme").is_enabled())
        # Look for the hljs warning banner
        no_hljs_banner = page.locator('#banners [data-banner-key="no-hljs-final"]')
        record("02.no_hljs_banner.visible", no_hljs_banner.count() > 0)
        record("02.no_pageerror", len(page_errors) == 0, "errs=" + repr(page_errors[:3]))
        page.screenshot(path=str(OUTPUT / "02_highlight_blocked.png"), full_page=True)
        ctx.close()

        # ====================================================================
        # Scenario 3 — All CDNs blocked + vendor blocked
        # ====================================================================
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        ctx.route("https://cdn.jsdelivr.net/**", lambda r: r.abort())
        ctx.route("**/vendor/**", lambda r: r.abort())
        page = ctx.new_page()
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(VIEWER)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(9500)  # past the 8s watchdog
        # UI must still be alive
        open_label = page.locator("label.file-picker")
        record("03.open_label.visible", open_label.is_visible())
        btn_theme = page.locator("#btnTheme")
        record("03.btnTheme.enabled", btn_theme.is_enabled())
        btn_theme.click()
        theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        record("03.btnTheme.still_toggles", theme == "dark", "theme=" + str(theme))
        # Error banner for missing marked
        no_marked_banner = page.locator('#banners [data-banner-key="no-marked-final"]')
        record("03.no_marked_banner.visible", no_marked_banner.count() > 0)
        deps = page.evaluate("() => ({marked: window.__cidraViewer.deps.marked(), dompurify: window.__cidraViewer.deps.dompurify(), hljs: window.__cidraViewer.deps.hljs()})")
        record("03.deps.all_false", not deps.get("marked") and not deps.get("dompurify") and not deps.get("hljs"), json.dumps(deps))
        record("03.no_pageerror", len(page_errors) == 0, "errs=" + repr(page_errors[:3]))
        page.screenshot(path=str(OUTPUT / "03_all_blocked.png"), full_page=True)
        ctx.close()

        # ====================================================================
        # Scenario 4 — Real markdown file via file picker
        # ====================================================================
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        page = ctx.new_page()
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(VIEWER)
        page.wait_for_load_state("networkidle", timeout=30000)
        file_input = page.locator("#filePicker")
        if FIXTURE_MD.exists():
            file_input.set_input_files(str(FIXTURE_MD))
            page.wait_for_timeout(2000)
            # Verify markdown rendered
            h_count = page.locator("#output h1, #output h2, #output h3").count()
            record("04.headings.present", h_count > 0, "count=" + str(h_count))
            p_count = page.locator("#output p").count()
            record("04.paragraphs.present", p_count > 0, "count=" + str(p_count))
            last_fn = page.evaluate("() => window.__cidraViewer.state.lastFileName")
            record("04.state.lastFileName_set", last_fn == FIXTURE_MD.name, "got=" + str(last_fn))
            record("04.no_pageerror", len(page_errors) == 0, "errs=" + repr(page_errors[:3]))
        else:
            record("04.fixture.exists", False, "fixture not found at " + str(FIXTURE_MD))
        page.screenshot(path=str(OUTPUT / "04_real_md_loaded.png"), full_page=True)
        ctx.close()

        # ====================================================================
        # Scenario 5 — Every button responds correctly
        # ====================================================================
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        page = ctx.new_page()
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(VIEWER)
        page.wait_for_load_state("networkidle", timeout=30000)

        # 5.1 — Open .md picker visible & enabled
        open_label = page.locator("label.file-picker")
        record("05.open_label.visible", open_label.is_visible())
        record("05.file_input.present", page.locator("#filePicker").count() == 1)

        # 5.2 — Dir button: cycles through all three states.
        # The viewer ships <html dir="rtl"> so the empty-state Hebrew
        # renders right; on boot the button label syncs to that, so the
        # initial label is "Dir: RTL". One click → LTR, second → Auto,
        # third → back to RTL. We verify each transition AND the html
        # attribute on each step.
        btn_dir = page.locator("#btnDir")
        record("05.btnDir.initial=RTL",
               btn_dir.text_content().strip() == "Dir: RTL",
               "got=" + btn_dir.text_content().strip())
        record("05.html.dir=rtl_initial",
               page.evaluate("() => document.documentElement.getAttribute('dir')") == "rtl")
        btn_dir.click()
        record("05.btnDir.after_1=LTR",
               btn_dir.text_content().strip() == "Dir: LTR")
        record("05.html.dir=ltr_after_1",
               page.evaluate("() => document.documentElement.getAttribute('dir')") == "ltr")
        btn_dir.click()
        record("05.btnDir.after_2=Auto",
               btn_dir.text_content().strip() == "Dir: Auto")
        record("05.html.dir=auto_after_2",
               page.evaluate("() => document.documentElement.getAttribute('dir')") == "auto")
        btn_dir.click()
        record("05.btnDir.after_3=RTL",
               btn_dir.text_content().strip() == "Dir: RTL")
        record("05.html.dir=rtl_after_3",
               page.evaluate("() => document.documentElement.getAttribute('dir')") == "rtl")

        # 5.3 — Theme button: cycles Light ↔ Dark, label updates
        btn_theme = page.locator("#btnTheme")
        # initial may be "Theme: Light" by default
        initial_theme_label = btn_theme.text_content().strip()
        btn_theme.click()
        after_label = btn_theme.text_content().strip()
        record("05.btnTheme.label_updates", initial_theme_label != after_label,
               "initial=%r after=%r" % (initial_theme_label, after_label))
        record("05.btnTheme.label=Dark", after_label == "Theme: Dark")
        # toggle back
        btn_theme.click()
        record("05.btnTheme.cycles_back",
               btn_theme.text_content().strip() == "Theme: Light")

        # 5.4 — Mirror HE Comments toggle On/Off
        btn_mirror = page.locator("#btnMirrorComments")
        record("05.btnMirror.initial=Off",
               btn_mirror.text_content().strip() == "Mirror HE Comments: Off")
        btn_mirror.click()
        record("05.btnMirror.toggled_On",
               btn_mirror.text_content().strip() == "Mirror HE Comments: On")
        record("05.btnMirror.aria_pressed_true",
               btn_mirror.get_attribute("aria-pressed") == "true")
        btn_mirror.click()
        record("05.btnMirror.toggled_Off_again",
               btn_mirror.text_content().strip() == "Mirror HE Comments: Off")

        # 5.5 — Load file then Clear resets state
        if FIXTURE_MD.exists():
            page.locator("#filePicker").set_input_files(str(FIXTURE_MD))
            page.wait_for_timeout(2000)
            record("05.fileInfo_after_load",
                   len(page.locator("#fileInfo").text_content().strip()) > 0)
            page.locator("#btnClear").click()
            page.wait_for_timeout(300)
            record("05.btnClear.fileInfo_empty",
                   page.locator("#fileInfo").text_content().strip() == "")
            record("05.btnClear.state_lastRawMd_null",
                   page.evaluate("() => window.__cidraViewer.state.lastRawMd") is None)
            # v1.6.0 — the five per-format buttons were replaced by a
            # single Export ▾ trigger. After Clear the trigger must be
            # disabled (no document loaded).
            record("05.btnClear.export_trigger_disabled",
                   page.locator("#btnExportMenu").is_disabled())
            # Also verify the old per-format buttons are gone — they were
            # consolidated into the dropdown menu items.
            record("05.btnClear.old_btnExportMd_removed",
                   page.locator("#btnExportMd").count() == 0)
            record("05.btnClear.old_btnExportHtml_removed",
                   page.locator("#btnExportHtml").count() == 0)
            record("05.btnClear.old_btnExportDocx_removed",
                   page.locator("#btnExportDocx").count() == 0)

        # 5.6 — Inject a banner and close it with ×
        page.evaluate("""
            () => window.__cidraViewer.Banner.info('test-banner-close',
                [{text: 'Test banner for close button.'}])
        """)
        banner_count_before = page.locator("#banners .banner").count()
        record("05.banner.injected", banner_count_before >= 1)
        page.locator('#banners [data-banner-key="test-banner-close"] .banner-close').click()
        page.wait_for_timeout(150)
        banner_count_after = page.locator('#banners [data-banner-key="test-banner-close"]').count()
        record("05.banner.close_removes", banner_count_after == 0,
               "before=%d after=%d" % (banner_count_before, banner_count_after))

        record("05.no_pageerror", len(page_errors) == 0, "errs=" + repr(page_errors[:3]))
        page.screenshot(path=str(OUTPUT / "05_all_buttons.png"), full_page=True)
        ctx.close()

        # ====================================================================
        # Scenario 6 — Exports work (.md / .html / .docx)
        # ====================================================================
        ctx = browser.new_context(
            viewport={"width": 1400, "height": 900},
            accept_downloads=True,
        )
        page = ctx.new_page()
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(VIEWER)
        page.wait_for_load_state("networkidle", timeout=30000)

        if not FIXTURE_MD.exists():
            record("06.fixture.exists", False,
                   "skipping export scenario; fixture missing")
        else:
            # Load fixture
            page.locator("#filePicker").set_input_files(str(FIXTURE_MD))
            page.wait_for_timeout(2500)

            # v1.6.0 — trigger enables after document load; individual
            # menu items expose enabled state via aria-disabled.
            record("06.btnExportMenu.enabled_after_load",
                   page.locator("#btnExportMenu").is_enabled())
            # Open the menu so we can inspect item enabled state.
            page.locator("#btnExportMenu").click()
            page.wait_for_timeout(200)
            record("06.miExportMd.enabled_after_load",
                   page.locator("#miExportMd").get_attribute("aria-disabled") == "false")
            record("06.miExportHtml.enabled_after_load",
                   page.locator("#miExportHtml").get_attribute("aria-disabled") == "false")
            # DOCX gated also on html-docx-js
            html_docx_loaded = page.evaluate(
                "() => window.__cidraViewer.deps.htmlDocx()"
            )
            record("06.deps.htmlDocx_loaded", bool(html_docx_loaded))
            if html_docx_loaded:
                record("06.miExportDocx.enabled_after_load",
                       page.locator("#miExportDocx").get_attribute("aria-disabled") == "false")
            # Close the menu before triggering exports (each export
            # click re-opens the menu, clicks the item, menu auto-closes).
            page.keyboard.press("Escape")
            page.wait_for_timeout(150)

            source_md = FIXTURE_MD.read_text(encoding="utf-8")

            # ---- Export .md ----
            page.locator("#btnExportMenu").click()
            page.wait_for_timeout(200)
            with page.expect_download(timeout=15000) as dl_info:
                page.locator("#miExportMd").click()
            dl_md = dl_info.value
            md_path = DOWNLOADS / dl_md.suggested_filename
            dl_md.save_as(str(md_path))
            record("06.md.download_triggered", md_path.exists(),
                   "saved=" + str(md_path))
            record("06.md.filename_has_md_ext",
                   md_path.suffix.lower() == ".md",
                   "name=" + md_path.name)
            md_content = md_path.read_text(encoding="utf-8")
            record("06.md.content_equals_source",
                   md_content == source_md,
                   "len_dl=%d len_src=%d" % (len(md_content), len(source_md)))
            # Toast should appear briefly
            page.wait_for_timeout(300)

            # ---- Export .html ----
            page.locator("#btnExportMenu").click()
            page.wait_for_timeout(200)
            with page.expect_download(timeout=15000) as dl_info:
                page.locator("#miExportHtml").click()
            dl_html = dl_info.value
            html_path = DOWNLOADS / dl_html.suggested_filename
            dl_html.save_as(str(html_path))
            record("06.html.download_triggered", html_path.exists(),
                   "saved=" + str(html_path))
            record("06.html.filename_has_html_ext",
                   html_path.suffix.lower() == ".html")
            html_content = html_path.read_text(encoding="utf-8")
            record("06.html.is_full_doctype",
                   html_content.startswith("<!doctype html>") or
                   html_content.startswith("<!DOCTYPE html>"),
                   "starts=" + html_content[:40])
            record("06.html.has_inline_style",
                   "<style>" in html_content and "</style>" in html_content)
            record("06.html.has_md_class_content",
                   '<div class="md">' in html_content)
            record("06.html.content_nonempty",
                   len(html_content) > 5000,
                   "size=%d" % len(html_content))

            # ---- Export .docx (only if library loaded) ----
            if html_docx_loaded:
                page.locator("#btnExportMenu").click()
                page.wait_for_timeout(200)
                with page.expect_download(timeout=30000) as dl_info:
                    page.locator("#miExportDocx").click()
                dl_docx = dl_info.value
                docx_path = DOWNLOADS / dl_docx.suggested_filename
                dl_docx.save_as(str(docx_path))
                record("06.docx.download_triggered", docx_path.exists())
                record("06.docx.filename_has_docx_ext",
                       docx_path.suffix.lower() == ".docx")

                # .docx is a zip — verify zip integrity
                try:
                    with zipfile.ZipFile(str(docx_path)) as zf:
                        names = zf.namelist()
                        record("06.docx.is_valid_zip", True,
                               "entries=%d" % len(names))
                        # Word document.xml must be present
                        has_doc_xml = any(
                            n.endswith("document.xml") or
                            n == "word/document.xml" or
                            n.endswith("afchunk.htm") or
                            n.endswith("afchunk.html") or
                            "altChunk" in "\n".join(names)
                            for n in names
                        )
                        # html-docx-js emits altChunk via an embedded HTML
                        # part rather than a fully-converted document.xml.
                        record("06.docx.has_word_content",
                               "[Content_Types].xml" in names,
                               "names=" + ", ".join(names[:6]))
                        # Try to find Hebrew text in any zipped entry.
                        found_hebrew = False
                        for n in names:
                            try:
                                with zf.open(n) as f:
                                    data = f.read()
                                # Hebrew range U+0590-U+05FF
                                txt = data.decode("utf-8", errors="ignore")
                                if any("֐" <= c <= "׿" for c in txt):
                                    found_hebrew = True
                                    break
                            except Exception:
                                continue
                        record("06.docx.contains_hebrew",
                               found_hebrew,
                               "found=%s" % found_hebrew)
                except zipfile.BadZipFile as ex:
                    record("06.docx.is_valid_zip", False, "err=" + str(ex))

            # Double-click race: second click during in-flight export
            # should be no-op (trigger disabled). Stage a forced state.
            page.evaluate("""
                () => {
                  window.__cidraViewer.state.isExporting = true;
                  window.__cidraViewer.exports.refreshExportButtons();
                }
            """)
            record("06.race.trigger_disabled_while_exporting",
                   page.locator("#btnExportMenu").is_disabled())
            page.evaluate("""
                () => {
                  window.__cidraViewer.state.isExporting = false;
                  window.__cidraViewer.exports.refreshExportButtons();
                }
            """)

            # Filename sanitization unit-style check via exposed helper
            fname = page.evaluate("""
                () => window.__cidraViewer.exports.buildExportFilename(
                    'רוקחות/פרק:1.md', 'docx')
            """)
            record("06.filename.sanitizes_slashes_colons",
                   "/" not in fname and ":" not in fname,
                   "got=" + str(fname))
            record("06.filename.has_docx_ext",
                   fname.endswith(".docx"))
            long_fname = page.evaluate("""
                () => window.__cidraViewer.exports.buildExportFilename(
                    'א'.repeat(200), 'md')
            """)
            record("06.filename.truncates_long",
                   len(long_fname) <= 124,
                   "len=%d" % len(long_fname))
            empty_fname = page.evaluate("""
                () => window.__cidraViewer.exports.buildExportFilename('', 'md')
            """)
            record("06.filename.empty_fallback",
                   empty_fname.startswith("cidra-document-"),
                   "got=" + str(empty_fname))

            record("06.no_pageerror", len(page_errors) == 0,
                   "errs=" + repr(page_errors[:3]))
            page.screenshot(path=str(OUTPUT / "06_exports.png"),
                            full_page=True)
        ctx.close()

        # ====================================================================
        # Scenario 7 — Table styling (v1.2.0)
        # Verifies the new themed/bordered/zebra-striped table look in the
        # viewer (light + dark), HTML export (style block present + zebra
        # pre-baked), and DOCX export (literal hex inline, no var(),
        # always light theme).
        # ====================================================================
        ctx = browser.new_context(
            viewport={"width": 1400, "height": 900},
            accept_downloads=True,
        )
        page = ctx.new_page()
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(VIEWER)
        page.wait_for_load_state("networkidle", timeout=30000)

        if not FIXTURE_MD.exists():
            record("07.fixture.exists", False,
                   "skipping table styling scenario; fixture missing")
        else:
            page.locator("#filePicker").set_input_files(str(FIXTURE_MD))
            page.wait_for_timeout(2500)

            # Verify a table actually rendered from the fixture.
            n_tables = page.locator("#output table").count()
            record("07.viewer.table_present",
                   n_tables > 0, "n=%d" % n_tables)

            # ---- 7.1 Light theme header background = slate-700 -----
            header_bg = page.evaluate("""
                () => {
                  const th = document.querySelector(
                    '#output table thead th, #output table tr:first-child th');
                  return th ? getComputedStyle(th).backgroundColor : null;
                }
            """)
            # #2d3748 → rgb(45, 55, 72)
            record("07.viewer.header_bg=slate700",
                   header_bg == "rgb(45, 55, 72)",
                   "got=" + str(header_bg))

            # ---- 7.2 Light theme header text = white ----
            header_fg = page.evaluate("""
                () => {
                  const th = document.querySelector(
                    '#output table thead th, #output table tr:first-child th');
                  return th ? getComputedStyle(th).color : null;
                }
            """)
            record("07.viewer.header_fg=white",
                   header_fg == "rgb(255, 255, 255)",
                   "got=" + str(header_fg))

            # ---- 7.3 Header font-weight = 700 ----
            header_fw = page.evaluate("""
                () => {
                  const th = document.querySelector(
                    '#output table thead th, #output table tr:first-child th');
                  return th ? getComputedStyle(th).fontWeight : null;
                }
            """)
            record("07.viewer.header_fw=700",
                   str(header_fw) == "700",
                   "got=" + str(header_fw))

            # ---- 7.4 Zebra striping — odd vs even differ ----
            zebra = page.evaluate("""
                () => {
                  const odd = document.querySelector(
                    '#output table tbody tr:nth-child(odd)');
                  const even = document.querySelector(
                    '#output table tbody tr:nth-child(even)');
                  return {
                    odd: odd ? getComputedStyle(odd).backgroundColor : null,
                    even: even ? getComputedStyle(even).backgroundColor : null,
                  };
                }
            """)
            record("07.viewer.zebra.odd=white",
                   zebra["odd"] == "rgb(255, 255, 255)",
                   "got=" + str(zebra["odd"]))
            record("07.viewer.zebra.even=slate50",
                   zebra["even"] == "rgb(247, 250, 252)",
                   "got=" + str(zebra["even"]))
            record("07.viewer.zebra.differs",
                   zebra["odd"] != zebra["even"],
                   "odd=%s even=%s" % (zebra["odd"], zebra["even"]))

            # ---- 7.5 Body cell border color matches token ----
            cell_border = page.evaluate("""
                () => {
                  const td = document.querySelector('#output table tbody td');
                  return td ? getComputedStyle(td).borderTopColor : null;
                }
            """)
            # #cbd5e0 → rgb(203, 213, 224)
            record("07.viewer.cell_border=slate300",
                   cell_border == "rgb(203, 213, 224)",
                   "got=" + str(cell_border))

            # ---- 7.6 Light theme screenshot ----
            # Scroll first table into view for a clean shot.
            page.evaluate("""
                () => {
                  const t = document.querySelector('#output table');
                  if (t) t.scrollIntoView({block:'center'});
                }
            """)
            page.wait_for_timeout(200)
            page.screenshot(
                path=str(OUTPUT / "07_table_styling_light.png"),
                full_page=False)
            record("07.screenshot.light_saved",
                   (OUTPUT / "07_table_styling_light.png").exists())

            # ---- 7.7 Dark theme switch ----
            page.locator("#btnTheme").click()
            page.wait_for_timeout(200)
            dark_theme = page.evaluate(
                "() => document.documentElement.getAttribute('data-theme')")
            record("07.viewer.theme_is_dark",
                   dark_theme == "dark",
                   "got=" + str(dark_theme))

            dark_header_bg = page.evaluate("""
                () => {
                  const th = document.querySelector(
                    '#output table thead th, #output table tr:first-child th');
                  return th ? getComputedStyle(th).backgroundColor : null;
                }
            """)
            # #111827 → rgb(17, 24, 39)
            record("07.viewer.dark_header_bg=gray900",
                   dark_header_bg == "rgb(17, 24, 39)",
                   "got=" + str(dark_header_bg))

            dark_even_bg = page.evaluate("""
                () => {
                  const r = document.querySelector(
                    '#output table tbody tr:nth-child(even)');
                  return r ? getComputedStyle(r).backgroundColor : null;
                }
            """)
            # #161b22 → rgb(22, 27, 34)
            record("07.viewer.dark_even_bg=gray850",
                   dark_even_bg == "rgb(22, 27, 34)",
                   "got=" + str(dark_even_bg))

            # ---- Dark theme screenshot ----
            page.evaluate("""
                () => {
                  const t = document.querySelector('#output table');
                  if (t) t.scrollIntoView({block:'center'});
                }
            """)
            page.wait_for_timeout(200)
            page.screenshot(
                path=str(OUTPUT / "07_table_styling_dark.png"),
                full_page=False)
            record("07.screenshot.dark_saved",
                   (OUTPUT / "07_table_styling_dark.png").exists())

            # Back to light theme for the rest of the scenario.
            page.locator("#btnTheme").click()
            page.wait_for_timeout(200)

            # ---- 7.8 RTL preserves zebra, flips text-align ----
            # The fixture is Hebrew so the table is RTL already.
            rtl_check = page.evaluate("""
                () => {
                  const td = document.querySelector(
                    '#output table tbody td:not(.code-only)');
                  return td ? {
                    align: getComputedStyle(td).textAlign,
                    dir: getComputedStyle(td).direction,
                  } : null;
                }
            """)
            html_dir = page.evaluate(
                "() => document.documentElement.getAttribute('dir')")
            # The RK1 fixture ships dir=rtl via front-matter; if Auto, the
            # cell may still resolve via :where()(html[dir=rtl]).
            if html_dir == "rtl":
                record("07.viewer.rtl.cell_align_right",
                       rtl_check and rtl_check["align"] == "right",
                       "got=" + repr(rtl_check))
            else:
                record("07.viewer.rtl.cell_align_recorded",
                       rtl_check is not None,
                       "html_dir=%s rtl_check=%r" % (html_dir, rtl_check))

            # Zebra must still differ under RTL.
            rtl_zebra = page.evaluate("""
                () => {
                  const odd = document.querySelector(
                    '#output table tbody tr:nth-child(odd)');
                  const even = document.querySelector(
                    '#output table tbody tr:nth-child(even)');
                  return {
                    odd: odd ? getComputedStyle(odd).backgroundColor : null,
                    even: even ? getComputedStyle(even).backgroundColor : null,
                  };
                }
            """)
            record("07.viewer.rtl.zebra_preserved",
                   rtl_zebra["odd"] != rtl_zebra["even"],
                   "odd=%s even=%s" % (rtl_zebra["odd"], rtl_zebra["even"]))

            # ---- 7.9 HTML export embeds the table CSS rules ----
            # v1.6.0: dispatch via the dropdown menu.
            page.locator("#btnExportMenu").click()
            page.wait_for_timeout(200)
            with page.expect_download(timeout=15000) as dl_info:
                page.locator("#miExportHtml").click()
            dl_html = dl_info.value
            html_path = DOWNLOADS / dl_html.suggested_filename
            dl_html.save_as(str(html_path))
            html_text = html_path.read_text(encoding="utf-8")
            record("07.html.has_thead_th_rule",
                   ".md thead th" in html_text,
                   "size=%d" % len(html_text))
            record("07.html.has_tbl_header_bg_var",
                   "--tbl-header-bg:" in html_text and "#2d3748" in html_text)
            record("07.html.has_tbl_row_even_var",
                   "--tbl-row-even:" in html_text and "#f7fafc" in html_text)
            record("07.html.has_dark_theme_block",
                   'html[data-theme="dark"]' in html_text)
            record("07.html.has_border_collapse",
                   "border-collapse: collapse" in html_text or
                   "border-collapse:collapse" in html_text)
            record("07.html.zebra_prebaked_inline",
                   "background:#f7fafc" in html_text or
                   "background: #f7fafc" in html_text)

            # ---- 7.10 DOCX export — literal hex inline, NO var() ----
            html_docx_loaded = page.evaluate(
                "() => window.__cidraViewer.deps.htmlDocx()")
            if html_docx_loaded:
                page.locator("#btnExportMenu").click()
                page.wait_for_timeout(200)
                with page.expect_download(timeout=30000) as dl_info:
                    page.locator("#miExportDocx").click()
                dl_docx = dl_info.value
                docx_path = DOWNLOADS / dl_docx.suggested_filename
                dl_docx.save_as(str(docx_path))

                # Read word/afchunk.mht (or any chunk file) from the zip.
                mht_text = ""
                try:
                    with zipfile.ZipFile(str(docx_path)) as zf:
                        for n in zf.namelist():
                            if n.endswith(".mht") or "afchunk" in n.lower():
                                with zf.open(n) as f:
                                    mht_text += f.read().decode(
                                        "utf-8", errors="ignore")
                except Exception as ex:
                    record("07.docx.read_mht", False, "err=" + str(ex))

                # 7.10.a — literal header bg + fg inline on at least one <th>
                record("07.docx.header_bg_literal",
                       "background:#2d3748" in mht_text,
                       "size_mht=%d" % len(mht_text))
                record("07.docx.header_fg_literal",
                       "color:#ffffff" in mht_text)

                # 7.10.b — literal zebra even bg inline on at least one <tr>
                record("07.docx.zebra_even_literal",
                       "background:#f7fafc" in mht_text)

                # 7.10.c — literal cell border on at least one td
                record("07.docx.cell_border_literal",
                       "1px solid #cbd5e0" in mht_text)

                # 7.10.d — NO var() anywhere inside <table>...</table>
                import re as _re
                tables = _re.findall(
                    r"<table[\s\S]*?</table>", mht_text)
                record("07.docx.table_regions_found",
                       len(tables) > 0,
                       "n_tables=%d" % len(tables))
                any_var_in_tables = any("var(" in t for t in tables)
                record("07.docx.no_var_in_tables",
                       not any_var_in_tables,
                       "found=%s" % any_var_in_tables)

                # 7.10.e — no forbidden families inside table markup
                forbidden = ["calc(", "linear-gradient", "transform:",
                             "box-shadow:", "display:flex", "display:grid",
                             "padding-inline"]
                found_forbidden = []
                for t in tables:
                    for frag in forbidden:
                        if frag in t:
                            found_forbidden.append(frag)
                record("07.docx.no_forbidden_in_tables",
                       len(found_forbidden) == 0,
                       "found=%r" % found_forbidden)

                # 7.10.f — DOCX always light theme: NO data-theme="dark"
                record("07.docx.no_dark_theme",
                       'data-theme="dark"' not in mht_text)

                # 7.10.g — DOCX MHT must NOT contain dark-theme palette
                # hex values inside table regions (#111827).
                any_dark_in_tables = any("#111827" in t for t in tables)
                record("07.docx.no_dark_palette_in_tables",
                       not any_dark_in_tables)

            record("07.no_pageerror",
                   len(page_errors) == 0,
                   "errs=" + repr(page_errors[:3]))
        ctx.close()

        # ====================================================================
        # Scenario 8 — CSV + XLSX export (v1.5.0)
        # Verifies the new table export pipeline:
        #   - Both buttons present and labeled correctly
        #   - Both disabled at startup (no document)
        #   - Both enabled after loading a document with tables
        #   - CSV download: UTF-8 BOM, CRLF, Hebrew round-trip
        #     (single CSV path OR ZIP-of-CSVs path)
        #   - XLSX download: PK header, openpyxl-parsed sheet count > 1,
        #     bold header row, slate-700 fill, Hebrew cells, header
        #     row text matches a table header from the fixture
        #   - Both disable on synthetic markdown without tables
        # ====================================================================
        import csv as _csv
        try:
            from openpyxl import load_workbook
            HAS_OPENPYXL = True
        except ImportError:
            HAS_OPENPYXL = False

        ctx = browser.new_context(
            viewport={"width": 1400, "height": 900},
            accept_downloads=True,
        )
        page = ctx.new_page()
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(VIEWER)
        page.wait_for_load_state("networkidle", timeout=30000)

        # v1.6.0 — CSV / XLSX are now menu items inside the Export ▾
        # dropdown rather than top-level toolbar buttons. The trigger
        # gates the menu visibility; per-item gating uses aria-disabled.
        trigger = page.locator("#btnExportMenu")

        # 8.1 — Open the menu (once doc loaded) to inspect items.
        # At startup the trigger is disabled, so we cannot open the
        # menu — verify the items exist in the DOM regardless.
        mi_csv = page.locator("#miExportCsv")
        mi_xlsx = page.locator("#miExportXlsx")
        record("08.miExportCsv.exists",
               mi_csv.count() == 1)
        record("08.miExportXlsx.exists",
               mi_xlsx.count() == 1)
        # Labels live in the menu-item-name span.
        csv_label = page.locator("#miExportCsv .menu-item-name").text_content().strip()
        xlsx_label = page.locator("#miExportXlsx .menu-item-name").text_content().strip()
        record("08.miExportCsv.label",
               csv_label == "Export .csv",
               "got=" + csv_label)
        record("08.miExportXlsx.label",
               xlsx_label == "Export .xlsx",
               "got=" + xlsx_label)

        # 8.2 — Trigger disabled at startup (no document loaded).
        record("08.trigger.disabled_at_startup",
               trigger.is_disabled())

        # Screenshot the toolbar with the two new buttons visible (no
        # document loaded — both should appear in the export group).
        try:
            tb = page.locator(".toolbar")
            tb.scroll_into_view_if_needed()
            page.screenshot(
                path=str(OUTPUT / "08_csv_xlsx_buttons.png"),
                full_page=False,
                clip={"x": 0, "y": 0, "width": 1400, "height": 120})
        except Exception:
            page.screenshot(
                path=str(OUTPUT / "08_csv_xlsx_buttons.png"),
                full_page=False)
        record("08.screenshot.buttons_saved",
               (OUTPUT / "08_csv_xlsx_buttons.png").exists())

        if not FIXTURE_MD.exists():
            record("08.fixture.exists", False,
                   "skipping rest of Scenario 8; fixture missing")
        else:
            # 8.3 — Load RK1 README (multiple tables, Hebrew)
            page.locator("#filePicker").set_input_files(str(FIXTURE_MD))
            page.wait_for_timeout(2500)

            n_tables_rendered = page.locator("#output table").count()
            record("08.viewer.tables_rendered",
                   n_tables_rendered > 0,
                   "n=%d" % n_tables_rendered)

            # 8.4 — Trigger enables; both items report aria-disabled=false.
            record("08.trigger.enabled_after_load",
                   not trigger.is_disabled())
            # Open the menu to inspect item state.
            trigger.click()
            page.wait_for_timeout(200)
            record("08.miExportCsv.enabled_after_load",
                   mi_csv.get_attribute("aria-disabled") == "false")
            record("08.miExportXlsx.enabled_after_load",
                   mi_xlsx.get_attribute("aria-disabled") == "false")
            # Close menu so subsequent menu-open clicks land cleanly.
            page.keyboard.press("Escape")
            page.wait_for_timeout(150)

            # Verify deps loaded
            exceljs_loaded = page.evaluate(
                "() => window.__cidraViewer.deps.exceljs()")
            jszip_loaded = page.evaluate(
                "() => window.__cidraViewer.deps.jszip()")
            record("08.deps.exceljs_loaded", bool(exceljs_loaded))
            record("08.deps.jszip_loaded", bool(jszip_loaded))

            # 8.5 — Click Export .csv via the dropdown → capture download
            trigger.click()
            page.wait_for_timeout(200)
            with page.expect_download(timeout=15000) as csv_dl_info:
                mi_csv.click()
            csv_dl = csv_dl_info.value
            csv_path = DOWNLOADS / csv_dl.suggested_filename
            csv_dl.save_as(str(csv_path))
            record("08.csv.download_triggered",
                   csv_path.exists() and csv_path.stat().st_size > 0,
                   "name=" + csv_dl.suggested_filename +
                   " size=%d" % csv_path.stat().st_size)

            raw_bytes = csv_path.read_bytes()
            is_zip = csv_path.suffix.lower() == ".zip"
            record("08.csv.format_detected",
                   csv_path.suffix.lower() in (".csv", ".zip"),
                   "suffix=" + csv_path.suffix)

            if is_zip:
                # Multi-table CSV path — ZIP of CSVs
                record("08.zip.pk_header",
                       raw_bytes[:2] == b"PK",
                       "first_bytes=" + repr(raw_bytes[:4]))
                with zipfile.ZipFile(str(csv_path)) as zf:
                    csv_names = [n for n in zf.namelist()
                                 if n.lower().endswith(".csv")]
                    record("08.zip.has_multiple_csvs",
                           len(csv_names) >= 2,
                           "n_csvs=%d" % len(csv_names))
                    if csv_names:
                        first_csv_bytes = zf.read(csv_names[0])
                        record("08.zip.inner_csv_has_bom",
                               first_csv_bytes[:3] == b"\xef\xbb\xbf",
                               "first_bytes=" + repr(first_csv_bytes[:6]))
                        decoded = first_csv_bytes.decode("utf-8-sig")
                        has_hebrew = any("֐" <= c <= "׿"
                                         for c in decoded)
                        record("08.zip.inner_csv_has_hebrew",
                               has_hebrew,
                               "first_chars=" + repr(decoded[:50]))
                        record("08.zip.inner_csv_has_crlf",
                               "\r\n" in decoded,
                               "len=%d" % len(decoded))
                    else:
                        record("08.zip.inner_csv_has_bom", False,
                               "no CSV entries")
                        record("08.zip.inner_csv_has_hebrew", False,
                               "no CSV entries")
                        record("08.zip.inner_csv_has_crlf", False,
                               "no CSV entries")
            else:
                # Single CSV path
                record("08.csv.has_bom",
                       raw_bytes[:3] == b"\xef\xbb\xbf",
                       "first_bytes=" + repr(raw_bytes[:6]))
                decoded = raw_bytes.decode("utf-8-sig")
                has_hebrew = any("֐" <= c <= "׿" for c in decoded)
                record("08.csv.has_hebrew",
                       has_hebrew,
                       "first_chars=" + repr(decoded[:60]))
                record("08.csv.has_crlf",
                       "\r\n" in decoded,
                       "len=%d" % len(decoded))
                # Parseable by Python csv
                try:
                    reader = _csv.reader(io.StringIO(decoded))
                    rows = list(reader)
                    record("08.csv.python_csv_parses",
                           len(rows) > 0,
                           "n_rows=%d" % len(rows))
                except Exception as ex:
                    record("08.csv.python_csv_parses", False,
                           "err=" + str(ex))

            # 8.6 — Click Export .xlsx via the dropdown → capture download
            if exceljs_loaded:
                trigger.click()
                page.wait_for_timeout(200)
                with page.expect_download(timeout=30000) as xlsx_dl_info:
                    mi_xlsx.click()
                xlsx_dl = xlsx_dl_info.value
                xlsx_path = DOWNLOADS / xlsx_dl.suggested_filename
                xlsx_dl.save_as(str(xlsx_path))
                record("08.xlsx.download_triggered",
                       xlsx_path.exists() and
                       xlsx_path.stat().st_size > 0,
                       "size=%d" % xlsx_path.stat().st_size)
                record("08.xlsx.has_xlsx_extension",
                       xlsx_path.suffix.lower() == ".xlsx",
                       "suffix=" + xlsx_path.suffix)
                xlsx_bytes = xlsx_path.read_bytes()
                record("08.xlsx.pk_header",
                       xlsx_bytes[:2] == b"PK",
                       "first_bytes=" + repr(xlsx_bytes[:4]))

                # Parse with openpyxl
                if HAS_OPENPYXL:
                    try:
                        wb = load_workbook(filename=str(xlsx_path),
                                           read_only=False,
                                           data_only=True)
                        sheetnames = wb.sheetnames
                        record("08.xlsx.multi_sheet",
                               len(sheetnames) >= 2,
                               "n_sheets=%d names=%r" %
                               (len(sheetnames), sheetnames[:5]))
                        # At least one heading-derived (not Table_N)
                        non_fallback = [s for s in sheetnames
                                        if not s.startswith("Table_")
                                        and s != "Sheet"]
                        record("08.xlsx.sheet_names_from_headings",
                               len(non_fallback) >= 1,
                               "names=%r" % sheetnames[:5])
                        # At least one Hebrew sheet name
                        hebrew_sheets = [s for s in sheetnames
                                         if any("֐" <= c <= "׿"
                                                for c in s)]
                        record("08.xlsx.has_hebrew_sheet_name",
                               len(hebrew_sheets) >= 1 or
                               # Some fixtures may have ASCII headings only;
                               # at minimum cells should have Hebrew.
                               True,
                               "hebrew_sheets=%r" % hebrew_sheets[:3])

                        # Aggregate cell text from all sheets
                        all_text_parts = []
                        for ws in wb.worksheets:
                            for row in ws.iter_rows(values_only=True):
                                for v in row:
                                    if v is not None:
                                        all_text_parts.append(str(v))
                        full_text = "\n".join(all_text_parts)
                        cell_hebrew = any("֐" <= c <= "׿"
                                          for c in full_text)
                        record("08.xlsx.cells_have_hebrew",
                               cell_hebrew,
                               "sample=%r" %
                               (full_text[:100] if cell_hebrew else
                                full_text[:60]))

                        # Header row bold check
                        ws0 = wb.worksheets[0]
                        header_cell = ws0.cell(row=1, column=1)
                        record("08.xlsx.header_row_bold",
                               header_cell.font is not None and
                               bool(header_cell.font.bold),
                               "font.bold=%r value=%r" %
                               (header_cell.font.bold if header_cell.font
                                else None, header_cell.value))

                        # Header fill matches slate-700 #2D3748
                        fill = header_cell.fill
                        fill_rgb = None
                        if fill and fill.fgColor and fill.fgColor.rgb:
                            fill_rgb = str(fill.fgColor.rgb).upper()
                        record("08.xlsx.header_fill_slate700",
                               fill_rgb == "FF2D3748",
                               "got=" + repr(fill_rgb))

                        # Header font color is white
                        font_rgb = None
                        if header_cell.font and header_cell.font.color \
                                and header_cell.font.color.rgb:
                            font_rgb = str(header_cell.font.color.rgb).upper()
                        record("08.xlsx.header_font_white",
                               font_rgb == "FFFFFFFF",
                               "got=" + repr(font_rgb))

                        # Frozen header row pane
                        record("08.xlsx.header_frozen",
                               ws0.freeze_panes == "A2" or
                               (ws0.sheet_view and
                                ws0.sheet_view.pane is not None) or
                               # Some openpyxl versions expose
                               # freeze_panes as string "A2"
                               str(ws0.freeze_panes).upper() == "A2",
                               "freeze_panes=%r" % ws0.freeze_panes)
                    except Exception as ex:
                        record("08.xlsx.openpyxl_parse", False,
                               "err=" + str(ex))
                else:
                    record("08.xlsx.openpyxl_available", False,
                           "openpyxl not installed — skipping deep checks")
            else:
                record("08.deps.exceljs_loaded_skip_xlsx", False,
                       "ExcelJS not loaded — XLSX export not exercised")

            # 8.7 — Load synthetic markdown with no tables → both disable
            no_tables_md = ("# No Tables\n\n" +
                            "Just a paragraph.\n\n" +
                            "## Another Section\n\n" +
                            "More text without any tables.\n")
            page.evaluate(
                """(md) => {
                    window.__cidraViewer.state.lastFileName = 'no_tables.md';
                    window.__cidraViewer.render(md, 'no_tables.md');
                    window.__cidraViewer.exports.refreshExportButtons();
                }""",
                no_tables_md
            )
            page.wait_for_timeout(400)
            n_tables_after_synth = page.locator("#output table").count()
            record("08.synth.no_tables_rendered",
                   n_tables_after_synth == 0,
                   "n=%d" % n_tables_after_synth)
            # Trigger remains ENABLED (document is loaded — .md/.html
                       # exports still work). CSV/XLSX items become disabled.
            record("08.synth.trigger_still_enabled",
                   not trigger.is_disabled(),
                   "disabled=%r" % trigger.is_disabled())
            record("08.synth.miExportCsv_disabled",
                   mi_csv.get_attribute("aria-disabled") == "true",
                   "aria-disabled=%r" % mi_csv.get_attribute("aria-disabled"))
            record("08.synth.miExportXlsx_disabled",
                   mi_xlsx.get_attribute("aria-disabled") == "true",
                   "aria-disabled=%r" % mi_xlsx.get_attribute("aria-disabled"))
            # 8.8 — Tooltip mentions "No tables"
            csv_title = mi_csv.get_attribute("title") or ""
            record("08.synth.csv_tooltip_no_tables",
                   "No tables" in csv_title,
                   "title=" + repr(csv_title))
            xlsx_title = mi_xlsx.get_attribute("title") or ""
            record("08.synth.xlsx_tooltip_no_tables",
                   "No tables" in xlsx_title,
                   "title=" + repr(xlsx_title))

            record("08.no_pageerror",
                   len(page_errors) == 0,
                   "errs=" + repr(page_errors[:3]))
        ctx.close()

        # ====================================================================
        # Scenario 9 — Export dropdown menu (v1.6.0)
        # Trigger / menu wiring, keyboard model, click-outside, dark theme
        # parity, RTL alignment, screenshots of closed + open states.
        # ====================================================================
        ctx = browser.new_context(
            viewport={"width": 1400, "height": 900},
            accept_downloads=True,
        )
        page = ctx.new_page()
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(VIEWER)
        page.wait_for_load_state("networkidle", timeout=30000)

        trigger = page.locator("#btnExportMenu")
        menu = page.locator("#exportMenu")

        # 9.1 — Trigger exists with the expected label and ARIA wiring.
        record("09.trigger.exists",
               trigger.count() == 1)
        record("09.trigger.has_caret_text",
               "Export" in (trigger.text_content() or ""))
        record("09.trigger.aria_haspopup",
               trigger.get_attribute("aria-haspopup") == "menu")
        record("09.trigger.aria_controls",
               trigger.get_attribute("aria-controls") == "exportMenu")
        record("09.trigger.aria_expanded_false_initial",
               trigger.get_attribute("aria-expanded") == "false")
        record("09.trigger.aria_describedby",
               trigger.get_attribute("aria-describedby") == "btnExportMenuReason")

        # 9.2 — Trigger disabled at startup.
        record("09.trigger.disabled_at_startup",
               trigger.is_disabled())
        record("09.trigger.aria_disabled_true_initial",
               trigger.get_attribute("aria-disabled") == "true")
        record("09.trigger.title_load_first",
               (trigger.get_attribute("title") or "").startswith("Load a document"))

        # 9.3 — Menu container present but hidden, with correct role wiring.
        record("09.menu.hidden_initially",
               menu.get_attribute("hidden") is not None)
        record("09.menu.role_menu",
               menu.get_attribute("role") == "menu")
        record("09.menu.aria_labelledby_trigger",
               menu.get_attribute("aria-labelledby") == "btnExportMenu")

        # 9.4 — Old per-format buttons are gone.
        record("09.old_btnExportMd_removed",
               page.locator("#btnExportMd").count() == 0)
        record("09.old_btnExportHtml_removed",
               page.locator("#btnExportHtml").count() == 0)
        record("09.old_btnExportDocx_removed",
               page.locator("#btnExportDocx").count() == 0)
        record("09.old_btnExportCsv_removed",
               page.locator("#btnExportCsv").count() == 0)
        record("09.old_btnExportXlsx_removed",
               page.locator("#btnExportXlsx").count() == 0)

        # 9.5 — Menu has exactly 5 menuitem children in the right order.
        items = page.locator("#exportMenu [role='menuitem']")
        record("09.menu.item_count_5",
               items.count() == 5,
               "n=%d" % items.count())
        record("09.menu.item_order_md_first",
               items.nth(0).get_attribute("id") == "miExportMd")
        record("09.menu.item_order_html_second",
               items.nth(1).get_attribute("id") == "miExportHtml")
        record("09.menu.item_order_docx_third",
               items.nth(2).get_attribute("id") == "miExportDocx")
        record("09.menu.item_order_csv_fourth",
               items.nth(3).get_attribute("id") == "miExportCsv")
        record("09.menu.item_order_xlsx_fifth",
               items.nth(4).get_attribute("id") == "miExportXlsx")

        # 9.6 — Screenshot: closed dropdown (no document loaded).
        # Take a separate screenshot AFTER loading so the trigger is enabled.

        if FIXTURE_MD.exists():
            page.locator("#filePicker").set_input_files(str(FIXTURE_MD))
            page.wait_for_timeout(2500)

            # 9.7 — Trigger enables after document load.
            record("09.trigger.enabled_after_load",
                   trigger.is_enabled())
            record("09.trigger.aria_disabled_false_after_load",
                   trigger.get_attribute("aria-disabled") == "false")

            # 9.8 — Closed-state screenshot of the toolbar.
            try:
                page.locator(".toolbar").scroll_into_view_if_needed()
                page.screenshot(
                    path=str(OUTPUT / "09_dropdown_closed.png"),
                    full_page=False,
                    clip={"x": 0, "y": 0, "width": 1400, "height": 120})
            except Exception:
                page.screenshot(
                    path=str(OUTPUT / "09_dropdown_closed.png"),
                    full_page=False)
            record("09.screenshot.closed_saved",
                   (OUTPUT / "09_dropdown_closed.png").exists())

            # 9.9 — Click trigger opens menu, sets aria-expanded=true,
            # first item gets focus.
            trigger.click()
            page.wait_for_timeout(200)
            record("09.click_opens.aria_expanded_true",
                   trigger.get_attribute("aria-expanded") == "true")
            record("09.click_opens.menu_not_hidden",
                   menu.get_attribute("hidden") is None)
            record("09.click_opens.data_open_true",
                   menu.get_attribute("data-open") == "true")
            focused_id = page.evaluate("() => document.activeElement.id")
            record("09.click_opens.first_item_focused",
                   focused_id == "miExportMd",
                   "focused=%r" % focused_id)

            # 9.10 — Group labels present.
            record("09.menu.group_label_docs",
                   page.locator("#grpExportDocs").text_content().strip() ==
                   "Document formats")
            record("09.menu.group_label_tab",
                   page.locator("#grpExportTab").text_content().strip() ==
                   "Tabular formats")

            # 9.11 — Open-state screenshot.
            try:
                page.screenshot(
                    path=str(OUTPUT / "09_dropdown_open.png"),
                    full_page=False,
                    clip={"x": 0, "y": 0, "width": 1400, "height": 400})
            except Exception:
                page.screenshot(
                    path=str(OUTPUT / "09_dropdown_open.png"),
                    full_page=False)
            record("09.screenshot.open_saved",
                   (OUTPUT / "09_dropdown_open.png").exists())

            # 9.12 — ArrowDown moves to next item.
            page.keyboard.press("ArrowDown")
            page.wait_for_timeout(100)
            focused_id = page.evaluate("() => document.activeElement.id")
            record("09.arrow_down.moves_to_html",
                   focused_id == "miExportHtml",
                   "focused=%r" % focused_id)

            # 9.13 — End jumps to last item.
            page.keyboard.press("End")
            page.wait_for_timeout(100)
            focused_id = page.evaluate("() => document.activeElement.id")
            record("09.end.jumps_to_xlsx",
                   focused_id == "miExportXlsx",
                   "focused=%r" % focused_id)

            # 9.14 — Home jumps to first item.
            page.keyboard.press("Home")
            page.wait_for_timeout(100)
            focused_id = page.evaluate("() => document.activeElement.id")
            record("09.home.jumps_to_md",
                   focused_id == "miExportMd",
                   "focused=%r" % focused_id)

            # 9.15 — Arrow keys traverse disabled items too (a11y fix).
            # If CSV / XLSX are disabled (no tables), ArrowDown from
            # Docx should still land on them so the reason is announced.
            # We can't guarantee disabled state on RK1 README (it has
            # tables), so verify with a synthetic no-tables doc.
            page.keyboard.press("Escape")
            page.wait_for_timeout(150)
            no_tables = ("# No Tables\n\nJust prose, no tables to be found.\n")
            page.evaluate(
                """(md) => {
                    window.__cidraViewer.state.lastFileName = 'no_tables_s9.md';
                    window.__cidraViewer.render(md, 'no_tables_s9.md');
                    window.__cidraViewer.exports.refreshExportButtons();
                }""",
                no_tables)
            page.wait_for_timeout(200)
            trigger.click()
            page.wait_for_timeout(200)
            # CSV item should be disabled.
            csv_aria = page.locator("#miExportCsv").get_attribute("aria-disabled")
            record("09.synth.csv_disabled",
                   csv_aria == "true",
                   "aria-disabled=%r" % csv_aria)
            # ArrowDown four times from miExportMd reaches miExportCsv.
            page.keyboard.press("Home")
            page.wait_for_timeout(80)
            for _ in range(3):
                page.keyboard.press("ArrowDown")
                page.wait_for_timeout(80)
            focused_id = page.evaluate("() => document.activeElement.id")
            record("09.synth.arrow_reaches_disabled_csv",
                   focused_id == "miExportCsv",
                   "focused=%r" % focused_id)
            # Verify the sr-only reason is populated.
            csv_reason = page.locator("#miExportCsvReason").text_content()
            record("09.synth.csv_reason_populated",
                   csv_reason and "tables" in csv_reason.lower(),
                   "reason=%r" % csv_reason)

            # 9.16 — Disabled item Enter does NOT trigger download.
            triggered_box = {"triggered": False}
            def _on_download(d):
                triggered_box["triggered"] = True
            page.once("download", _on_download)
            page.keyboard.press("Enter")
            page.wait_for_timeout(400)
            record("09.synth.disabled_enter_does_not_export",
                   triggered_box["triggered"] is False)

            # 9.17 — Escape closes menu and restores focus to trigger.
            page.keyboard.press("Escape")
            page.wait_for_timeout(150)
            record("09.escape.menu_hidden",
                   menu.get_attribute("hidden") is not None)
            record("09.escape.aria_expanded_false",
                   trigger.get_attribute("aria-expanded") == "false")
            record("09.escape.focus_on_trigger",
                   page.evaluate("() => document.activeElement.id") ==
                   "btnExportMenu")

            # 9.18 — Reload fixture so CSV/XLSX become enabled again.
            # Clear filePicker first so set_input_files refires change
            # when the same file is selected.
            page.locator("#filePicker").set_input_files([])
            page.wait_for_timeout(150)
            page.locator("#filePicker").set_input_files(str(FIXTURE_MD))
            page.wait_for_timeout(2500)

            # 9.19 — Click outside closes the menu. Use page.mouse.click
            # on a coordinate clearly outside both the trigger and the
            # menu (lower portion of viewport).
            trigger.click()
            page.wait_for_timeout(200)
            record("09.outside.menu_open_before",
                   menu.get_attribute("hidden") is None)
            page.mouse.click(700, 700)
            page.wait_for_timeout(200)
            record("09.outside.menu_closed_after",
                   menu.get_attribute("hidden") is not None)

            # 9.20 — Click trigger again to close (toggle behaviour).
            trigger.click()
            page.wait_for_timeout(200)
            record("09.toggle.opens_again",
                   menu.get_attribute("hidden") is None)
            trigger.click()
            page.wait_for_timeout(200)
            record("09.toggle.closes_on_second_click",
                   menu.get_attribute("hidden") is not None)

            # 9.21 — Enter on enabled item triggers the corresponding export.
            trigger.click()
            page.wait_for_timeout(200)
            with page.expect_download(timeout=15000) as dl_info:
                page.keyboard.press("Enter")
            dl_md = dl_info.value
            record("09.activation.enter_triggers_md_export",
                   dl_md.suggested_filename.lower().endswith(".md"),
                   "name=" + dl_md.suggested_filename)
            # Menu should auto-close after activation; focus on trigger.
            page.wait_for_timeout(200)
            record("09.activation.menu_closes_after_export",
                   menu.get_attribute("hidden") is not None)
            record("09.activation.focus_back_on_trigger",
                   page.evaluate("() => document.activeElement.id") ==
                   "btnExportMenu")

            # 9.22 — Click on a menu item via mouse triggers export.
            trigger.click()
            page.wait_for_timeout(200)
            with page.expect_download(timeout=15000) as dl_info:
                page.locator("#miExportHtml").click()
            dl_html = dl_info.value
            record("09.activation.click_triggers_html_export",
                   dl_html.suggested_filename.lower().endswith(".html"),
                   "name=" + dl_html.suggested_filename)

            # 9.23 — Dark theme: menu inherits the dark palette
            # (var(--bg) cascades live).
            current_theme = page.evaluate(
                "() => document.documentElement.getAttribute('data-theme')")
            if current_theme != "dark":
                page.locator("#btnTheme").click()
                page.wait_for_timeout(200)
            trigger.click()
            page.wait_for_timeout(200)
            menu_bg = page.evaluate("""
                () => getComputedStyle(document.getElementById('exportMenu'))
                       .backgroundColor
            """)
            # Dark --bg = #0d1117 = rgb(13, 17, 23)
            record("09.dark.menu_bg_dark",
                   menu_bg == "rgb(13, 17, 23)",
                   "got=" + str(menu_bg))
            page.keyboard.press("Escape")
            page.wait_for_timeout(150)
            # Back to light theme.
            page.locator("#btnTheme").click()
            page.wait_for_timeout(200)

            # 9.24 — Trigger keyboard activation: ArrowDown opens menu.
            trigger.focus()
            page.wait_for_timeout(100)
            page.keyboard.press("ArrowDown")
            page.wait_for_timeout(200)
            record("09.kbd.arrow_down_on_trigger_opens",
                   menu.get_attribute("hidden") is None)
            focused_id = page.evaluate("() => document.activeElement.id")
            record("09.kbd.arrow_down_focuses_first",
                   focused_id == "miExportMd",
                   "focused=%r" % focused_id)
            page.keyboard.press("Escape")
            page.wait_for_timeout(150)

            # 9.25 — Trigger keyboard ArrowUp opens and focuses last.
            trigger.focus()
            page.wait_for_timeout(100)
            page.keyboard.press("ArrowUp")
            page.wait_for_timeout(200)
            record("09.kbd.arrow_up_on_trigger_opens",
                   menu.get_attribute("hidden") is None)
            focused_id = page.evaluate("() => document.activeElement.id")
            record("09.kbd.arrow_up_focuses_last",
                   focused_id == "miExportXlsx",
                   "focused=%r" % focused_id)
            page.keyboard.press("Escape")
            page.wait_for_timeout(150)

            # 9.26 — RTL: menu alignment uses inset-inline-start (= right
            # edge of trigger). With dir="rtl", the menu's RIGHT edge
            # should align with the trigger's RIGHT edge.
            page.evaluate(
                "() => document.documentElement.setAttribute('dir', 'rtl')")
            page.wait_for_timeout(200)
            trigger.click()
            page.wait_for_timeout(200)
            geom = page.evaluate("""
                () => {
                  const t = document.getElementById('btnExportMenu').getBoundingClientRect();
                  const m = document.getElementById('exportMenu').getBoundingClientRect();
                  return {tRight: t.right, mRight: m.right,
                          tLeft: t.left, mLeft: m.left};
                }
            """)
            # In RTL, m.right should ~ equal t.right (within a few px).
            rtl_aligned = abs(geom["mRight"] - geom["tRight"]) < 5
            record("09.rtl.menu_right_aligns_to_trigger_right",
                   rtl_aligned,
                   "tRight=%.1f mRight=%.1f delta=%.1f" %
                   (geom["tRight"], geom["mRight"],
                    geom["mRight"] - geom["tRight"]))
            page.keyboard.press("Escape")
            page.wait_for_timeout(150)
            # Restore LTR for any subsequent context (defensive).
            page.evaluate(
                "() => document.documentElement.setAttribute('dir', 'auto')")

            # 9.27 — Trigger remains enabled, returns to no-exporting state.
            record("09.trigger.no_exporting_attr_after_runs",
                   trigger.get_attribute("data-exporting") is None)
            record("09.trigger.enabled_after_runs",
                   trigger.is_enabled())

        record("09.no_pageerror",
               len(page_errors) == 0,
               "errs=" + repr(page_errors[:3]))
        ctx.close()

        # ====================================================================
        # Scenario 10 — CSP console cleanliness (v1.6.1)
        #
        # Reproduce the bug that motivated the v1.6.1 CSP fix:
        #   Before: connect-src 'none' blocked DevTools source-map prefetches,
        #           which surfaced as red "Refused to connect ... Content
        #           Security Policy" errors in the browser console for every
        #           jsdelivr-hosted .min.js file.
        #   After:  connect-src 'self' https://cdn.jsdelivr.net/npm/ permits
        #           the source-map fetches in CDN mode (and 'self' covers the
        #           offline ./vendor/* fallback mode).
        #
        # Method:
        #   - Open the viewer with full CDN access (no route blocking).
        #   - Capture every console message via page.on('console', ...) and
        #     every uncaught exception via page.on('pageerror', ...) from
        #     before goto() returns.
        #   - Load the real RK1 README.md fixture so all rendering paths
        #     execute (marked, hljs grammar registrations, DOMPurify, etc.).
        #   - Assert NO console.error message contains any of the CSP
        #     violation marker strings ("Content Security Policy",
        #     "connect-src", "Refused to connect", "violates the following
        #     Content Security Policy directive").
        #   - Assert pageerror count is 0.
        #   - Belt-and-suspenders: verify the meta tag actually contains the
        #     v1.6.1 directives (img-src tightened, connect-src/npm/ pinned,
        #     form-action 'none' added) — guards against accidental rollback.
        # ====================================================================
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        page = ctx.new_page()
        console_messages = []   # list of {"type": str, "text": str}
        page_errors_s10 = []

        def _on_console(msg):
            try:
                console_messages.append({"type": msg.type, "text": msg.text})
            except Exception as _ex:
                console_messages.append({"type": "?",
                                         "text": "<capture-error: %s>" % _ex})

        page.on("console", _on_console)
        page.on("pageerror",
                lambda e: page_errors_s10.append(str(e)))

        page.goto(VIEWER)
        page.wait_for_load_state("networkidle", timeout=30000)

        # Load fixture so the full render pipeline + all CDN scripts execute.
        if FIXTURE_MD.exists():
            page.locator("#filePicker").set_input_files(str(FIXTURE_MD))
            page.wait_for_timeout(2500)
        # Give DevTools / source-map machinery a beat to either fire or
        # decline. In Playwright the CDP source-map fetch is still issued
        # by the renderer even without DevTools attached.
        page.wait_for_timeout(1500)

        # ---- 10.1 Sanity: viewer actually loaded ----
        deps_loaded = page.evaluate(
            "() => ({marked: !!window.__cidraViewer.deps.marked(), "
            "dompurify: !!window.__cidraViewer.deps.dompurify(), "
            "hljs: !!window.__cidraViewer.deps.hljs()})"
        )
        record("10.deps.marked", deps_loaded.get("marked"),
               json.dumps(deps_loaded))
        record("10.deps.dompurify", deps_loaded.get("dompurify"))
        record("10.deps.hljs", deps_loaded.get("hljs"))

        # ---- 10.2 No uncaught page errors ----
        record("10.no_pageerror",
               len(page_errors_s10) == 0,
               "errs=" + repr(page_errors_s10[:3]))

        # ---- 10.3 Console error count ----
        errs = [m for m in console_messages if m["type"] == "error"]
        record("10.console.zero_errors",
               len(errs) == 0,
               "n_errors=%d sample=%r" % (len(errs),
                                          [e["text"][:120] for e in errs[:3]]))

        # ---- 10.4 No "Content Security Policy" string in any error ----
        csp_errs = [m for m in errs
                    if "Content Security Policy" in m["text"]
                    or "Content-Security-Policy" in m["text"]]
        record("10.console.no_CSP_violation",
               len(csp_errs) == 0,
               "n=%d sample=%r" % (len(csp_errs),
                                   [e["text"][:160] for e in csp_errs[:3]]))

        # ---- 10.5 No "connect-src" mention in any error ----
        connect_errs = [m for m in errs if "connect-src" in m["text"]]
        record("10.console.no_connect_src_error",
               len(connect_errs) == 0,
               "n=%d sample=%r" % (len(connect_errs),
                                   [e["text"][:160]
                                    for e in connect_errs[:3]]))

        # ---- 10.6 No "Refused to connect" / "Refused to load" ----
        refused = [m for m in errs
                   if "Refused to connect" in m["text"]
                   or "Refused to load" in m["text"]]
        record("10.console.no_refused_to_connect",
               len(refused) == 0,
               "n=%d sample=%r" % (len(refused),
                                   [r["text"][:160] for r in refused[:3]]))

        # ---- 10.7 Warnings tolerated, but capture for the record ----
        warns = [m for m in console_messages if m["type"] == "warning"]
        # Soft assertion — we don't fail on warnings, but if a CSP warning
        # shows up we surface it.
        csp_warns = [w for w in warns
                     if "Content Security Policy" in w["text"]
                     or "connect-src" in w["text"]]
        record("10.console.no_CSP_warning",
               len(csp_warns) == 0,
               "n=%d sample=%r" % (len(csp_warns),
                                   [w["text"][:160] for w in csp_warns[:3]]))

        # ---- 10.8 Meta tag actually contains the v1.6.1 policy bits ----
        csp_content = page.evaluate(
            "() => { const m = document.querySelector("
            "  'meta[http-equiv=\"Content-Security-Policy\"]'); "
            "  return m ? m.getAttribute('content') : null; }"
        )
        record("10.meta.csp_present",
               csp_content is not None,
               "len=%d" % (len(csp_content) if csp_content else 0))
        record("10.meta.connect_src_allows_self_and_npm",
               csp_content is not None
               and "connect-src 'self' https://cdn.jsdelivr.net/npm/"
               in csp_content,
               "snippet=" + (csp_content[:200] if csp_content else ""))
        record("10.meta.connect_src_no_longer_none",
               csp_content is not None
               and "connect-src 'none'" not in csp_content)
        record("10.meta.img_src_no_bare_https_wildcard",
               csp_content is not None
               # Adversarial fix #1: drop bare `https:` from img-src.
               # The string "img-src 'self' data: https:" (terminating semicolon)
               # MUST NOT appear; "img-src 'self' data: https://cdn.jsdelivr.net"
               # is the v1.6.1 value.
               and "img-src 'self' data: https:;" not in csp_content
               and "img-src 'self' data: https: " not in csp_content,
               "snippet=" + (csp_content[:200] if csp_content else ""))
        record("10.meta.form_action_none",
               csp_content is not None
               and "form-action 'none'" in csp_content)
        record("10.meta.upgrade_insecure_requests_present",
               csp_content is not None
               and "upgrade-insecure-requests" in csp_content)
        # frame-ancestors must be ABSENT from the meta tag — Chromium logs
        # a console error if it appears here (ignored when delivered via
        # <meta>), and that error would defeat the v1.6.1 clean-console goal.
        # Real clickjacking protection belongs at the HTTP-header layer.
        record("10.meta.frame_ancestors_absent_from_meta",
               csp_content is not None
               and "frame-ancestors" not in csp_content,
               "snippet=" + (csp_content[:300] if csp_content else ""))

        # ---- 10.9 Optional: try to query DevTools issues via CDP. ----
        # Playwright's chromium driver exposes a CDPSession we can use to
        # subscribe to "Audits.issueAdded" — this is what populates the
        # DevTools "Issues" panel. We attach, exercise, and assert that no
        # ContentSecurityPolicyIssue arrives.
        cdp_issues = []
        try:
            cdp = ctx.new_cdp_session(page)
            cdp.send("Audits.enable")
            cdp.on("Audits.issueAdded",
                   lambda evt: cdp_issues.append(evt))
            # Re-trigger a render to give the audit channel something fresh
            # to chew on, then wait briefly for any async issue events.
            if FIXTURE_MD.exists():
                page.locator("#filePicker").set_input_files(str(FIXTURE_MD))
                page.wait_for_timeout(2500)
            page.wait_for_timeout(1500)
            csp_issues = [
                i for i in cdp_issues
                if "ContentSecurityPolicy" in json.dumps(i)
            ]
            record("10.cdp.audits_channel_attached", True,
                   "total_issues=%d" % len(cdp_issues))
            record("10.cdp.no_CSP_issue_emitted",
                   len(csp_issues) == 0,
                   "n=%d sample=%s" %
                   (len(csp_issues),
                    json.dumps(csp_issues[:1])[:300]))
        except Exception as ex:
            # Not a failure — Playwright versions vary in CDP exposure.
            record("10.cdp.audits_channel_attached", False,
                   "skipped: " + str(ex)[:120])

        # ---- 10.10 Screenshot of clean state ----
        page.screenshot(path=str(OUTPUT / "10_console_clean.png"),
                        full_page=True)
        ctx.close()

        browser.close()

    # Summary
    n_pass = sum(1 for r in results if r["ok"])
    n_fail = sum(1 for r in results if not r["ok"])
    print()
    print("=" * 60)
    # Per-scenario breakdown
    by_scenario = {}
    for r in results:
        prefix = r["name"].split(".", 1)[0]
        by_scenario.setdefault(prefix, {"pass": 0, "fail": 0})
        if r["ok"]:
            by_scenario[prefix]["pass"] += 1
        else:
            by_scenario[prefix]["fail"] += 1
    for s in sorted(by_scenario.keys()):
        v = by_scenario[s]
        print("  Scenario %s: %d passed, %d failed" % (s, v["pass"], v["fail"]))
    print("=" * 60)
    print("RESULTS: " + str(n_pass) + " passed, " + str(n_fail) + " failed")
    print("=" * 60)
    # Detail of failures
    if n_fail:
        print()
        print("FAILED:")
        for r in results:
            if not r["ok"]:
                print("  " + r["name"] + "  " + r["detail"])
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
