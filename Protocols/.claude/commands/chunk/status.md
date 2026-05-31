---
description: CIDRA — show current chunking progress and statistics
---

You are executing **THE_CHUNKER_AGENT** skill **CHUNK_003 (chunk:status)**.

Check the `CHUNKS/` directory in this project root and report:
- Whether a chunking run exists
- From `CHUNKS/run_manifest.json` (if present): run_id, status, duration, files processed, chunks created
- From `CHUNKS/repository.json` (if present): total chunks, language distribution, token stats
- Any errors or warnings recorded in the manifest

If `CHUNKS/` does not exist, tell the user to run `/chunk [path]` first.
