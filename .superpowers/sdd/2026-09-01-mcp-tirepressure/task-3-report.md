# Task 3 Report: bikes.py — Bike Profiles

**Status:** DONE
**Commit:** `30ce727` — feat(bikes): 5 bike profiles (pydantic) + get_bikes()/get_bike()

## Files created
- `tests/test_bikes.py` — exact test code from plan (Task 3, Step 1), 5 test cases
- `src/mcp_tirepressure/bikes.py` — `BikeProfile` pydantic model, `BIKE_PROFILES` (5 profiles), `get_bikes()`, `get_bike(name)`; code matches plan (Task 3, Step 3) exactly

## TDD sequence
1. Test-first: `tests/test_bikes.py` written, run → FAIL as expected
   (`ModuleNotFoundError: No module named 'mcp_tirepressure.bikes'`)
2. Implementation written → `pytest tests/test_bikes.py -v` → **5 passed**
3. Full suite `pytest -v` → **26 passed** (21 core + 5 bikes), nothing broken

## Implementation notes
- `BikeProfile` pydantic model with fields: `name`, `tire_width`, `inner_rim_width`,
  `wheel_diameter`, `ride_style`, `rim_type`, `tire_casing`, `bike_weight` (float).
- 5 profiles with plan values: bmc-teamachine (8.0 kg), merida-big-nine (14.0),
  merida-esixty-8000 (26.0), rose-gravel-gravel (9.5), rose-gravel-road (9.5).
- `get_bikes()` → `list[dict]` via `model_dump()`, sorted by name.
- `get_bike(name)` → `BikeProfile`, raises `ValueError("Unknown bike '…'")` for unknown names.

## Concerns
- None. Note: the parent task's CONTEXT block listed different bike names/weights
  (e.g. "bmc-team" 10.0 kg) than the plan file; the plan file (authoritative source,
  including the exact test code) was followed throughout, so the tests pass as planned.