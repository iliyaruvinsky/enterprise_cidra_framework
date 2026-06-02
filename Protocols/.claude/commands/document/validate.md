---
description: CIDRA — run 100-point validation on existing documentation
---

You are executing **THE_DOCUMENTER_AGENT** skill **DOC_003 (document:validate)**.

**Reads:**
- [.cidra/Agents/THE_DOCUMENTER_AGENT/skills.yaml](.cidra/Agents/THE_DOCUMENTER_AGENT/skills.yaml) — skill DOC_003 (deductions table)
- [.cidra/Agents/THE_DOCUMENTER_AGENT/validation_framework.md](.cidra/Agents/THE_DOCUMENTER_AGENT/validation_framework.md)

**User arguments (path to docs dir):** `$ARGUMENTS`

If `$ARGUMENTS` is empty, ask which `Screens/<COMPONENT>/` directory to validate.

---

## Primary path: invoke the PowerShell scorer

The framework ships a 488-line PowerShell scorer with 4 profiles
(maccabi_icm / enterprise_client / internal_team / quick_notes) and 11
checks. Prefer it over inline LLM scoring — it is deterministic and
produces the same numbers every run.

### Step 1 — derive ConfigProfile

Look up the profile in this order and stop at the first hit:

1. `DOCUMENTER_PROJECT_CONFIG.yaml` → `documenter.config_profile` (if present)
2. `DOCUMENTER_PROJECT_CONFIG.yaml` → `documenter.template`, map:
   - `enterprise_7_file` → `maccabi_icm`
   - `compact_5_file` → `internal_team`
   - `quick_3_file` → `quick_notes`
   - anything else / custom → `enterprise_client`
3. `BRAINSTORM_OUTPUT.yaml` → `documenter_config.template` (key name is
   `documenter_config:` — NOT `documenter_directives:`), apply the same
   mapping as #2
4. Default → `maccabi_icm`

### Step 2 — locate the source directory

- If `DOCUMENTER_PROJECT_CONFIG.yaml` defines a source directory, use it.
- Otherwise default to `"Source Code"` (the conventional CIDRA layout).
  Quote the path so the space survives.

### Step 3 — run the scorer

**POWERSHELL** (run from project root):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File `
  .cidra/Agents/THE_DOCUMENTER_AGENT/scripts/Validate-Documentation.ps1 `
  -DocPath "$ARGUMENTS" `
  -SourcePath "Source Code" `
  -ConfigProfile <derived-profile>
```

Capture stdout, stderr, and `$LASTEXITCODE`.

### Step 4 — handle the result

- **Scorer succeeded** (exit 0 or 1; both are valid scorer outcomes — 0
  means passing, 1 means fixes required, both are legitimate scores):
  - Summarize for the user: configuration used, final score, list of
    failed checks, and the certification line printed by the scorer
    ("READY FOR DELIVERY" / "FIXES REQUIRED" / "MODERATE FIXES REQUIRED"
    / "MAJOR REWORK NEEDED").
  - Persist the scorer's stdout to `<DocPath>/VALIDATION_REPORT.md` (or
    the Hebrew name per project config) wrapped in a fenced block, plus
    a one-paragraph LLM-written summary at the top in the project's
    documentation language.
  - **Done.** Do not run the inline path.

- **Scorer unavailable or crashed** (the `.ps1` file is missing,
  `pwsh` is not on PATH, or the process aborted before printing
  `END OF VALIDATION` — distinct from "scored low"):
  - Tell the user the scorer was unavailable and you are falling back to
    inline LLM scoring.
  - Continue to the fallback path below.

---

## Fallback path: inline LLM scoring

Use this only when the scorer cannot run. The deductions table is the
same one the scorer applies, kept here so a scorer-less environment
still produces a defensible number.

**Run all checks. Starting score: 100.**

| Check | Deduction |
|-------|-----------|
| Wrong file count (≠ 7) | -30 |
| Forbidden words (DOC_INT_006 list) | -5 each |
| Missing careful language (<5 occurrences) | -10 |
| Estimate language ("approximately", "roughly", "about") | -15 each |
| Missing Limitations section | -20 |
| Missing cross-reference marking | -25 |
| Inaccurate line count | -40 |
| Inaccurate element count | -15 per element type |

**Verify line counts and element counts against actual source code** — open the source, count exactly with `(Get-Content FILE).Count`, compare to what the doc claims.

**Output a validation report** to `<path>/VALIDATION_REPORT.md` (or Hebrew name per project config) with:
- Files scanned
- Exact counts verification (with commands used)
- Cross-reference check results
- Language checks (forbidden words count, careful language count)
- Final score
- Certification line: "Ready for delivery" (100) or "Needs fixes" (<100) with specific items

Only 100/100 passes.
