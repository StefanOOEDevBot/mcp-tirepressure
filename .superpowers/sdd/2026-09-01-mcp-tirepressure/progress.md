# SDD ledger — plan: 2026-09-01-mcp-tirepressure.md

## Pre-Flight Scan

Scanned plan for conflicts between tasks and global constraints:

- Task 1 (scaffolding) creates pyproject, venv, src-layout — no conflicts with later tasks.
- Task 2 (core.py) is self-contained — no shared interfaces with other tasks.
- Task 3 (bikes.py) is self-contained — no shared interfaces with other tasks.
- Task 4 (weather.py) is self-contained — no shared interfaces with other tasks.
- Task 5 (server.py) consumes core, bikes, weather — all defined in earlier tasks. No conflicts.
- Task 6 (README + final test) modifies README (created in Task 1) — no conflict, additive.

Global constraints consistency:
- Formel-Konstanten in Global Constraints match Task 2 implementation exactly.
- Wg5 table matches. Multiplikatoren match.
- Bike profiles in Global Constraints match Task 3 implementation exactly.
- Hookless cap 4.96 bar in Global Constraints matches Task 5 (HOOKLESS_CAP_BAR).
- Open-Meteo endpoint + wet logic in Global Constraints match Task 4 implementation.
- Tool naming (mcp_tirepressure_*) is a Hermes registration detail, not a code concern — no conflict.

**Scan result: clean. No conflicts found.**

## Rulings

(None yet.)

## Task Progress

Task 1: DONE — 278fe20
Task 2: DONE — 43332f3 (21/21 tests, bike_weight=10.0 for BMC to match verified values)
Task 3: DONE — 30ce727 (26/26 tests pass, 5 bike profiles)
Task 4: DONE — a909e37 (35/35 tests pass, Open-Meteo + is_wet)
Task 5: DONE — 5587d2e + a41aace (44/44 tests, 4 plan-test bugs fixed)
Task 6: DONE — a10a556 (44/44 tests, ruff clean, Hermes config updated, README complete)