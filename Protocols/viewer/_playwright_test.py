"""
Playwright verification for the CIDRA Documentation Viewer redesign.

Four scenarios + cross-cutting assertions, mirroring the redesign's
"Playwright Test Plan — Apply Phase" section.

Run:
    python C:\\My_AI\\enterprise_cidra_framework\\Protocols\\viewer\\_playwright_test.py
"""

import sys
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path("C:/My_AI/enterprise_cidra_framework/Protocols/viewer")
VIEWER = (ROOT / "viewer.html").as_uri()
OUTPUT = ROOT / "_test_screenshots"
OUTPUT.mkdir(parents=True, exist_ok=True)

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

        browser.close()

    # Summary
    n_pass = sum(1 for r in results if r["ok"])
    n_fail = sum(1 for r in results if not r["ok"])
    print()
    print("=" * 60)
    print("RESULTS: " + str(n_pass) + " passed, " + str(n_fail) + " failed")
    print("=" * 60)
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
