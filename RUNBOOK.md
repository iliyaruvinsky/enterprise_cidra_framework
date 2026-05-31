# CIDRA Project Runbook
## Starting a new CIDRA documentation project from scratch

> Step-by-step instructions for initializing a new project using the CIDRA Framework on **Windows + PowerShell + Cursor (or VS Code)**.
> Total time to first documentation pass: ~2-4 hours depending on codebase size.

> **Mechanical setup is now a single command** (`Scripts\bootstrap.ps1`). Steps 2-9 happen inside the IDE in a Claude Code chat. Step 10 is back in PowerShell to zip the deliverable.

---

## Step 1 — Run the bootstrap (one command, all mechanical setup)

This single PowerShell script does every mechanical step: prerequisite check, framework clone or pull, project directory creation, source copy, framework install, slash command registration, and IDE launch.

### 1a. One-time prerequisites (per machine)

The bootstrap will tell you which of these are missing. Install only what it asks for:

**POWERSHELL — copy-paste:**

```powershell
# Git (required)
winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements

# Cursor (required — or use VS Code instead)
winget install --id Anysphere.Cursor -e --accept-source-agreements --accept-package-agreements
# Alternative: winget install --id Microsoft.VisualStudioCode -e --accept-source-agreements --accept-package-agreements

# Recommended: PowerShell 7 (pwsh) for reliable Hebrew / Unicode path handling
winget install --id Microsoft.PowerShell -e --accept-source-agreements --accept-package-agreements
```

Then **close and reopen PowerShell** so the new tools land on PATH. (`refreshenv` is a Chocolatey helper and does NOT exist on winget-only machines — closing and reopening the shell is the universal solution.)

**Critical, easy to miss:** inside Cursor or VS Code, install the **Claude Code** extension and sign in with your Anthropic account. Without this, none of Steps 2-9 work.

1. Open Cursor / VS Code.
2. Extensions panel → search "Claude Code".
3. Install.
4. Sign in with your Anthropic account.

Optional add-ons (skip unless you need them):

```powershell
# Only if you will pre-render Mermaid diagrams:
winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements
npm install -g @mermaid-js/mermaid-cli

# Only if you will verify with Playwright:
winget install --id Python.Python.3.11 -e --accept-source-agreements --accept-package-agreements
pip install playwright
playwright install chromium
```

### 1b. Decide your two scoping values

These are **human decisions** — the bootstrap script asks for them as parameters:

- **`-ProjectFolder`** — short ASCII directory name (e.g. `rk1_pharmacy`). This becomes the leaf folder under `C:\projects\`. No spaces. NTFS-illegal characters (`<>:"/\|?*`) are rejected.
- **`-ComponentId`** — UPPER_SNAKE_CASE logical identifier (e.g. `RK1_PHARMACY_JOURNAL`). This flows through `CHUNKS/`, `Screens/<COMPONENT>/`, `RECOMMENDATIONS/<COMPONENT>/`, and the delivery zip filename. ASCII only because it lands inside filenames.

Do NOT auto-derive these from the source folder name — they are client-facing naming and a wrong autoguess pollutes the deliverable.

### 1c. Get the framework (once per machine)

Clone the framework into a canonical location. This becomes your "home" for the framework code; future projects reuse the same checkout.

**POWERSHELL:**

```powershell
$framework = "C:\Users\$env:USERNAME\tools\enterprise_cidra_framework"
New-Item -ItemType Directory -Path (Split-Path $framework) -Force | Out-Null
git clone https://github.com/iliyaruvinsky/enterprise_cidra_framework.git $framework
```

> **Already have the framework cloned somewhere else?** Skip this and pass `-FrameworkPath "<your path>"` to `bootstrap.ps1` in 1d. If you run `bootstrap.ps1` from inside an existing checkout (e.g. `cd $framework\Scripts`), it detects that and uses that location as canonical — no redundant clone.

### 1d. Run the bootstrap

From the framework's `Scripts\` directory, invoke `bootstrap.ps1` with your two values:

**POWERSHELL:**

```powershell
cd $framework\Scripts
.\bootstrap.ps1 `
    -ProjectFolder "rk1_pharmacy" `
    -ComponentId   "RK1_PHARMACY_JOURNAL" `
    -SourcePath    "C:\incoming\customer_code"
```

**AS/400 source-library example** — append `.cob` to every COBOL member so the chunker's `extension_matching` (priority 1) picks them up alongside the new `source_library_patterns` regexes (priority 4 — confirming signal):

```powershell
.\bootstrap.ps1 `
    -ProjectFolder "pharmacy_cidra" `
    -ComponentId   "RK1_PHARMACY_JOURNAL" `
    -SourcePath    "G:\My Drive\Maccabi AI\רוקחות_פקודות_יומן" `
    -SourceFilter  "QCBLLESRC.*" `
    -SourceRenameTo ".cob"
```

> `-SourceFilter "QCBLLESRC.*"` uses the Win32 glob via `Get-ChildItem -Filter`, which may have legacy 8.3 short-name fallback. For extensionless AS/400 exports, prefer `-Filter '*'` plus explicit `-SourceExclude` over a strict `-Filter "QCBLLESRC.*"`.

Optional flags:

| Flag | Purpose |
|------|---------|
| `-ReferenceDocsPath "<path>"` | Folder (or single file) of reference materials (spec docs, sample CSVs) — copied to `<project>\Reference\` (NOT project root) so they cannot collide with downstream artifacts |
| `-SourceFilter "*.txt"` | Glob filter for which source files to copy (default `*`) |
| `-SourceExclude @('*.csv','*.exe')` | Glob exclusions during source copy (default excludes binaries and sample data — `*.csv`, `*.xlsx`, `*.exe`, `*.dll`, `*.zip`, etc.). Pass `@()` to disable. |
| `-SourceRenameTo ".cob"` | Append the given extension as a final suffix to every copied source file (e.g. `".cob"` turns `QCBLLESRC.SEWKXFKB` into `QCBLLESRC.SEWKXFKB.cob`). Designed for AS/400 source-library exports so the chunker and IDE recognize the language. Idempotent — files already ending in the suffix are left alone (mixed-case is canonicalized to lowercase). Skips on collision or MAX_PATH (>259 chars on PS 5.1); surfaced in the completion sentinel. Changing the value between runs requires `-ForceSource` (stale renamed files are wiped before re-copy). **CAUTION**: append (not replace) semantics — `README` becomes `README.cob`; `report.txt` becomes `report.txt.cob`. |
| `-ProjectRoot "D:\work"` | Override the default `C:\projects` parent directory |
| `-FrameworkPath "<path>"` | Override the default framework location (`C:\Users\<USER>\tools\enterprise_cidra_framework`) |
| `-Ide vscode` | Prefer VS Code over Cursor for the auto-launch (default `cursor`) |
| `-SkipIdeLaunch` | Don't try to open the IDE; just print the manual instruction |
| `-ForceSource` | Re-copy source files even if a successful previous copy sentinel exists |
| `-ForceFramework` | Pass `-Force` to `install.ps1` (overwrite `.cidra/`) AND fully replace `.claude\commands\` (clears stale command files from older framework versions) |
| `-AdoptExistingDirectory` | Allow bootstrap to write into a pre-existing non-empty project directory that does NOT already contain `.cidra/` |
| `-AllowSyncDrive` | Suppress the OneDrive / Google Drive / Dropbox guard (use only if you have paused sync) |
| `-AllowStaleFramework` | Allow continuing with an existing framework checkout that cannot be fast-forwarded |
| `-SkipUnblock` | Skip `Unblock-File` entirely (useful on sync drives) |
| `-GitTimeoutSec 300` | Hard timeout on git clone / pull (default 300 s) |
| `-WhatIf` | Dry run — print every action without making changes |

### 1e. What the bootstrap does

1. Verifies Git and Cursor/VS Code are on PATH **or** in standard install locations (`%LOCALAPPDATA%\Programs\cursor\`, `%LOCALAPPDATA%\Programs\Microsoft VS Code\`). If missing, prints the winget command and exits.
2. Warns if running under Windows PowerShell 5.1 (Hebrew path handling can fail; PowerShell 7 recommended).
3. Validates `-SourcePath` (and `-ReferenceDocsPath` if given) exist.
4. Forces UTF-8 console output and `chcp 65001` so Hebrew / Unicode paths render correctly.
5. Clones the framework atomically via temp-rename — a Ctrl+C mid-clone never leaves a half-checkout at the canonical location.
6. On re-run: health-checks the existing framework (`.git/` + `Scripts/install.ps1` + `Agents/` all present), refuses to pull a dirty / mid-merge tree, and only fast-forwards.
7. Selective `Unblock-File` — only files actually carrying the Zone.Identifier ADS, gated by a sentinel so re-runs are instant.
8. Creates `C:\projects\<ProjectFolder>\` and `Source Code\` subdirectory.
9. Refuses to overwrite a pre-existing non-empty directory unless `-AdoptExistingDirectory` is passed.
10. Detects OneDrive / Google Drive / Dropbox / iCloud / Box sync paths by NAME (not drive letter) and refuses unless `-AllowSyncDrive`.
11. Copies source files via literal-path enumeration (handles `[]`, spaces, Hebrew) with a default exclude-list for binary / sample-data extensions.
12. Writes a copy-completion sentinel containing expected vs copied file counts — a partial copy (Ctrl+C mid-copy) is detected on re-run and self-heals.
13. Copies reference materials into `<project>\Reference\` (NOT project root) so re-runs cannot clobber Stage 0/1/2 artifacts.
14. Runs `Scripts\install.ps1 -ProjectPath <project>` as a **child process** so its exit code is observable. `install.ps1` now:
    - Creates `.cidra\Agents\` with all agent folders (chunker, brainstormer, documenter, recommender).
    - Writes `.cidra\config.yaml`.
    - Installs IDE integrations (`.cursorrules`, `.vscode\cidra-settings.json`, `CLAUDE.md`).
    - **Copies `.claude\commands\`** (14 slash command templates — 4 entry points + 10 sub-commands). On re-install with `-ForceFramework`, fully replaces them; otherwise merges new files only.
15. Strictly verifies `.cidra\Agents\` (with expected agent tokens) and `.claude\commands\` (with expected entry points) landed. Refuses to declare success on a partial install.
16. Writes `cidra.env.ps1` at the project root so Step 10 (and any other future PowerShell step) can recover `$project` / `$component` / `$framework` via `. .\cidra.env.ps1` instead of re-typing.
17. Opens the project in Cursor (or VS Code as fallback) — warns loudly if the preferred IDE is unavailable so you know to install the Claude Code extension in the fallback IDE.
18. Prints the next-step instructions (extension check → open chat → `/brainstorm`).

### 1f. What you get when it finishes

```
C:\projects\rk1_pharmacy\
├── .cidra\Agents\                  # framework files
│   └── _bootstrap\                 # bootstrap state sentinels (do not edit)
├── .claude\commands\               # 14 slash command templates (.md)
├── .cursorrules                    # IDE integration
├── .vscode\cidra-settings.json     # IDE integration
├── CLAUDE.md                       # project-level Claude instructions
├── cidra.env.ps1                   # dot-source to restore $project/$component
├── Reference\                      # reference materials (if -ReferenceDocsPath given)
└── Source Code\                    # your source files
```

You are now ready to use Claude Code in the IDE that just opened. **All further steps happen inside the IDE chat, not in PowerShell — until Step 10 (delivery zip).**

> **Idempotent:** safe to re-run. Each stage has a completion sentinel (source copy, MOTW unblock, install). A failed run is detected on the next invocation and only the failed stage is redone — successful stages are skipped.
>
> **`-ForceSource` vs `-ForceFramework`:** these are orthogonal. Use `-ForceSource` to refresh source from disk (new customer drop). Use `-ForceFramework` to nuke and rebuild `.cidra/` and `.claude\commands\` (after a framework upgrade that removes commands).
>
> **Re-using on the next project:** run the same `bootstrap.ps1` with a different `-ProjectFolder` / `-ComponentId` / `-SourcePath`. The framework is reused from the same `C:\Users\<USER>\tools\enterprise_cidra_framework\`.

---

## Step 2 — Stage 0: `/brainstorm` (this is THINKING, not a script)

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
- For each item: respond ✓ (will provide), ✗ (won't / can't), ? (will check)
- Discuss with the customer if any 🔴 CRITICAL items are unresolved

---

## Step 3 — Source preprocessing (if your code needs it)

If your source has vendor-specific artifacts (e.g. CA 2E identification tags on COBOL, sequence numbers), clean it now. Mark-of-the-Web is already handled by the bootstrap.

**Example for CA 2E COBOL** (right-aligned Y-prefix tags):

```powershell
# Recover variables without re-typing:
cd C:\projects\rk1_pharmacy
. .\cidra.env.ps1

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

## Step 4 — Stage 1: `/chunk`

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

## Step 5 — Stage 2 setup: `/document:setup`

One-time configuration:

```
/document:setup
```

You will be asked:
- Documentation language (English / Hebrew / bilingual / other)
- Template (`enterprise_7_file` / variants)
- Output directory (default `./Screens/`)
- Validation report naming convention

The brainstormer's `BRAINSTORM_OUTPUT.yaml` provides defaults — `/document:setup` either confirms them or lets you override.

Output: `DOCUMENTER_PROJECT_CONFIG.yaml` at project root.

---

## Step 6 — Stage 2 run: `/document <COMPONENT>`

In the Claude Code chat (substitute the actual ComponentId you passed to bootstrap):

```
/document RK1_PHARMACY_JOURNAL
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

## Step 7 — Validate

```
/document:validate Screens\RK1_PHARMACY_JOURNAL
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
/document:fix Screens\RK1_PHARMACY_JOURNAL
```

…and re-validate.

---

## Step 8 — `/brainstorm:gap` (checkpoint 3)

After validation:

```
/brainstorm:gap
```

Refreshes `MISSING_INPUTS.md` with the post-validation gap list. The customer sees exactly which inputs would have lifted documentation quality (if they want to invest more).

---

## Step 9 (optional) — Stage 3: `/recommend`

Only if `purpose` from `/brainstorm` included modernization:

```
/recommend RK1_PHARMACY_JOURNAL
```

The recommender runs a dialog (direction → options → confirmation), then produces:
- `RECOMMENDATIONS\<COMPONENT>\RECOMMENDATION_REPORT.md`
- Technology comparison, migration roadmap, risk assessment, cost-benefit analysis

---

## Step 10 — Package for delivery

**POWERSHELL — recover your variables, then build the zip:**

```powershell
# In any new PowerShell session, recover the project variables:
cd C:\projects\rk1_pharmacy
. .\cidra.env.ps1
# Now $project, $component, $framework, $projectFolder, $projectRoot are all defined.

$delivery = "$project\${component}_Documentation_$(Get-Date -Format yyyy-MM-dd).zip"
$staging  = "$env:TEMP\cidra_delivery_$(Get-Random)"

New-Item -ItemType Directory -Path "$staging\$component" -Force | Out-Null
Copy-Item "$project\Screens\$component\*" -Destination "$staging\$component\" -Recurse

# Optional: include brainstormer artifacts as context
Copy-Item "$project\BRAINSTORM_OUTPUT.yaml" -Destination "$staging\$component\" -ErrorAction SilentlyContinue
Copy-Item "$project\MISSING_INPUTS.md"      -Destination "$staging\$component\" -ErrorAction SilentlyContinue

Compress-Archive -Path "$staging\$component" -DestinationPath $delivery -CompressionLevel Optimal
Remove-Item $staging -Recurse -Force
Write-Output "Delivery zip: $delivery"
```

Optionally write a Hebrew/English cover letter alongside — see the Maccabi RK1 project's `COVER_LETTER_FOR_CLIENT.md` for a template.

---

## Quick reference — full happy path

| Step | Shell | Command |
|------|-------|---------|
| Prereqs (once per machine) | PS | `winget install Git + Cursor + PowerShell`; install Claude Code extension; sign in |
| 1c (once per machine)      | PS | `git clone` the framework to `C:\Users\<USER>\tools\enterprise_cidra_framework` |
| 1d (per project)           | PS | `.\bootstrap.ps1 -ProjectFolder <name> -ComponentId <ID> -SourcePath <path>` |
| 2                          | IDE | `/brainstorm` → 3 files at root, customer acknowledges gaps |
| 3                          | PS  | Preprocess source if needed (CA 2E tags, sequence numbers, encoding) |
| 4                          | IDE | `/chunk:analyze Source Code`, then `/chunk Source Code` → `CHUNKS\` |
| 5                          | IDE | `/document:setup` → `DOCUMENTER_PROJECT_CONFIG.yaml` |
| 6                          | IDE | `/document <COMPONENT>` → `Screens\<COMPONENT>\` |
| 7                          | IDE | `/document:validate` → 100/100 target (loop with `/document:fix`) |
| 8                          | IDE | `/brainstorm:gap` → refreshed `MISSING_INPUTS.md` |
| 9 [opt]                    | IDE | `/recommend <COMPONENT>` → `RECOMMENDATIONS\<COMPONENT>\` |
| 10                         | PS  | `. .\cidra.env.ps1`; `Compress-Archive` → delivery zip |

`PS` = PowerShell. `IDE` = Claude Code chat in Cursor / VS Code.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `bootstrap.ps1`: "missing prerequisites" | Git or Cursor/VS Code not on PATH | Run the winget commands the script printed, **close and reopen PowerShell**, re-run bootstrap |
| `bootstrap.ps1`: "Detected ... sync path" | Project lands on OneDrive / Google Drive / Dropbox | Move project to `C:\projects\`, or pause sync and pass `-AllowSyncDrive` |
| `bootstrap.ps1`: "Project directory already exists and contains N items but no .cidra/" | Accidentally pointing at a non-CIDRA directory | Pick a different `-ProjectFolder`, or pass `-AdoptExistingDirectory` if intentional |
| `bootstrap.ps1`: "Framework checkout cannot be fast-forwarded" | You edited framework files locally, or upstream rebased | Run `git -C <FrameworkPath> status` to inspect; clean it, OR pass `-AllowStaleFramework` to use the current SHA |
| `bootstrap.ps1`: "Framework has uncommitted changes or a stuck merge" | Dirty working tree | Run `git stash` / `git reset --hard` / `git merge --abort` in the framework, then retry |
| `bootstrap.ps1`: previous copy was interrupted | Source Code\ has partial files | Re-run bootstrap; the sentinel mismatch is detected automatically and the copy is redone |
| `bootstrap.ps1`: "install.ps1 returned exit code N" | `install.ps1` failed inside its child process | Read the captured output above the error. Pass `-ForceFramework` to wipe and reinstall `.cidra/` + `.claude\commands\` |
| `install.ps1`: "Access is denied" | Mark-of-the-Web on freshly downloaded scripts | The bootstrap handles this automatically. If running `install.ps1` directly: `Get-ChildItem $framework -Recurse -File \| Unblock-File` |
| `install.ps1`: Notepad opens instead of running | You are in `cmd.exe`, not PowerShell | Open PowerShell. Run `powershell` first if needed. |
| Slash commands don't autocomplete | `.claude\commands\` was not copied by `install.ps1` | Verify framework has the updated `install.ps1` (it copies `.claude\commands\` automatically). Re-run `bootstrap.ps1 -ForceFramework` |
| Hebrew text shows as mojibake in script outputs | File written as UTF-8 without BOM, PowerShell 5.1 reading as CP1252 | Use PowerShell 7 (`pwsh`). Or re-write with UTF-8 BOM: `[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($true))` |
| `/document` produces score <100 | Forbidden words, estimate language, or missing sections | Run `/document:fix`, re-validate |
| Chunker produces oversized chunks (>8000 tokens) | Single section too large | Use a splitting post-step (paragraph-boundary aware). See Maccabi RK1's `_chunker.ps1` for a working example. |
| Mermaid diagrams render as raw code in viewer | Viewer doesn't support Mermaid | Pre-render to SVG with `mmdc`, embed as `<img src="data:image/svg+xml;base64,...">` |

---

## What lives where (after a complete run)

```
<project>/
├── .cidra/                              # framework files (don't edit)
│   └── _bootstrap/                      # bootstrap state sentinels
├── .claude/commands/                    # slash commands
├── Source Code/                         # your source code (preprocessed)
├── Reference/                           # reference materials (if -ReferenceDocsPath was used)
├── cidra.env.ps1                        # dot-source to restore variables
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
THE_BRAINSTORMER_AGENT (Stage 0)
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

*CIDRA Framework v1.1.0 (B+CIDRA) · Runbook v2.0 (bootstrap.ps1) · 2026-05-31*
*Repository: https://github.com/iliyaruvinsky/enterprise_cidra_framework*
