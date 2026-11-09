# Materials on the P1S

Temperatures are typical Bambu-preset ranges; the filament preset in Bambu Studio sets them —
only change them when the spool's label disagrees.

| Material | Nozzle °C | Bed °C | Enclosure | Plate | AMS | Notes |
|---|---|---|---|---|---|---|
| **PLA** | 210–230 | 55–65 | **Open lid/door** | Textured PEI, Cool (glue) | ✓ | Default choice. Softens ~55 °C. Stiff, brittle-ish. |
| PLA Matte / Silk | 210–230 | 55–65 | Open | Textured PEI | ✓ | Silk is weaker between layers — cosmetic only. |
| **PETG** | 240–260 | 70–80 | Closed or slightly open | Textured PEI (no glue); smooth PEI **with glue** (sticks too well) | ✓ | Tougher, ~70 °C, outdoor-OK, strings; slower cooling. |
| TPU 95A | 220–240 | 35–45 | Open | Textured PEI | ✗ external spool | Flexible. Slow (≈ 3.5 mm³/s). No thin walls < 1.2 mm. |
| **ABS** | 250–270 | 90–100 | **Closed** | Textured PEI / Engineering (glue) | ✓ | Warps on big parts: brim, rounded corners, preheat 10 min. Fumes → ventilate. |
| **ASA** | 250–270 | 90–100 | Closed | Textured PEI | ✓ | UV-stable ABS — best for outdoor/car. |
| PC | 260–280 | 100 | Closed | Textured PEI / High-temp (glue) | ✓ | Strong, hot; near the P1S's passive-chamber limit, warps. |
| PLA-CF / PETG-CF | 220–260 | per base | per base | Textured PEI | ✓ (abrasive, brittle — external spool safer) | Needs hardened nozzle (P1S stock is hardened steel). Matte, stiff. |
| PA6-CF / PAHT-CF | 270–300 | 80–100 | Closed | Engineering (glue) | external, **dry first** | Very strong & heat resistant. Must be dried (80 °C 8–12 h). |
| PVA / Support W | 210–230 | 45–60 | Open | — | ✓ if dry | Water-soluble support for PLA. Store sealed. |

## Choosing quickly
- Indoor decor, organisers, prototypes → **PLA**
- Functional, flexing a bit, outdoor shade, dishwasher-top-rack-ish → **PETG**
- Car interior, sunlight, outdoors → **ASA**
- Grips, bumpers, gaskets, phone cases → **TPU**
- Stiff + light brackets → PLA-CF / PETG-CF

## Moisture
PETG, TPU, PA, PVA absorb water → stringing, popping, weak parts. Dry before printing
(PETG 65 °C 6 h, TPU 55 °C 6 h, PA 80 °C 8–12 h). Keep AMS desiccant fresh (< 20 % RH).

## Shrinkage (scale if exact size matters)
PLA ≈ 0.2–0.3 %, PETG ≈ 0.3 %, ABS/ASA ≈ 0.6–0.8 % — matters for parts > 150 mm that mate
with something rigid; use the filament's Shrinkage setting in Bambu Studio rather than scaling
the model.
