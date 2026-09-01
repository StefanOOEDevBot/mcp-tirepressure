# mcp-tirepressure

Lokaler MCP-Server (FastMCP, stdio), der eine SRAM-ähnliche Reifendruck-Formel
implementiert und als Tools für den Hermes Agent verfügbar macht.

> **Hinweis:** Diese Implementierung basiert auf der Formel aus dem
> [SRAM AXS Tire Pressure Calculator](https://axs.sram.com/tire-pressure).
> Die Formel wurde reverse-engineered aus dem SRAM-Webclient (August 2026).
> **Keine offizielle SRAM-Produktlösung.**

## Sicherheitshinweis

> **Wichtig:** Die berechneten Reifendrücke sind Empfehlungen auf Basis
> einer vereinfachten physikalischen Formel. Sie ersetzen **nicht** die
> Herstellerangaben auf dem Reifen und nicht das eigene Fahrgefühl.
> Immer den **maximalen Reifendruck** (auf der Reifenflanke) beachten und
> bei Unsicherheit den Druck um 0,2–0,3 bar nach oben korrigieren.
> **Verwendung auf eigenes Risiko.**

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Tools

- `get_bikes()` — alle 5 Rad-Profile
- `get_bike(name)` — ein Rad-Profile
- `calc_pressure(bike, rider_weight, bike_weight, surface)` — Druck v/h in bar
- `get_recommended_pressure(bike, rider_weight, bike_weight, lat, lon)` — mit Live-Wetter

## Registrierung in Hermes

```yaml
mcp_servers:
  mcp-tirepressure:
    command: /path/to/mcp-tirepressure/.venv/bin/python
    args: ["-m", "mcp_tirepressure"]
```

## Tool-Referenz

### `get_bikes()`
Listet alle 5 konfigurierten Rad-Profile auf.
Return: `[{name, tire_width, inner_rim_width, wheel_diameter, ride_style, rim_type, tire_casing, bike_weight}, ...]`

### `get_bike(name: str)`
Rückgabe eines einzelnen Rad-Profils.
Args: `name` — Key aus `get_bikes()` (z.B. `"bmc-teamachine"`).
Return: Profile als dict.

### `calc_pressure(bike, rider_weight, bike_weight, surface="DRY")`
Berechnet den empfohlenen Reifendruck (vorne/hinten) in bar.
Args:
- `bike` — Rad-Name
- `rider_weight` — Fahrergewicht in kg
- `bike_weight` — Radgewicht in kg
- `surface` — `"DRY"`, `"WET"` oder `"SNOW"` (default: `"DRY"`)
Return: `{bike, surface, front_bar, rear_bar, notes}`

### `get_recommended_pressure(bike, rider_weight, bike_weight, lat, lon)`
One-Call-Empfehlung mit Live-Wetter (Open-Meteo).
Args:
- `bike`, `rider_weight`, `bike_weight` — wie oben
- `lat`, `lon` — Koordinaten (z.B. Wien: 48.2082, 16.3738)
Return: `{bike, surface, weather_reason, front_bar, rear_bar, notes}`

## Formel

Die Berechnung basiert auf der Formel aus dem
[SRAM AXS Tire Pressure Calculator](https://axs.sram.com/tire-pressure):

```
P = 10^8.6847 / C^1.3046 × (1 + (2.2 × (W_bike + W_rider) - 180) × 0.0025)
    × R_pos × R_rim × R_style × R_surface × R_casing × 68.9476 × 0.001
```

- `C` — Reifenumfang in mm (abgeleitet aus Reifendurchmesser + effektiver Breite)
- `R_pos` — Vorder-/Hinterrad-Faktor (0.94 / 1.0)
- `R_rim` — Felgentyp-Faktor (CROCHET, STRAIGHT_SIDE, TUBES, TUBULAR)
- `R_style` — Fahrstil-Faktor (ROAD=1.0, GRAVEL=0.9, MTB=0.9–1.1)
- `R_surface` — Oberfläche (DRY=1.0, WET=0.9, SNOW=0.5)
- `R_casing` — Reifenguß (THIN=1.025, STANDARD=1.0, REINFORCED=0.95, DOUBLE=0.9)
- `68.9476` — Umrechnung PSI → bar (÷ 1000)

Details: `src/mcp_tirepressure/core.py`

## Hookless-Obergrenze

Bei `rim_type == STRAIGHT_SIDE` (hookless) wird der Druck auf max.
**4.96 bar (72 PSI)** begrenzt. Eine Note im `notes`-Feld gibt an,
ob die Grenze ausgelöst wurde.

## Beispiel (CLI)

```bash
.venv/bin/python -c "
from mcp_tirepressure.server import calc_pressure
import json
print(json.dumps(calc_pressure('bmc-teamachine', 93.0, 8.0, 'DRY'), indent=2))
"
```

## Lizenz

[MIT](LICENSE)