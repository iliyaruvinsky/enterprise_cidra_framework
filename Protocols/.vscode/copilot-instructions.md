# CIDRA Documentation Instructions for GitHub Copilot

## 🎯 Project Context

This project uses **CIDRA Framework** for accurate code documentation.

**Framework**: Chunker + Interpreter + Documenter + Recommender + Applicator  
**Goal**: 100% accurate documentation with zero hallucinations

---

## 📋 Critical Rules (NO EXCEPTIONS)

### **1. Code-Only Documentation**

- **NEVER** document anything not found in actual code files
- **ALWAYS** base documentation on files in `Source Code/` directory
- **MUST** scan ALL source files before documenting any component
- **NEVER** copy content from other components

### **2. Accurate Counting**

- **COUNT** lines exactly using: `(Get-Content file).Count`
- **COUNT** methods/functions from actual code
- **COUNT** data structures field by field
- **NO** "approximately", "around", or "+" signs

### **3. Shared Component Detection**

**Technology-specific:**
- **SAP**: Check Component Controller for shared nodes
- **React**: Check for shared hooks/contexts  
- **Python**: Check for shared modules/classes
- **AS/400**: Check copy members

**MARK** clearly: "(shared from [SOURCE])" or "(unique)"

### **4. Careful Language**

- **USE**: "appears that", "according to code", "seems to"
- **NEVER**: "the system does", "definitely performs"
- **AVOID**: "advanced", "intelligent", "smart"

### **5. Standard Documentation Structure**

**MUST** create exactly 7 files per component:

1. `01_SPECIFICATION.md` - Technical overview
2. `02_UI_MOCKUP.md` - Interface description
3. `03_TECHNICAL_ANALYSIS.md` - Detailed analysis
4. `04_BUSINESS_LOGIC.md` - Business rules
5. `05_CODE_ARTIFACTS.md` - Code snippets with citations
6. `README.md` - Quick reference (~200 lines max)
7. `VALIDATION_REPORT.md` - Accuracy verification (100/100 required)

---

## 🎯 Success Criteria

Documentation is ready when:

- ✅ All 7 files created
- ✅ All code cited with line numbers
- ✅ All counts exact (no estimates)
- ✅ Shared components identified
- ✅ Careful language used throughout
- ✅ Limitations section included
- ✅ Validation report shows 100/100
- ✅ Zero invented content

---

**GitHub Copilot is now configured to follow CIDRA documentation standards!**
