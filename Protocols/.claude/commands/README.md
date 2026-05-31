# CIDRA Slash Command Templates

These are the slash command files that Claude Code (Cursor / VS Code extension) loads when you type `/<command>` in a chat.

## Installation into a project

Copy this entire `commands/` folder into your project's `.claude/` directory:

**POWERSHELL:**
```powershell
$framework = "C:\Users\$env:USERNAME\tools\enterprise_cidra_framework"
$project   = "C:\projects\<your_project>"

Copy-Item -Path "$framework\Protocols\.claude\commands" `
          -Destination "$project\.claude\" -Recurse -Force
```

After copying, restart Cursor / VS Code (or `Ctrl+Shift+P` → "Developer: Reload Window"). The slash commands will appear in autocomplete.

## What's included

| Entry point | Sub-commands |
|-------------|--------------|
| `/brainstorm` | `/brainstorm:gap`, `/brainstorm:status`, `/brainstorm:format` |
| `/chunk` | `/chunk:analyze`, `/chunk:status` |
| `/document` | `/document:setup`, `/document:validate`, `/document:fix` |
| `/recommend` | `/recommend:compare`, `/recommend:risk` |

14 files total: 4 entry-point files + 10 sub-command files.

## File format

Each file is a markdown file with YAML frontmatter:

```markdown
---
description: One-line summary of the command
---

Body: the instructions Claude executes when the command runs.
References the appropriate agent specification + skills.yaml.
```

## How they work

When you type `/brainstorm` in Claude Code:
1. The extension finds `.claude/commands/brainstorm.md`
2. It uses the `description` frontmatter for autocomplete display
3. It uses the body as the prompt that Claude executes
4. The body tells Claude to load the corresponding agent spec from `.cidra/Agents/`
5. Claude executes the agent's workflow

Sub-commands work the same way — `/brainstorm:gap` loads `.claude/commands/brainstorm/gap.md`.

## Project-agnostic

These templates are project-agnostic — they reference the agent specs via relative paths (`.cidra/Agents/...`) which the installer places in every project. No project-specific edits needed.

## Customization

If you want to add project-specific instructions (e.g. "always document in Hebrew first, then English"), edit the project's local copy at `.claude/commands/*.md`. The framework's `Protocols/.claude/commands/` originals stay untouched.
