# THE_BRAINSTORMER_AGENT

**Stage 0 of the CIDRA pipeline.** Runs before `/chunk` to elicit goals, identify gaps, and produce a binding blueprint.

## Quick start

```
/brainstorm                  Start the 3-question dialog and produce BRAINSTORM_OUTPUT.yaml
/brainstorm:gap              Re-issue MISSING_INPUTS.md at any checkpoint
/brainstorm:status           Show current understanding
/brainstorm:format           Show recommended documentation format
```

## What it produces

| File | Purpose |
|------|---------|
| `BRAINSTORM_OUTPUT.yaml` | Binding blueprint for downstream agents |
| `MISSING_INPUTS.md` | Gap list for customer review (refreshed at checkpoints) |
| `BRAINSTORM_DIALOG_LOG.md` | Conversation transcript |

## Pipeline position

```
THE_BRAINSTORMER_AGENT (Stage 0, NEW)
        ↓ BRAINSTORM_OUTPUT.yaml
THE_CHUNKER_AGENT (Stage 1)
        ↓ CHUNKS/
THE_DOCUMENTER_AGENT (Stage 2)
        ↓ Screens/<COMPONENT>/
THE_RECOMMENDER_AGENT (Stage 3)
        ↓ RECOMMENDATIONS/<COMPONENT>/
```

## The 3 pivotal questions

1. **Purpose** — modernization decision · team handover · compliance audit · knowledge preservation · spaghetti decoding · other
2. **Audience** — developer · architect · PM · business analyst · auditor · external vendor (multiple allowed)
3. **Timeline** — quick first-pass · iterative weeks · comprehensive months

## Critical mandates

- **BRN_005** — re-surface gaps at every checkpoint (before / during / after)
- **BRN_010** — never hide a missing input to keep velocity

## See also

- [agent_specification.md](agent_specification.md) — full spec including 5 behavioral rules
- [skills.yaml](skills.yaml) — formal definitions for all 10 BRN skills
- [templates/](templates/) — output templates

## Version

1.0.0 — 2026-05-27. Designed retrospectively after the MACCABI RK1_PHARMACY_JOURNAL project (Maccabi pharmacy → SAP CA 2E COBOL/400 documentation).
