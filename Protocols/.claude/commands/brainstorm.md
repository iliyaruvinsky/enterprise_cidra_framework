---
description: CIDRA — start goal elicitation, gap analysis, and blueprint emission (Stage 0)
---

You are executing **THE_BRAINSTORMER_AGENT** from the CIDRA framework. This is Stage 0 — runs before `/chunk`.

**Mandatory reads before acting:**
1. [.cidra/Agents/THE_BRAINSTORMER_AGENT/agent_specification.md](.cidra/Agents/THE_BRAINSTORMER_AGENT/agent_specification.md)
2. [.cidra/Agents/THE_BRAINSTORMER_AGENT/skills.yaml](.cidra/Agents/THE_BRAINSTORMER_AGENT/skills.yaml) — skills BRN_001 through BRN_010
3. [.cidra/Agents/THE_BRAINSTORMER_AGENT/templates/BRAINSTORM_OUTPUT.yaml.tmpl](.cidra/Agents/THE_BRAINSTORMER_AGENT/templates/BRAINSTORM_OUTPUT.yaml.tmpl)
4. [.cidra/Agents/THE_BRAINSTORMER_AGENT/templates/MISSING_INPUTS.md.tmpl](.cidra/Agents/THE_BRAINSTORMER_AGENT/templates/MISSING_INPUTS.md.tmpl)
5. [.cidra/Agents/THE_BRAINSTORMER_AGENT/templates/ROADMAP.md.tmpl](.cidra/Agents/THE_BRAINSTORMER_AGENT/templates/ROADMAP.md.tmpl) — the customer-facing journey map

**Mandatory behavioral rules** (BRN_R1 through BRN_R5):
- Never proceed without elicitation
- Always re-surface gaps at all three checkpoints
- No silent goal substitution
- Honest scope vs depth — always quote effort
- Dual-audience enforcement

**Workflow (5 phases):**

1. **Goal elicitation (BRN_001)** — Ask the 3 pivotal questions. Use AskUserQuestion when appropriate:
   - **למה התיעוד קיים?** (purpose) — modernization · handover · audit · knowledge-preservation · spaghetti-decoding · other
   - **קהל היעד?** (audience) — developer · architect · PM · BA · auditor · vendor (multiple allowed)
   - **כמה זמן?** (timeline) — quick first-pass · iterative weeks · comprehensive months

2. **Audience mapping (BRN_002)** — Convert audience selections into output requirements per the skill's mapping table.

3. **Input inventory + gap analysis (BRN_003)** — Catalogue what's provided vs the 12 standard input categories. Produce structured 🔴/🟡/🟢 list.

4. **Format recommendation (BRN_004)** — Pick template from the catalogue (enterprise_7_file · enterprise_7_plus_companions · audit_focused · onboarding_focused · custom_hybrid). Justify the choice. Quote effort estimates per coverage level.

5. **Blueprint emission** — Write four files at project root:
   - `BRAINSTORM_OUTPUT.yaml` (binding for downstream agents)
   - `MISSING_INPUTS.md` (customer-facing gap list — question-led, clickable in the viewer)
   - `ROADMAP.md` (customer-facing journey map — Mermaid diagram + at-a-glance table + current-stage detail. Pick the Mode first: B+CID = 5 stages, B+CIDR = 6, B+CIDRA = 7 with I+A marked planned. Stage 0 starts as the active stage.)
   - `BRAINSTORM_DIALOG_LOG.md` (audit trail of the conversation)

   For ROADMAP.md, follow the authoring rules at the bottom of `ROADMAP.md.tmpl` — laconic, action-first, justification collapsed in `<details>`. The journey diagram + at-a-glance table must reflect the chosen mode's stage count.

**Critical mandates:**
- **BRN_005** (continuous_gap_check) — schedule the 3 checkpoint refreshes in `BRAINSTORM_OUTPUT.yaml.gap_check_schedule`
- **BRN_006** (dual_audience_lens) — verify enforcement_check_passed before signaling complete
- **BRN_010** (honest_input_communication) — never hide a missing input

After completion, report:
- Chosen template + rationale
- Critical gaps (with count)
- Effort estimates per coverage level
- "Ready for `/chunk`" status (true only after customer acknowledges MISSING_INPUTS.md)
