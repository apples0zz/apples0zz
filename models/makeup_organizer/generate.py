"""Bathroom makeup organizer - 6 modules that tile two 8.75" x 22.5" shelves.

Shelf 222 x 572 mm. Each module is 186 x 214 mm (3 per shelf, ~4 mm gaps), and each one
fits one P1S plate. Every product has its own slot, tiered so the back rows sit higher
and nothing hides anything else.

  Shelf 1 - "small stuff":  M1 Eyes | M2 Lips & concealer | M3 Cheek, sticks & jars
  Shelf 2 - "face":         M4 Bottle stairs | M5 Tubes & big sticks | M6 Compact rack

Product sizes are ESTIMATES from photos. To change a slot, edit the numbers below and
re-run:  python3 models/makeup_organizer/generate.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude/skills/bambu-p1s/scripts"))
from p1s import *  # noqa: E402,F403

OUT = Path(__file__).resolve().parent
MAT = "PLA"

# ---- shelf & module footprint ----------------------------------------------
SHELF_W, SHELF_D = 571.5, 222.25          # 22.5" x 8.75" as measured
# The shelves have ~5/8" rims on the back and sides. To fit whether the measurement was taken
# inside or outside the rims, size the modules for the worst case (outside measurement):
RIM = 16.0
INNER_W, INNER_D = SHELF_W - 2 * RIM, SHELF_D - RIM   # ≈ 540 x 206 mm usable
MOD_W, MOD_D = 176.0, 204.0               # 3 across = 528 mm + 2 x 6 mm gaps = 540 mm
CORNER_R = 6.0

# ---- tiered slot blocks ---------------------------------------------------------
BASE_H, STEP_H = 26.0, 12.0   # front tier height, rise per row toward the back
HOLE_D = 40.0                 # max slot depth (items rest on the slot floor)
POCKET_D = 4.0                # shallow recess depth for jars / compacts
EDGE = 2.4                    # minimum plastic between slots and edges (≈ 6 lines)


def C(d):            # round slot, Ø d
    return ("c", d, d)


def R(w, l):         # rounded-rectangle slot, w across (X) x l deep (Y)
    return ("r", w, l)


def P(d):            # shallow jar pocket, Ø d
    return ("p", d, d)


# Each module: rows from FRONT to BACK; each row = list of (shape, count, label).
MODULES = {
    "M1_eyes": [
        [(C(28), 5, "mascara")],                      # Lancôme-style, tartelette XL, gold mascara, Maybelline bubble, pink 'jet black', cream stick
        [(C(17), 8, "eye stick / thick liner")],     # Morphe, skywash, Laura Mercier caviar, CT Forbidden Rose, ...
        [(C(13), 9, "pencil / liner / brow")],       # wnw breakup proof, CT liner, Epic Wear, Black Silk, kohl, Lip Cheat, brow pen...
        [(C(13), 9, "pencil / liner / brow")],
    ],
    "M2_lips_concealer": [
        [(R(36, 20), 4, "flat tube (Summer Fridays, Blistex, cloud paint)")],
        [(C(24), 6, "gloss / lip / liquid shadow")],
        [(C(24), 6, "gloss / lip / liquid blush")],
        [(C(24), 6, "concealer")],                    # CG Clean Invisible, Flower, Real Flawless, NARS
    ],
    "M3_cheek_jars": [
        [(P(72), 2, "jar stack (essence matt, Fenty cream)")],
        [(P(68), 1, "elf putty bronzer"), (P(46), 2, "Colourpop / small pot")],
        [(R(30, 25), 4, "about-face stick")],
        [(C(26), 5, "blush wand / Rare Beauty / cream stick")],
    ],
    "M5_tubes_sticks": [
        [(C(34), 2, "Fenty hex stick"), (R(46, 34), 1, "Pixi stick"), (C(34), 1, "spare stick")],
        [(R(29, 58), 5, "squeeze tube, cap down")],   # NARS, wnw Impossible, SPF 50, Anua, Laura Mercier
        [(R(29, 58), 5, "squeeze tube, cap down")],
    ],
}


def slot2d(shape):
    k, w, l = shape
    if k == "r":
        return rect2d(w, l, min(8.0, w / 2 - 0.5, l / 2 - 0.5)).translate((-w / 2, -l / 2))
    return circle2d(w)


def tiered_block(rows, width=MOD_W, depth=MOD_D):
    """Stadium block: each row is a tier STEP_H higher than the one in front."""
    row_l = [max(s[0][2] for s in row) for row in rows]
    need = sum(row_l) + EDGE * (len(rows) + 1)
    assert need <= depth, f"rows need {need:.0f} mm > {depth}"
    extra = (depth - need) / len(rows)
    tiers, cuts, layout = [], [], []
    y = EDGE
    for i, (row, L) in enumerate(zip(rows, row_l)):
        y0 = y - EDGE / 2 if i else 0
        top = BASE_H + i * STEP_H
        tiers.append(rounded_box(width, depth - y0, top, r=CORNER_R, top_chamfer=0.8).translate((0, y0, 0)))
        cy = y + extra / 2 + L / 2
        items = [s for s, n, _ in row for _ in range(n)]
        labels = [lab for _, n, lab in row for _ in range(n)]
        total = sum(s[1] for s in items)
        gap_x = (width - total) / (len(items) + 1)
        # +2: the 1 mm lead-in chamfer eats into the wall on each side
        min_gap = EDGE if any(s[0] == "p" for s in items) else EDGE + 2  # pockets have no lead-in chamfer
        assert gap_x >= min_gap, f"row {i} too crowded ({gap_x:.1f} mm between slots)"
        x = gap_x
        for s, lab in zip(items, labels):
            cx = x + s[1] / 2
            d = POCKET_D if s[0] == "p" else min(HOLE_D, top - 2.0)
            cut = extrude(slot2d(s), d + 1).translate((cx, cy, top - d))
            if s[0] != "p":   # 1 mm lead-in chamfer so things drop in easily
                lead = Manifold.batch_hull([extrude(slot2d(s), 0.01).translate((cx, cy, top - 1.0)),
                                            extrude(slot2d(s).offset(1.0), 0.01).translate((cx, cy, top + 0.01))])
                cut = cut + lead
            cuts.append(cut)
            layout.append((s, cx, cy, lab))
            x += s[1] + gap_x
        y += L + EDGE + extra
    return union(*tiers) - union(*cuts), layout


# ---- M4: bottle stairs (printed on its side - light, no supports) -------------
STAIRS = [(0, 68, 6), (68, 136, 40), (136, MOD_D, 74)]   # (y from, y to, step height)
LIP = 5.0          # little front lip on each step so bottles don't slide off
SHELL = 2.4


def bottle_stairs():
    prof = CrossSection.batch_boolean([rect2d(MOD_D - y0, h).translate((y0, 0)) for y0, _, h in STAIRS], ADD)
    # lips: thin ridge at the front of each step
    lips = [rect2d(SHELL, LIP + 0.5).translate((y0, h - 0.5)) for y0, _, h in STAIRS]
    prof = CrossSection.batch_boolean([prof] + lips, ADD)
    # hollow it: keep an outer shell plus vertical ribs under each step edge
    inner = CrossSection.batch_boolean([rect2d(MOD_D - y0, h).translate((y0, 0)) for y0, _, h in STAIRS], ADD).offset(-SHELL, JoinType.Miter)
    ribs = [rect2d(SHELL, 200).translate((y0 - SHELL / 2, 0)) for y0, _, _ in STAIRS[1:]]
    ribs += [rect2d(SHELL, 200).translate(((a + b) / 2 - SHELL / 2, 0)) for a, b, _ in STAIRS]
    hollow = inner - CrossSection.batch_boolean(ribs, ADD)
    prof = prof - hollow
    # profile is in (Y, Z); extrude along X by the module width, then stand it up for use.
    solid = extrude(prof, MOD_W)                         # profile in XY, width along Z = print orientation
    use = solid.rotate((90, 0, 0)).rotate((0, 0, 90))     # -> width along X, depth along Y, height Z
    use = place_on_bed(use, center=False)
    return solid, use


# ---- M6: compact rack (stand compacts on edge, stepped like a record bin) ----
# slot widths front -> back = compact thickness + ~3 mm (thin/low in front, thick/high in back)
COMPACT_SLOTS = [(16, "W7 Duo Blusher"), (16, "wet n wild bronzer"), (17, "Charlotte Tilbury compact"),
                 (17, "black square palette"), (18, "pink palette"), (21, "H&M palette"),
                 (22, "Glossier quad"), (24, "rose-gold round compact"), (29, "TIRTIR cushion")]
DIV = 1.68            # divider thickness (4 lines)
RACK_BASE, RACK_STEP, RACK_HOLD = 4.0, 7.0, 28.0   # floor heights & how high each divider stands above its floor
SIDE_H = 14.0


def compact_rack():
    parts, layout = [], []
    y = 0.0
    walls_y = []
    floors = []
    for k, (w, lab) in enumerate(COMPACT_SLOTS):
        walls_y.append(y)
        fz = RACK_BASE + k * RACK_STEP
        floors.append((y + DIV, w, fz))
        layout.append((k, y + DIV + w / 2, fz, lab))
        y += DIV + w
    walls_y.append(y)
    depth = y + DIV
    assert depth <= MOD_D, f"compact rack {depth:.0f} mm deep > {MOD_D}"
    # dividers: full-width walls from the shelf up to (floor of slot behind + hold height)
    for i, wy in enumerate(walls_y):
        k = min(i, len(COMPACT_SLOTS) - 1)
        h = RACK_BASE + k * RACK_STEP + RACK_HOLD
        if i == len(walls_y) - 1:
            h = RACK_BASE + (len(COMPACT_SLOTS) - 1) * RACK_STEP + RACK_HOLD + 10   # taller back wall
        parts.append(box(MOD_W, DIV, h).translate((0, wy, 0)))
    # floors: plates bridging between neighbouring dividers (≤ 30 mm bridges, no supports)
    for fy, w, fz in floors:
        parts.append(box(MOD_W, w + 0.2, 1.6).translate((0, fy - 0.1, fz - 1.6)))
    # side cheeks follow the floor line so compacts can't slide out sideways
    for sx in (0, MOD_W - DIV):
        for fy, w, fz in floors:
            parts.append(box(DIV, w + 2 * DIV, fz + SIDE_H).translate((sx, fy - DIV, 0)))
    rack = union(*parts).translate((0, (MOD_D - depth) / 2, 0))
    return rack, layout, depth


def spot_map(path, layouts):
    """Top-down map of both shelves: every slot outlined and colour-coded by what goes in it."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

    shelves = [("Shelf 1: eyes, lips, cheeks", ["M1_eyes", "M2_lips_concealer", "M3_cheek_jars"]),
               ("Shelf 2: face", ["M4_bottle_stairs", "M5_tubes_sticks", "M6_compact_rack"])]
    cats = {}
    palette = plt.get_cmap("tab20").colors
    fig, axes = plt.subplots(2, 1, figsize=(15, 13))
    for ax, (title, names) in zip(axes, shelves):
        ax.add_patch(Rectangle((0, 0), SHELF_W, SHELF_D, fill=False, lw=2, ls="--", ec="#999"))
        for rx, ry, rw, rh in [(0, 0, RIM, SHELF_D), (SHELF_W - RIM, 0, RIM, SHELF_D), (0, SHELF_D - RIM, SHELF_W, RIM)]:
            ax.add_patch(Rectangle((rx, ry), rw, rh, fc="#a16207", alpha=.35, ec="none"))   # rims (worst case)
        for j, name in enumerate(names):
            ox = RIM + j * (MOD_W + 6)
            ax.add_patch(FancyBboxPatch((ox, 4), MOD_W, MOD_D, boxstyle="round,pad=0,rounding_size=6",
                                        fc="#fdf2f8", ec="#db2777", lw=1.5))
            ax.text(ox + MOD_W / 2, MOD_D + 12, name.replace("_", " "), ha="center", fontsize=11, weight="bold")
            if name == "M4_bottle_stairs":
                for (y0, y1, h), lab in zip(STAIRS, ["front step: short bottles", "middle step: foundations",
                                                      "top step: tallest bottles"]):
                    c = cats.setdefault(lab, palette[len(cats) % 20])
                    ax.add_patch(Rectangle((ox + 4, 4 + y0 + 3), MOD_W - 8, y1 - y0 - 6, fc=c, alpha=.55))
                    ax.text(ox + MOD_W / 2, 4 + (y0 + y1) / 2, f"{lab}\n(step {h:.0f} mm high)", ha="center", va="center", fontsize=8)
                continue
            if name == "M6_compact_rack":
                for k, cy, fz, lab in layouts[name]:
                    w = COMPACT_SLOTS[k][0]
                    c = cats.setdefault("compact (stand on edge)", palette[len(cats) % 20])
                    ax.add_patch(Rectangle((ox + 3, 4 + cy - w / 2), MOD_W - 6, w, fc=c, alpha=.55))
                    ax.text(ox + MOD_W / 2, 4 + cy, lab, ha="center", va="center", fontsize=7.5)
                continue
            for (k, w, l), cx, cy, lab in layouts[name]:
                c = cats.setdefault(lab, palette[len(cats) % 20])
                if k == "r":
                    ax.add_patch(FancyBboxPatch((ox + cx - w / 2, 4 + cy - l / 2), w, l,
                                                boxstyle=f"round,pad=0,rounding_size={min(8, w / 2 - .5, l / 2 - .5)}", fc=c, ec="k", lw=.5))
                else:
                    ax.add_patch(Circle((ox + cx, 4 + cy), w / 2, fc=c, ec="k", lw=.5, alpha=.6 if k == "p" else 1))
        ax.set_xlim(-5, SHELF_W + 5); ax.set_ylim(-14, SHELF_D + 26); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(title + "   (bottom edge = front of shelf)", fontsize=13)
    handles = [Rectangle((0, 0), 1, 1, fc=c) for c in cats.values()]
    fig.legend(handles, list(cats), loc="lower center", ncol=3, fontsize=9, frameon=False)
    fig.subplots_adjust(bottom=0.13, hspace=0.12)
    fig.savefig(path, dpi=110)
    plt.close(fig)


# ---------------------------------------------------------------------------------
def build():
    mods, layouts = {}, {}
    for name, rows in MODULES.items():
        mods[name], layouts[name] = tiered_block(rows)
    side, mods["M4_bottle_stairs"] = bottle_stairs()
    mods["M6_compact_rack"], layouts["M6_compact_rack"], _ = compact_rack()
    return mods, layouts, side


if __name__ == "__main__":
    mods, layouts, stairs_side = build()
    total = 0.0
    for name, m in mods.items():
        printed = stairs_side if name == "M4_bottle_stairs" else m
        r = report(printed, MAT, infill=0.08, name=name)
        total += r["est_filament_g"]
        export_3mf(OUT / f"{name}.3mf", [Part(name, printed, 1, settings={"sparse_infill_pattern": "lightning",
                                                                          "sparse_infill_density": "10%"})])
        export_stl(OUT / f"{name}.stl", printed)
        preview(OUT / f"{name}.png", m)
    print(f"\nTOTAL ≈ {total:.0f} g PLA")
    # fit-test sampler: one of every slot size, ~1 h print - check before the big ones
    sampler, _ = tiered_block([[(C(13), 1, ""), (C(17), 1, ""), (C(24), 1, ""), (C(26), 1, ""), (C(28), 1, ""), (C(34), 1, "")],
                               [(R(30, 25), 1, ""), (R(36, 20), 1, ""), (R(46, 34), 1, ""), (R(29, 58), 1, "")]],
                              width=MOD_W, depth=100)
    report(sampler, MAT, infill=0.08, name="00_fit_test_sampler")
    export_3mf(OUT / "00_fit_test_sampler.3mf", [Part("fit test sampler", sampler, 1)])
    preview(OUT / "00_fit_test_sampler.png", sampler)
    # shelf previews
    s1 = [mods["M1_eyes"], mods["M2_lips_concealer"].translate((MOD_W + 6, 0, 0)),
          mods["M3_cheek_jars"].translate((2 * (MOD_W + 6), 0, 0))]
    s2 = [mods["M4_bottle_stairs"], mods["M5_tubes_sticks"].translate((MOD_W + 6, 0, 0)),
          mods["M6_compact_rack"].translate((2 * (MOD_W + 6), 0, 0))]
    preview(OUT / "shelf1_preview.png", s1, colors=["#f9a8d4", "#fbcfe8", "#f472b6"], elev=35, azim=-75)
    preview(OUT / "shelf2_preview.png", s2, colors=["#f9a8d4", "#fbcfe8", "#f472b6"], elev=35, azim=-75)
    spot_map(OUT / "spot_map.png", layouts)
