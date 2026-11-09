"""Support-free phone stand with a cable pass-through.

Design trick: the side profile is drawn in 2D and extruded by the stand's width,
then printed ON ITS SIDE (profile flat on the bed). Every wall is then vertical,
layer lines run along the backrest (strong against the phone's lean), and the
only possible overhangs are the cable holes - which are teardrops.

Run:  python3 .claude/skills/bambu-p1s/examples/phone_stand.py [width] [phone_thickness]
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from p1s import *  # noqa: E402,F403

W = float(sys.argv[1]) if len(sys.argv) > 1 else 70.0          # stand width -> print height
PHONE = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0      # phone + case thickness
LEAN, BACK_L, BACK_T, FOOT_T, DEPTH = 65, 95, 6.0, 6.0, 100.0
LIP_X, LIP_T, LIP_H = 24.0, 6.0, 22.0
slot = PHONE + 2 * CLEAR["loose"]

# --- 2D side profile (X = depth, Y = height in use) --------------------------
t = math.radians(LEAN)
u = (math.cos(t), math.sin(t))              # up the backrest
n = (math.sin(t), -math.cos(t))             # backrest's rear normal
p0 = (LIP_X + LIP_T + slot, FOOT_T + 4)      # bottom of the backrest front face
pt = (p0[0] + BACK_L * u[0], p0[1] + BACK_L * u[1])
pa = lambda p, v, k: (p[0] + k * v[0], p[1] + k * v[1])  # noqa: E731

foot = rect2d(DEPTH, FOOT_T)
lip = rect2d(LIP_T, LIP_H).translate((LIP_X, 0))
slot_floor = rect2d(LIP_T + slot + 2, FOOT_T + 4).translate((LIP_X, 0))
backrest = CrossSection.batch_hull([poly2d([p0, pt, pa(pt, n, BACK_T), pa(p0, n, BACK_T)]), rect2d(4, 1).translate((p0[0], 0))])
q = pa(pa(p0, n, BACK_T), u, BACK_L * 0.55)
brace = CrossSection.batch_hull([poly2d([q, pa(q, u, 12), (DEPTH - 2, FOOT_T), (DEPTH - 18, FOOT_T)])])
profile = CrossSection.batch_boolean([foot, lip, slot_floor, backrest, brace], ADD)
profile = profile.offset(-1.5, JoinType.Round).offset(1.5, JoinType.Round)   # round inside & outside corners

stand = extrude(profile, W)   # extruded along Z: prints with the profile on the bed

# --- cable routing --------------------------------------------------------------
# 1) vertical (in use) hole down through the slot floor, under the phone's port
cx = LIP_X + LIP_T + slot / 2
drop = teardrop_hole(10, 40, axis="y").translate((cx, FOOT_T + 4, W / 2))
# 2) groove under the foot running to the back so the stand sits flat on the cable
groove = teardrop_hole(8, DEPTH, axis="x").translate((cx + DEPTH / 2, 0, W / 2))
stand = place_on_bed(stand - drop - groove, center=False)

out = Path(__file__).resolve().parents[4] / "models" / "phone_stand"
out.mkdir(parents=True, exist_ok=True)
report(stand, name="phone stand")
export_3mf(out / "phone_stand.3mf", [Part("phone stand", stand, 1, settings={"wall_loops": "4"})])
export_stl(out / "phone_stand.stl", stand)
preview(out / "preview.png", stand.rotate((90, 0, 0)), elev=20, azim=-60)   # shown in use
print("wrote", out)
