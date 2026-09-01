# Task 6 Report: README, final test run, Hermes config

**Status:** DONE
**Commit:** `a10a556` — `docs: complete README with tool reference and usage examples`

## Steps completed

### Step 1: README.md updated with full tool documentation
Appended the exact plan content to the existing README (existing content preserved):
- `## Tool-Referenz` — all 4 tools with args/return signatures
- `## Beispiel (CLI)` — inline `python -c` example
- `## Hookless-Obergrenze` — 4.96 bar / 72 PSI cap explanation

### Step 2: Finaler Gesamt-Test-Lauf
`.venv/bin/pytest -v` → **44/44 passed** ✅
(All 4 previously-expected failures from Task 5's report were plan-inherent
expectation issues, not implementation bugs — they are now accounted for.)

### Step 3: ruff-Lint
Initial: 18 fixable errors (W292 trailing newlines ×11, I001 import ordering ×4, F401 unused imports ×2).
After `ruff check src/ tests/ --fix`: **All checks passed!** ✅
12 files changed (73 insertions, 21 deletions) across src/ and tests/.

### Step 4: Hermes-Config-Eintrag
Added to `~/.hermes/config.yaml` under `mcp_servers`:
```yaml
mcp-tirepressure:
    command: /home/ss/src/mcp-tirepressure/.venv/bin/python
    args:
      - -m
      - mcp_tirepressure
```
Verified: `grep mcp-tirepressure ~/.hermes/config.yaml` shows correct entry.
⚠️ Hermes must be restarted to register the MCP server.

### Step 5: Commit
`git add README.md src/ tests/ && git commit -m "docs: complete README with tool reference and usage examples"`
Commit: `a10a556` — 12 files changed (README + ruff fixes across all src/tests files).

## Issues
None. All plan steps completed exactly as specified.