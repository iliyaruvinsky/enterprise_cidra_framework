---
description: CIDRA — show recommended documentation format with justification
---

You are executing **THE_BRAINSTORMER_AGENT** skill **BRN_004_CMD (brainstorm:format)**.

**Reads:**
- `BRAINSTORM_OUTPUT.yaml` at project root — `format` section

**Report:**

1. **Chosen template** — enterprise_7_file / enterprise_7_plus_companions / audit_focused / onboarding_focused / custom_hybrid
2. **Rationale** — why this fits the elicited goals
3. **Dual-audience breakdown** — which files serve primary audience, which serve secondary, which serve both (per BRN_006)
4. **File list** — exact filenames the documenter will produce
5. **Effort estimate**:
   - Skeleton (deterministic + structural): X hours
   - Standard (full first pass): Y hours
   - Deep (per-feature dives): Z hours

If `BRAINSTORM_OUTPUT.yaml` doesn't exist, tell the user to run `/brainstorm` first.

If the user wants to change the template, run a brief dialog:
- Show the catalogue (BRN_004 template_catalogue)
- Confirm the change
- Update `format.template` and `documenter_config.template` in the YAML
- Re-run BRN_006 dual-audience enforcement check
