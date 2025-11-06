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
# MUST scan entire Source Code/ directory before documenting
grep -r "COMPONENT_NAME" "Source Code/"

# Record exact results:
"Found X relevant files out of Y total files"
```

### **2. Count Exactly**

- NO "approximately", "around", "~", or "+"
- Count field by field in structures
- Use exact tools: `(Get-Content file).Count`

### **3. Cite Everything**

Every code snippet MUST include:
- Exact file path
- Exact line numbers
- Exact code (copy-paste)

```language
actual_code_here

**Source**: Source Code/[PATH]/[FILE] lines [START]-[END]
```

### **4. Identify Shared Components**

Check for shared/common components:
- SAP: Component Controller
- React: Shared hooks/contexts
- Python: Common modules
- AS/400: Copy members

Mark: "(shared from [SOURCE])" or "(unique)"

### **5. Use Careful Language**

| ❌ Never Use | ✅ Always Use |
|-------------|--------------|
| "The system does" | "According to code" |
| "Definitely" | "Appears to" |
| "Advanced/Smart/Intelligent" | [Remove] |

### **6. Acknowledge What You Don't Know**

MUST include limitations section:

```markdown
## Documentation Limitations

### What Cannot Be Known:
- [List unknowns]

### What Is Known:
- [List what's documented]
```

### **7. Validate Everything**

Create VALIDATION_REPORT.md with:
- Files scanned count
- Components found
- Accuracy verification
- Zero hallucinations confirmation

---

## Enforcement

**BEFORE claiming documentation complete:**

- [ ] Scanned ALL files in Source Code/
- [ ] Counted exactly (no estimates)
- [ ] Cited all code with line numbers
- [ ] Checked shared components
- [ ] Used careful language
- [ ] Added limitations section
- [ ] Created validation report

**If ANY checkbox unchecked → STOP and fix!**

---

**These rules prevent hallucinations and ensure 100% accuracy.**
