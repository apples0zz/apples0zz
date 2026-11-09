"""Bathroom makeup organizer - 6 modules + press-in feet for two shelves, 22.5" x 8.75" measured INSIDE the rims.

  Shelf 1 - sticks:   M1 Eyes & lips | M2 Cheeks & tubes | M3 Brushes, sponges & puffs  (slot blocks)
  Shelf 2 - face:     M4 Bottle stairs | M5 Thin compacts rack | M6 Thick compacts & jars rack

Every flat product (compacts, palettes, pans, jars) stands ON ITS SIDE in a slot sized to that
item's thickness, like a record bin, with back rows raised so you can see every one.

How sizes were measured: widths/diameters from the top-down photo, scaled with the keyboard
(keycaps sit on a 19.05 mm grid → ≈3.1 px/mm). Thickness can't be seen from above, so it's
taken from the angled photos and each slot gets +4 mm so things drop in easily.
Edit a number below and re-run:  python3 models/makeup_organizer/generate.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude/skills/bambu-p1s/scripts"))
from p1s import *  # noqa: E402,F403

OUT = Path(__file__).resolve().parent
MAT = "PLA"

# ---- shelf & module footprint ----------------------------------------------------
SHELF_W, SHELF_D = 571.5, 222.25    # 22.5" x 8.75", measured inside the rims
GAP = 5.0                           # between modules
MOD_W, MOD_D = 184.0, 216.0         # 3 x 184 + 2 x 5 = 562 mm -> 9.5 mm side slack, 6 mm depth slack
CORNER_R = 6.0

# ---- slot blocks (sticks / tubes) ---------------------------------------------------
BASE_H, STEP_H = 23.0, 9.0    # front tier height, rise per row toward the back (kept low: less plastic)
HOLE_D = 24.0                 # max slot depth (deep enough to hold, shallow enough to save plastic)
EDGE = 2.4


def C(d, depth=None, drain=0.0):   # round slot, Ø d (optional fixed depth, drain hole to the shelf)
    return ("c", d, d, depth, drain)


def R(w, l, depth=None):           # rounded-rectangle slot, w across x l deep
    return ("r", w, l, depth, 0.0)


# rows FRONT -> BACK; each row = list of (shape, count, label)
SLOT_GAP = 5.0      # plastic between neighbouring slots (≈3 mm after the 1 mm lead-in chamfers)
ROW_GAP = 5.0       # same between rows; leftover depth becomes a flat ledge at the front

BLOCKS = {
    "M1_eyes_lips": [
        [(C(28), 5, "mascara")],                               # 5 mascaras
        [(C(28), 1, "big beige stick"), (C(22), 1, "Glossier brow gel"),
         (C(17), 4, "chunky eye stick")],                      # white pen, Morphe, Skywash (+1 spare)
        [(C(13), 10, "pencil / liner / brow")],                # Annabelle, LM caviar, CT Forbidden Rose, wnw liner,
                                                               # CT liner, Epic Wear, Black Silk, kohl, Lip Cheat, brow pen
        [(R(36, 20), 3, "flat tube (Summer Fridays, Blistex, Cloud Paint)"), (C(22), 1, "gloss / lip / liquid shadow")],
        [(C(24), 4, "concealer"), (C(22), 2, "gloss / lip / liquid shadow")],   # CG, Flower, Real Flawless, NARS
        [(C(22), 6, "gloss / lip / liquid shadow")],          # 9 lip items in total
    ],
    "M2_cheeks_tubes": [
        [(C(26), 3, "liquid blush / wand"), (C(34), 2, "Fenty hex stick")],   # elf blush, Rare Beauty, Halo Glow
        [(R(32, 24), 3, "about-face stick"), (R(46, 34), 1, "Pixi stick")],
        [(R(29, 58), 5, "squeeze tube, cap down")],            # wnw Impossible, SPF 50, Anua, LM Pure Canvas + 1 spare
    ],
    "M3_brushes_sponges_puffs": [
        [(R(84, 20, depth=20), 2, "powder puff (stand on edge)")],   # velour puffs (2-3 seen) + 1 spare
        [(R(84, 20, depth=24), 2, "powder puff (stand on edge)")],
        [(C(50, depth=22, drain=12), 3, "sponge cup (air hole underneath)")],   # orange blender, pink sponge + 1 spare
        [(C(26), 3, "big brush / kabuki"), (C(15), 4, "brush")],     # ~15 brushes -> 26 holes, room to grow
        [(C(15), 9, "brush")],
        [(C(12), 10, "thin / detail brush")],
    ],
}


def slot2d(shape):
    k, w, l = shape[:3]
    if k == "r":
        return rect2d(w, l, min(8.0, w / 2 - 0.5, l / 2 - 0.5)).translate((-w / 2, -l / 2))
    return circle2d(w)


FRONT_LEDGE = 10.0  # flat strip in front of the first row; the module is only as deep as it needs


def tiered_block(rows, width=MOD_W, depth=MOD_D, base_h=BASE_H, step_h=STEP_H):
    """Stadium block: each row is a tier STEP_H higher than the one in front. Slots are packed
    SLOT_GAP apart and centred; rows sit ROW_GAP apart against the back, and any spare depth
    becomes a flat ledge at the front (handy for setting things down)."""
    row_l = [max(s[0][2] for s in row) for row in rows]
    need = sum(row_l) + ROW_GAP * (len(rows) + 1)
    assert need <= depth, f"rows need {need:.0f} mm > {depth}"
    depth = min(depth, need + FRONT_LEDGE)   # don't print empty ledge: the block sits at the back of the shelf
    ledge = depth - need
    tiers, cuts, layout = [], [], []
    y = ledge + ROW_GAP
    for i, (row, L) in enumerate(zip(rows, row_l)):
        y0 = y - ROW_GAP / 2 if i else 0
        top = base_h + i * step_h
        tiers.append(rounded_box(width, depth - y0, top, r=CORNER_R, top_chamfer=0.8).translate((0, y0, 0)))
        cy = y + L / 2
        items = [s for s, n, _ in row for _ in range(n)]
        labels = [lab for _, n, lab in row for _ in range(n)]
        span = sum(s[1] for s in items) + SLOT_GAP * (len(items) - 1)
        margin = (width - span) / 2
        assert margin >= EDGE + 1, f"row {i} too wide ({span:.0f} mm in {width:.0f})"
        x = margin
        for s, lab in zip(items, labels):
            cx = x + s[1] / 2
            d = min(s[3] or HOLE_D, top - 5.0)   # keep >= 5 mm under every slot (room for the foot sockets)
            lead = Manifold.batch_hull([extrude(slot2d(s), 0.01).translate((cx, cy, top - 1.0)),
                                        extrude(slot2d(s).offset(1.0), 0.01).translate((cx, cy, top + 0.01))])
            cuts.append(extrude(slot2d(s), d + 1).translate((cx, cy, top - d)) + lead)
            if s[4]:   # drain / air hole down to the shelf (damp sponges & brushes dry from below)
                cuts.append(cyl(top + 2, s[4]).translate((cx, cy, -1)))
            layout.append((s, cx, cy, lab))
            x += s[1] + SLOT_GAP
        y += L + ROW_GAP
    return union(*tiers) - union(*cuts), layout


# ---- little feet ------------------------------------------------------------------------
# Separate press-in feet: a flat body bottom is the only way to print the modules without
# supports, so the feet are printed on their own plate and pushed into sockets underneath.
FOOT_D, FOOT_H = 14.0, 3.0           # foot pad: Ø14 x 3 mm (lifts every module 3 mm)
SOCKET_D, SOCKET_H = 6.0, 3.0        # socket in the module bottom
PIN_D = SOCKET_D - 2 * 0.05          # 0.05 mm/side: tight press fit (add a drop of glue if loose)
PIN_H = SOCKET_H - 0.3
FOOT_INSET = 14.0                    # foot centre from the module's edges


def foot_positions(m):
    x0, y0, _, x1, y1, _ = m.bounding_box()
    i = FOOT_INSET
    return [(x0 + i, y0 + i), (x1 - i, y0 + i), (x0 + i, y1 - i), (x1 - i, y1 - i)]


def add_sockets(m, feet=None):
    """Cut 4 foot sockets into the bottom. feet=[(x, y, pillar_h)] (racks) first adds solid
    Ø(FOOT_D) pillars up to the slot floor above, so each socket has plastic around it."""
    pts = foot_positions(m) if feet is None else [(x, y) for x, y, _ in feet]
    if feet:
        m = union(m, *[cyl(h, FOOT_D).translate((x, y, 0)) for x, y, h in feet])
    sock = union(*[cyl(SOCKET_H + 0.01, SOCKET_D).translate((x, y, -0.01)) for x, y in pts])
    # every socket must be fully surrounded by plastic (no breaking into a slot)
    shell = union(*[cyl(SOCKET_H + 1.0, SOCKET_D + 2.0).translate((x, y, 0)) for x, y in pts])
    assert abs((shell ^ m).volume() - shell.volume()) < 1.0, "a foot socket breaks into a slot - move it"
    return m - sock


def foot():
    pad = Manifold.batch_hull([cyl(0.01, FOOT_D - 1.0), cyl(0.01, FOOT_D).translate((0, 0, 0.5))]) \
        + cyl(FOOT_H - 0.5, FOOT_D).translate((0, 0, 0.5))
    pin = cyl(PIN_H - 0.4, PIN_D).translate((0, 0, FOOT_H)) + \
        cyl(0.4, PIN_D, PIN_D - 0.8).translate((0, 0, FOOT_H + PIN_H - 0.4))   # chamfered tip finds the socket
    return pad + pin


# ---- M4: bottle stairs (solid upright steps + lightning infill: light and fast) -----
STAIRS = [(0, 72, 8), (72, 144, 40), (144, MOD_D, 72)]   # (y from, y to, step height)
LIP, SHELL = 5.0, 1.68          # 4-line walls: plenty for bottles


def bottle_stairs():
    """Solid steps printed upright (lightning infill keeps them light). A low lip along the front
    of each step stops bottles sliding off. Returns (print pose, in-use pose) - the same here."""
    tiers = [rounded_box(MOD_W, MOD_D - y0, h, r=CORNER_R, top_chamfer=0.6).translate((0, y0, 0)) for y0, _, h in STAIRS]
    lips = [rounded_box(MOD_W, SHELL, h + LIP, r=0.6, bottom_chamfer=0).translate((0, y0, 0)) for y0, _, h in STAIRS]
    m = add_sockets(union(*tiers, *lips))
    return m, m


# ---- M5 / M6: compact racks ---------------------------------------------------------
# Item: (label, width mm along the row, thickness mm). Width = longest side that stands on the
# floor (diameter for rounds). Measured from the top-down photo; thickness estimated.
FIT_T, FIT_W = 4.0, 6.0      # slot = thickness + 4; each item gets width + 6
DIV = 1.26                   # divider / rib thickness (3 lines: stiff enough, less plastic)
FLOOR_T = 1.2                # slot floor thickness
RACK_BASE, RACK_STEP, HOLD = 4.0, 4.0, 18.0   # floor heights; divider height above its floor (low = less plastic)
BRIDGE_MAX = 26.0            # wider floors get a support wall underneath (no sagging bridges)

THIN_RACK = [   # M5, front -> back (shortest items in front)
    [("NARS blush", 65, 13), ("wet n wild blush", 63, 15)],
    [("Charlotte Tilbury compact", 77, 15), ("Colourpop pot", 42, 18)],
    [("peach round compact", 60, 20), ("Morphe blush", 73, 20)],
    [("W7 Duo Blusher", 94, 13)],
    [("essence all about matt", 80, 15)],
    [("marie claire setting powder", 75, 15)],
    [("wet n wild bronzer", 75, 14)],
    [("H&M palette", 133, 15)],
    [("essence sun club bronzer", 103, 18)],
]
THIN_SIDE = ("Too Faced Italian Spritz", 209, 15)   # long edge down, in a side slot running front-to-back

THICK_RACK = [  # M6 (front row left empty for new compacts)
    [("spare: new compact", 80, 18), ("spare: new compact", 70, 18)],
    [("Fenty cream blush", 55, 25), ("Milani blush", 69, 22)],
    [("elf putty bronzer", 47, 28), ("Glossier jar", 74, 33)],
    [("Glossier quad", 71, 22), ("rose-gold compact", 80, 22)],
    [("TIRTIR cushion", 95, 32), ("Morphe powder jar", 70, 38)],
]


def compact_rack(rows, side=None, width=MOD_W, depth=MOD_D, fit_t=FIT_T):
    """Record-bin rack. Each row = one slot across the module, sized to its thickest item,
    split by short ribs so each item has its own spot. Floors step up toward the back.
    side=(label, length, thickness): an extra slot along the LEFT edge running front-to-back."""
    parts, layout = [], []
    x0 = 0.0
    if side:
        lab, L, t = side
        sw = t + fit_t
        # open at the front (only a back stop), so a tin a little longer than measured still fits
        assert L <= depth - DIV + 10, "side slot too long"
        parts += [box(DIV, depth, RACK_BASE + 28), box(DIV, depth, RACK_BASE + 28).translate((sw + DIV, 0, 0)),
                  box(sw + 2 * DIV, DIV, RACK_BASE + 28).translate((0, depth - DIV, 0)),
                  box(sw, depth, RACK_BASE).translate((DIV, 0, 0))]
        layout.append(("side", lab, DIV + sw / 2, depth / 2, sw, L))
        x0 = sw + DIV
    row_w = width - x0
    slots = [max(t for _, _, t in row) + fit_t for row in rows]
    rack_d = sum(slots) + DIV * (len(rows) + 1)
    assert rack_d <= depth, f"rack {rack_d:.0f} mm > {depth}"
    yoff = (depth - rack_d) / 2
    y = yoff
    centres = []
    for k, (row, sw) in enumerate(zip(rows, slots)):
        fz = RACK_BASE + k * RACK_STEP
        need = sum(w + FIT_W for _, w, _ in row) + DIV * (len(row) + 1)
        assert need <= row_w + 0.01, f"row {k} needs {need:.0f} mm > {row_w:.0f}"
        # front divider of this slot, and the floor
        parts.append(box(row_w, DIV, fz + HOLD).translate((x0, y, 0)))
        parts.append(box(row_w, sw + 0.2, FLOOR_T).translate((x0, y + DIV - 0.1, fz - FLOOR_T)))
        if sw > BRIDGE_MAX:   # support wall under wide floors keeps every bridge short
            parts.append(box(row_w, DIV, fz - FLOOR_T).translate((x0, y + DIV + sw / 2 - DIV / 2, 0)))
        # side cheeks + ribs between items (each item gets an equal share of spare width)
        spare = (row_w - need) / len(row)
        x = x0
        parts.append(box(DIV, sw + 2 * DIV, fz + 8).translate((x, y, 0)))
        for lab, w, t in row:
            cell = w + FIT_W + spare
            layout.append(("row", lab, x + DIV + cell / 2, y + DIV + sw / 2, cell, sw))
            x += DIV + cell
            parts.append(box(DIV, sw + 2 * DIV, fz + 8).translate((x, y, 0)))
        centres.append((y + DIV + sw / 2, fz))
        y += DIV + sw
    # back wall
    fz_last = RACK_BASE + (len(rows) - 1) * RACK_STEP
    parts.append(box(row_w, DIV, fz_last + HOLD + 4).translate((x0, y, 0)))
    # no base plate (saves ~60 g): feet sit on pillars that rise to the floor of the first & last slot
    feet = []
    for cy, fz in (centres[0], centres[-1]):
        for fx in (FOOT_INSET, width - FOOT_INSET):
            feet.append((fx, cy, RACK_BASE if fx < x0 else fz))
    return union(*parts), layout, rack_d, feet


DEPTHS = {}


def spot_map(path, layouts):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

    shelves = [("Shelf 1: sticks & tubes", ["M1_eyes_lips", "M2_cheeks_tubes", "M3_brushes_sponges_puffs"]),
               ("Shelf 2: face", ["M4_bottle_stairs", "M5_thin_compacts", "M6_thick_compacts"])]
    cats, palette = {}, plt.get_cmap("tab20").colors
    fig, axes = plt.subplots(2, 1, figsize=(15, 15.5))
    for ax, (title, names) in zip(axes, shelves):
        ax.add_patch(Rectangle((0, 0), SHELF_W, SHELF_D, fill=False, lw=2, ls="--", ec="#999"))
        for j, name in enumerate(names):
            ox = (SHELF_W - 3 * MOD_W - 2 * GAP) / 2 + j * (MOD_W + GAP)
            oy = (SHELF_D - MOD_D) / 2 + MOD_D - DEPTHS.get(name, MOD_D)   # pushed to the back
            if name is None:   # free third of the shelf
                ax.add_patch(Rectangle((ox, oy), MOD_W, MOD_D, fill=False, ls=":", ec="#999", lw=1.5))
                ax.text(ox + MOD_W / 2, oy + MOD_D / 2, "open space\n(brushes & sponges)", ha="center", va="center", color="#777")
                continue
            ax.add_patch(FancyBboxPatch((ox, oy), MOD_W, DEPTHS.get(name, MOD_D), boxstyle="round,pad=0,rounding_size=6",
                                        fc="#fdf2f8", ec="#db2777", lw=1.5))
            ax.text(ox + MOD_W / 2, SHELF_D + 8, name.replace("_", " "), ha="center", fontsize=11, weight="bold")
            if name == "M4_bottle_stairs":
                for (y0, y1, h), lab in zip(STAIRS, ["front step: short bottles", "middle step", "top step: tallest bottles"]):
                    c = cats.setdefault(lab, palette[len(cats) % 20])
                    ax.add_patch(Rectangle((ox + 4, oy + y0 + 3), MOD_W - 8, y1 - y0 - 6, fc=c, alpha=.55))
                    ax.text(ox + MOD_W / 2, oy + (y0 + y1) / 2, f"{lab}\n({h:.0f} mm high)", ha="center", va="center", fontsize=8)
                continue
            if name.startswith("M5") or name.startswith("M6"):
                c = cats.setdefault("compact / jar (stands on its side)", palette[len(cats) % 20])
                for kind, lab, cx, cy, w, l in layouts[name]:
                    if kind == "side":
                        ax.add_patch(Rectangle((ox + cx - w / 2, oy + cy - l / 2), w, l, fc=c, ec="k", lw=.5))
                        ax.text(ox + cx, oy + cy, lab, rotation=90, ha="center", va="center", fontsize=6.5)
                    else:
                        ax.add_patch(Rectangle((ox + cx - w / 2, oy + cy - l / 2), w, l, fc=c, ec="k", lw=.5))
                        ax.text(ox + cx, oy + cy, lab, ha="center", va="center", fontsize=5.6, wrap=True)
                continue
            for shp, cx, cy, lab in layouts[name]:
                k, w, l = shp[:3]
                c = cats.setdefault(lab, palette[len(cats) % 20])
                if k == "r":
                    ax.add_patch(FancyBboxPatch((ox + cx - w / 2, oy + cy - l / 2), w, l,
                                                boxstyle=f"round,pad=0,rounding_size={min(8, w / 2 - .5, l / 2 - .5)}", fc=c, ec="k", lw=.5))
                else:
                    ax.add_patch(Circle((ox + cx, oy + cy), w / 2, fc=c, ec="k", lw=.5))
        ax.set_xlim(-5, SHELF_W + 5); ax.set_ylim(-8, SHELF_D + 22); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(title + "   (bottom edge = front of shelf)", fontsize=13)
    handles = [Rectangle((0, 0), 1, 1, fc=c) for c in cats.values()]
    fig.legend(handles, list(cats), loc="lower center", ncol=3, fontsize=9, frameon=False)
    fig.subplots_adjust(bottom=0.17, top=0.97, hspace=0.1)
    fig.savefig(path, dpi=110)
    plt.close(fig)


def build():
    mods, layouts, print_pose = {}, {}, {}
    for name, rows in BLOCKS.items():
        blk, layouts[name] = tiered_block(rows)
        mods[name] = add_sockets(blk)
    print_pose["M4_bottle_stairs"], mods["M4_bottle_stairs"] = bottle_stairs()
    m5, layouts["M5_thin_compacts"], _, f5 = compact_rack(THIN_RACK, side=THIN_SIDE)
    m6, layouts["M6_thick_compacts"], _, f6 = compact_rack(THICK_RACK, fit_t=FIT_T + 2)  # jars get extra room
    mods["M5_thin_compacts"] = add_sockets(m5, f5)
    mods["M6_thick_compacts"] = add_sockets(m6, f6)
    return mods, layouts, print_pose


if __name__ == "__main__":
    for old in OUT.glob("M*_*.*"):
        old.unlink()
    mods, layouts, print_pose = build()
    total = 0.0
    for name, m in mods.items():
        printed = print_pose.get(name, m)
        total += report(printed, MAT, infill=0.08, name=name)["est_filament_g"]
        export_3mf(OUT / f"{name}.3mf", [Part(name, printed, 1, settings={"sparse_infill_pattern": "lightning",
                                                                          "sparse_infill_density": "10%"})])
        export_stl(OUT / f"{name}.stl", printed)
        preview(OUT / f"{name}.png", m)
    n_feet = 4 * len(mods) + 4                # 4 per module + 4 spares
    cols_n = 6
    feet = union(*[foot().translate(((i % cols_n) * (FOOT_D + 6), (i // cols_n) * (FOOT_D + 6), 0)) for i in range(n_feet)])
    r = report(feet, MAT, infill=1.0, name=f"feet_x{n_feet}")
    total += r["est_filament_g"]
    export_3mf(OUT / "M0_feet.3mf", [Part(f"{n_feet} feet", feet, 1)])
    export_stl(OUT / "M0_feet.stl", feet)
    preview(OUT / "M0_feet.png", feet, elev=40)
    print(f"\nTOTAL ≈ {total:.0f} g PLA")

    # fit-test sampler: every stick slot size + a mini rack with every compact slot thickness
    sticks, _ = tiered_block([[(C(13), 1, ""), (C(17), 1, ""), (C(22), 1, ""), (C(24), 1, ""), (C(26), 1, ""), (C(28), 1, "")],
                              [(R(32, 24), 1, ""), (R(36, 20), 1, ""), (C(34), 1, "")],
                              [(R(46, 34), 1, ""), (R(29, 58), 1, "")]],
                             width=MOD_W, depth=140, base_h=14.0, step_h=0.0)   # low: fit test only
    widths = [13, 15, 18, 22, 32, 38]   # NARS/W7 · most powders · sun club · Glossier quad · TIRTIR · Morphe jar
    mini, _, mini_d, _ = compact_rack([[("", 40, t)] for t in widths], width=60, depth=200)
    sticks = add_sockets(sticks)   # test the foot press-fit too
    report(sticks, MAT, infill=0.08, name="00_sampler_sticks")
    report(mini, MAT, infill=0.08, name="00_sampler_compact_slots")
    print("  compact sampler slot thicknesses (front→back):", [t + FIT_T for t in widths])
    export_3mf(OUT / "00_fit_test_sampler.3mf", [Part("stick slots", sticks, 1),
                                                 Part("compact slots", mini.translate((MOD_W + 10, 0, 0)), 1),
                                                 Part("test feet", union(*[foot().translate((MOD_W + 90 + 20 * i, 20, 0))
                                                                           for i in range(4)]), 1)],
               separate_objects=True)
    preview(OUT / "00_fit_test_sampler.png", [sticks, mini.translate((MOD_W + 10, 0, 0))])

    shelf = lambda names: [mods[n].translate(((MOD_W + GAP) * i, MOD_D - mods[n].bounding_box()[4], 0))  # noqa: E731
                           for i, n in enumerate(names)]
    cols = ["#f9a8d4", "#fbcfe8", "#f472b6"]
    preview(OUT / "shelf1_preview.png", shelf(["M1_eyes_lips", "M2_cheeks_tubes", "M3_brushes_sponges_puffs"]), colors=cols, elev=35, azim=-75)
    preview(OUT / "shelf2_preview.png", shelf(["M4_bottle_stairs", "M5_thin_compacts", "M6_thick_compacts"]), colors=cols, elev=35, azim=-75)
    DEPTHS.update({n: mods[n].bounding_box()[4] for n in BLOCKS})
    spot_map(OUT / "spot_map.png", layouts)
