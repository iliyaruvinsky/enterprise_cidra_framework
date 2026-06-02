# B+CIDRA Framework
## Brainstormer + Chunker + Interpreter + Documenter + Recommender + Applicator

**Framework גנרי לתיעוד ומודרניזציה של מערכות Legacy באמצעות AI.**

B+CIDRA מאחדת שישה מנועים משלימים. ארבעה חיים היום (B, C, D, R); שניים מתוכננים (I, A):

- `the_brainstormer` – Stage 0 · גילוי מטרות, מיפוי קלטים, חוזה לשלבים הבאים (🟢 Live)
- `the_chunker` – Stage 1 · ארגון קוד לחתיכות אופטימליות ל-LLM (🟢 Live)
- `the_documenter` – Stage 2 · תיעוד מדויק 100% עם anti-hallucination (🟢 Live)
- `the_recommender` – Stage 3 · המלצות מודרניזציה מבוססות ROI (🟢 Live)
- `the_interpreter` – Stage 4 · *מתוכנן* (שכבת תרגום ל-IR לפני יצירת קוד)
- `the_applicator` – Stage 5 · *מתוכנן* (יצירת קוד יעד עם traceability)

ה-framework נבנה מתוך ניסיון בשטח ומותאם לכל ארגון בישראל שמבצע תיעוד ומודרניזציה בקנה מידה גדול.

> **B** הוקדם ל-CIDRA המקורי כדי לכפות אלסיטציית מטרות לפני כל עבודה טכנית. סדר ה-acronym (B-C-I-D-R-A) שומר על השם ההיסטורי, אבל סדר ההרצה בפועל הוא **B → C → D → R → I → A**.

---

## 📖 How to read this repo

| Doc | Purpose | When to open it |
|-----|---------|-----------------|
| **[THE_PROCESS.md](THE_PROCESS.md)** | Strategic overview of the B+CIDRA pipeline — six stages, three exit modes (📘 B+CID / 📗 B+CIDR / 📕 B+CIDRA), decision tree for scoping | Customer scoping, sales conversations, "what is this thing?" |
| **[RUNBOOK.md](RUNBOOK.md)** | Step-by-step execution guide — every command, every flag, every troubleshooting symptom for a real project run | Developers actually running the pipeline |
| **[QUICK_START.md](QUICK_START.md)** | 5-minute setup recap for returning users | You've done this before and need a reminder |
| `Agents/shared/agent_handoff_protocol.md` | Inter-agent contract specification | Framework maintainers, plugin authors |

**Reading order for a new user:** README (this file) → THE_PROCESS.md → RUNBOOK.md.

---

## ⚡ Quick Start (5 Minutes)

**New to B+CIDRA?** Start here: **[QUICK_START.md](QUICK_START.md)** 🚀

---

## 🚀 Full Setup

The whole per-project mechanical setup is a single PowerShell command. From the canonical `RUNBOOK.md` TL;DR:

**POWERSHELL:**

```powershell
cd "$env:USERPROFILE\tools\enterprise_cidra_framework"
git pull
cd Scripts
.\bootstrap.ps1 -ProjectFolder "<short_name>" -ComponentId "<UPPER_SNAKE_ID>" -SourcePath "<path-to-source>" -ReferenceDocsPath "<optional>" -SourceRenameTo ".cob"
```

The `git pull` is **not optional** — framework updates ship daily during the early build-out; running a stale `bootstrap.ps1` reintroduces already-fixed bugs.

What `Scripts\bootstrap.ps1` does in one shot:

1. Verifies prerequisites (Git + Cursor/VS Code on PATH).
2. Clones or fast-forwards the framework checkout.
3. Creates `C:\projects\<ProjectFolder>\` with a `Source Code\` subdirectory.
4. Copies your source files (literal-path enumeration; handles Hebrew, spaces, brackets).
5. Optionally renames AS/400 source-library exports with `-SourceRenameTo ".cob"`.
6. Installs `.cidra\Agents\` (all four live agents: brainstormer, chunker, documenter, recommender).
7. Registers the 14 slash command templates under `.claude\commands\`.
8. Writes `cidra.env.ps1` so future PowerShell sessions can `. .\cidra.env.ps1` to restore `$project` / `$component` / `$framework`.
9. Opens the project in Cursor (or VS Code as fallback).

When it finishes, open a Claude Code chat in the IDE and run `/brainstorm`. All further steps happen inside the IDE chat — see RUNBOOK.md Steps 2–9.

> First-time-on-this-machine? See `RUNBOOK.md` §1a for the one-time prerequisite installs (Git, Cursor/VS Code, PowerShell 7, Claude Code extension sign-in).

---

## 📁 מבנה הפרויקט

```
enterprise_cidra_framework/
├── Agents/
│   ├── THE_BRAINSTORMER_AGENT/       ← Stage 0 (NEW)
│   │   ├── agent_specification.md
│   │   └── skills.yaml
│   ├── THE_CHUNKER_AGENT/            ← Stage 1
│   │   ├── agent_specification.md
│   │   └── skills.yaml
│   ├── THE_DOCUMENTER_AGENT/         ← Stage 2
│   │   ├── agent_specification.md
│   │   └── skills.yaml
│   ├── THE_RECOMMENDER_AGENT/        ← Stage 3
│   │   ├── agent_specification.md
│   │   └── skills.yaml
│   ├── shared/
│   │   ├── agent_handoff_protocol.md
│   │   ├── anti_hallucination_engine.yaml
│   │   ├── validation_framework.yaml
│   │   └── templates/
│   └── registry.yaml
├── Documentation/
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   ├── USER_GUIDE.md
│   ├── PLUGINS_OVERVIEW.md
│   ├── ACTIVATION_COMMANDS.md       ← NEW
│   └── SKILLS_SPECIFICATION.md      ← NEW
├── Plugins/
│   ├── sap_plugin.yaml
│   ├── as400_plugin.yaml
│   ├── react_plugin.yaml
│   └── python_plugin.yaml
├── Protocols/   (תבניות להפעלה ב-IDE שונים)
│   ├── .vscode/
│   ├── .claude/
│   ├── .cursor/                     ← NEW
│   └── .windsurf/
├── Scripts/
│   ├── bootstrap.ps1                 ← single-command per-project setup
│   ├── install.ps1
│   ├── install.sh
│   └── add-agent.ps1
├── cidra.manifest.yaml
├── README.md                          ← you are here
├── THE_PROCESS.md                     ← strategic overview (start here)
├── RUNBOOK.md                         ← step-by-step execution guide
├── QUICK_START.md                     ← 5-minute recap
├── LICENSE (ברירת מחדל: MIT)
└── .gitignore
```

---

## 🤖 Agents

| Stage | Agent | תפקיד | סטטוס |
|:-----:|-------|-------|--------|
| **0** | `the_brainstormer` | גילוי מטרות, מיפוי קלטים, גזירת חוזה (`BRAINSTORM_OUTPUT.yaml`) | 🟢 Live |
| **1** | `the_chunker` | ארגון חכם של קוד, מיפוי תלותים ויצירת metadata | 🟢 Live |
| **2** | `the_documenter` | תיעוד מדויק עם Anti-Hallucination Framework | 🟢 Live |
| **3** | `the_recommender` | המלצות מודרניזציה + ROI + Risk Assessment | 🟢 Live |
| **4** | `the_interpreter` | (Reservado) שכבת IR בין המלצה ליצירת קוד | 🟣 Roadmap |
| **5** | `the_applicator` | (Reservado) יצירת קוד יעד עם traceability ל-source | 🟣 Roadmap |

> **Stage 0** הוא העוגן של ה-framework: כל החלטה למטה בצינור (תבנית תיעוד, שפה, מדיניות careful-language, scope) נגזרת מ-`BRAINSTORM_OUTPUT.yaml` שמופק כאן.

כל Agent מגיע עם:
- מפרט מלא (`agent_specification.md`)
- הגדרת יכולות (`skills.yaml`)
- מסמכי אינטגרציה לכלי פיתוח
- קובצי YAML לניהול תצורה
- מדריכי הפעלה ל-IDE (Cursor, Claude Code, VS Code)

---

## 🎯 Skills System (NEW)

כל Agent כולל `skills.yaml` שמגדיר:

### פקודות הפעלה (Slash Commands)

| Agent | פקודה | תיאור |
|-------|-------|-------|
| **Brainstormer** | `/brainstorm` | Stage 0 · אלסיטציית מטרות + ייצור `BRAINSTORM_OUTPUT.yaml` |
| **Brainstormer** | `/brainstorm:gap` | רענון `MISSING_INPUTS.md` ב-checkpoint |
| **Brainstormer** | `/brainstorm:status` | מצב נוכחי של ההבנה (מטרות / קלטים / פערים) |
| **Brainstormer** | `/brainstorm:format` | המלצה על פורמט תיעוד עם הצדקה |
| **Chunker** | `/chunk [path]` | חיתוך קוד לחלקים |
| **Chunker** | `/chunk:analyze [path]` | תצוגה מקדימה |
| **Chunker** | `/chunk:status` | סטטוס פעולה |
| **Documenter** | `/document:setup` | הגדרת פרויקט (פעם אחת) |
| **Documenter** | `/document [component]` | תיעוד רכיב |
| **Documenter** | `/document:validate` | בדיקת איכות 100 נקודות |
| **Documenter** | `/document:fix` | תיקון אוטומטי |
| **Recommender** | `/recommend [component]` | המלצות מודרניזציה |
| **Recommender** | `/recommend:compare` | השוואת טכנולוגיות |
| **Recommender** | `/recommend:risk` | הערכת סיכונים |

> ההפעלה מתבצעת תמיד דרך slash commands ב-Claude Code chat — אין יותר תבנית `@THE_*_AGENT`.

### סוגי Skills

- **user_invoked** - פקודות שהמשתמש מפעיל
- **dialog** - אינטראקציה עם המשתמש
- **internal** - יכולות אוטומטיות
- **output** - הגדרת פלטים
- **quality** - בדיקות איכות

מסמך מלא: `Documentation/SKILLS_SPECIFICATION.md`

---

## 🔧 התקנה מהירה (One-Line Install)

### Windows (PowerShell)
```powershell
# Clone והתקנה
git clone https://github.com/iliyaruvinsky/enterprise_cidra_framework.git
cd enterprise_cidra_framework
.\Scripts\install.ps1 -ProjectPath "C:\your\project"
```

### Linux/Mac
```bash
# Clone והתקנה
git clone https://github.com/iliyaruvinsky/enterprise_cidra_framework.git
cd enterprise_cidra_framework
./Scripts/install.sh -p /path/to/your/project
```

### אפשרויות התקנה

| אפשרות | תיאור |
|--------|-------|
| `-ProjectPath` / `-p` | נתיב לפרויקט היעד |
| `-Force` / `-f` | דריסת התקנה קיימת |
| `-Uninstall` / `-u` | הסרת CIDRA מפרויקט |
| `-Help` / `-h` | עזרה |

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
2. **Bootstrap** – הרצת `Scripts\bootstrap.ps1` (יוצר את ספריית הפרויקט, מעתיק source, מתקין `.cidra/`, רושם slash commands, פותח IDE)
3. **Stage 0 — Brainstorm** – `/brainstorm` ב-Claude Code chat → `BRAINSTORM_OUTPUT.yaml` + `MISSING_INPUTS.md` + `BRAINSTORM_DIALOG_LOG.md`
4. **Stage 1 — Chunking** – `/chunk:analyze Source Code` ואז `/chunk Source Code` → `CHUNKS/` עם graph + analysis + handoff
5. **Stage 2 — Documentation** – `/document:setup` (פעם אחת) ואז `/document <COMPONENT>` → 7 קבצי תיעוד תחת `Screens\<COMPONENT>\`
6. **Validation** – `/document:validate` (יעד 100/100) ולולאת `/document:fix` במידת הצורך
7. **Checkpoint** – `/brainstorm:gap` לרענון `MISSING_INPUTS.md` לאחר ולידציה
8. **Stage 3 (אופציונלי) — Recommendations** – `/recommend <COMPONENT>` → `RECOMMENDATIONS\<COMPONENT>\RECOMMENDATION_REPORT.md`
9. **Delivery** – אריזת zip עם `Compress-Archive` (ראה RUNBOOK.md Step 10)

> שלבים 4, 5 (Interpreter, Applicator) מתוכננים. הצינור הפעיל היום הוא **B → C → D → R**.

כל שלב מתועד מלא ב-`RUNBOOK.md` ומותאם לעבודה עם Cursor, Claude Code, VS Code ו-GitHub Copilot.

---

## 🔐 מדיניות שימוש

- Repository זה הוא **Read-Only** למפתחים. רק צוות הפלטפורמה מעדכן אותו.
- כל פרויקט יוצר קונפיגורציה ייעודית (`.cidra\config.yaml` + `BRAINSTORM_OUTPUT.yaml`) ומשתמש בכלים בהתאם.
- תרומות מתקבלות דרך Pull Requests והערכת צוות הפלטפורמה.

---

## 📞 תמיכה

לשאלות, תמיכה ופיתוח תוספים חדשים:  
`support@cidra-framework.example`

---

**B+CIDRA = הדרך החכמה לתעד ולחדש מערכות Legacy בישראל.**

*B+CIDRA Framework · README · 2026-06-02*
*Repository: <https://github.com/iliyaruvinsky/enterprise_cidra_framework>*
