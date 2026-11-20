"""Game tokens for the NARUTO Mythos TCG: Power, Chakra and Edge.

Original ninja-themed designs (no official logos or artwork):
  Power  - red coins with white "+1" / "+5"         (each +1 = one Power token, per the rules)
  Chakra - black coins with a yellow chakra swirl    ("5" coins for big turns)
  Edge   - yellow 4-point shuriken with a black "EDGE" hub (one per game, plus a spare)

Two colours per file, and colour only in the top 3 layers (flush inlay), so AMS purge stays small.
Each file is ONE object made of two parts (base + inlay); in Bambu Studio set the inlay part's
filament. Run: python3 models/naruto_tokens/generate.py
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude/skills/bambu-p1s/scripts"))
from p1s import *  # noqa: E402,F403

OUT = Path(__file__).resolve().parent
T = 3.0            # token thickness
INLAY = 0.6        # colour depth: 3 layers at 0.20
CH = 0.5           # edge chamfers (bottom one also beats elephant's foot)

COUNTS = {"power_1": 24, "power_5": 6, "chakra_1": 24, "chakra_5": 6, "edge": 2}


def coin(d):
    """Disc with 45° chamfers top and bottom."""
    return Manifold.batch_hull([cyl(0.01, d - 2 * CH), cyl(0.01, d).translate((0, 0, CH)),
                                cyl(0.01, d).translate((0, 0, T - CH)), cyl(0.01, d - 2 * CH).translate((0, 0, T - 0.01))])


def inlay(cs):
    """Flush colour inlay: the top INLAY mm of the token, shaped like `cs`."""
    return extrude(cs, INLAY).translate((0, 0, T - INLAY))


def swirl2d(r_end=8.0, turns=2.2, width=1.6, seg=240):
    """Original chakra swirl: an Archimedean spiral band with rounded ends + centre dot."""
    r0 = 1.8
    k = (r_end - r0) / (2 * math.pi * turns)
    th = [2 * math.pi * turns * i / seg for i in range(seg + 1)]
    outer = [((r0 + k * t + width / 2) * math.cos(t), (r0 + k * t + width / 2) * math.sin(t)) for t in th]
    inner = [((r0 + k * t - width / 2) * math.cos(t), (r0 + k * t - width / 2) * math.sin(t)) for t in th]
    band = poly2d(outer + inner[::-1])
    t1 = th[-1]
    ends = [circle2d(width, 48).translate(((r0) , 0)),
            circle2d(width, 48).translate(((r0 + k * t1) * math.cos(t1), (r0 + k * t1) * math.sin(t1)))]
    return CrossSection.batch_boolean([band] + ends + [circle2d(2.2, 48)], ADD)


def ring2d(d_out, w):
    return circle2d(d_out) - circle2d(d_out - 2 * w)


def shuriken2d(R=26.0, r=11.5, tip=1.2):
    """4-point throwing star with softened tips."""
    pts = []
    for i in range(8):
        a = math.radians(90 + i * 45)
        rr = R if i % 2 == 0 else r
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    star = poly2d(pts)
    return star.offset(-tip, JoinType.Round).offset(tip, JoinType.Round)


# ---- one token = (base solid, inlay solid) ------------------------------------------------
def power(n, d):
    art = text2d(f"+{n}", 9.0 if d < 22 else 8.5)
    body = coin(d)
    return body - inlay(art), inlay(art)


def chakra_1(d=22.0):
    art = swirl2d(r_end=7.2)
    return coin(d) - inlay(art), inlay(art)


def chakra_5(d=26.0):
    art = CrossSection.batch_boolean([text2d("5", 11.0), ring2d(d - 3.0, 1.0)], ADD)
    return coin(d) - inlay(art), inlay(art)


def edge():
    star = shuriken2d()
    body = extrude(star, T)   # flat edges: a hull-based chamfer would fill the gaps between the points
    art = CrossSection.batch_boolean([ring2d(20.0, 1.2), text2d("EDGE", 4.0)], ADD)
    art = art ^ star.offset(-1.0, JoinType.Round)   # never print colour outside the star
    return body - inlay(art), inlay(art)


def grid(tokens, pitch, cols):
    bases, inlays = [], []
    for i, (b, il) in enumerate(tokens):
        x, y = (i % cols) * pitch, -(i // cols) * pitch
        bases.append(b.translate((x, y, 0)))
        inlays.append(il.translate((x, y, 0)))
    return union(*bases), union(*inlays)


SETS = {
    # file: (tokens, pitch, cols, base colour, inlay colour)
    "power_tokens": ([power(1, 20.0)] * COUNTS["power_1"] + [power(5, 24.0)] * COUNTS["power_5"], 27, 6, "red", "white"),
    "chakra_tokens": ([chakra_1()] * COUNTS["chakra_1"] + [chakra_5()] * COUNTS["chakra_5"], 29, 6, "black", "yellow"),
    "edge_tokens": ([edge()] * COUNTS["edge"], 54, 2, "yellow", "black"),
}
SWATCH = {"red": "#dc2626", "white": "#f5f5f5", "black": "#262626", "yellow": "#facc15"}

if __name__ == "__main__":
    for name, (tokens, pitch, cols, c_base, c_inlay) in SETS.items():
        for b, il in tokens[:1] + tokens[-1:]:      # colour must sit at least 1 mm inside the edge
            top = b.slice(T - INLAY - 0.05)
            assert (il.slice(T - 0.1) - top.offset(-1.0, JoinType.Round)).area() < 0.5, f"{name}: design too close to edge"
        base, art = grid(tokens, pitch, cols)
        report(base + art, "PLA", infill=0.15, name=name)
        e = estimate(base + art, layer=0.20, walls=2, top_layers=5, bottom_layers=3, infill=0.15)
        print(f"  estimate @0.20: {e}")
        export_3mf(OUT / f"{name}.3mf", [Part(f"{c_base} base", base, 1), Part(f"{c_inlay} design", art, 2)],
                   object_name=name.replace("_", " "))
        preview(OUT / f"{name}.png", [base, art], colors=[SWATCH[c_base], SWATCH[c_inlay]], elev=60, azim=-90)
