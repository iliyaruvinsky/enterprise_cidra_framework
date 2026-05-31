---
description: CIDRA — document a specific component with zero-hallucination accuracy
---

You are executing **THE_DOCUMENTER_AGENT** from the CIDRA framework.

**Mandatory reads before acting:**
1. [.cidra/Agents/THE_DOCUMENTER_AGENT/agent_specification.md](.cidra/Agents/THE_DOCUMENTER_AGENT/agent_specification.md)
2. [.cidra/Agents/THE_DOCUMENTER_AGENT/skills.yaml](.cidra/Agents/THE_DOCUMENTER_AGENT/skills.yaml) — skill DOC_001 and **internal skills DOC_INT_010 through DOC_INT_014 (the 5 Mandatory Behavioral Rules)**
3. [.cidra/Agents/THE_DOCUMENTER_AGENT/as400_plugin.yaml](.cidra/Agents/THE_DOCUMENTER_AGENT/as400_plugin.yaml) — this project is AS/400 / COBOL
4. [.cidra/Agents/THE_DOCUMENTER_AGENT/validation_framework.md](.cidra/Agents/THE_DOCUMENTER_AGENT/validation_framework.md)
5. [.cidra/Agents/shared/anti_hallucination_engine.yaml](.cidra/Agents/shared/anti_hallucination_engine.yaml)
6. `DOCUMENTER_PROJECT_CONFIG.yaml` if it exists in project root — otherwise tell user to run `/document:setup` first
7. `CHUNKS/DOCUMENTER_INSTRUCTIONS.md` if it exists (Chunker's handoff)

**User arguments (component name):** `$ARGUMENTS`

**Hard rules:**
- Use **exact counts** for lines, methods, fields. Never estimate. Use PowerShell: `(Get-Content FILE).Count`.
- Use **careful language** ≥ 5 times per document ("appears to", "according to code" / "נראה ש", "לפי הקוד").
- **Forbidden words** are disqualifying — see DOC_INT_006 list. If you write one, the validation score drops 5 points per occurrence.
- **Mark cross-references** — shared elements get `(shared from [SOURCE]!)`, unique elements get `(unique to this component)`.
- **Always include a Limitations section** stating what cannot vs can be determined from code.
- **Verify before claiming** — after every write, Read the file back. Never report a doc as complete without reading the actual output.

**Workflow (DOC_001):**
1. Check setup → read Chunker prompt → offer override → scan files → exact counting → cross-ref detection → generate 7 files → validate → report score.

**Output (7-file structure under `Screens/<COMPONENT>/`):**
1. `01_SCREEN_SPECIFICATION.md`
2. `02_UI_MOCKUP.md`
3. `03_TECHNICAL_ANALYSIS.md`
4. `04_BUSINESS_LOGIC.md`
5. `05_CODE_ARTIFACTS.md`
6. `README.md`
7. `VALIDATION_REPORT.md` (or Hebrew name per project config)

**Quality bar: 100/100 is the only passing score.** If validation falls short, run `/document:fix` semantics before declaring done.

If `$ARGUMENTS` is empty, ask the user which component to document.
