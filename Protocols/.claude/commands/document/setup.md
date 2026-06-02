---
description: CIDRA — one-time documentation setup for this project
---

You are executing **THE_DOCUMENTER_AGENT** skill **DOC_002 (document:setup)**.

**Reads:**
- [.cidra/Agents/THE_DOCUMENTER_AGENT/skills.yaml](.cidra/Agents/THE_DOCUMENTER_AGENT/skills.yaml) — skill DOC_002 dialog_flow

**Ask the user, via AskUserQuestion when possible, the 4 setup questions:**

1. **Documentation language** — English only / Hebrew only / Hebrew + English (bilingual) / Other
2. **Template** — `enterprise_7_file` (recommended) / `compact_5_file` / `quick_3_file` / custom
3. **Output directory** — default `./Screens/[COMPONENT_NAME]/`
4. **Validation report naming** — `validation_report_[COMPONENT].md` / `דוח_אימות_[COMPONENT].md` (Hebrew) / `[COMPONENT]_validation.md`

## Defaults
If BRAINSTORM_OUTPUT.yaml exists at the project root, derive defaults
from its documenter_directives section.
Otherwise infer:
  project_name: <basename of $PWD> OR <component_id from BRAINSTORM_OUTPUT.yaml>
  documentation_language: <from BRAINSTORM_OUTPUT.yaml documenter_config.language, or prompt>
  template: <from BRAINSTORM_OUTPUT.yaml format_recommendation, or enterprise_7_file>
  output_directory: ./Screens/
Never write a hard-coded project_name into the YAML template the model
produces — substitute at write time.

After writing, Read the file back to confirm it's correct, then report the choices to the user.
