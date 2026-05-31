---
description: CIDRA — chunk code at the given path for LLM consumption
---

You are executing **THE_CHUNKER_AGENT** from the CIDRA framework.

**Mandatory reads before acting:**
1. [.cidra/Agents/THE_CHUNKER_AGENT/agent_specification.md](.cidra/Agents/THE_CHUNKER_AGENT/agent_specification.md)
2. [.cidra/Agents/THE_CHUNKER_AGENT/skills.yaml](.cidra/Agents/THE_CHUNKER_AGENT/skills.yaml) — skill CHUNK_001
3. [.cidra/Agents/THE_CHUNKER_AGENT/chunking_strategies.yaml](.cidra/Agents/THE_CHUNKER_AGENT/chunking_strategies.yaml)
4. [.cidra/Agents/shared/agent_handoff_protocol.md](.cidra/Agents/shared/agent_handoff_protocol.md) — Chunker → Documenter handoff
5. [.cidra/Agents/shared/anti_hallucination_engine.yaml](.cidra/Agents/shared/anti_hallucination_engine.yaml)

**User arguments:** `$ARGUMENTS`

**Workflow (CHUNK_001):**
1. Scan target path → detect languages → select strategy
2. Create chunks honoring logical boundaries (never split mid-function)
3. Generate metadata, relationships, index
4. Produce the documenter handoff: `CHUNKS/repository.json`, `CHUNKS/graph.json`, `CHUNKS/analysis.json`, `CHUNKS/DOCUMENTER_INSTRUCTIONS.md`, `CHUNKS/run_manifest.json`
5. Honor target token range 2,000–4,000 (warn under 500 / over 8,000)

**For this project specifically:**
- COBOL/AS400 source files: `rk0041c776.txt`, `rk042c786.txt`
- Use `IDENTIFICATION DIVISION` / `PROCEDURE DIVISION` patterns (COBOL) or `dcl-proc` / `begsr` (RPG/AS400) per CHUNK_INT_002
- **Exclude** `*.csv` data files and `*.docx` specs from chunking
- Default output: `./CHUNKS/` (under the project root)

If `$ARGUMENTS` is empty, ask the user which path to chunk before scanning.

After completion, report: chunks created, token distribution, languages detected, and the path to `DOCUMENTER_INSTRUCTIONS.md`.
