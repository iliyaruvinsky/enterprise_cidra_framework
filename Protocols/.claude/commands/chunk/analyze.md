---
description: CIDRA — pre-analysis before chunking; show what would happen without writing chunks
---

You are executing **THE_CHUNKER_AGENT** skill **CHUNK_002 (chunk:analyze)**.

**Reads:**
- [.cidra/Agents/THE_CHUNKER_AGENT/skills.yaml](.cidra/Agents/THE_CHUNKER_AGENT/skills.yaml) — skill CHUNK_002
- [.cidra/Agents/THE_CHUNKER_AGENT/agent_specification.md](.cidra/Agents/THE_CHUNKER_AGENT/agent_specification.md)

**User arguments (path):** `$ARGUMENTS`

**Do not write any chunks.** Produce a preview only:
- File inventory: count, types, sizes
- Language detection: which languages found, distribution per file
- Recommended chunking strategy (file_level / function_level / class_level / method_level / semantic)
- Estimated chunk count
- Detected shared/reusable components

Output as a structured report to the user. If `$ARGUMENTS` is empty, default to the project root and clearly state that's what you're analyzing.
