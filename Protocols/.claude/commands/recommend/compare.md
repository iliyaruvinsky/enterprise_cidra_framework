---
description: CIDRA — compare two technologies side-by-side
---

You are executing **THE_RECOMMENDER_AGENT** skill **REC_002 (recommend:compare)**.

**Reads:**
- [.cidra/Agents/THE_RECOMMENDER_AGENT/skills.yaml](.cidra/Agents/THE_RECOMMENDER_AGENT/skills.yaml) — skill REC_002 and internal skill REC_INT_002 (technology_mapping)
- [.cidra/Agents/THE_RECOMMENDER_AGENT/recommendation_strategies.yaml](.cidra/Agents/THE_RECOMMENDER_AGENT/recommendation_strategies.yaml)

**User arguments (tech1 tech2):** `$ARGUMENTS`

If fewer than 2 technologies given, ask the user for both.

**Produce a side-by-side comparison table** with columns:
- Technology
- Confidence (from REC_INT_002 mapping if available)
- Learning curve
- Migration complexity
- Pros (3-5 bullets)
- Cons (3-5 bullets)
- Best for (use cases)

If either technology is in REC_INT_002.mappings (ABAP, WebDynpro, COBOL, CPP), use the data there. Otherwise, base the comparison on documented characteristics; mark any claims you cannot ground in the framework's mapping as "based on general industry knowledge, not project-specific evidence".

Do not invent numbers. If a cost or timeline isn't grounded in either the framework data or the project documentation, say so.
