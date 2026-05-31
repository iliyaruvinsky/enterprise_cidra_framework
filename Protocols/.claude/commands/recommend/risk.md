---
description: CIDRA — run risk assessment for a component without full recommendation
---

You are executing **THE_RECOMMENDER_AGENT** skill **REC_003 (recommend:risk)**.

**Reads:**
- [.cidra/Agents/THE_RECOMMENDER_AGENT/skills.yaml](.cidra/Agents/THE_RECOMMENDER_AGENT/skills.yaml) — skill REC_003 and internal skill REC_INT_003 (risk_scoring)
- The Documenter output at `Screens/<COMPONENT>/` (must exist)

**User arguments (component):** `$ARGUMENTS`

If `$ARGUMENTS` empty, ask which component.

**Prerequisite:** documentation must exist for the component. If missing → tell user to run `/document <COMPONENT>` first.

**Score risk on the 5 weighted factors from REC_INT_003:**

| Factor | Weight | Indicators |
|--------|--------|-----------|
| Technical complexity | 0.30 | LOC, cyclomatic, dependencies |
| Business criticality | 0.25 | User impact, financial impact |
| Team readiness | 0.20 | Skill gap, domain knowledge |
| Testing coverage | 0.15 | Test automation % |
| Timeline pressure | 0.10 | Deadline horizon |

For each factor, extract the indicator from the documentation (exact counts only — never estimate), classify low/medium/high, and compute the weighted score 0-100.

**Output:**
- Risk score (total) and band (0-30 low / 31-60 medium / 61-100 high)
- Per-factor breakdown with the indicator value and classification
- Top 3 mitigation suggestions tied to whichever factors scored highest

For any indicator you cannot ground in the documentation (e.g., financial impact not in the docs), state "not available from documentation" and skip that sub-indicator rather than guessing.
