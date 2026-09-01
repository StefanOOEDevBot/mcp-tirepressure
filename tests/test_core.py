"""Tests for the SRAM AXS tire pressure formula (core.py)."""
import pytest

from mcp_tirepressure.core import (
    Bg5,
    Fg5,
    Hg5,
    calc_pressure,
    ev5,
    jg5,
    rim_mults,
)

# --- ev5: Wg5 boundary tests ---

@pytest.mark.parametrize("width,expected", [
    (18, 15),   # min of first range
    (21, 15),   # max of first range (exclusive of 22)
    (22, 17),   # start of second range
    (28, 19),   # middle of third range
    (34, 21),   # max of fourth range
    (35, 23),   # start of fifth range
    (57, 25),   # max of sixth range
    (58, 30),   # start of seventh range
    (71, 35),   # max of eighth range
    (72, 45),   # start of ninth range
    (95, 55),   # max of tenth range
    (96, 76),   # start of eleventh range
    (112, 76),  # max of eleventh range
    (113, 0),   # gap between eleventh (ends 113) and twelfth (starts 114)
    (132, 94),  # max of twelfth range
])
def test_ev5_boundaries(width, expected):
    assert ev5(width) == expected

def test_ev5_out_of_range_returns_zero():
    assert ev5(10) == 0
    assert ev5(200) == 0

# --- Lookup dicts: spot-check known values ---

def test_lookup_dicts_known_values():
    assert Fg5["ROAD"] == 1.0
    assert Fg5["GRAVEL"] == 0.9
    assert rim_mults["CROCHET"] == 1.03
    assert rim_mults["STRAIGHT_SIDE"] == 0.955
    assert jg5["STANDARD"] == 1.0
    assert jg5["DOUBLE"] == 0.9
    assert Bg5["FRONT"] == 0.94
    assert Bg5["REAR"] == 1.0
    assert Hg5["DRY"] == 1.0
    assert Hg5["WET"] == 0.9
    assert Hg5["SNOW"] == 0.5

# --- calc_pressure: verified wiki values (BMC Teammachine, 93 kg) ---

BMC = dict(
    rider_weight=93.0, bike_weight=10.0, tire_width=28, inner_rim_width=20,
    wheel_diameter=622, ride_style="ROAD", rim_type="CROCHET",
    tire_casing="STANDARD",
)

def test_calc_pressure_bmc_dry():
    front = calc_pressure(wheel_position="FRONT", surface="DRY", **BMC)
    rear  = calc_pressure(wheel_position="REAR",  surface="DRY", **BMC)
    assert front == pytest.approx(4.94, abs=0.01)
    assert rear  == pytest.approx(5.26, abs=0.01)

def test_calc_pressure_bmc_wet_is_dry_times_0_9():
    front_dry = calc_pressure(wheel_position="FRONT", surface="DRY", **BMC)
    front_wet = calc_pressure(wheel_position="FRONT", surface="WET", **BMC)
    assert front_wet == pytest.approx(front_dry * 0.9, abs=0.001)

def test_calc_pressure_weight_sensitivity():
    """Heavier rider → higher pressure."""
    b = {k: v for k, v in BMC.items() if k != "rider_weight"}
    light = calc_pressure(rider_weight=80.0, wheel_position="FRONT", surface="DRY", **b)
    heavy = calc_pressure(rider_weight=105.0, wheel_position="FRONT", surface="DRY", **b)
    assert heavy > light

def test_calc_pressure_rear_higher_than_front():
    front = calc_pressure(wheel_position="FRONT", surface="DRY", **BMC)
    rear  = calc_pressure(wheel_position="REAR",  surface="DRY", **BMC)
    assert rear > front
