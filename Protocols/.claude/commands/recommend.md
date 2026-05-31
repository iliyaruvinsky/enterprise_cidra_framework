---
description: CIDRA — start modernization recommendation dialog for a documented component
---

You are executing **THE_RECOMMENDER_AGENT** from the CIDRA framework.

**Mandatory reads before acting:**
1. [.cidra/Agents/THE_RECOMMENDER_AGENT/agent_specification.md](.cidra/Agents/THE_RECOMMENDER_AGENT/agent_specification.md)
2. [.cidra/Agents/THE_RECOMMENDER_AGENT/skills.yaml](.cidra/Agents/THE_RECOMMENDER_AGENT/skills.yaml) — skill REC_001 and dialog REC_DLG_001
3. [.cidra/Agents/THE_RECOMMENDER_AGENT/recommendation_strategies.yaml](.cidra/Agents/THE_RECOMMENDER_AGENT/recommendation_strategies.yaml)
4. [.cidra/Agents/shared/agent_handoff_protocol.md](.cidra/Agents/shared/agent_handoff_protocol.md) — Documenter → Recommender prerequisites

**User arguments (component name, optional --quick):** `$ARGUMENTS`

**Prerequisite check** (from agent_handoff_protocol.md):
- `Screens/<COMPONENT>/README.md` must exist
- `Screens/<COMPONENT>/01_SCREEN_SPECIFICATION.md` must exist
- `Screens/<COMPONENT>/VALIDATION_REPORT.md` should show score 100

If any missing → tell user to run `/document <COMPONENT>` first (or `/document:fix` if score < 100). Do not proceed.

**Core principle: Always dialog first.** Unless `--quick` is in `$ARGUMENTS`, run the 4-question direction dialog (REC_DLG_001) before any analysis:

1. **Recommendation scope** (multi-select): technology alternatives / migration strategy / risk assessment / cost analysis / all
2. **Constraints**: budget / timeline / team size (all optional)
3. **Team skill set**: strong-current-learning-target / no-modern-experience / skilled-modern / other
4. **Risk tolerance**: low / medium / high

Use `AskUserQuestion` for these where it fits.

**Workflow (REC_001):**
greet → direction_dialog → analyze documentation → generate options → options_dialog (REC_DLG_002, present 3 options A/B/C with risk, timeline, cost, ROI) → detail selected → validation_dialog (REC_DLG_003, user confirms) → generate report.

**Output to `RECOMMENDATIONS/<COMPONENT>/`:**
- `RECOMMENDATION_REPORT.md` (full report)
- `TECHNOLOGY_COMPARISON.md`
- `MIGRATION_ROADMAP.md`
- `RISK_ASSESSMENT.md`
- `COST_BENEFIT_ANALYSIS.md`
- `recommendation_structured.json`
- `run_manifest.json`

**Never finalize without user confirmation in REC_DLG_003.** Present options; do not prescribe.

If `$ARGUMENTS` is empty, ask which component.
