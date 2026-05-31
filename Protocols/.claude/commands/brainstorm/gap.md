---
description: CIDRA — re-issue the MISSING_INPUTS.md checklist for the current checkpoint
---

You are executing **THE_BRAINSTORMER_AGENT** skill **BRN_005 (continuous_gap_check)** — a CRITICAL skill.

**Reads:**
- [.cidra/Agents/THE_BRAINSTORMER_AGENT/skills.yaml](.cidra/Agents/THE_BRAINSTORMER_AGENT/skills.yaml) — skill BRN_005
- `BRAINSTORM_OUTPUT.yaml` at project root — what's known and what's still gap-listed
- Current state of the project — has `/chunk` run? Has `/document` run? Has `/document:validate` run?

**Determine current checkpoint:**

| State | Checkpoint to issue |
|-------|---------------------|
| `/brainstorm` done but `/chunk` not run yet | Checkpoint 1 — pre-chunking |
| `/chunk` done, partial `/document` work | Checkpoint 2 — mid-documentation |
| `/document:validate` has run | Checkpoint 3 — post-validation |

**Produce a refreshed `MISSING_INPUTS.md`** with:
- 🔴 CRITICAL items still unfilled
- 🟡 HIGH items still unfilled
- 🟢 MEDIUM items still unfilled
- ✗ Acknowledged gaps from previous checkpoints
- New items the recent work has revealed (e.g. "the chunker discovered 18 external programs — sources still missing")

**Refresh history table** at the bottom must record what changed since the last issuance.

This is non-optional. Per BRN_010, gaps are surfaced even if the customer didn't ask.
