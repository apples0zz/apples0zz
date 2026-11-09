# Bambu Studio for the P1S — the settings that matter

Printer preset: **Bambu Lab P1S 0.4 nozzle**. The P1S shares Bambu's X1C process profiles
(e.g. "0.20mm Standard @BBL X1C"). Always pick the matching **Bambu filament preset**
(e.g. "Bambu PLA Basic") or the generic one for third-party filament, and the **plate type**
actually installed — it sets bed temperature.

## Process profiles (layer height)
| Profile | Use |
|---|---|
| 0.08 Extra Fine / 0.12 Fine | Miniatures, small text, curved tops |
| **0.20 Standard** | Default for almost everything |
| 0.24 / 0.28 Draft | Big functional parts, prototypes |
Use variable layer height (Adaptive, then Smooth) for organic shapes.

## Where settings live (Process tab, Advanced mode on)
- **Quality**: layer height, seam position (Aligned / Back / Rear — pick Back for cosmetics),
  *Precision* → X-Y hole compensation (+0.05–0.1 makes holes true), Elephant foot compensation
  (default 0.15), Arc fitting.
- **Strength**: wall loops (2 default; 4 for functional), top/bottom shell layers (5/3 default;
  6+ top for smooth tops), sparse infill density & pattern (gyroid or grid 15 %; 25–40 % for
  load), "Ensure vertical shell thickness".
- **Speed**: leave defaults; slow outer wall to ~100–150 mm/s only for showpieces.
- **Support**: Enable, Type **tree(auto)**, threshold angle 30 (supports anything steeper than
  60° from vertical), "On build plate only" when possible. Paint support enforcers/blockers.
- **Others**: Brim (auto / outer only 3–8 mm for tall or warpy parts; mouse ears for corners),
  Skirt, Prime tower (multi-colour), Fuzzy skin, Ironing (top surfaces, flat parts).

## Per-object / per-part overrides
Right-click an object or part in the object list → add setting (walls, infill, …).
(`Part(settings=...)` is only written with `export_3mf(..., bambu_config=True)`, which makes
Bambu Studio show an "invalid config" warning, so put these overrides in the recipe instead.)
Modifiers (right-click → Add modifier → box/cylinder) change settings in a region only:
e.g. 100 % infill around a screw hole. Height range modifier: settings by Z range.

## Multi-colour / multi-material
- 3MF from `export_3mf()` arrives as one object made of named parts (e.g. "base", "inlay").
  Click each part in the object list and pick its filament; colours sync from the AMS.
- STL route: import all colour STLs at once → "Load these files as a single object with
  multiple parts?" → **Yes**, then set each part's filament.
- Painting: Color painting tool (N) for quick colour on a single mesh.
- Reduce waste: Flushing volumes button (lower multiplier to 0.7–0.8 for light→dark changes),
  "Flush into objects' infill", put colours in few layers, prime tower on.
- Colour by layer (no AMS): drag the layer slider, click "+" → Change filament / Pause.

## Pauses (magnets, nuts, inserts)
Layer slider → right-click at the layer **just above** the pocket's top → Add pause.
Pocket depth = part height + 0.2–0.4 so the nozzle doesn't hit the inserted part.

## Built-in tools worth using
- Cut tool (C): split oversize parts, with connectors (dowels/plugs) auto-added.
- Text (T) / SVG emboss: quick labels without remodelling.
- Arrange (A), Auto-orient (/), Lay on face (F).
- Calibration menu: flow dynamics, flow rate, max volumetric speed — run for new 3rd-party filament.

## Sending
Slice plate → check the Preview (color scheme "Line type", look for red overhang lines and
floating islands) → Print plate (LAN or cloud) or Export plate sliced file (`.gcode.3mf`) for
the SD card. P1S: enable "Timelapse" only if wanted (adds a little time).

## Handoff template (give the user this, filled in)
```
File:      models/<name>/<name>.3mf
Printer:   Bambu Lab P1S 0.4 nozzle · Plate: Textured PEI
Filament:  Bambu PLA Basic (slot 1: black, slot 2: orange)
Process:   0.20mm Standard · walls 4 · infill 15% gyroid · top layers 5
Supports:  none needed (checked: 0 mm² >45° overhang)
Brim:      off · Orientation: as loaded (do not auto-orient)
Extras:    pause at layer 18 (Z=3.6) to insert 6x2 mm magnets
Est.:      ~18 g filament
Risks:     lid fit is 0.25 mm/side — if tight, sand or reprint with CLEAR["loose"]
```
