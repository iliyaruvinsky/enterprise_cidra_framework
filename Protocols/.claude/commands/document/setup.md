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

**Recommended defaults for this project** (Hebrew/Maccabi context):
- Language: Hebrew + English bilingual
- Template: enterprise_7_file
- Output: `./Screens/`
- Validation naming: `דוח_אימות_[COMPONENT].md`

**Persist answers to `DOCUMENTER_PROJECT_CONFIG.yaml`** in project root using this schema:

```yaml
project_name: "רוקחות_פקודות_יומן"
setup_date: "<today>"
documentation_language: "<answer>"
template: "<answer>"
output_directory: "<answer>"
validation_report_naming: "<answer>"
quality_threshold: 100
```

After writing, Read the file back to confirm it's correct, then report the choices to the user.
