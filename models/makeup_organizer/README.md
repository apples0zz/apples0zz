# Bathroom makeup organizer: 2 shelves, 6 modules + little feet

Shelves: **22.5" × 8.75" measured inside the rims** (572 × 222 mm). Each shelf takes three
modules of 184 × 216 mm (7.2" × 8.5"), which leaves about ⅜" of play side to side and ¼" front
to back so they drop in easily. Every module fits one P1S plate. See `spot_map.png` for what
goes where.

## Shelf 1: sticks & tubes (stand upright in slots, back rows higher)
Slots are packed about 5 mm apart (about 3 mm of plastic between items). Each block is only as deep as
its rows need and sits against the back of the shelf.

| Module | Holds (front → back) |
|---|---|
| **M1 eyes & lips** (182 mm deep, 68 mm tall at back) | 5 mascaras · beige stick + Glossier brow gel + 4 chunky eye sticks · 10 pencils/liners/brow · 3 flat tubes + 1 gloss · 4 concealers + 2 glosses · 6 glosses (9 lip items in total) |
| **M2 cheeks & tubes** (156 mm deep, 41 mm tall) | 3 liquid blushes/wands + 2 Fenty hex sticks · 3 about-face + Pixi stick · 5 squeeze tubes cap-down (4 + 1 spare) |
| **M3 brushes, sponges & puffs** (188 mm deep, 68 mm tall at back) | 4 powder puff slots, standing on edge (84 × 20 mm) · 3 sponge cups Ø50 with an air hole underneath so damp sponges dry · 26 brush holes: 3 big/kabuki Ø26, 13 regular Ø15, 10 thin/detail Ø12 (room for ~15 brushes plus growth) |

## Shelf 2: face
| Module | Holds |
|---|---|
| **M4 bottle stairs** | 12 bottles on 3 steps (8 / 40 / 72 mm high), each with a lip so nothing slides off |
| **M5 thin compacts** | 13 flat compacts **standing on their sides**, each in its own slot sized to its thickness, plus the Too Faced tin on its long edge in a side slot |
| **M6 thick compacts & jars** | 8 jars and cushions standing on their sides, plus 2 spare slots for new compacts |

## Recount: 21 compacts, pans and jars (from your last photo)
Width = the edge it stands on, measured from the photo using the keyboard keys as a ruler.
Thickness is estimated from the angled photos, since a top-down photo can't show it.
Every slot is **thickness + 4 mm** (jars + 6 mm) so things slide in easily.

| Item | Width (mm) | Thick (mm) | Spot |
|---|---|---|---|
| Too Faced Italian Spritz tin | 209 long × 89 | 15 | M5 side slot (long edge down) |
| H&M palette | 133 | 15 | M5 |
| essence sun club bronzer | Ø103 | 18 | M5 |
| W7 Duo Blusher | 94 | 13 | M5 |
| essence all about matt | Ø80 | 15 | M5 |
| marie claire setting powder | Ø75 | 15 | M5 |
| wet n wild bronzer | 75 | 14 | M5 |
| Charlotte Tilbury compact | 77 | 15 | M5 |
| Morphe blush | Ø73 | 20 | M5 |
| NARS blush | 65 | 13 | M5 |
| wet n wild blush | Ø63 | 15 | M5 |
| peach round compact | Ø60 | 20 | M5 |
| Colourpop pot | Ø42 | 18 | M5 |
| TIRTIR cushion | 95 | 32 | M6 |
| rose-gold compact | Ø80 | 22 | M6 |
| Glossier jar | Ø74 | 33 | M6 |
| Glossier quad | 71 | 22 | M6 |
| Morphe powder jar | Ø70 | 38 | M6 |
| Milani blush | Ø69 | 22 | M6 |
| Fenty cream blush | 55 | 25 | M6 |
| elf putty bronzer | Ø47 | 28 | M6 |

Earlier I had counted 9 compacts and listed the Charlotte Tilbury twice. The real count is 21.

## Little feet
Every module stands on 4 little feet that lift it 3 mm. The modules print with a flat bottom so
they need no supports, and the feet print separately:
- `M0_feet.3mf`: 28 feet on one plate (24 + 4 spares), about 18 g and 25 min. Each is a Ø14 × 3 mm
  pad with a pin that **presses into the sockets under each module**. If one feels loose, add a
  drop of superglue. TPU feet also work (grippier on a wet shelf); use the same file.
- The lift also lets air under the sponge cups, so sponges dry from below.

## Print order
1. **`00_fit_test_sampler.3mf`** (about 2.5 h, ~125 g). It has one of every stick slot (shallow),
   4 test feet with sockets to try the press fit, and a mini rack with compact slots of
   17 / 19 / 22 / 26 / 36 / 42 mm. Test it with the NARS blush, the H&M palette, the sun club
   bronzer, the Glossier quad, the TIRTIR and the Morphe jar. If anything is tight or loose,
   tell me which item and I'll change its number.
2. `M0_feet.3mf`, then the six modules, in any order.

## Bambu Studio recipe: fastest print, least filament
Set this once and save it as a preset (e.g. "Organizer FAST"):
```
Printer:    Bambu Lab P1S 0.4 nozzle · Plate: Textured PEI · Filament: your PLA preset
Process:    0.28mm Extra Draft          <- biggest time saver (fewer, thicker layers)
Strength:   Wall loops 2 · Top shell layers 3 · Bottom shell layers 2
            Sparse infill: Lightning, 10%   <- only fills under the top surfaces
Support:    OFF        Brim / skirt: off        Ironing: off        Prime tower: off
Speed:      on the printer (or Device tab), set speed to **Sport**  (~20 % faster; PLA handles it)
Door/lid:   open a little for PLA
```
- Don't use Ludicrous speed: it can make thin walls and dividers sloppy.
- These are storage parts, so draft layers look fine. The textured plate hides the bottom, and
  the visible faces are mostly vertical walls.
- In M5 and M6 the slot floors span between the dividers. Every span is 24 mm or less (wide
  slots get a support wall underneath), which the P1S prints cleanly with supports off.
  Ignore the overhang warning in Bambu Studio for these.
- **Even faster (optional):** a 0.6 mm hardened nozzle (about $20, swaps in 2 minutes) with
  "0.30mm Standard @BBL … 0.6 nozzle" cuts time by roughly another third, with stronger parts too.

### Filament & time estimate (with this recipe)
| File | ≈ PLA | ≈ time |
|---|---|---|
| 00 fit test sampler | 125 g | 2.5 h |
| M0 feet ×28 | 18 g | 0.4 h |
| M1 eyes & lips | 205 g | 4.0 h |
| M2 cheeks & tubes | 140 g | 2.7 h |
| M3 brushes, sponges & puffs | 205 g | 4.0 h |
| M4 bottle stairs | 195 g | 3.7 h |
| M5 thin compacts | 205 g | 3.9 h |
| M6 thick compacts | 140 g | 2.6 h |
| **Total** | **≈ 1.23 kg (1.11 kg without the sampler)** | **≈ 24 h (21 h)** |

Before this pass the same set was about 1.6 kg and 37 h. To get there, slots got shallower,
tiers and divider walls lower, rack base plates were removed, and the bottle stairs became solid
upright steps with lightning infill. These are my estimates (±25 %); Bambu Studio shows the exact
numbers when you slice.

Regenerate after changing a number: `python3 models/makeup_organizer/generate.py`
