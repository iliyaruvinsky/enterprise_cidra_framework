# B+CIDRA Framework - Quick Start Guide

**Get started with B+CIDRA in 5 minutes!**

---

## 🤖 For AI Agents

**First time here?** Read these files in order:
1. This file (`QUICK_START.md`) - Overview
2. `THE_PROCESS.md` - End-to-end pipeline (B+CID / B+CIDR / B+CIDRA)
3. `Agents/registry.yaml` - Pipeline and agent capabilities
4. `Agents/shared/agent_handoff_protocol.md` - How agents communicate

**To run an agent**, use the slash commands registered by `bootstrap.ps1`:
`/brainstorm`, `/chunk:analyze`, `/chunk`, `/document <COMPONENT>`,
`/document:validate`, `/document:fix`, `/recommend <COMPONENT>`.

---

## 🎯 What is B+CIDRA?

**B+CIDRA** = **B**rainstormer + **C**hunker + **I**nterpreter + **D**ocumenter + **R**ecommender + **A**pplicator

> The leading **B** is for **Brainstormer** (Stage 0). The original acronym was CIDRA; the Brainstormer was added in front so the first artifact a project produces is a project-scoping blueprint, not raw chunks.

A framework for documenting and modernizing legacy systems using AI agents.

**What B+CIDRA does:**
- 🧠 Scopes the project up front (Brainstormer)
- 📦 Organizes your code (Chunker)
- 📝 Documents it accurately (Documenter)
- 💡 Recommends modernization (Recommender)
- 🚀 Zero hallucinations, 100% accuracy

Today, the **B+CID** (stop after Documenter) and **B+CIDR** (stop after Recommender) exits are live. The full **B+CIDRA** exit (Interpreter + Applicator) is on the roadmap — see `THE_PROCESS.md`.

---

## ⚡ 5-Minute Setup

The entire per-project mechanical setup is one PowerShell script: `Scripts\bootstrap.ps1`. It clones (or updates) the framework, creates the project folder, copies your source, installs `.cidra/`, registers slash commands, and launches the IDE.

### **Step 1: One-time prerequisites** (per machine, not per project)

**POWERSHELL:**

```powershell
# Git (required)
winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements

# Cursor (required — or VS Code instead)
winget install --id Anysphere.Cursor -e --accept-source-agreements --accept-package-agreements

# Recommended: PowerShell 7 for reliable Hebrew / Unicode path handling
winget install --id Microsoft.PowerShell -e --accept-source-agreements --accept-package-agreements
```

Close and reopen PowerShell so the new tools land on PATH. Then, inside Cursor/VS Code, install the **Claude Code** extension and sign in with your Anthropic account — without it, none of the slash commands work.

### **Step 2: Clone the framework once** (per machine)

**POWERSHELL:**

```powershell
$framework = "$env:USERPROFILE\tools\enterprise_cidra_framework"
New-Item -ItemType Directory -Path (Split-Path $framework) -Force | Out-Null
git clone https://github.com/iliyaruvinsky/enterprise_cidra_framework.git $framework
```

### **Step 3: Run the bootstrap** (per project — the actual 5 minutes)

**POWERSHELL:**

```powershell
cd "$env:USERPROFILE\tools\enterprise_cidra_framework"
git pull
cd Scripts
.\bootstrap.ps1 -ProjectFolder "<short_name>" `
                -ComponentId  "<UPPER_SNAKE_ID>" `
                -SourcePath   "<path-to-source>" `
                -ReferenceDocsPath "<optional>" `
                -SourceRenameTo ".cob"
```

The `git pull` is **not optional** — framework updates ship daily during the early build-out; running an old `bootstrap.ps1` is how today's already-fixed bugs come back.

Bootstrap parameters:
1. **`-ProjectFolder`** — short ASCII directory name (e.g. `rk1_pharmacy`).
2. **`-ComponentId`** — UPPER_SNAKE_CASE id (e.g. `RK1_PHARMACY_JOURNAL`) — flows through `CHUNKS/`, `Screens/<COMPONENT>/`, `RECOMMENDATIONS/<COMPONENT>/`.
3. **`-SourcePath`** — folder containing the legacy source to document.
4. **`-ReferenceDocsPath`** — optional Hebrew/English spec docs the Documenter may consult as marked reference.
5. **`-SourceRenameTo`** — optional extension rename (e.g. `.cob`) so syntax highlighting and tools recognize the dialect.

Result: a new project folder with `.cidra/` installed, slash commands registered, and Cursor/VS Code opened on it. See `RUNBOOK.md` for the full per-step explanation (and the `-ForceFramework` first-run quirk).

---

## 🚀 Your First Documentation

Once `bootstrap.ps1` has opened your project in Cursor / VS Code with Claude Code signed in, drive the pipeline from the chat using slash commands.

### **Option A: Using Cursor or Claude Code** (recommended)

```text
# In the Claude Code chat panel:
/brainstorm
# Answer the brainstormer's questions; it emits BRAINSTORM_OUTPUT.yaml.

/chunk:analyze
# Optional dry-run: shows the chunking plan without writing CHUNKS/.

/chunk
# Produces CHUNKS/ for the component.

/document <COMPONENT_NAME>
# Example for AS/400: /document RK1_PHARMACY_JOURNAL
# Example for SAP:    /document LOGIN_SCREEN
# Example for React:  /document UserProfile

/document:validate <COMPONENT_NAME>
# Runs the 100-point validation gate on the produced docs.

/document:fix <COMPONENT_NAME>
# Auto-fixes common documentation issues to reach 100/100.
```

**Result**: the 7 standard documentation files for the component, plus a `VALIDATION_REPORT.md` at 100/100.

### **Option B: Using VS Code + GitHub Copilot**

Slash commands require Claude Code. If you must drive via Copilot Chat, copy the IDE protocols and reference the agent specs explicitly:

```powershell
# Copy IDE protocols into your project
Copy-Item -Recurse "$env:USERPROFILE\tools\enterprise_cidra_framework\Protocols\.vscode" .
# Restart VS Code, then in Copilot Chat reference:
#   .cidra/Agents/THE_DOCUMENTER_AGENT/agent_specification.md
# and instruct Copilot to follow it against your component.
```

---

## 📁 What You Get

B+CIDRA creates **7 standard documentation files** per component:

```
Screens/<COMPONENT>/
├── 01_SPECIFICATION.md      # Technical overview
├── 02_UI_MOCKUP.md          # UI/Interface (if applicable)
├── 03_TECHNICAL_ANALYSIS.md # Detailed analysis
├── 04_BUSINESS_LOGIC.md     # Business rules
├── 05_CODE_ARTIFACTS.md     # Code snippets with citations
├── README.md                # Quick reference
└── VALIDATION_REPORT.md     # 100% accuracy verification
```

**Every file is based on actual code - zero hallucinations!**

---

## 🔄 Complete Workflow

### **Stage 0: Brainstormer** (project scoping)

```text
/brainstorm
```

**Result**: `BRAINSTORM_OUTPUT.yaml` — goals, gap analysis, documenter/chunker config, and the blueprint that downstream stages consume.

### **Stage 1: Chunker** (code organization)

```text
/chunk:analyze
/chunk
```

**Result**: organized code chunks under `CHUNKS/<COMPONENT>/`.

### **Stage 2: Documenter** (core)

```text
/document COMPONENT_1
/document COMPONENT_2
# Repeat per component, then:
/document:validate COMPONENT_1
/document:fix COMPONENT_1
```

**Result**: Complete documentation under `Screens/<COMPONENT>/`, validated to 100/100.

### **Stage 3: Recommender** (modernization)

```text
/recommend <COMPONENT>
```

**Result** in `RECOMMENDATIONS/<COMPONENT>/`:
- Technology comparison
- Migration strategy
- ROI analysis
- Risk assessment

> **Stages 4-5: Interpreter + Applicator** are on the roadmap. See `THE_PROCESS.md`.

---

## ✅ Verify Success

### **Check 1: Brainstorm artifact present**

```powershell
Get-Content BRAINSTORM_OUTPUT.yaml | Select-Object -First 20
# Should see: goals, documenter_config, chunker_config
```

### **Check 2: Documentation Generated**

```powershell
Get-ChildItem "Screens\<COMPONENT_NAME>\"
# Should see: 7 .md files
```

### **Check 3: Validation Passed**

```powershell
Get-Content "Screens\<COMPONENT_NAME>\VALIDATION_REPORT.md" | Select-String "score"
# Should see: 100/100 accuracy score
```

---

## 🎓 Next Steps

### **For First-Time Users:**

1. ✅ You completed quick start - great!
2. 📖 Read: `THE_PROCESS.md` (end-to-end pipeline, exit altitudes)
3. 📖 Read: `RUNBOOK.md` (full per-step setup, including edge cases)
4. 🏗️ Read: `Documentation/ARCHITECTURE.md` (understand the system)
5. 🔌 Read: `Documentation/PLUGINS_OVERVIEW.md` (customize for your tech)

### **For Experienced Users:**

1. 🔧 Customize: `BRAINSTORM_OUTPUT.yaml` (`documenter_config`, `chunker_config`) with your business rules
2. 🎯 Optimize: Choose chunking strategy via `/chunk:analyze`
3. 📊 Scale: Document entire system one component at a time
4. 💡 Modernize: Run `/recommend <COMPONENT>` for migration planning

### **For Team Leads:**

1. 📋 Review: `THE_PROCESS.md` (end-to-end flow, modes, and the agent decision tree) and `RUNBOOK.md` (the per-project mechanical setup contract)
2. 🎯 Plan: How many components to document
3. 👥 Train: Share this guide with your team
4. 📈 Track: Monitor quality scores in validation reports

---

## 💡 Pro Tips

### **Tip 1: Start Small**
Don't document everything at once. Start with 1-2 components to learn the system.

### **Tip 2: Always run `/brainstorm` first**
The brainstormer's `BRAINSTORM_OUTPUT.yaml` is what makes the downstream stages deterministic. Skipping it is the #1 cause of mismatched chunking / off-target docs.

### **Tip 3: Verify Everything**
Check VALIDATION_REPORT.md for each component - should always be 100/100. Use `/document:fix` to close the last gaps automatically.

### **Tip 4: Scan All Source Files**
B+CIDRA scans all files under the path you passed as `-SourcePath` — the more complete the source, the better the docs.

### **Tip 5: Choose Your IDE**
B+CIDRA works with:
- ✅ Cursor + Claude Code (recommended)
- ✅ VS Code + Claude Code (recommended)
- ✅ VS Code + GitHub Copilot (fallback — see Option B)
- ✅ Windsurf

Slash commands are registered by `bootstrap.ps1` for Claude Code. For other IDEs, copy the appropriate protocol from `Protocols/`.

---

## 🆘 Troubleshooting

### **Problem: Slash commands not appearing**

```powershell
# Confirm .cidra/ and .claude/commands/ landed in your project
Get-ChildItem .cidra, .claude\commands

# Confirm the framework checkout exists where bootstrap expected it
Get-ChildItem "$env:USERPROFILE\tools\enterprise_cidra_framework\Agents"
```

If `.claude/commands/` is empty, re-run `bootstrap.ps1` — it re-registers them idempotently.

### **Problem: Documentation incomplete**

```powershell
# Check validation report
Get-Content "Screens\<COMPONENT>\VALIDATION_REPORT.md"
# Then run the auto-fixer for whatever it flagged:
# /document:fix <COMPONENT>
```

### **Problem: Hallucinations detected**

B+CIDRA has strict anti-hallucination rules (see `Agents/shared/anti_hallucination_engine.yaml`). Check that:
- You scanned ALL files under `-SourcePath`.
- Every claim cites an actual source file with a line number.
- The brainstormer's `BRAINSTORM_OUTPUT.yaml` reflects the real scope.

---

## 📞 Getting Help

**Pipeline reference**: `THE_PROCESS.md`
**Setup reference**: `RUNBOOK.md`
**Architecture**: `Documentation/ARCHITECTURE.md`
**Installation**: `Documentation/INSTALLATION.md`
**Plugins**: `Documentation/PLUGINS_OVERVIEW.md`

**Support**: Open an issue on GitHub

---

> **Footnote — real-world example.** Pre-B+CIDRA (pre-bootstrap) the MACCABI ICM project used the original CIDRA pipeline to document 33 SAP WebDynpro screens, reporting ~18× faster turnaround per screen and "built very well" client feedback. That run pre-dates the Brainstormer stage and the `bootstrap.ps1` setup described above, so the exact commands it used do not match this guide; it is cited only as historical evidence that the pipeline scales to dozens of screens.

---

**You're ready to start documenting! Pick your first component and go!** 🚀

**Estimated time**: 5 minutes setup + 25 minutes per component
