# CIDRA Project Runbook
## Starting a new CIDRA documentation project from scratch

> Step-by-step instructions for initializing a new project using the CIDRA Framework on **Windows + PowerShell + Cursor (or VS Code)**.
> Total time to first documentation pass: ~2-4 hours depending on codebase size.

---

## Prerequisites — install once per machine

**POWERSHELL — copy-paste this whole block** (it skips anything already installed):

```powershell
# Git (required)
winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements

# Cursor (required — or use VS Code: winget install --id Microsoft.VisualStudioCode)
winget install --id Anysphere.Cursor -e --accept-source-agreements --accept-package-agreements

# Node.js LTS (optional — only needed if you'll pre-render Mermaid diagrams)
winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements

# Python 3.11 (optional — only needed if you'll verify with Playwright)
winget install --id Python.Python.3.11 -e --accept-source-agreements --accept-package-agreements
```

After install, **close and reopen PowerShell** so the new tools land on PATH.

**Optional global npm package** (only if you installed Node):

```powershell
npm install -g @mermaid-js/mermaid-cli
```

**Optional Python packages** (only if you installed Python):

```powershell
pip install playwright
playwright install chromium
```

**Inside Cursor / VS Code:** install the **Claude Code** extension and sign in with your Anthropic key.

**Verify everything is on PATH:**

```powershell
git --version
node --version          # only if you installed Node
mmdc --version          # only if you installed mermaid-cli
python --version        # only if you installed Python
```

---

## Step 0 — Set your variables (do this once per project)

**POWERSHELL — edit the two CHANGE-ME values, then copy-paste the whole block:**

```powershell
# === CHANGE THESE TWO ===
$projectName = "my_project"       # ASCII, no spaces — used as folder name
$component   = "MY_COMPONENT"     # logical name for what you're documenting, e.g. "RK1_PHARMACY_JOURNAL"

# === leave these as-is unless you have a strong reason ===
$framework   = "C:\Users\$env:USERNAME\tools\enterprise_cidra_framework"
$projectRoot = "C:\projects"
$project     = "$projectRoot\$projectName"

# Confirm
Write-Output "Framework:   $framework"
Write-Output "Project:     $project"
Write-Output "Component:   $component"
```

Every step below uses `$framework`, `$project`, and `$component` — no further variable editing.

---

## Step 1 — Clone the framework (once per machine)

**POWERSHELL:**

```powershell
New-Item -ItemType Directory -Path (Split-Path $framework) -Force | Out-Null
if (Test-Path $framework) {
    cd $framework; git pull
} else {
    git clone https://github.com/iliyaruvinsky/enterprise_cidra_framework.git $framework
}
```

(Idempotent — first run clones, later runs update.)

---

## Step 2 — Create the project working directory

**Recommended location:** local NTFS drive (`C:\`). **Do not use Google Drive** (`G:\My Drive\` is FAT32 — 4 GB file limit, sync race conditions during long agent runs).

**POWERSHELL:**

```powershell
New-Item -ItemType Directory -Path "$project\Source Code" -Force | Out-Null
Write-Output "Created: $project\Source Code"
```

---

## Step 3 — Add the source code + reference materials

Replace `<source_location>` with the path where your source files actually live, then run.

**POWERSHELL:**

```powershell
$sourceLocation = "<source_location>"   # e.g. "C:\incoming\customer_code"

# Copy ALL source files (adjust filter for your case)
Copy-Item "$sourceLocation\*" -Destination "$project\Source Code\" -Recurse -Force

# Place reference materials (spec docs, sample data) at the PROJECT ROOT
# Example:
# Copy-Item "$sourceLocation\spec.docx"   -Destination $project
# Copy-Item "$sourceLocation\samples\*.csv" -Destination $project

Write-Output "Source copied to: $project\Source Code"
Get-ChildItem "$project\Source Code" | Select-Object Name, Length | Format-Table -AutoSize
```

The brainstormer will ask about the reference materials in Step 7.

> **If your source has vendor identification tags** (CA 2E COBOL, etc.) — leave them for now. Strip them in Step 8 after the brainstormer runs.

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

The installer copies `.cidra\` but not (yet) the slash command files. Copy the templates from the framework's `Protocols\.claude\commands\` folder into your project:

**POWERSHELL:**

```powershell
Copy-Item -Path "$framework\Protocols\.claude\commands" `
          -Destination "$project\.claude\" -Recurse -Force
```

That's it. All 14 slash command templates (4 entry points + 10 sub-commands) land at `$project\.claude\commands\`. They are project-agnostic — the same templates work for any CIDRA project.

**Verify:**

```powershell
Get-ChildItem "$project\.claude\commands" -Recurse -File | Select-Object Name
# Expected: brainstorm.md, chunk.md, document.md, recommend.md +
#           brainstorm/{format,gap,status}.md, chunk/{analyze,status}.md,
#           document/{fix,setup,validate}.md, recommend/{compare,risk}.md
```

> **Future:** the installer will copy these automatically; this step will disappear.

---

## Step 6 — Open the project in Cursor/VS Code

**POWERSHELL:**

```powershell
# Cursor (try in order — first one that's on PATH wins)
& cursor $project 2>$null
if ($LASTEXITCODE -ne 0) { & code $project }
```

If neither command is on PATH, open the IDE manually and `File → Open Folder` → `$project`.

The IDE's Claude Code extension will discover the slash commands automatically. Type `/` in a chat and you should see `/brainstorm`, `/chunk`, `/document`, `/recommend` (and their sub-commands) in autocomplete.

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

## Step 11 — Stage 2 run: `/document $component`

In the Claude Code chat (substitute the value of `$component` you set in Step 0):

```
/document MY_COMPONENT
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
/document:validate Screens\MY_COMPONENT
```

(Use the actual value of `$component` set in Step 0.)

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
/document:fix Screens\MY_COMPONENT
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
/recommend MY_COMPONENT
```

(Use the actual value of `$component`.)

The recommender runs a dialog (direction → options → confirmation), then produces:
- `RECOMMENDATIONS\<COMPONENT>\RECOMMENDATION_REPORT.md`
- Technology comparison, migration roadmap, risk assessment, cost-benefit analysis

---

## Step 15 — Package for delivery

**POWERSHELL — copy-paste as-is (uses `$project` and `$component` from Step 0):**

```powershell
$delivery = "$project\${component}_Documentation_$(Get-Date -Format yyyy-MM-dd).zip"
$staging = "$env:TEMP\cidra_delivery_$(Get-Random)"

New-Item -ItemType Directory -Path "$staging\$component" -Force | Out-Null
Copy-Item "$project\Screens\$component\*" -Destination "$staging\$component\" -Recurse

# Optional: include brainstormer artifacts as context
Copy-Item "$project\BRAINSTORM_OUTPUT.yaml" -Destination "$staging\$component\" -ErrorAction SilentlyContinue
Copy-Item "$project\MISSING_INPUTS.md"     -Destination "$staging\$component\" -ErrorAction SilentlyContinue

Compress-Archive -Path "$staging\$component" -DestinationPath $delivery -CompressionLevel Optimal
Remove-Item $staging -Recurse -Force
Write-Output "Delivery zip: $delivery"
```

Optionally write a Hebrew/English cover letter alongside — see the Maccabi RK1 project's `COVER_LETTER_FOR_CLIENT.md` for a template.

---

## Quick reference — full happy path

```
Prereqs (once per machine):  winget install Git + Cursor (+ Node + Python if optional features)
Step 0  (once per project):  set $projectName + $component, run the variables block
Step 1  (once per machine):  git clone the framework
Step 2:  New-Item $project + Source Code/
Step 3:  Copy source + reference docs
Step 4:  .\Scripts\install.ps1 -ProjectPath $project
Step 5:  Copy-Item Protocols\.claude\commands → $project\.claude\
Step 6:  cursor $project
Step 7:  /brainstorm                  → 3 files at root, customer acknowledges gaps
Step 8:  preprocess source if needed
Step 9:  /chunk:analyze, then /chunk  → CHUNKS/
Step 10: /document:setup             → DOCUMENTER_PROJECT_CONFIG.yaml
Step 11: /document $component         → Screens/<COMPONENT>/
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
