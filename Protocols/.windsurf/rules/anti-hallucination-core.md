# Anti-Hallucination Core Rules for CIDRA

**Version**: 1.0.0  
**Applies to**: All CIDRA documentation projects

---

## Core Principle

**Document ONLY what exists in actual code. Never invent, assume, or speculate.**

---

## Mandatory Rules

### **1. Scan All Source Files**

```bash
# MUST scan entire Source Code/ directory
grep -r "COMPONENT_NAME" "Source Code/"

# Record: "Found X relevant files out of Y total files"
```

### **2. Count Exactly**

- NO "approximately", "around", "~", or "+"
- Count field by field
- Use exact tools

### **3. Cite Everything**

```language
code_here

**Source**: Source Code/[FILE] lines [START]-[END]
```

### **4. Identify Shared Components**

Check for shared components:
- SAP: Component Controller
- React: Shared hooks
- Python: Common modules

Mark: "(shared)" or "(unique)"

### **5. Use Careful Language**

✅ "According to code, appears to"  
❌ "The system does"

### **6. Acknowledge Limitations**

MUST include limitations section.

### **7. Validate**

Create VALIDATION_REPORT.md with 100/100 score.

---

**These rules ensure 100% accuracy.**
