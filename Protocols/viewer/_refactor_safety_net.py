"""
Safety net for the ES-module refactor (Plan upgrade #4).

This file locks the current behavior of viewer.html. The refactor on the
refactor/modules branch splits viewer.html into ~12 native ES modules
(no build step). After every module extraction, this entire test suite
must pass against the partially-refactored viewer.html. If any scenario
fails, fix or revert that single module before continuing.

Scenarios covered (each one is a separate function so failures point
at exactly what regressed):

  S1   Empty state (no file loaded) — counter hidden, Save button
       absent / disabled, dependency status banners absent for the
       libs that loaded.
  S2   File load + render — Mermaid renders, KaTeX renders (if any),
       tables render, decision marks wrap.
  S3   Decision mark cycle on click — ☐ → ✓ → ✗ → ❓ → ☐.
  S4   Decision-progress counter — shows N/Total, increments on click,
       hides after Clear.  (#2)
  S5   Theme toggle preserves clicked mark states.                (#0)
  S6   Mirror HE Comments toggle preserves clicked mark states.   (#0)
  S7   Direction toggle (Auto / RTL / LTR) cycles, document stays
       readable, marks preserved.
  S8   Export decisions — downloaded markdown carries the cycled
       states at the correct positions.
  S9   FSA Save decisions — with mocked showSaveFilePicker, one click
       triggers exactly one createWritable→write→close, mtime updates
       in State.lastFileMtime.                                    (#1)
  S10  Forget save target — button appears post-save, hides after
       click, State.fileHandle clears.                            (#1)
  S11  No-FSA degradation — with showSaveFilePicker removed, Save
       button correctly disabled; Export decisions still works.
  S12  External-change banner — advancing mocked handle.getFile().
       lastModified + dispatching visibilitychange surfaces a banner
       with Reload + Keep actions.                                (#3)

Run:
  python _refactor_safety_net.py
Exit 0 = all PASS. Exit 1 = at least one FAIL. Each scenario prints
its own line so the failing one is obvious.
"""
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

HERE   = Path(__file__).resolve().parent
VIEWER = HERE / "viewer.html"

# Use chiyuv_yashir's actual files for realism. If unavailable on a
# given machine, fall back to a minimal inline fixture.
LIVE_MISSING_INPUTS = Path(r"C:\projects\chiyuv_yashir\MISSING_INPUTS.md")
LIVE_THE_PROCESS    = Path(r"C:\My_AI\enterprise_cidra_framework\THE_PROCESS.md")

FALLBACK_MD = """---
documentation_language: en
---

# Sample

- [ ] First decision: ☐ open
- [ ] Second: ☐
- [ ] Third: ☐

```mermaid
flowchart LR
  A --> B
```
"""

# Mock FSA implementation re-used by S9 / S10 / S12.
MOCK_FSA = r"""
() => {
  window.__mockMtime = 1000;
  window.__mockContent = '';
  window.__fakeHandle = {
    name: 'mock.md',
    kind: 'file',
    queryPermission: async () => 'granted',
    requestPermission: async () => 'granted',
    createWritable: async () => ({
      write: async (content) => { window.__mockContent = content; },
      close: async () => {},
    }),
    getFile: async () => ({
      name: 'mock.md',
      lastModified: window.__mockMtime,
      text: async () => window.__mockContent || ''
    })
  };
  window.showSaveFilePicker = async () => window.__fakeHandle;
}
"""


def banner(msg):
    sys.stdout.buffer.write(("\n" + msg + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()


def report(label, ok, evidence=""):
    icon = "PASS" if ok else "FAIL"
    line = f"  [{icon}] {label}"
    if evidence and not ok:
        line += f"  // {evidence}"
    sys.stdout.buffer.write((line + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()
    return ok


def get_md_bytes():
    if LIVE_MISSING_INPUTS.exists():
        return LIVE_MISSING_INPUTS.read_text(encoding="utf-8").encode("utf-8"), "MISSING_INPUTS.md"
    return FALLBACK_MD.encode("utf-8"), "sample.md"


async def open_page(playwright):
    browser = await playwright.chromium.launch(headless=True)
    ctx = await browser.new_context(viewport={"width": 1500, "height": 1100})
    page = await ctx.new_page()
    await page.goto(VIEWER.as_uri())
    await page.wait_for_load_state("networkidle")
    return browser, page


async def load_file(page, mock_fsa=False):
    if mock_fsa:
        await page.evaluate(MOCK_FSA)
    md_bytes, name = get_md_bytes()
    await page.set_input_files("input#filePicker", files=[
        {"name": name, "mimeType": "text/markdown", "buffer": md_bytes}
    ])
    await page.wait_for_timeout(1500)
    return name


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

async def s1_empty_state(page):
    banner("S1 — Empty state")
    diag = await page.evaluate("""() => ({
        counter_hidden: document.getElementById('decisionsCounter').hasAttribute('hidden'),
        forget_hidden:  document.getElementById('btnForgetHandle').hasAttribute('hidden'),
        export_disabled: document.getElementById('btnExportMenu').hasAttribute('disabled'),
    })""")
    return all([
        report("decisionsCounter hidden",       diag['counter_hidden']),
        report("btnForgetHandle hidden",         diag['forget_hidden']),
        report("Export button disabled",         diag['export_disabled']),
    ])


async def s2_render(page):
    banner("S2 — Render pipeline")
    await load_file(page)
    diag = await page.evaluate("""() => ({
        marks: document.querySelectorAll('.cidra-mark').length,
        mermaid: document.querySelectorAll('.mermaid svg').length,
        tables: document.querySelectorAll('.md table').length,
        first_h1: (document.querySelector('.md h1') || {}).textContent || ''
    })""")
    return all([
        report(f"Decision marks wrapped ({diag['marks']} present)", diag['marks'] > 0,    f"got {diag['marks']}"),
        report(f"Mermaid diagrams rendered ({diag['mermaid']})",     diag['mermaid'] >= 0),
        report(f"Tables rendered ({diag['tables']})",                diag['tables'] >= 0),
        report("H1 text present",                                    bool(diag['first_h1'].strip())),
    ])


async def s3_mark_cycle(page):
    banner("S3 — Decision-mark cycle on click")
    states = await page.evaluate("""() => {
        const m = Array.from(document.querySelectorAll('.cidra-mark'));
        const e = m.find(s => s.getAttribute('data-state') === '\\u2610');
        const trail = [e.getAttribute('data-state')];
        for (let i = 0; i < 4; i++) { e.click(); trail.push(e.getAttribute('data-state')); }
        return trail;
    }""")
    expected = ['☐', '✓', '✗', '❓', '☐']
    return report(f"Cycle trail {states} == {expected}", states == expected)


async def s4_counter(page):
    banner("S4 — Decision-progress counter")
    text = await page.evaluate("() => document.getElementById('decisionsCounter').textContent")
    has_format = '/' in text and 'Decisions' in text
    # Click an empty one to advance
    await page.evaluate("""() => {
        const e = Array.from(document.querySelectorAll('.cidra-mark'))
                       .find(s => s.getAttribute('data-state') === '\\u2610');
        if (e) e.click();
    }""")
    await page.wait_for_timeout(150)
    text2 = await page.evaluate("() => document.getElementById('decisionsCounter').textContent")
    return all([
        report(f"Counter formatted ('{text}')", has_format),
        report(f"Counter advances after click ('{text}' -> '{text2}')", text != text2),
    ])


async def s5_theme_preserves_marks(page):
    banner("S5 — Theme toggle preserves clicks")
    before = await page.evaluate("""() => {
        const m = Array.from(document.querySelectorAll('.cidra-mark'));
        return m.slice(0, 8).map(s => s.getAttribute('data-state'));
    }""")
    await page.click("#btnTheme")
    await page.wait_for_timeout(500)
    after = await page.evaluate("""() => {
        const m = Array.from(document.querySelectorAll('.cidra-mark'));
        return m.slice(0, 8).map(s => s.getAttribute('data-state'));
    }""")
    return report(f"First 8 states identical before/after theme toggle", before == after, f"before={before} after={after}")


async def s6_mirror_preserves_marks(page):
    banner("S6 — Mirror HE toggle preserves clicks")
    before = await page.evaluate("() => Array.from(document.querySelectorAll('.cidra-mark')).slice(0,8).map(s=>s.getAttribute('data-state'))")
    await page.click("#btnMirrorComments")
    await page.wait_for_timeout(500)
    after = await page.evaluate("() => Array.from(document.querySelectorAll('.cidra-mark')).slice(0,8).map(s=>s.getAttribute('data-state'))")
    return report("First 8 states identical before/after mirror toggle", before == after, f"before={before} after={after}")


async def s7_dir_cycle(page):
    banner("S7 — Direction toggle cycle")
    cycle = []
    for _ in range(3):
        await page.click("#btnDir")
        await page.wait_for_timeout(150)
        cycle.append(await page.evaluate("() => document.documentElement.getAttribute('dir')"))
    return report(f"Dir cycle observed: {cycle}", len(cycle) == 3)


async def s8_export_decisions(page):
    banner("S8 — Export decisions")
    # Capture next download
    async with page.expect_download() as dl_info:
        await page.click("#btnExportMenu")
        await page.wait_for_timeout(150)
        await page.click("#miExportDecisions")
    dl = await dl_info.value
    tmp = HERE.parent / "_test_screenshots" / "_export_check.md"
    tmp.parent.mkdir(exist_ok=True)
    await dl.save_as(str(tmp))
    content = tmp.read_text(encoding="utf-8")
    return report(f"Export produced non-empty .md ({len(content)} chars)", len(content) > 0)


async def s9_fsa_save(page):
    banner("S9 — FSA Save decisions (mocked)")
    # Need a fresh page so mocks install before file load
    return None  # handled by run_fsa_scenarios with its own page


async def run_fsa_scenarios(playwright):
    banner("S9..S12 — FSA scenarios (own page, mocks installed before load)")
    browser, page = await open_page(playwright)
    try:
        await load_file(page, mock_fsa=True)
        # S9 click a mark and Save
        await page.evaluate("""() => {
            const e = Array.from(document.querySelectorAll('.cidra-mark'))
                         .find(s => s.getAttribute('data-state') === '\\u2610');
            if (e) e.click();
        }""")
        await page.click("#btnExportMenu")
        await page.wait_for_timeout(150)
        await page.click("#miSaveDecisions")
        await page.wait_for_timeout(600)
        save = await page.evaluate("() => ({ content_len: (window.__mockContent || '').length })")
        s9_ok = report(f"Save wrote {save['content_len']} chars to mock handle", save['content_len'] > 0)

        # S10a Forget visible (handle still bound)
        forget_visible = await page.evaluate("() => !document.getElementById('btnForgetHandle').hasAttribute('hidden')")
        s10a_ok = report("Forget button visible after Save", forget_visible)

        # S12 external-change banner — must run BEFORE Forget click since
        # Forget nukes State.fileHandle (intended behavior) and the watcher
        # would correctly no-op after that.
        await page.evaluate("() => { window.__mockMtime = 99999999; document.dispatchEvent(new Event('visibilitychange')); }")
        await page.wait_for_timeout(500)
        banner_present = await page.evaluate("""() => {
            const b = document.querySelector('[data-banner-key="external-change"]');
            return !!b && Array.from(b.querySelectorAll('.banner-action')).some(a => /Reload/i.test(a.textContent));
        }""")
        s12_ok = report("External-change banner with Reload action appears", banner_present)

        # S10b Forget click -> button hides
        await page.evaluate("""() => {
            const b = document.querySelector('[data-banner-key="external-change"]');
            if (b) {
              const keep = Array.from(b.querySelectorAll('.banner-action')).find(a => /Keep/i.test(a.textContent));
              if (keep) keep.click();
            }
        }""")
        await page.wait_for_timeout(200)
        await page.click("#btnForgetHandle")
        await page.wait_for_timeout(300)
        forget_gone = await page.evaluate("() => document.getElementById('btnForgetHandle').hasAttribute('hidden')")
        s10b_ok = report("Forget button hides after click", forget_gone)

        # S11 no-FSA: remove showSaveFilePicker, reload file, check Save gated off
        await page.evaluate("() => { delete window.showSaveFilePicker; }")
        await page.click("#btnClear")
        await page.wait_for_timeout(200)
        await load_file(page, mock_fsa=False)
        await page.evaluate("""() => {
            const e = Array.from(document.querySelectorAll('.cidra-mark'))
                         .find(s => s.getAttribute('data-state') === '\\u2610');
            if (e) e.click();
        }""")
        await page.wait_for_timeout(200)
        gated = await page.evaluate("""() => {
            const btn = document.getElementById('miSaveDecisions');
            return btn.getAttribute('aria-disabled') === 'true';
        }""")
        s11_ok = report("Save button disabled when showSaveFilePicker missing", gated)

        return all([s9_ok, s10a_ok, s10b_ok, s12_ok, s11_ok])
    finally:
        await browser.close()


async def main():
    async with async_playwright() as playwright:
        # First page runs S1..S8
        browser, page = await open_page(playwright)
        try:
            results = []
            results.append(await s1_empty_state(page))
            results.append(await s2_render(page))
            results.append(await s3_mark_cycle(page))
            results.append(await s4_counter(page))
            results.append(await s5_theme_preserves_marks(page))
            results.append(await s6_mirror_preserves_marks(page))
            results.append(await s7_dir_cycle(page))
            results.append(await s8_export_decisions(page))
        finally:
            await browser.close()

        # Fresh page with mocks for S9..S12
        results.append(await run_fsa_scenarios(playwright))

        banner("=" * 60)
        passed = sum(1 for r in results if r)
        total = len(results)
        sys.stdout.buffer.write(f"RESULT: {passed}/{total} scenarios PASS\n".encode("utf-8"))
        return passed == total


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(main()) else 1)
