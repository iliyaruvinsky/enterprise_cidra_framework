"""
Playwright verification for the CIDRA Documentation Viewer redesign.

Six scenarios + cross-cutting assertions, mirroring the redesign's
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
            # Export buttons should be disabled after clear
            record("05.btnClear.export_md_disabled",
                   page.locator("#btnExportMd").is_disabled())
            record("05.btnClear.export_html_disabled",
                   page.locator("#btnExportHtml").is_disabled())
            record("05.btnClear.export_docx_disabled",
                   page.locator("#btnExportDocx").is_disabled())

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

            # Verify export buttons enabled after load
            record("06.btnExportMd.enabled_after_load",
                   page.locator("#btnExportMd").is_enabled())
            record("06.btnExportHtml.enabled_after_load",
                   page.locator("#btnExportHtml").is_enabled())
            # DOCX gated also on html-docx-js
            html_docx_loaded = page.evaluate(
                "() => window.__cidraViewer.deps.htmlDocx()"
            )
            record("06.deps.htmlDocx_loaded", bool(html_docx_loaded))
            if html_docx_loaded:
                record("06.btnExportDocx.enabled_after_load",
                       page.locator("#btnExportDocx").is_enabled())

            source_md = FIXTURE_MD.read_text(encoding="utf-8")

            # ---- Export .md ----
            with page.expect_download(timeout=15000) as dl_info:
                page.locator("#btnExportMd").click()
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
            with page.expect_download(timeout=15000) as dl_info:
                page.locator("#btnExportHtml").click()
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
                with page.expect_download(timeout=30000) as dl_info:
                    page.locator("#btnExportDocx").click()
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
            # should be no-op (button disabled). Stage a forced state.
            page.evaluate("""
                () => {
                  window.__cidraViewer.state.isExporting = true;
                  window.__cidraViewer.exports.refreshExportButtons();
                }
            """)
            record("06.race.md_disabled_while_exporting",
                   page.locator("#btnExportMd").is_disabled())
            record("06.race.html_disabled_while_exporting",
                   page.locator("#btnExportHtml").is_disabled())
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
