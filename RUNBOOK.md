# CIDRA Project Runbook
## Starting a new CIDRA documentation project from scratch

> Step-by-step instructions for initializing a new project using the CIDRA Framework on **Windows + PowerShell + Cursor (or VS Code)**.
> Total time to first documentation pass: ~2-4 hours depending on codebase size.

---

## Prerequisites

Install once (if not already on the machine):

| Tool | Required for | Verify |
|------|--------------|--------|
| **Git** | Cloning the framework | `git --version` |
| **PowerShell 5.1+** | All shell commands (built-in on Win10/11) | `$PSVersionTable.PSVersion` |
| **Cursor** or **VS Code** | Running CIDRA slash commands | Open the IDE |
| **Claude Code extension** | Slash command execution | Sign in with your Anthropic key |
| **Node.js + npm** *(optional)* | Pre-rendering Mermaid diagrams to SVG | `node --version` |
| **mmdc (mermaid-cli)** *(optional)* | Same as above | `mmdc --version` (or `npm install -g @mermaid-js/mermaid-cli`) |

---

## Step 1 — Clone the framework (once per machine)

Pick a tools folder. Suggested: `C:\Users\<you>\tools\`.

**POWERSHELL:**

```powershell
$framework = "C:\Users\$env:USERNAME\tools\enterprise_cidra_framework"
New-Item -ItemType Directory -Path (Split-Path $framework) -Force | Out-Null
git clone https://github.com/iliyaruvinsky/enterprise_cidra_framework.git $framework
```

To update later:

```powershell
cd $framework; git pull
```

---

## Step 2 — Create the project working directory

**Recommended location:** local NTFS drive (`C:\` or `D:\`), **not Google Drive** — Drive's `G:\My Drive\` is FAT32 (4 GB file limit, sync race conditions during long agent runs).

**POWERSHELL:**

```powershell
$project = "C:\projects\<your_project_name>"
New-Item -ItemType Directory -Path "$project\Source Code" -Force | Out-Null
```

Replace `<your_project_name>` with your project's name. Use ASCII-safe characters in the path if possible (avoid spaces and non-Latin characters if your toolchain is sensitive).

---

## Step 3 — Add the source code

Copy the source files you want to document into `Source Code\`:

**POWERSHELL:**

```powershell
# Example: copy COBOL/ABAP/Python source from somewhere
Copy-Item "C:\where_source_lives\*.cbl" -Destination "$project\Source Code\"

# If your code came from a vendor system and has identification tags
# (e.g. CA 2E COBOL right-aligned tags), strip them now — the chunker
# expects clean source. Example strip is shown in Step 7.
```

Also place any **reference materials** at the project root (spec docs, sample data CSVs, etc.). The brainstormer will ask about them.

---

## Step 4 — Run the framework installer

**POWERSHELL (must be PowerShell, not CMD):**

```powershell
# If the script fails with "Access is denied", first unblock it
Get-ChildItem $framework -Recurse -File | Unblock-File

# Run the installer
cd $framework
.\Scripts\install.ps1 -ProjectPath $project
```

**Verify the install:**

```powershell
Get-ChildItem $project | Select-Object Name
# Expected: .cidra, Source Code (plus CLAUDE.md and .vscode if installer wrote them)
```

You should see `.cidra\Agents\` containing 4 agent folders including `THE_BRAINSTORMER_AGENT`.

---

## Step 5 — Register the slash commands

The installer copies the framework's `.cidra/` folder. To make slash commands work in Cursor/VS Code, copy the command templates into `.claude\commands\`:

**POWERSHELL:**

```powershell
# Make the commands directory
New-Item -ItemType Directory -Path "$project\.claude\commands\brainstorm" -Force | Out-Null
New-Item -ItemType Directory -Path "$project\.claude\commands\chunk" -Force | Out-Null
New-Item -ItemType Directory -Path "$project\.claude\commands\document" -Force | Out-Null
New-Item -ItemType Directory -Path "$project\.claude\commands\recommend" -Force | Out-Null

# Copy template commands from a reference project (the Maccabi project has them) OR
# create them manually following the patterns in:
#   .cidra\Agents\<AGENT>\skills.yaml
# (Future: installer will auto-create these.)
```

**Minimum file you must create yourself** — `.claude\commands\brainstorm.md`:

```markdown
---
description: CIDRA Stage 0 — goal elicitation, gap analysis, blueprint
---

Execute THE_BRAINSTORMER_AGENT per `.cidra/Agents/THE_BRAINSTORMER_AGENT/agent_specification.md`.
Run the 5-phase workflow. Produce BRAINSTORM_OUTPUT.yaml, MISSING_INPUTS.md, BRAINSTORM_DIALOG_LOG.md at project root.
```

Repeat for `/chunk`, `/document`, `/recommend` (template patterns in each agent's `skills.yaml`).

> **Tip:** if you have a previously-set-up CIDRA project (e.g. the Maccabi RK1 project), copy its entire `.claude\commands\` folder — same templates work for any project.

---

## Step 6 — Open the project in Cursor/VS Code

```powershell
cursor $project    # or: code $project
```

The IDE's Claude Code extension will discover the slash commands automatically. You should now see `/brainstorm`, `/chunk`, `/document`, `/recommend` (and their sub-commands) in the slash-command autocomplete.

---

## Step 7 — Stage 0: `/brainstorm`

Open a Claude Code chat in the project and run:

```
/brainstorm
```

The brainstormer will:

1. Ask 3 pivotal questions:
   - **Purpose** — modernization · handover · audit · knowledge-preservation · spaghetti-decoding · other
   - **Audience** — developer / architect / PM / BA / auditor / vendor (multiple allowed)
   - **Timeline** — quick / iterative / comprehensive
2. Inventory your inputs against 12 standard categories
3. Produce 3 files at project root:
   - `BRAINSTORM_OUTPUT.yaml` — binding blueprint for downstream agents
   - `MISSING_INPUTS.md` — gap list (review with the customer)
   - `BRAINSTORM_DIALOG_LOG.md` — conversation audit trail

**Action required after `/brainstorm`:**
- Read `MISSING_INPUTS.md`
- For each item: respond **✓** (will provide), **✗** (won't / can't), **?** (will check)
- Discuss with the customer if any 🔴 CRITICAL items are unresolved

---

## Step 8 — Source preprocessing (if your code needs it)

If your source has vendor-specific artifacts (e.g. CA 2E identification tags on COBOL, sequence numbers, Mark-of-the-Web on Windows), clean it now.

**Example for CA 2E COBOL** (right-aligned Y-prefix tags):

```powershell
$src = "$project\Source Code"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
foreach ($f in Get-ChildItem $src -Filter "*.txt") {
    $out = $f.FullName -replace '\.txt$', '.cob'
    $lines = [System.IO.File]::ReadAllLines($f.FullName)
    $stripped = $lines | ForEach-Object {
        ($_ -replace '\s{2,}Y[A-Z0-9]{4,}\s*$', '').TrimEnd()
    }
    [System.IO.File]::WriteAllLines($out, $stripped, $utf8NoBom)
}
```

Adjust the regex for your vendor (Synon, IBM, SAP, etc.) — or skip this step entirely if your source is already clean.

---

## Step 9 — Stage 1: `/chunk`

```
/chunk:analyze Source Code
```

This shows a preview without writing anything: how many chunks, what languages, recommended strategy. Review the output. If reasonable, run:

```
/chunk Source Code
```

The chunker will produce:
- `CHUNKS\repository.json` — all chunks with metadata + content
- `CHUNKS\graph.json` — relationships (PERFORM/CALL/COPY/etc.)
- `CHUNKS\analysis.json` — codebase inventory + statistics
- `CHUNKS\DOCUMENTER_INSTRUCTIONS.md` — handoff prompt for Stage 2
- `CHUNKS\run_manifest.json` — pipeline state

**Expected runtime:** seconds for small codebases, ~1 minute per 50k LOC.

---

## Step 10 — Stage 2 setup: `/document:setup`

One-time configuration:

```
/document:setup
```

You'll be asked:
- Documentation language (English / Hebrew / bilingual / other)
- Template (`enterprise_7_file` / variants)
- Output directory (default `./Screens/`)
- Validation report naming convention

The brainstormer's `BRAINSTORM_OUTPUT.yaml` provides defaults — `/document:setup` either confirms them or lets you override.

Output: `DOCUMENTER_PROJECT_CONFIG.yaml` at project root.

---

## Step 11 — Stage 2 run: `/document <COMPONENT>`

Replace `<COMPONENT>` with a logical name for what you're documenting (e.g. `MY_PROGRAM`):

```
/document MY_PROGRAM
```

The documenter will:
- Read `CHUNKS\DOCUMENTER_INSTRUCTIONS.md` + `BRAINSTORM_OUTPUT.yaml`
- Apply the appropriate plugin (AS/400, SAP ABAP, React, Python — auto-detected)
- Use **exact counts** from the source (no estimates)
- Use **careful language** ("appears to", "according to code")
- Mark cross-references explicitly (shared from / unique to)
- Include a Limitations section in every file
- Produce 7 files at `Screens\<COMPONENT>\`

**Expected runtime:** 10-30 minutes depending on codebase size and depth.

---

## Step 12 — Validate

```
/document:validate Screens\<COMPONENT>
```

The validator runs a 100-point check:
- File count = 7
- No forbidden words (marketing language)
- ≥5 careful-language phrases per file
- No estimate language (approximately, ~, several)
- Limitations section present
- Cross-references marked
- All counts match source

**Target:** 100/100. Anything less, run:

```
/document:fix Screens\<COMPONENT>
```

…and re-validate.

---

## Step 13 — `/brainstorm:gap` (checkpoint 3)

After validation:

```
/brainstorm:gap
```

Refreshes `MISSING_INPUTS.md` with the post-validation gap list. The customer sees exactly which inputs would have lifted documentation quality (if they want to invest more).

---

## Step 14 (optional) — Stage 3: `/recommend`

Only if `purpose` from `/brainstorm` included modernization:

```
/recommend <COMPONENT>
```

The recommender runs a dialog (direction → options → confirmation), then produces:
- `RECOMMENDATIONS\<COMPONENT>\RECOMMENDATION_REPORT.md`
- Technology comparison, migration roadmap, risk assessment, cost-benefit analysis

---

## Step 15 — Package for delivery

```powershell
$component = "MY_PROGRAM"
$delivery = "$project\$component`_Documentation_$(Get-Date -Format yyyy-MM-dd).zip"
$staging = "$env:TEMP\cidra_delivery_$(Get-Random)"

New-Item -ItemType Directory -Path "$staging\$component" -Force | Out-Null
Copy-Item "$project\Screens\$component\*" -Destination "$staging\$component\" -Recurse

# Optional: include the brainstormer artifacts as context
Copy-Item "$project\BRAINSTORM_OUTPUT.yaml" -Destination "$staging\$component\" -ErrorAction SilentlyContinue
Copy-Item "$project\MISSING_INPUTS.md" -Destination "$staging\$component\" -ErrorAction SilentlyContinue

Compress-Archive -Path "$staging\$component" -DestinationPath $delivery -CompressionLevel Optimal
Remove-Item $staging -Recurse -Force
Write-Output "Delivery zip: $delivery"
```

Optionally write a Hebrew/English cover letter alongside — see the Maccabi RK1 project's `COVER_LETTER_FOR_CLIENT.md` for a template.

---

## Quick reference — full happy path

```
Step 1 (once): git clone the framework
Step 2-3: create project + add source
Step 4: install.ps1 -ProjectPath <project>
Step 5: register slash commands
Step 6: open in Cursor
Step 7: /brainstorm                  → 3 files at root, customer acknowledges gaps
Step 8: preprocess source if needed
Step 9: /chunk:analyze, then /chunk  → CHUNKS/
Step 10: /document:setup             → DOCUMENTER_PROJECT_CONFIG.yaml
Step 11: /document <COMPONENT>       → Screens/<COMPONENT>/
Step 12: /document:validate          → 100/100 target
Step 13: /brainstorm:gap             → refreshed MISSING_INPUTS.md
Step 14 (opt): /recommend            → RECOMMENDATIONS/
Step 15: zip + deliver
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `install.ps1`: "Access is denied" | Mark-of-the-Web on freshly downloaded scripts | `Get-ChildItem $framework -Recurse -File | Unblock-File` |
| `install.ps1`: Notepad opens instead of running | You're in `cmd.exe`, not PowerShell | Open PowerShell. Run `powershell` first if needed. |
| Slash commands don't autocomplete | `.claude\commands\` missing or empty | Re-do Step 5. Reload Cursor (`Ctrl+Shift+P` → "Developer: Reload Window") |
| Hebrew text shows as mojibake in script outputs | File written as UTF-8 without BOM, PowerShell 5.1 reading as CP1252 | Re-write with UTF-8 BOM: `[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($true))` |
| `/document` produces score <100 | Forbidden words, estimate language, or missing sections | Run `/document:fix`, re-validate |
| Chunker produces oversized chunks (>8000 tokens) | Single section too large | Use a splitting post-step (paragraph-boundary aware). See Maccabi RK1's `_chunker.ps1` for a working example. |
| Mermaid diagrams render as raw code in viewer | Viewer doesn't support Mermaid | Pre-render to SVG with `mmdc`, embed as `<img src="data:image/svg+xml;base64,...">` |

---

## What lives where (after a complete run)

```
<project>/
├── .cidra/                              # framework files (don't edit)
├── .claude/commands/                    # slash commands
├── Source Code/                         # your source code (preprocessed)
├── BRAINSTORM_OUTPUT.yaml                # blueprint (Stage 0)
├── MISSING_INPUTS.md                     # gap list (Stage 0, refreshed)
├── BRAINSTORM_DIALOG_LOG.md              # audit trail (Stage 0)
├── DOCUMENTER_PROJECT_CONFIG.yaml        # documenter config (Stage 2)
├── CHUNKS/                               # chunker output (Stage 1)
├── Screens/<COMPONENT>/                  # documentation (Stage 2) — DELIVERABLE
└── RECOMMENDATIONS/<COMPONENT>/          # modernization advice (Stage 3, optional)
```

---

## Pipeline reference

```
THE_BRAINSTORMER_AGENT (Stage 0, NEW)
        ↓ BRAINSTORM_OUTPUT.yaml
THE_CHUNKER_AGENT (Stage 1)
        ↓ CHUNKS/
THE_DOCUMENTER_AGENT (Stage 2)
        ↓ Screens/<COMPONENT>/
THE_RECOMMENDER_AGENT (Stage 3, optional)
        ↓ RECOMMENDATIONS/<COMPONENT>/
THE_INTERPRETER_AGENT (Stage 4, planned)
THE_APPLICATOR_AGENT (Stage 5, planned)
```

---

*CIDRA Framework v1.1.0 (B+CIDRA) · Runbook v1.0 · 2026-05-27*
*Repository: https://github.com/iliyaruvinsky/enterprise_cidra_framework*
