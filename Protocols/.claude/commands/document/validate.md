---
description: CIDRA — run 100-point validation on existing documentation
---

You are executing **THE_DOCUMENTER_AGENT** skill **DOC_003 (document:validate)**.

**Reads:**
- [.cidra/Agents/THE_DOCUMENTER_AGENT/skills.yaml](.cidra/Agents/THE_DOCUMENTER_AGENT/skills.yaml) — skill DOC_003 (deductions table)
- [.cidra/Agents/THE_DOCUMENTER_AGENT/validation_framework.md](.cidra/Agents/THE_DOCUMENTER_AGENT/validation_framework.md)

**User arguments (path to docs dir):** `$ARGUMENTS`

If `$ARGUMENTS` is empty, ask which `Screens/<COMPONENT>/` directory to validate.

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
