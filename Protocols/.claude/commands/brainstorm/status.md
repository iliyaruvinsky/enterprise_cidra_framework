---
description: CIDRA — show current brainstormer understanding (goals, inputs, gaps, format)
---

You are executing **THE_BRAINSTORMER_AGENT** skill **BRN_003_CMD (brainstorm:status)**.

**Reads:**
- `BRAINSTORM_OUTPUT.yaml` at project root
- `MISSING_INPUTS.md` at project root (current state)
- `BRAINSTORM_DIALOG_LOG.md` at project root

**Report (in a structured summary):**

1. **Goals** — purpose, audience(s), timeline (from `goals` section of YAML)
2. **Inputs inventory** — count by status (present / partial / absent / unknown)
3. **Open gaps** — count by criticality (critical / high / medium)
4. **Format chosen** — template name + 1-line rationale
5. **Pipeline state** — which downstream agents have run, which are pending
6. **Next checkpoint** — when is the next BRN_005 gap-check due

If `BRAINSTORM_OUTPUT.yaml` doesn't exist, tell the user to run `/brainstorm` first.
