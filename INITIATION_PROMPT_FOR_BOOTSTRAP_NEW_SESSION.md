## B+CIDRA — Initiation prompt for a fresh Claude Code session
## (adapted from the XSODUS 4-agent template; B+CIDRA runs single-agent)

Use this checklist whenever a fresh Claude Code session opens against the
B+CIDRA framework (`C:\My_AI\enterprise_cidra_framework`). The intent: make the
new session productive from minute one with no re-learning of state.

This is NOT only for emergency low-context closeouts. It also covers:
(a) End-of-day closeout when context is heavy and the next sprint starts tomorrow.
(b) Pivot-to-fresh-sprint refresh when priorities shift and you want a clean slate.
(c) Periodic hygiene refresh (every 1–2 weeks) to keep slash-command stubs lean.

---

### 1. State summary — fill in at every closeout

Update the "Current state" block below before opening the next session.
The fresh agent reads this block first.

**Current state (last updated: 2026-06-02)**
- `main` tip: `c782035` — Viewer #3: external-change watcher via visibilitychange + focus
- Active long-lived branches:
    - `refactor/modules`: `145ae84` — viewer.html ES-module split, baseline 9/9 PASS locked, execution pending. Resume doc at `Protocols/viewer/REFACTOR_RESUME.md`.
- Open items (in priority order):
    1. **chiyuv_yashir (`C:\projects\chiyuv_yashir\`)** — Mode 1 (B+CID) run paused at the BRN_R2 customer-acknowledgment gate. Three 🔴 critical gaps in `MISSING_INPUTS.md` await customer marks: (a) CA 2E (Synon) action-diagram model, (b) ~57 missing sibling-program sources (XFKB/UPKB/UPRB families), (c) callers / runtime triggers. Iliya is communicating these to the client. Once marked, update `BRAINSTORM_OUTPUT.yaml.acknowledged_gaps` and flip `ready_for_chunker: true`, then `/chunk`.
    2. **C/C++ dry-run** — fresh project to validate the post-AS/400 framework end-to-end. Blocked on source-path delivery from Iliya. When path arrives, propose `-ProjectFolder` + `-ComponentId`, run `Scripts\bootstrap.ps1` (no `-SourceRenameTo` for C/C++; `-ForceFramework` not needed post-F7 sentinel relocation).
    3. **`refactor/modules` execution** — viewer.html (~4800 lines) splits into 12 native ES modules (no build step). 7 dependency-ordered extraction waves + 1 final-assembly wave. Estimated 1 working week. Safety net (`_refactor_safety_net.py`) must stay at 9/9 PASS after every wave. Full plan in `Protocols/viewer/REFACTOR_RESUME.md`.
- Parked / blocked-external: Customer-facing copy of `MISSING_INPUTS.md` — once Iliya receives marked answers from Maccabi, ingest back into `BRAINSTORM_OUTPUT.yaml`. No technical blocker; waiting on human turnaround.
- What shipped on 2026-06-02 (most recent → oldest):
    - `145ae84` (on `refactor/modules`) — Refactor branch setup: 9-scenario safety net + REFACTOR_RESUME.md
    - `c782035` — Viewer #3: external-change watcher via visibilitychange + focus
    - `0cd37b9` — Viewer #1: FSA direct save-back with IndexedDB-persisted file handle
    - `fb2c26f` — Viewer #2: decision-progress counter in toolbar
    - `828ae26` — Viewer #0: preserve clicked decision-mark states across re-renders (precursor bug fix discovered during plan validation)
    - `424b7ef` — De-hardcode framework from AS/400: plugin-agnostic /document + general_plugin.yaml + c_cpp_plugin.yaml + technology elicitation
    - `6363cdd` — Brainstormer slash-command stubs: wire ROADMAP.md into emission + refresh
    - `414138d` — Brainstormer: emit ROADMAP.md as the customer's journey map

When the new session opens, the agent's first action is to verify the
state block matches what's actually on disk (see Section 5).

---

### 2. Mandatory first reads for the fresh session

In this order:

1. **This file** — top-to-bottom.
2. **`C:\Users\iliya\.claude\projects\g--My-Drive-Maccabi-AI-------------------\memory\MEMORY.md`** — every entry. Standing directives + user/project memory.
3. **`CLAUDE.md`** in the framework root — project-level instructions.
4. **`THE_PROCESS.md`** — strategic overview of the B+CIDRA pipeline (Mode 1 / 2 / 3).
5. **`RUNBOOK.md`** — step-by-step execution guide.
6. **The latest commits on `main`**: `git log --oneline -10`.
7. **If continuing a long-lived branch**: that branch's `RESUME.md` (e.g. `Protocols/viewer/REFACTOR_RESUME.md` for the module refactor).

Verify the framework HEAD on disk matches origin/main with `git status` + `git log`.

---

### 3. Standing directives (firing-level — current as of 2026-06-02)

These rules apply to every agent action. Violating them is a session-level breach.

**Framework UX north star** ([[feedback-framework-ux-principles]]):
- Enterprise customers are the audience — low LLM context, time-poor, won't fight ambiguous UIs. Per touchpoint: laconic, clear, predictable, transparent, user-friendly, deterministic structure.
- Same starting point + same milestones every project. The customer's first artifact is always `ROADMAP.md`; the first decision surface is always `MISSING_INPUTS.md`.
- The viewer (`Protocols/viewer/viewer.html`) is a **communication tool with the customer**, not just a renderer. Decisions, gap acknowledgments, modernization sign-offs flow through artifacts the customer opens, clicks through, exports back. Chat (Claude Code) stays as the second channel.

**No AI-default graphics** ([[feedback-no-default-graphics]]):
- B+CIDRA is meant to look distinct. Avoid Bootstrap/Material/Tailwind-default aesthetics, generic emoji-heavy chrome, stock icon libraries. Functional semantic colors (green ✓ / red ✗ / amber ❓) are fine because they're indicators, not decoration.
- When Iliya supplies his design rules, those override defaults.

**Shell callout in commands** ([[feedback-shell-callout]]):
- Every command block starts with **POWERSHELL** / **CMD** / **BASH** in caps. PowerShell is Iliya's default (Windows 11). PowerShell 5.1 is the lowest supported; PowerShell 7 is preferred for Unicode/Hebrew path handling.

**Language separation** ([[feedback-language-separation]]):
- Chat replies: **English only**.
- Produced files / customer-facing artifacts: project language (Hebrew/bilingual for Maccabi projects; English for framework-level docs).
- Code, identifiers, command names: English always.
- Quoting Hebrew comments/text from source in chat is fine; surrounding commentary stays English.

**File-based source of truth (B+CIDRA architectural invariant)**:
- `.md` and `.yaml` files in the project tree (`BRAINSTORM_OUTPUT.yaml`, `MISSING_INPUTS.md`, `ROADMAP.md`, `Screens/<COMPONENT>/`, `RECOMMENDATIONS/<COMPONENT>/`) ARE the state. Not a database. Not a SaaS. This is the moat for enterprise (auditable, air-gap friendly, no installer).
- Whatever UI lives in front, those files stay authoritative. Architectural changes that violate this require explicit owner approval.

**Anti-hallucination + exact counts**:
- Per `DOC_INT_010 – DOC_INT_014`: verify before claiming, no assumptions as facts, mandatory verification workflow, honest reporting, anti-hallucination mandate.
- Never estimate line counts / method counts / field counts. Use `(Get-Content FILE).Count` in PowerShell. Always.
- Use careful language in produced docs: English "appears to / according to code"; Hebrew "נראה ש / לפי הקוד". Minimum 5 occurrences per doc.

**Decide, don't ask the obvious**:
- In auto mode, the agent makes and reports obvious / reversible / in-mandate decisions without asking. Asks only for ambiguous, irreversible, or owner-governed forks (project naming, target technology, budget, scope).
- The bar for asking: would a competent contractor with full context still ask? If no → decide.

**Pre-draft owner questions**:
- For substantive feature work, ask the decision-shaping forks **before** drafting code, not after. Batched ≤4. Sharp forks only.
- Use plan mode for non-trivial implementation work — the Explore→Plan→ExitPlanMode flow caught a shippable-severity bug in the most recent feature ship (#0 mark preservation).

**Workflow tool when ultracode is on**:
- Under ultracode, default to Workflow for every substantive task. Token cost is not a constraint; correctness is.
- Workflow scripts CANNOT use `Date.now()`, `Math.random()`, or argless `new Date()` — they throw (resume safety). Pass timestamps in via `args`; stamp results after the workflow returns.
- Workflow agents run in their own context — heavy reads (full file dumps) belong in agents, not in the parent loop.

**Steps format for command sequences**:
- Multi-command sequences are explicit numbered Steps:
    ```
    ### Step 1 — title
    <command>

    ### Step 2 — title
    <command>
    ```
- Iliya uses the step number as the anchor to report results back.

**Slash-command stub line budget**:
- Files under `Protocols/.claude/commands/*.md` are the agent's primary load path on every `/slash` invocation. Bloat costs tokens on every use.
- **Healthy target: ≤200 lines** per stub. **Soft warning: 250 lines.** **Hard cap: 400 lines** (firing-level).
- If a stub crosses 250, factor reusable content into the agent's `skills.yaml` (which the stub already references via Mandatory Reads) and trim the stub to its dispatch logic. Don't duplicate skill descriptions in the stub.
- At session close: `Get-ChildItem Protocols/.claude/commands -Recurse -Filter *.md | ForEach-Object { '{0,5}  {1}' -f (Get-Content $_.FullName).Count, $_.FullName }` — flag overflows.

**Long branches carry a RESUME doc**:
- Any branch that may outlive a session writes `<scope>_RESUME.md` (or `REFACTOR_RESUME.md`) at the branch root so the next session picks up cleanly. Module list, wave order, safety-net commands, known sharp edges.

---

### 4. Verification discipline (proven across the viewer-upgrade rollout — REUSE)

These four practices carried the #0 → #3 viewer rollout cleanly (4 commits to main, zero false-DONE rounds):

**Verify against LIVE CODE — never the report, the memory, or a screenshot alone.**
Before endorsing any change, before acting on any finding, and before re-touching a file: read the actual `git diff` and run the relevant probe (Playwright for viewer, PowerShell + `Test-Path` for filesystem, `git log --oneline` for branch state). The #0 bug (theme toggle nukes decision marks) was missed by 3 previous viewer audits because they ran against the report shape, not the actual `render()` code path. Plan mode's Explore agent caught it.

**Adversarial verify inside the workflow that did the change.**
Every multi-agent workflow ends with a verify phase where each apply agent's claims are re-tested against the live tree. Pipeline pattern: `apply(F) → verify(F)` per fix, not `apply-all-fixes → verify-all`. This caught a missed name-mismatch (`documenter_directives` → `documenter_config`) on the second fix workflow today.

**Playwright is mandatory for every viewer change.**
The viewer ships to enterprise customers. Every change ends with a probe that:
- Loads a real fixture (`chiyuv_yashir/MISSING_INPUTS.md` is the standing reference) — not an inline string
- Asserts both DOM facts (counts, attributes) AND visual facts (`page.screenshot` saved to `_test_screenshots/` for cross-session diff)
- Uses `sys.stdout.buffer.write(... .encode("utf-8"))` for output — Windows console cp1252 dies on ☐/✓/✗/❓

**Working-tree hygiene before every commit.**
Run `git status --short` first. Stage explicit paths only (`git add Protocols/viewer/viewer.html`), never `git add -A`. Untracked probe scripts under `Protocols/viewer/_*.py` and `_test_screenshots/` are local-only — they stay untracked unless explicitly designated as fixtures.

---

### 5. First actions for the fresh session (verbatim)

After absorbing this file + the mandatory reads (Section 2):

1. **POWERSHELL** — verify framework on disk:
    ```
    cd "C:\My_AI\enterprise_cidra_framework"
    git log --oneline -10
    git status --short
    git branch -a
    ```
    Confirm `main` tip matches Section 1 "Current state". If mismatched, **stop and ask Iliya** — something landed since the state was written.

2. Print the absorbed-bootstrap acknowledgment to chat:
    > Bootstrap absorbed. Framework HEAD: `<sha>` on `main`. Active branches: `<list>`. Standing directives confirmed: framework UX north star, no AI-default graphics, shell callout, language separation, file-based source of truth, anti-hallucination, decide-don't-ask-obvious, workflow-under-ultracode. Open items: `<count>`. Ready for direction.

3. If a long-lived branch has a `RESUME.md`, read it next. Do NOT switch to that branch unless Iliya directs.

4. Wait for Iliya's direction. Default posture is **stand by**. If he asks for status, surface the open-items list from Section 1.

---

### 6. Per-task tooling reminders

**Plan mode** — for any feature work over 30 minutes. The Explore → Plan → ExitPlanMode flow forces validation before code. Today's #0 bug discovery proved this saves more than it costs.

**Workflow tool** — for fan-out + parallel apply→verify. Under ultracode, the default for substantive tasks. Patterns:
- Adversarial verify panel: `apply(F) → 3 independent skeptics verify(F)`
- Loop-until-dry for unknown-size discovery
- Multi-modal sweep: same target, different lenses
- Completeness critic: "what's missing?" pass at the end

**TodoWrite** — for tasks of ≥3 distinct steps. Mark in-progress BEFORE starting, completed IMMEDIATELY after finishing. One in-progress at a time.

**AskUserQuestion** — only for ambiguous / irreversible / owner-governed forks. Not for "is this plan okay" (that's ExitPlanMode's job).

**Memory** — at `C:\Users\iliya\.claude\projects\g--My-Drive-Maccabi-AI-------------------\memory\`. Read on relevant turns. Update when user explicitly says "remember X" or when a surprising/non-obvious decision was made. Index in `MEMORY.md`.

---

### 7. Git discipline

The current arrangement: **the agent runs git mutations** (add, commit, push) — Iliya does not. Per-path discipline still applies:

- `git status --short` before every commit. FLAG stray untracked files in untracked locations; commit only the intended paths.
- `git add <path1> <path2>` — never `git add -A` or `git add .`.
- Commit messages: subject + 2-line gap + body. HEREDOC pattern via `cat <<'EOF'` for multi-paragraph bodies (PowerShell-safe).
- Co-author trailer mandatory: `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`.
- Push immediately after commit unless the user said otherwise.
- Branches: `main` is shippable; long-lived branches carry RESUME docs (see Section 3).

---

### 8. Final rule

Do NOT continue feature work during a closeout / bootstrap-preparation pass. Focus is session closeout, documentation hygiene, branch handoff. Feature work resumes in the next session.

---

*Drafted from the XSODUS 4-agent initiation template (2026-05-29 revision).*
*Adapted for B+CIDRA single-agent flow against `C:\My_AI\enterprise_cidra_framework`.*
*Last edited: 2026-06-02.*
