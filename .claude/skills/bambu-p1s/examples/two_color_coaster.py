"""Two-colour hex coaster for the AMS: base in filament 1, inlay pattern in filament 2.

The inlay is flush with the top (it replaces the top 0.6 mm = 3 layers of the base),
so colour changes happen on only 3 layers -> little purge waste.
Run:  python3 .claude/skills/bambu-p1s/examples/two_color_coaster.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from p1s import *  # noqa: E402,F403

D, T, INLAY = 100.0, 4.0, 0.6       # across-flats-ish diameter, thickness, inlay depth (3 layers)
RIM = 4.0

def hexagon(d):
    return poly2d([(d / 2 * math.cos(math.radians(60 * i + 30)), d / 2 * math.sin(math.radians(60 * i + 30))) for i in range(6)])

outline = hexagon(D).offset(-3, JoinType.Round).offset(3, JoinType.Round)   # round the corners
base_full = Manifold.batch_hull([extrude(outline.offset(-0.4), 0.01), extrude(outline, 0.01).translate((0, 0, 0.4))]) \
    + extrude(outline, T - 0.4).translate((0, 0, 0.4))

# Pattern: concentric hex rings + radial spokes, clipped inside the rim.
field = outline.offset(-RIM)
rings = [hexagon(D - 2 * RIM - k).offset(0) - hexagon(D - 2 * RIM - k - 3.6) for k in (10, 26, 42, 58)]
spokes = [CrossSection.square((2.0, D), True).rotate(60 * i) for i in range(3)]
pattern = CrossSection.batch_boolean(rings + spokes, ADD) ^ field
pattern = pattern - circle2d(8) + (circle2d(14) - circle2d(10))

inlay = extrude(pattern, INLAY).translate((0, 0, T - INLAY))
base = base_full - inlay

out = Path(__file__).resolve().parents[4] / "models" / "two_color_coaster"
out.mkdir(parents=True, exist_ok=True)
report(base, name="coaster base")
report(inlay, name="coaster inlay", sub_part=True)
export_3mf(out / "two_color_coaster.3mf",
           [Part("base", base, filament=1), Part("inlay", inlay, filament=2)],
           object_name="hex coaster")
preview(out / "preview.png", [base, inlay], colors=["#1f2937", "#f59e0b"], elev=55)
print("wrote", out)
