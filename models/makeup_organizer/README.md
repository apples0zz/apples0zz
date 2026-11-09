# Bathroom makeup organizer: 2 shelves, 6 modules

Shelves: 8.75" × 22.5" (222 × 572 mm). Three modules sit side by side on each shelf. Each
module is 186 × 214 mm and fits one P1S plate. Back rows are higher than front rows, like
stadium seating, so everything stays visible. See `spot_map.png` for what goes where.

| Shelf | Module | Holds | Max height | Est. PLA |
|---|---|---|---|---|
| 1 | **M1 eyes** | 5 mascaras · 8 eye sticks/thick liners · 20 pencils/liners/brow | 62 mm | ~230 g |
| 1 | **M2 lips & concealer** | 6 concealers · 12 glosses/lip/liquid shadow · 4 flat tubes | 62 mm | ~225 g |
| 1 | **M3 cheek & jars** | 2 jar stacks (essence, Fenty) · elf putty · 2 Colourpop pots · 4 about-face · 5 blush wands/sticks | 62 mm | ~200 g |
| 2 | **M4 bottle stairs** | ~15 bottles on 3 steps (6 / 40 / 74 mm) with lips so nothing slides | 79 mm | ~160 g |
| 2 | **M5 tubes & sticks** | 10 squeeze tubes cap-down · 2 Fenty hex sticks · Pixi stick · 1 spare | 50 mm | ~170 g |
| 2 | **M6 compact rack** | 9 compacts standing on edge, each slot higher than the one in front | 98 mm | ~205 g |
| — | **00 fit test sampler** | one of every slot size; print this first | 38 mm | ~80 g |

**Total ≈ 1.2 kg PLA** (a bit over one 1 kg spool). These are rough estimates; Bambu Studio
shows the exact grams and time when you slice.

## Print order
1. `00_fit_test_sampler.3mf`. Drop your fattest mascara, a pencil, a concealer, an about-face
   stick and a squeeze tube into it. If something is too tight or too loose, tell me and I'll
   adjust that slot size in `generate.py` and re-export.
2. The six modules, in any order. Each `.3mf` already sits on the plate in the right pose.
   The bottle stairs (M4) print **on their side** on purpose, so they need no supports.

## Bambu Studio recipe (same for every module)
```
Printer:   Bambu Lab P1S 0.4 nozzle · Plate: Textured PEI · Filament: your PLA preset
Process:   0.20mm Standard · walls 2 (default) · top layers 5 · bottom 3
Infill:    10% lightning (already set in the 3MF). It only fills under the tops, so it saves a lot of filament
Supports:  OFF. None needed: checked by code, 0 mm² of overhang steeper than 45°
Brim:      off (M4 on its side is 186 mm tall but 79 mm wide; turn brim on if it wobbles)
Door/lid:  open a little for PLA
```
M6's slot floors are short bridges (≤ 30 mm) between its dividers. The P1S bridges these
cleanly with supports off, so ignore the overhang warning for that part.

## What I assumed (please check)
- **Product sizes are estimated from your photos.** Every slot has a few mm of slack, but
  the sampler is the real test.
- **Shelf height:** the tallest point is the M4 top step (79 mm) plus your tallest bottle,
  about 22 cm in total. If the space above a shelf is shorter, tell me and I'll lower the steps.
- Brushes, sponges and the mirror aren't included. Want a brush cup module too?

Regenerate after changing any number: `python3 models/makeup_organizer/generate.py`
