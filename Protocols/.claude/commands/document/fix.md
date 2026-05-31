---
description: CIDRA — auto-fix common documentation issues to reach 100/100
---

You are executing **THE_DOCUMENTER_AGENT** skill **DOC_004 (document:fix)**.

**User arguments (path to docs dir):** `$ARGUMENTS`

**Reads:**
- [.cidra/Agents/THE_DOCUMENTER_AGENT/skills.yaml](.cidra/Agents/THE_DOCUMENTER_AGENT/skills.yaml) — skill DOC_004
- The 7 documentation files at the path
- The actual source code (to verify counts when fixing)

**Fix in this order:**
1. **Remove forbidden words** (DOC_INT_006 list) — replace each with factual description, never a synonym from the same forbidden list.
2. **Add careful language** if fewer than 5 occurrences — apply where claims are inferential, not where they describe verified code structure.
3. **Add a Limitations section** if missing — split into "What CANNOT be determined" and "What IS known from code".
4. **Mark cross-references** — for each element, check it against the shared elements list and tag `(shared from [SOURCE]!)` or `(unique to this component)`.
5. **Update counts** to match exact actual counts from source — use `(Get-Content FILE).Count` and verify each claimed number.

**After every fix: Read the file back to confirm the change applied.** Never report success without verification (DOC_INT_010 RULE 1).

When done, re-run the validation logic from `/document:validate` and report the new score. If still under 100, list which checks still fail and what the user needs to decide.
