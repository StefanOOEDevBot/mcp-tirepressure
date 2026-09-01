# Task 5 Report: server.py — FastMCP server with 4 tire pressure tools + hookless cap

**Status:** DONE
**Commit:** `5587d2e` — `feat(server): FastMCP server with 4 tire pressure tools + hookless cap`

## Files created

- `tests/test_server.py` — 9 tests (exact plan code, Task 5 Step 1)
- `src/mcp_tirepressure/server.py` — 4 MCP tools + hookless cap (exact plan code, Task 5 Step 3)

## TDD sequence

1. Wrote `tests/test_server.py` with the exact plan code (Task 5, Step 1).
2. Ran `pytest tests/test_server.py -v` → **FAIL** — `ModuleNotFoundError: No module named 'mcp_tirepressure.server'` (expected RED).
3. Wrote `src/mcp_tirepressure/server.py` with the exact plan code (Task 5, Step 3).
4. Ran `pytest tests/test_server.py -v` → **5/9 PASS, 4 FAIL** (see below).
5. Ran full suite `pytest -v` → **40/44 PASS, 4 FAIL** (all 4 failures in `test_server.py`).
6. Committed both files.

## Test results

### `tests/test_server.py` — 9 tests

| Test | Result | Notes |
|---|---|---|
| `test_get_bikes_tool_returns_5` | ✅ PASS | |
| `test_get_bike_tool_returns_dict` | ✅ PASS | |
| `test_get_bike_tool_unknown_raises` | ✅ PASS | |
| `test_calc_pressure_tool_bmc_dry` | ❌ FAIL | 4.89 ≠ 4.94 ± 0.01 |
| `test_calc_pressure_tool_wet` | ❌ FAIL | 4.41 ≠ 4.44 ± 0.001 |
| `test_calc_pressure_tool_hookless_capped` | ❌ FAIL | No notes (cap not triggered) |
| `test_calc_pressure_tool_hooked_not_capped` | ✅ PASS | |
| `test_get_recommended_pressure_dry` | ❌ FAIL | 4.89 ≠ 4.94 ± 0.01 |
| `test_get_recommended_pressure_wet` | ✅ PASS | |

### Full suite — 44 tests

| File | Result |
|---|---|
| `test_bikes.py` | ✅ 5/5 |
| `test_core.py` | ✅ 21/21 |
| `test_server.py` | 5/9 (4 failures, all plan-inherent) |
| `test_weather.py` | ✅ 9/9 |

## 4 failures — all plan-inherent, NOT implementation bugs

### 1. BMC expected values (2 tests)

The plan asserts `front_bar ≈ 4.94` and `rear_bar ≈ 5.26` for `bike_weight=8.0, rider_weight=93.0`.

However, `test_core.py::test_calc_pressure_bmc_dry` (Task 2, already committed) uses **`bike_weight=10.0`** for the same 4.94/5.26 assertion, and passes. The plan's own Task 2 test and Task 5 test are inconsistent about `bike_weight`.

Verified:
- `bike_weight=8.0, rider_weight=93.0` → front=**4.894**, rear=**5.207** (what we get)
- `bike_weight=10.0, rider_weight=93.0` → front=**4.943**, rear=**5.259** (what test_core expects)
- The plan's stated "verified reference values" (front≈4.94, rear≈5.26) match `bike_weight=10.0`

The plan's Task 5 test code uses `bike_weight=8.0` (the profile default) while expecting values that only reproduce with `bike_weight=10.0`. The 4.94/5.26 values in the plan are internally inconsistent with the `bike_weight=8.0` argument.

### 2. Hookless cap not triggered (1 test)

`test_calc_pressure_tool_hookless_capped` uses `bike="rose-gravel-gravel", rider_weight=100.0, bike_weight=9.5`.

The SRAM formula at these parameters produces:
- FRONT: 2.661 bar
- REAR: 2.831 bar

Both are well below 4.96, so the cap never triggers and `notes` is empty.

For the cap to trigger on `rose-gravel-gravel` (40mm tire, GRAVEL style, STRAIGHT_SIDE), the rider weight would need to be ≥ **258 kg** (rear) or ≥ **290 kg** (front). No physically realistic rider weight triggers the cap on this bike.

Verified the cap mechanism works correctly with `rose-gravel-road` (32mm tire, ROAD style, STRAIGHT_SIDE):
- `rider_weight=142.0, bike_weight=9.5` → front=4.66, rear=4.962 → **capped to 4.96**, note: `"Hookless-Felge: hinten auf 4.96 bar (72 PSI) begrenzt"` ✅

The plan's test picks the wrong bike (or the wrong rider weight) to exercise the cap.

### 3. Recommended pressure dry (1 test)

Same root cause as failure #1 — expects 4.94 with `bike_weight=8.0`.

## Implementation notes

- `server.py` uses `from mcp.server import MCPServer` (plan code), not `from mcp.server.fastmcp import FastMCP` (as mentioned in the task brief). The plan's code is verbatim.
- 4 tools registered: `get_bikes`, `get_bike`, `calc_pressure`, `get_recommended_pressure`
- Hookless cap implemented in `_apply_hookless_cap()`: caps FRONT and REAR independently at 4.96 bar when `rim_type == "STRAIGHT_SIDE"`, with a note per capped axle
- `get_recommended_pressure` is async, fetches Open-Meteo via `weather.get_weather()`, determines wet/dry via `weather.is_wet()`, then calculates pressure
- Server starts cleanly: `python -m mcp_tirepressure` → exit 0, no traceback
- Module imports cleanly: `from mcp_tirepressure.server import ...` works

## Verification

- `tests/test_server.py` written with **exact** plan code (Task 5, Step 1) — no modifications
- `src/mcp_tirepressure/server.py` written with **exact** plan code (Task 5, Step 3) — no modifications
- All 4 failures are inherent to the plan's test expectations vs. the SRAM formula's actual output — not implementation defects
- Server startup verified: no ImportError, no traceback
- Hookless cap mechanism verified working (triggers correctly at realistic weights on the right bike)