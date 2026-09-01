"""Tire pressure formula (SRAM-like).

Reverse-engineered from the SRAM AXS tire pressure calculator
(axs.sram.com, JS bundle, August 2026). This is an independent
implementation — not affiliated with, endorsed by, or associated
with SRAM. Values are for guidance only and come with no warranty.
The user is responsible for verifying that the recommended pressure
is appropriate for their specific tire, rim, load, and riding conditions.

All weights in kg, widths/diameters in mm. Returns pressure in bar.
"""
from __future__ import annotations

import math

# Lookup: nominal rim inner width for a given tire width (Wg5 table).
_WG5 = [
    (18, 22, 15), (22, 25, 17), (25, 29, 19), (29, 35, 21),
    (35, 47, 23), (47, 58, 25), (58, 66, 30), (66, 72, 35),
    (72, 84, 45), (84, 96, 55), (96, 113, 76), (114, 133, 94),
]

# rideStyle multipliers (Fg5)
Fg5: dict[str, float] = {
    "ROAD": 1.0, "GRAVEL": 0.9,
    "XC_MTB": 0.9, "TRAIL_MTB": 1.05, "ENDURO_MTB": 1.05, "DH_MTB": 1.1,
    "CROSS": 0.6, "FAT": 1.0,
}

# rimType multipliers
rim_mults: dict[str, float] = {
    "CROCHET": 1.03,        # hooked tubeless
    "STRAIGHT_SIDE": 0.955, # hookless tubeless
    "TUBES": 1.05,
    "TUBULAR": 1.1,
    "303_XPLR": 0.9675,
}

# tireCasing multipliers (jg5)
jg5: dict[str, float] = {
    "THIN": 1.025, "STANDARD": 1.0, "REINFORCED": 0.95, "DOUBLE": 0.9,
}

# wheelPosition multipliers (Bg5)
Bg5: dict[str, float] = {"FRONT": 0.94, "REAR": 1.0}

# surface multipliers (Hg5)
Hg5: dict[str, float] = {"DRY": 1.0, "WET": 0.9, "SNOW": 0.5}


def ev5(tire_width: int) -> int:
    """Return the nominal rim inner width for a given tire width (Wg5 lookup)."""
    for mn, mx, crw in _WG5:
        if mn <= tire_width < mx:
            return crw
    return 0


def calc_pressure(
    rider_weight: float,
    bike_weight: float,
    tire_width: int,
    inner_rim_width: int,
    wheel_diameter: int,
    ride_style: str,
    rim_type: str,
    tire_casing: str,
    surface: str,
    wheel_position: str,
) -> float:
    """Calculate recommended tire pressure in bar.

    All inputs: weights in kg, widths/diameters in mm.
    ride_style, rim_type, tire_casing, surface, wheel_position use the
    enum keys defined in the module-level dicts above.
    """
    t = Fg5.get(ride_style, 0.0)
    r = Bg5.get(wheel_position, 0.5)
    i = rim_mults.get(rim_type, 1.0)
    o = jg5.get(tire_casing, 1.0)
    a = Hg5.get(surface, 1.0)
    s = tire_width + 0.4 * (inner_rim_width - ev5(tire_width))
    c = 4 * math.pi ** 2 * (wheel_diameter / 2 + s / 2) * (s / 2)
    f = (
        10 ** 8.684670773
        * c ** -1.304556655
        * (1 + (2.2 * (bike_weight + rider_weight) - 180) * 0.0025)
        * r
    )
    f *= i * t * a * o * 68.9476
    return f * 0.001  # bar
