# Claude Code Setup for CIDRA

**IDE**: Claude Code  
**Purpose**: Configure Claude Code to work with CIDRA Framework

---

## 📋 Setup Instructions

### **Step 1: Copy Rules to Your Project**

```bash
# In your project directory
cp -r [PATH_TO_CIDRA]/Protocols/.claude .

# Verify
ls .claude/rules/
# Should see: anti-hallucination-core.md, documentation-standards.md
```

### **Step 2: Activate Rules**

Claude Code automatically loads rules from `.claude/rules/` directory.

**Restart Claude Code** to activate.

### **Step 3: Verify Activation**

```bash
# In Claude Code chat:
"Are you following CIDRA anti-hallucination rules?"

# Should confirm: Yes, scanning Source Code/, exact counting, etc.
```

---

## 📁 Files in This Directory

### **rules/**
- `anti-hallucination-core.md` - Universal accuracy rules
- `documentation-standards.md` - 7-file structure standard

### **settings.local.json**
- Permissions configuration for Claude Code
- Allows bash/PowerShell for code scanning

---

## 🎯 Usage

Once setup complete:

```
@THE_DOCUMENTER_AGENT document component [NAME]
```

Claude Code will:
1. Scan all Source Code/ files
2. Count exactly
3. Document only what exists
4. Create 7 files with 100% accuracy
5. Generate validation report

---

## 🔧 Customization

### **Add Project-Specific Rules**

Create `.claude/rules/project-specific.md`:

```markdown
# Project-Specific Rules

## Your Custom Rules Here
- Rule 1
- Rule 2
```

### **Modify Permissions**

Edit `settings.local.json` to add/remove allowed commands.

---

**Claude Code is now configured for CIDRA!**
