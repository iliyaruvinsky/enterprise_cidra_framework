# CIDRA Framework - Quick Start Guide

**Get started with CIDRA in 5 minutes!**

---

## 🎯 What is CIDRA?

**CIDRA** = **C**hunker + **I**nterpreter + **D**ocumenter + **R**ecommender + **A**pplicator

A framework for documenting and modernizing legacy systems using AI agents.

**What CIDRA does:**
- 📦 Organizes your code (Chunker)
- 📝 Documents it accurately (Documenter)  
- 💡 Recommends modernization (Recommender)
- 🚀 Zero hallucinations, 100% accuracy

---

## ⚡ 5-Minute Setup

### **Step 1: Clone CIDRA** (1 minute)

```bash
git clone https://github.com/iliyaruvinsky/enterprise_cidra_framework.git
cd enterprise_cidra_framework
```

### **Step 2: Prepare Your Code** (2 minutes)

Create your project structure:

```bash
# Create your project directory
mkdir MY_PROJECT
cd MY_PROJECT

# Create Source Code directory
mkdir "Source Code"

# Copy your code files to Source Code/
# For SAP: Export from SAP GUI → Source Code/
# For React: Copy src/ → Source Code/
# For Python: Copy app/ → Source Code/
```

### **Step 3: Run Setup Wizard** (2 minutes)

```bash
# Linux/Mac
../enterprise_cidra_framework/Wizards/setup-wizard.sh

# Windows
..\enterprise_cidra_framework\Wizards\setup-wizard.ps1
```

The wizard asks:
1. **Technology?** (SAP / AS/400 / React / Python / Custom)
2. **Project name?** (e.g., "HR_SYSTEM")
3. **Code location?** (default: "./Source Code")
4. **Language?** (Hebrew / English)

Result: `.cidra-config.json` created in your project!

---

## 🚀 Your First Documentation

### **Option A: Using Cursor or Claude Code**

```bash
# Open your project in Cursor/Claude Code
cursor .

# In the chat, type:
@THE_DOCUMENTER_AGENT document component [COMPONENT_NAME]

# Example for SAP:
@THE_DOCUMENTER_AGENT document screen LOGIN_SCREEN

# Example for React:
@THE_DOCUMENTER_AGENT document component UserProfile
```

**Result**: 7 documentation files created automatically!

### **Option B: Using VS Code + GitHub Copilot**

```bash
# Open VS Code
code .

# Copy IDE protocols
cp -r ../enterprise_cidra_framework/Protocols/.vscode .

# Restart VS Code

# Open Copilot Chat (Ctrl+Shift+I):
@workspace Document component [COMPONENT_NAME] following CIDRA standards
```

---

## 📁 What You Get

CIDRA creates **7 standard documentation files** per component:

```
Your_Component/
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

### **Stage 0: Chunker** (Optional but Recommended)

```bash
@THE_CHUNKER_AGENT analyze my codebase using adaptive strategy
```

**Result**: Organized code chunks in `/chunks/` directory

### **Stage 1: Documenter** (Core)

```bash
@THE_DOCUMENTER_AGENT document component COMPONENT_1
@THE_DOCUMENTER_AGENT document component COMPONENT_2
# Repeat for all components
```

**Result**: Complete documentation for each component

### **Stage 2: Recommender** (Modernization)

```bash
@THE_RECOMMENDER_AGENT recommend modernization for MY_SYSTEM
```

**Result**: 
- Technology comparison
- Migration strategy
- ROI analysis
- Risk assessment

---

## ✅ Verify Success

### **Check 1: Configuration Created**

```bash
cat .cidra-config.json
# Should see: project_name, technology, plugin, code_location
```

### **Check 2: Documentation Generated**

```bash
ls [COMPONENT_NAME]/
# Should see: 7 .md files
```

### **Check 3: Validation Passed**

```bash
cat [COMPONENT_NAME]/VALIDATION_REPORT.md
# Should see: 100/100 accuracy score
```

---

## 🎓 Next Steps

### **For First-Time Users:**

1. ✅ You completed quick start - great!
2. 📖 Read: `Documentation/USER_GUIDE.md` (detailed workflows)
3. 🏗️ Read: `Documentation/ARCHITECTURE.md` (understand the system)
4. 🔌 Read: `Documentation/PLUGINS_OVERVIEW.md` (customize for your tech)

### **For Experienced Users:**

1. 🔧 Customize: `.cidra-config.json` with your business rules
2. 🎯 Optimize: Choose chunking strategy
3. 📊 Scale: Document entire system
4. 💡 Modernize: Use Recommender for planning

### **For Team Leads:**

1. 📋 Review: `WORKFLOW.md` (understand agent flow)
2. 🎯 Plan: How many components to document
3. 👥 Train: Share this guide with your team
4. 📈 Track: Monitor quality scores in validation reports

---

## 💡 Pro Tips

### **Tip 1: Start Small**
Don't document everything at once. Start with 1-2 components to learn the system.

### **Tip 2: Use Adaptive Chunking**
Let the_chunker organize your code first - it improves documentation quality.

### **Tip 3: Verify Everything**
Check VALIDATION_REPORT.md for each component - should always be 100/100.

### **Tip 4: Scan All Source Files**
CIDRA scans all files in `Source Code/` - the more complete your code, the better the docs.

### **Tip 5: Choose Your IDE**
CIDRA works with:
- ✅ Cursor (recommended)
- ✅ Claude Code (recommended)
- ✅ VS Code + GitHub Copilot
- ✅ Windsurf

Copy the appropriate protocol from `Protocols/` directory.

---

## 🆘 Troubleshooting

### **Problem: Agent not responding**

```bash
# Check configuration
cat .cidra-config.json

# Verify CIDRA framework location
ls ../enterprise_cidra_framework/Agents/
```

### **Problem: Documentation incomplete**

```bash
# Check validation report
cat [COMPONENT]/VALIDATION_REPORT.md

# Look for missing sections
```

### **Problem: Hallucinations detected**

```bash
# CIDRA has strict anti-hallucination rules
# Check that you scanned ALL files in Source Code/
# Verify you're citing actual code with line numbers
```

---

## 📞 Getting Help

**Full Documentation**: `Documentation/USER_GUIDE.md`  
**Architecture**: `Documentation/ARCHITECTURE.md`  
**Installation**: `Documentation/INSTALLATION.md`  
**Plugins**: `Documentation/PLUGINS_OVERVIEW.md`

**Support**: Open an issue on GitHub

---

## 🎯 Real-World Example

**MACCABI ICM Project** used CIDRA to document 33 SAP WebDynpro screens:

- **Time saved**: 18x faster (18 hours → 1 hour per screen)
- **Accuracy**: 100% code alignment
- **Result**: Client feedback: "Built very well"

See: https://github.com/iliyaruvinsky/maccabi_cidra

---

**You're ready to start documenting! Pick your first component and go!** 🚀

**Estimated time**: 5 minutes setup + 25 minutes per component

