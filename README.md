# CIDRA Framework
## Chunker + Interpreter + Documenter + Recommender + Assistant

**Framework גנרי לתיעוד ומודרניזציה של מערכות Legacy באמצעות AI.**

CIDRA מאחדת חמישה מנועים משלימים:

- `the_chunker` – ארגון קוד לחתיכות אופטימליות ל-LLM
- `the_interpreter` – *עתידי* (שמורה למנוע ניתוח הקשר)
- `the_documenter` – תיעוד מדויק 100%
- `the_recommender` – המלצות מודרניזציה מבוססות ROI
- `the_assistant` – פיתוח מואץ עם Agentic AI

ה-framework נבנה מתוך ניסיון בשטח ומותאם לכל ארגון בישראל שמבצע תיעוד ומודרניזציה בקנה מידה גדול.

---

## 🚀 התחלה מהירה

```bash
# Clone הפרויקט (Read-Only למפתחים)
git clone https://github.com/iliyaruvinsky/enterprise_cidra_framework.git
cd enterprise_cidra_framework

# הרצת אשף ההגדרות (יוצר .cidra-config.json)
./Wizards/setup-wizard.sh
# או ב-Windows
Wizards\setup-wizard.ps1
```

האינטראקציה עם האשף:

1. בחירת טכנולוגיה (SAP / AS/400 / React / Python / Custom)
2. שם הפרויקט
3. מיקום קוד המקור
4. שפת התיעוד (עברית / אנגלית)
5. הגדרות מתקדמות (naming conventions, business rules, quality gates)

האשף יוצר קובץ `.cidra-config.json` שמאפשר ל-CIDRA להתאים את עצמו לפרויקט הספציפי.

---

## 📁 מבנה הפרויקט

```
enterprise_cidra_framework/
├── Agents/
│   ├── THE_CHUNKER_AGENT/
│   ├── THE_DOCUMENTER_AGENT/
│   └── THE_RECOMMENDER_AGENT/
├── Documentation/
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   ├── USER_GUIDE.md
│   └── PLUGINS_OVERVIEW.md
├── Plugins/
│   ├── sap_plugin.yaml
│   ├── as400_plugin.yaml
│   ├── react_plugin.yaml
│   └── python_plugin.yaml
├── Protocols/   (תבניות להפעלה ב-IDE שונים)
│   ├── .vscode/
│   ├── .claude/
│   └── .windsurf/
├── Wizards/
│   ├── setup-wizard.sh
│   ├── setup-wizard.ps1
│   └── wizard-config-schema.json
├── README.md
├── LICENSE (ברירת מחדל: MIT)
└── .gitignore
```

---

## 🤖 Agents

| Agent | תפקיד | סטטוס |
|-------|-------|--------|
| `the_chunker` | ארגון חכם של קוד, מיפוי תלותים ויצירת metadata | Production Ready |
| `the_documenter` | תיעוד מדויק עם Anti-Hallucination Framework | Production Ready |
| `the_recommender` | המלצות מודרניזציה + ROI + Risk Assessment | Production Ready |
| `the_interpreter` | (Reservado) עתידי – הבנת הקוד בזמן אמת | Roadmap |
| `the_assistant` | (Reservado) Agentic Development Assistant | Roadmap |

כל Agent מגיע עם:
- מפרט מלא (`agent_specification.md`)
- מסמכי אינטגרציה לכלי פיתוח
- קובצי YAML לניהול תצורה
- מדריכי הפעלה ל-IDE (Cursor, Claude Code, VS Code)

---

## 📚 מדריכי התקנה ושימוש

- `Documentation/ARCHITECTURE.md` – תיאור מלא של תשתית CIDRA
- `Documentation/INSTALLATION.md` – הוראות התקנה ל-Linux / Windows / Mac
- `Documentation/USER_GUIDE.md` – תרחישים נפוצים + דוגמאות קוד
- `Documentation/PLUGINS_OVERVIEW.md` – פירוט תוספים לכל טכנולוגיה

כל מסמך נכתב כך שיתאים לארגונים שונים – ללא אזכורים ספציפיים ללקוחות.

---

## 🔌 Plugins

CIDRA כוללת תוספים מוכנים לטכנולוגיות מובילות:

- `sap_plugin.yaml` – SAP WebDynpro, ABAP, FI/CO, HR, BI/BW
- `as400_plugin.yaml` – RPG/RPGLE, COBOL, CL, DDS
- `react_plugin.yaml` – אפליקציות React/Node
- `python_plugin.yaml` – מערכות Django/FastAPI

כל Plugin מגדיר:
- תבניות תיעוד
- חוקים ייחודיים (naming conventions, validations)
- מסמכים נדרשים
- תהליכי בקרת איכות

ניתן ליצור Plugin חדש לכל טכנולוגיה ע"י שכפול והרחבה של אחד הקיימים.

---

## ⚙️ Workflow מומלץ

1. **הכנת הקוד** – משיכת קוד מקור למחשב שלך
2. **הפעלת wizard** – יצירת `.cidra-config.json`
3. **Chunking** – הפעלת `the_chunker` לקבלת קוד מאורגן ו-relationship map
4. **Documentation** – הפעלת `the_documenter` ליצירת 7 קבצי תיעוד לכל רכיב
5. **Validation** – הרצת בדיקות איכות (PowerShell/CLI) לווידוא 100% דיוק
6. **Recommendations** – שימוש ב-`the_recommender` למפת דרכים מודרנית

כל שלב מתועד היטב במדריכים הכלולים ומותאם לעבודה עם Cursor, Claude Code, VS Code ו-GitHub Copilot.

---

## 🔐 מדיניות שימוש

- Repository זה הוא **Read-Only** למפתחים. רק צוות הפלטפורמה מעדכן אותו.
- כל פרויקט יוצר קונפיגורציה ייעודית (`.cidra-config.json`) ומשתמש בכלים בהתאם.
- תרומות מתקבלות דרך Pull Requests והערכת צוות הפלטפורמה.

---

## 📞 תמיכה

לשאלות, תמיכה ופיתוח תוספים חדשים:  
`support@cidra-framework.example`

---

**CIDRA = הדרך החכמה לתעד ולחדש מערכות Legacy בישראל.**
