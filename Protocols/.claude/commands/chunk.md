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
6. `BRAINSTORM_OUTPUT.yaml` at project root, IF it exists — Stage 0 output with chunking_strategy hints and component scope.

**User arguments:** `$ARGUMENTS`

**Workflow (CHUNK_001):**
1. Scan target path → detect languages → select strategy
2. Create chunks honoring logical boundaries (never split mid-function)
3. Generate metadata, relationships, index
4. Produce the documenter handoff: `CHUNKS/repository.json`, `CHUNKS/graph.json`, `CHUNKS/analysis.json`, `CHUNKS/DOCUMENTER_INSTRUCTIONS.md`, `CHUNKS/run_manifest.json`
5. Honor target token range 2,000–4,000 (warn under 500 / over 8,000)

## For this project
Source files: scan the path passed in $ARGUMENTS (default: `Source Code/`).
If BRAINSTORM_OUTPUT.yaml exists at the project root, honor any
`chunking_strategy` it declares; otherwise fall back to skills.yaml
CHUNK_INT_002 strategy selection.

If `$ARGUMENTS` is empty, ask the user which path to chunk before scanning.

After completion, report: chunks created, token distribution, languages detected, and the path to `DOCUMENTER_INSTRUCTIONS.md`.
