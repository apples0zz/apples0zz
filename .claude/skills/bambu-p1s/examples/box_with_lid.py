"""Parametric storage box with a slide-on lid (two objects on one plate).

Run:  python3 .claude/skills/bambu-p1s/examples/box_with_lid.py [outer_x outer_y height]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from p1s import *  # noqa: E402,F403

X, Y, H = (float(a) for a in sys.argv[1:4]) if len(sys.argv) >= 4 else (80.0, 60.0, 40.0)
WALL, FLOOR, R = 1.6, 1.2, 4.0          # 4 perimeters, 6 bottom layers
LIP_H, LIP_W = 6.0, 1.2                 # lid skirt that slides inside the box
FIT = CLEAR["slide"]                    # 0.25 mm per side
LID_T = 1.6

box_body = shell_box(X, Y, H, WALL, FLOOR, R)

# Lid: plate + an inner skirt that drops into the box opening.
ix, iy = X - 2 * WALL - 2 * FIT, Y - 2 * WALL - 2 * FIT
ir = max(R - WALL - FIT, 0.5)
plate = rounded_box(X, Y, LID_T, R, bottom_chamfer=0.4, top_chamfer=0.6)
skirt_outer = extrude(rect2d(ix, iy, ir), LIP_H).translate((WALL + FIT, WALL + FIT, LID_T))
skirt_inner = extrude(rect2d(ix - 2 * LIP_W, iy - 2 * LIP_W, max(ir - LIP_W, 0.3)), LIP_H + 1).translate(
    (WALL + FIT + LIP_W, WALL + FIT + LIP_W, LID_T))
lid = plate + skirt_outer - skirt_inner      # prints upside-down: flat top on the bed, skirt up

out = Path(__file__).resolve().parents[4] / "models" / "box_with_lid"
out.mkdir(parents=True, exist_ok=True)
report(box_body, name="box")
report(lid, name="lid")

# Verify the fit: flip the lid onto the box in "assembled" pose and measure the gap.
# (The plate rests on the rim, so measure the skirt - the part that must slide.)
skirt = (skirt_outer - skirt_inner).mirror((0, 0, 1)).translate((0, 0, H + LID_T))
print(f"  skirt↔box wall clearance when assembled: {gap(box_body, skirt):.3f} mm (target {FIT})")

export_3mf(out / "box_with_lid.3mf",
           [Part("box", box_body, 1), Part("lid", lid.translate((X + 10, 0, 0)), 1)],
           separate_objects=True)
export_stl(out / "box.stl", box_body)
export_stl(out / "lid.stl", lid)
preview(out / "preview.png", [box_body, lid.translate((X + 10, 0, 0))])
print("wrote", out)
