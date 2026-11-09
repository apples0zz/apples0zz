---
name: bambu-p1s
description: Design, model and prepare 3D-printable parts for a Bambu Lab P1S in Bambu Studio. Use whenever the user asks to make, model, design, fix, or print something on their 3D printer, wants an STL/3MF, asks about fits/tolerances, supports, materials, multi-color (AMS) prints, or Bambu Studio settings.
---

# Bambu Lab P1S + Bambu Studio — design & print-prep expert

You turn an idea ("a hook for my bike helmet", "a box for my SD cards", "a two-colour sign")
into a **watertight, support-minimised, correctly-toleranced model**, checked by code, exported
as a **3MF that opens in Bambu Studio with filaments pre-assigned**, plus the exact slicer
settings to use.

## The machine (design to these numbers)

| Spec | P1S value | What it means for design |
|---|---|---|
| Build volume | 256 × 256 × 256 mm | Split anything bigger; leave ~5 mm margin for brim/purge |
| Nozzle | 0.4 mm hardened steel (0.2 / 0.6 / 0.8 optional) | Line width ≈ 0.42 mm → design walls as multiples: 0.84, 1.26, 1.68… |
| Hotend / bed max | 300 °C / 100 °C | PLA, PETG, TPU, ABS, ASA, PC, PA-CF, PET-CF all possible |
| Enclosure | Passive (no chamber heater), exhaust + aux fan | ABS/ASA OK at moderate size; door/lid **open for PLA** to avoid heat creep |
| Motion | CoreXY, up to 500 mm/s, 20 m/s² | Fast → tall thin parts wobble: add brim or widen base |
| AMS (optional) | 4 slots per unit, up to 4 units = 16 filaments | Multi-colour by **parts** (separate meshes) or by painting; every change purges ~ 0.1–0.5 g |
| Stock plate | Textured PEI | No glue for PLA/PETG/ABS; texture is imprinted on the bottom face |
| No lidar | — | First-layer quality depends on a clean plate (wash with dish soap) |

## Workflow (always follow)

1. **Pin down requirements.** Real dimensions of the thing it attaches to / holds (ask for
   caliper measurements; never guess a phone/screw/bottle size when it matters), load
   direction, environment (sun/car → PETG/ASA, not PLA), colours, and whether it's one part
   or an assembly.
2. **Choose print orientation first, then design for it.** Orientation decides strength
   (layers are ~50 % weaker in Z), overhangs and surface quality. Best flat face on the bed.
3. **Model parametrically in Python** with the toolkit `scripts/p1s.py` (manifold3d: booleans
   are always watertight). Put every dimension in named variables at the top.
4. **Check with code** — `report(part, material)` must show `watertight True`, `fits_p1s True`,
   `on_bed True`, and ~0 `overhang_mm2_gt45` (or a deliberate decision to use supports).
   For mating parts, measure the real clearance with `gap(a, b)` in the assembled pose.
5. **Look at it** — `preview("x.png", parts)` and Read the PNG. Fix anything that looks wrong.
6. **Export** to `models/<name>/`: `export_3mf()` (preferred — keeps parts, colours, per-part
   settings) and `export_stl()` for sharing. Keep the generator `.py` next to the outputs.
7. **Hand off** with a short slicer recipe: plate, filament, process profile, walls / infill,
   supports, brim, and any pause/colour changes. Template in `reference/bambu-studio.md`.

Setup once per environment: `pip install manifold3d trimesh numpy matplotlib networkx lxml`

```python
import sys; sys.path.insert(0, ".claude/skills/bambu-p1s/scripts")
from p1s import *
body = shell_box(80, 60, 40, wall=1.6, floor=1.2, r=4)
body = body - teardrop_hole(5, 100, axis="x").translate((40, 30, 20))   # support-free side hole
report(body, "PETG")
export_3mf("models/demo/demo.3mf", [Part("box", body, filament=1)])
```
Worked, verified examples: `examples/box_with_lid.py` (fit clearance check, two objects),
`examples/two_color_coaster.py` (AMS 2-colour flush inlay as parts of one object),
`examples/phone_stand.py` (print-on-side strategy, teardrop cable routing, per-part settings).

## Design rules for FDM on the P1S

**Walls & features**
- Minimum wall 0.8 mm (2 lines); structural walls ≥ 1.6 mm (4 lines). Make thin walls an exact
  multiple of 0.42 so the slicer doesn't leave gaps or skip them.
- Floors/roofs ≥ 1.0 mm (5 layers at 0.2) — 1.2 mm reads solid.
- Minimum printable detail ≈ 0.4 mm in XY, one layer (0.2 / 0.08 fine) in Z.
- Pins/posts: ≥ 3 mm diameter, add a fillet/chamfer at the root; anything < 2 mm snaps.
- Embossed/engraved text: ≥ 5 mm tall (≥ 3 mm at 0.08 mm layers), stroke ≥ 0.6 mm,
  depth 0.6–1.0 mm. Bold sans fonts. Text on the top face, never on a vertical face for tiny text.

**Overhangs, bridges, supports**
- ≤ 45° from vertical prints clean; 50–60° OK-ish with cooling (PLA). Replace bottom
  fillets/horizontal ledges with **45° chamfers**.
- Horizontal holes: use `teardrop_hole()` (45° roof) or accept slight droop for < 6 mm holes.
- Bridges ≤ ~25–30 mm are fine on the P1S; longer ones sag — add a rib or rotate the part.
- Prefer re-orienting or splitting the part to supports. If supports are needed: **tree(auto)**,
  top Z distance 0.2, paint support blockers on cosmetic faces. Use PETG as an interface
  material for PLA (and vice-versa) on an AMS for supports that peel off cleanly.
- Splitting: add alignment pins (pin d=4, hole d=4+2×0.15) or dovetails, glue with CA.

**Tolerances & fits** (per side, PLA/PETG at 0.2 mm, tuned P1S — `CLEAR` in the toolkit)
| Fit | Clearance | Use |
|---|---|---|
| press | 0.10 | bearings, magnets (+ a drop of CA) |
| snug | 0.15 | pins, plugs that shouldn't fall out |
| slide | 0.25 | lids, drawers, sliding parts |
| print-in-place | 0.35 | hinges/joints printed assembled |
| loose | 0.40 | free-spinning, things you drop in |
- Holes print ~0.1–0.2 mm small: model screw holes at nominal + 0.2–0.3 (M3 clearance = 3.4,
  M3 heat-set insert = 4.0–4.2 for the common short inserts, check the insert's spec).
- Self-tapping into plastic: M3 → 2.5–2.7 mm pilot. Hex nut trap: across-flats + 0.3.
- Magnets: hole = magnet Ø + 0.2, depth + 0.2; embed via "pause at layer" if fully enclosed.
- Elephant's foot: the toolkit adds a 0.4 mm bottom chamfer; keep it on mating edges.
- Test-print a **fit coupon** (a 10 mm slice of the joint) before a 6-hour print.

**Strength**
- Layers are the weak plane: orient so the load is along the layers (hooks/brackets are
  printed on their side, like `phone_stand.py`).
- More walls beat more infill: 4 walls + 15–25 % gyroid is stronger than 2 walls + 50 %.
- Round inside corners (r ≥ 1–2 mm) — sharp inside corners crack.
- Heat: PLA softens ~55 °C (cars, sunny windows → PETG ≥ 70 °C, ASA ≥ 95 °C).

**Multi-colour (AMS)**
- Model each colour as a **separate solid** (`Part(name, solid, filament=n)`) that touches but
  doesn't overlap — the toolkit exports them as parts of one object so they stay aligned.
- Put colour in the **top 2–4 layers** (flush inlay) or the **bottom layers face-down on the
  textured plate** — fewer layers with colour changes = much less purge waste and time.
- Same material across colours (PLA+PLA). Mixing PLA/PETG in one part = weak bond, only for
  support interfaces.
- Single-extruder alternative without AMS: colour-by-layer — add a filament change/pause on the
  layer slider (e.g. raised letters in another colour).

## Gotchas you must check before handing over
- Units are mm. If Bambu Studio asks "convert from inches/meters?", the export was wrong.
- Bodies that touch only at an edge or a point = non-manifold; fuse with ≥ 0.4 mm overlap.
- Zero-thickness / coplanar booleans: overshoot cutters by 0.5–1 mm past the surface.
- Smooth curves: the toolkit uses 96 segments; increase for > 100 mm diameter arcs.
- Never claim a print "will work" — say it passed the checks and name the remaining risks
  (e.g. "the clip's flex is untested; print the fit coupon first").

More: `reference/bambu-studio.md` (slicer settings, profiles, multi-colour, pauses, handoff
template) and `reference/materials.md` (per-material temps, plates, enclosure, drying).
