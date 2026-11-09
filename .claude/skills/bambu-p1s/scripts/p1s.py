"""
p1s.py - parametric modeling toolkit for the Bambu Lab P1S + Bambu Studio.

Build solids with manifold3d (guaranteed watertight booleans), run print-
readiness checks tuned to the P1S, and export STL or a Bambu-Studio-friendly
multi-part / multi-color 3MF.

    import sys; sys.path.insert(0, ".claude/skills/bambu-p1s/scripts")
    from p1s import *

    body = rounded_box(60, 40, 30, r=4) - rounded_box(56, 36, 30, r=2).translate((2, 2, 2))
    report(body, "PLA")
    export_3mf("box.3mf", [Part("box", body, filament=1)])

All units are millimetres. +Z is up; the bed is Z=0.
Requires: pip install manifold3d trimesh numpy   (matplotlib optional for previews)
"""
from __future__ import annotations

import math
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from manifold3d import CrossSection, JoinType, Manifold

# --------------------------------------------------------------------------
# Printer + material constants
# --------------------------------------------------------------------------
BED_X, BED_Y, BED_Z = 256.0, 256.0, 256.0   # P1S build volume, mm
NOZZLE = 0.4                                  # stock hardened-steel nozzle
LINE_W = 0.42                                 # Bambu default outer wall line width @0.4
LAYER = 0.20                                  # "0.20mm Standard" profile
FIRST_LAYER = 0.20

# Fit clearances (per side, mm) that work on a tuned P1S with PLA/PETG at 0.2 layers.
CLEAR = {
    "press": 0.10,     # interference-ish, needs force / mallet
    "snug": 0.15,      # friction fit, stays put
    "slide": 0.25,     # lids, drawers, sliding parts
    "loose": 0.40,     # free rotation, print-in-place joints
    "print_in_place": 0.35,
}

# Densities g/cm^3 (Bambu filament datasheets, rounded)
DENSITY = {"PLA": 1.24, "PETG": 1.25, "ABS": 1.05, "ASA": 1.07, "TPU": 1.22,
           "PLA-CF": 1.22, "PETG-CF": 1.25, "PA6-CF": 1.17, "PC": 1.20}

SEG = 96  # default circle resolution - smooth enough that facets don't print


# --------------------------------------------------------------------------
# Primitives (all sit on Z=0, positioned from their min corner unless noted)
# --------------------------------------------------------------------------
def box(x, y, z, center=False) -> Manifold:
    return Manifold.cube((x, y, z), center)


def cyl(h, d, d2=None, seg=SEG, center=False) -> Manifold:
    """Cylinder/cone by DIAMETER, centred in XY, base on Z=0 (unless center)."""
    return Manifold.cylinder(h, d / 2, (d2 if d2 is not None else d) / 2, seg, center)


def rect2d(x, y, r=0.0) -> CrossSection:
    """Rectangle from (0,0) to (x,y) with optional corner radius r."""
    if r <= 0:
        return CrossSection.square((x, y))
    r = min(r, x / 2 - 1e-3, y / 2 - 1e-3)
    return CrossSection.square((x - 2 * r, y - 2 * r)).translate((r, r)).offset(r, JoinType.Round, circular_segments=SEG)


def circle2d(d, seg=SEG) -> CrossSection:
    return CrossSection.circle(d / 2, seg)


def poly2d(points) -> CrossSection:
    """Simple polygon from (x, y) points; either winding order works."""
    from manifold3d import FillRule
    return CrossSection([list(map(tuple, points))], FillRule.NonZero)


def extrude(cs: CrossSection, h, scale_top=(1.0, 1.0), twist=0.0, div=0) -> Manifold:
    return Manifold.extrude(cs, h, div, twist, scale_top)


def revolve(cs: CrossSection, seg=SEG, degrees=360.0) -> Manifold:
    """Revolve a 2D profile drawn in X(radius)/Y(height) around Z."""
    return Manifold.revolve(cs, seg, degrees)


def rounded_box(x, y, z, r=3.0, bottom_chamfer=0.4, top_chamfer=0.0) -> Manifold:
    """
    Box with vertical rounded corners (radius r). Adds a small bottom chamfer by
    default to cancel elephant's foot - cheaper and more printable than a bottom
    fillet. top_chamfer breaks the top edge with a 45-degree chamfer of that size.
    """
    parts = []
    zc = 0.0
    if bottom_chamfer > 0:
        c = bottom_chamfer
        parts.append(Manifold.batch_hull([
            extrude(rect2d(x - 2 * c, y - 2 * c, max(r - c, 0.01)).translate((c, c)), 0.01),
            extrude(rect2d(x, y, r), 0.01).translate((0, 0, c - 0.01)),
        ]))
        zc = c - 0.01
    tc = max(top_chamfer, 0.0)
    mid_h = z - zc - tc
    parts.append(extrude(rect2d(x, y, r), mid_h).translate((0, 0, zc)))
    if tc > 0:
        parts.append(Manifold.batch_hull([
            extrude(rect2d(x, y, r), 0.01).translate((0, 0, z - tc - 0.01)),
            extrude(rect2d(x - 2 * tc, y - 2 * tc, max(r - tc, 0.01)).translate((tc, tc)), 0.01).translate((0, 0, z - 0.01)),
        ]))
    return Manifold.batch_boolean(parts, _ADD)


def shell_box(x, y, z, wall=1.6, floor=1.2, r=3.0) -> Manifold:
    """Open-top container. Default wall = 4 lines @0.4, floor = 6 layers @0.2."""
    outer = rounded_box(x, y, z, r)
    inner = extrude(rect2d(x - 2 * wall, y - 2 * wall, max(r - wall, 0.5)), z).translate((wall, wall, floor))
    return outer - inner


def teardrop_hole(d, length, axis="x", seg=SEG) -> Manifold:
    """
    Horizontal hole that prints without support: circle + 45-degree pointed roof.
    Centred on origin, runs along `axis` ('x' or 'y'). Subtract it from a part.
    """
    r = d / 2
    tip = r * math.sqrt(2)
    cs = CrossSection.batch_hull([circle2d(d, seg), poly2d([(-0.001, tip - 0.002), (0.001, tip - 0.002), (0, tip)])])
    m = extrude(cs, length).translate((0, 0, -length / 2))   # profile in XY, along Z
    m = m.rotate((90, 0, 0))                                 # now along Y, point up +Z
    if axis == "x":
        m = m.rotate((0, 0, 90))
    return m


def counterbore(d_hole, d_head, head_depth, total_h) -> Manifold:
    """Vertical screw hole with counterbore from the top; subtract from a part whose top is at total_h."""
    return cyl(total_h + 2, d_hole).translate((0, 0, -1)) + cyl(head_depth + 1, d_head).translate((0, 0, total_h - head_depth))


def chamfer_edge_ring(d, c) -> Manifold:
    """Cone to subtract at the top of a hole for a c-mm lead-in chamfer."""
    return cyl(c, d, d + 2 * c)


from manifold3d import OpType  # noqa: E402

ADD, SUB, AND = OpType.Add, OpType.Subtract, OpType.Intersect
_ADD = ADD


def union(*ms) -> Manifold:
    return Manifold.batch_boolean(list(ms), _ADD)


def place_on_bed(m: Manifold, center=True) -> Manifold:
    """Drop the part so min Z = 0 and (optionally) centre it on the plate."""
    (x0, y0, z0, x1, y1, z1) = m.bounding_box()
    dx = BED_X / 2 - (x0 + x1) / 2 if center else 0
    dy = BED_Y / 2 - (y0 + y1) / 2 if center else 0
    return m.translate((dx, dy, -z0))


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------
def _tri(m: Manifold):
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3].astype(float)
    f = np.asarray(mesh.tri_verts).astype(np.int64)
    return v, f


def overhang_area(m: Manifold, max_angle=45.0, bed_tol=0.05):
    """
    Area (mm^2) of downward faces steeper than max_angle from vertical that are
    NOT resting on the bed. These need supports or redesign (chamfer at 45°,
    teardrop holes, or split the part). Bridges also show up here - short
    bridges (< ~25 mm on P1S) are fine without support.
    """
    v, f = _tri(m)
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    n = np.cross(b - a, c - a)
    area = np.linalg.norm(n, axis=1) / 2
    with np.errstate(invalid="ignore", divide="ignore"):
        nz = n[:, 2] / np.linalg.norm(n, axis=1)
    zmin = v[:, 2].min()
    on_bed = np.all(np.stack([a[:, 2], b[:, 2], c[:, 2]]) < zmin + bed_tol, axis=0)
    limit = -math.cos(math.radians(max_angle)) - 0.01   # strictly steeper than max_angle (45° chamfers pass)
    bad = (nz < limit) & ~on_bed
    return float(area[bad].sum()), int(bad.sum())


def estimate(m: Manifold, material="PLA", layer=0.20, walls=2, top_layers=5, bottom_layers=3,
             infill=0.15, flow_mm3_s=10.0) -> dict:
    """
    Slicer-style filament & time estimate. Slices the part every layer like a slicer does:
    per layer, perimeters = ring of `walls` x line width inside the outline; top/bottom skins =
    inner area not covered `top_layers` above / `bottom_layers` below; infill = the rest x infill
    (lightning ≈ 0.03-0.05 effective). Time = volume / average flow (P1S PLA ≈ 10 mm³/s,
    Sport ≈ 12) + ~1.5 s per layer. Rough (±25 %); Bambu Studio's slice is the real number.
    """
    z0, z1 = m.bounding_box()[2], m.bounding_box()[5]
    zs = np.arange(z0 + layer / 2, z1, layer)
    outer = [m.slice(float(z)) for z in zs]
    inner = [c.offset(-walls * LINE_W, JoinType.Miter) for c in outer]
    empty = CrossSection()
    vol = 0.0
    for i, (o, n) in enumerate(zip(outer, inner)):
        above = inner[i + top_layers] if i + top_layers < len(inner) else empty
        below = inner[i - bottom_layers] if i - bottom_layers >= 0 else empty
        skin = (n - above) + (n - below)
        a_in = n.area()
        a_skin = min(skin.area(), a_in)
        vol += ((o.area() - a_in) + a_skin + (a_in - a_skin) * infill) * layer
    secs = vol / flow_mm3_s + len(zs) * 1.5
    return {"grams": round(vol / 1000 * DENSITY.get(material, 1.24), 1), "hours": round(secs / 3600, 2)}


def report(m: Manifold, material="PLA", infill=0.15, walls=2, name="part", quiet=False, sub_part=False) -> dict:
    """Print-readiness report: manifoldness, bed fit, mass estimate, overhangs.
    sub_part=True for a part of a multi-part object (e.g. a colour inlay) that legitimately floats above Z=0."""
    x0, y0, z0, x1, y1, z1 = m.bounding_box()
    size = (x1 - x0, y1 - y0, z1 - z0)
    vol = m.volume()                     # mm^3
    area = m.surface_area()
    # mass estimate: perimeter shell (walls*line_w) + top/bottom ~ approximated via
    # surface area * shell thickness, plus infill fraction of the remaining core.
    shell_t = max(walls * LINE_W, 0.8)
    shell_v = min(vol, area * shell_t * 0.5)   # 0.5: area counts both sides of thin features
    core_v = max(vol - shell_v, 0)
    printed_v = shell_v + core_v * infill
    grams = printed_v / 1000 * DENSITY.get(material, 1.24)
    ov_area, ov_n = overhang_area(m)
    comps = m.decompose()
    pieces = sum(1 for c in comps if c.volume() > 0)      # solid bodies
    voids = sum(1 for c in comps if c.volume() < 0)       # sealed internal cavities (e.g. under bridged floors)
    fits = size[0] <= BED_X and size[1] <= BED_Y and size[2] <= BED_Z
    r = {
        "name": name,
        "status": str(m.status()),
        "watertight": m.status().name == "NoError" and not m.is_empty(),
        "genus": m.genus(),
        "separate_bodies": pieces,
        "sealed_voids": voids,
        "size_mm": tuple(round(s, 2) for s in size),
        "fits_p1s": fits,
        "on_bed": abs(z0) < 1e-3,
        "volume_cm3": round(vol / 1000, 2),
        "est_filament_g": round(grams, 1),
        "overhang_mm2_gt45": round(ov_area, 1),
    }
    warnings = []
    if not fits:
        warnings.append(f"does not fit 256x256x256 - split it or rotate; size={r['size_mm']}")
    if not r["on_bed"] and not sub_part:
        warnings.append(f"min Z is {z0:.3f}, call place_on_bed()")
    if ov_area > 5:
        warnings.append(f"{ov_area:.0f} mm² of >45° overhang off the bed - add 45° chamfers, teardrops, or enable supports (tree, auto)")
    if pieces > 1:
        warnings.append(f"{pieces} disconnected bodies (fine for print-in-place / multiple parts, otherwise check booleans)")
    if size[2] > 4 * min(size[0], size[1]) and size[2] > 60:
        warnings.append("tall & thin - add a brim (Others > Brim type: outer, 5mm) or lay it flat")
    if min(size[0], size[1]) > 150 and material in ("ABS", "ASA", "PC", "PA6-CF"):
        warnings.append("large footprint in a warpy material - enclosure closed, bed 100°C, brim, round corners")
    r["warnings"] = warnings
    if not quiet:
        print(f"── {name} ({material}) " + "─" * max(0, 40 - len(name)))
        for k, v in r.items():
            if k not in ("warnings", "name"):
                print(f"  {k:20s} {v}")
        for w in warnings:
            print(f"  ⚠ {w}")
        if not warnings:
            print("  ✓ ready to slice")
    return r


def gap(a: Manifold, b: Manifold, search=2.0) -> float:
    """Minimum distance between two parts (verify fit clearances / print-in-place gaps)."""
    return a.min_gap(b, search)


# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------
@dataclass
class Part:
    name: str
    solid: Manifold
    filament: int = 1          # AMS slot / filament index in Bambu Studio (1-16)
    subtype: str = "normal_part"   # normal_part | modifier_part | negative_part | support_enforcer | support_blocker
    settings: dict = field(default_factory=dict)  # per-part overrides e.g. {"wall_loops": "4", "sparse_infill_density": "40%"}


def export_stl(path, m: Manifold):
    import trimesh
    v, f = _tri(m)
    trimesh.Trimesh(v, f, process=False).export(str(path))
    return path


def export_3mf(path, parts: list[Part], object_name: str | None = None, center=True, separate_objects=False,
               bambu_config=False):
    """
    Write a plain (core-spec) 3MF that Bambu Studio opens cleanly.

    bambu_config=False (default): geometry only. A hand-written Bambu
    Metadata/model_settings.config makes Bambu Studio warn "The 3mf file has invalid
    config, load geometry data only" (verified on a real install), so per-part
    filament/settings are NOT embedded - give them in the slicer recipe instead.
    bambu_config=True writes that config anyway (experimental; expect the warning).

    Default: all parts become ONE object with multiple parts (like Bambu's
    "Add Part"), keeping their relative positions - this is what you want for
    multi-colour prints (base + inlay text, etc). Parts with subtype
    'modifier_part' carry per-region settings instead of geometry.

    separate_objects=True: each Part is its own object (independently movable,
    arrangeable, and sliced as separate items on the plate).
    """
    path = Path(path)
    solids = [p.solid for p in parts if p.subtype == "normal_part"]
    bb = union(*solids).bounding_box() if solids else parts[0].solid.bounding_box()
    dx = BED_X / 2 - (bb[0] + bb[3]) / 2 if center else 0
    dy = BED_Y / 2 - (bb[1] + bb[4]) / 2 if center else 0
    dz = -bb[2]

    ns = 'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"'
    objs, build, cfg = [], [], []

    def mesh_xml(m):
        v, f = _tri(m)
        vs = "\n".join(f'     <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in v)
        ts = "\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in f)
        return f"   <mesh>\n    <vertices>\n{vs}\n    </vertices>\n    <triangles>\n{ts}\n    </triangles>\n   </mesh>"

    def part_cfg(pid, p):
        extra = "".join(f'\n      <metadata key="{escape(k)}" value="{escape(str(v))}"/>' for k, v in p.settings.items())
        return (f'    <part id="{pid}" subtype="{p.subtype}">\n'
                f'      <metadata key="name" value="{escape(p.name)}"/>\n'
                f'      <metadata key="extruder" value="{p.filament}"/>{extra}\n'
                f'    </part>')

    next_id = 1
    xf = f"1 0 0 0 1 0 0 0 1 {dx:.4f} {dy:.4f} {dz:.4f}"
    if separate_objects:
        for p in parts:
            oid = next_id; next_id += 1
            objs.append(f'  <object id="{oid}" type="model" name="{escape(p.name)}">\n{mesh_xml(p.solid)}\n  </object>')
            build.append(f'  <item objectid="{oid}" transform="{xf}" printable="1"/>')
            cfg.append(f'  <object id="{oid}">\n    <metadata key="name" value="{escape(p.name)}"/>\n'
                       f'    <metadata key="extruder" value="{p.filament}"/>\n{part_cfg(oid, p)}\n  </object>')
    else:
        comp_ids = []
        for p in parts:
            oid = next_id; next_id += 1
            comp_ids.append((oid, p))
            objs.append(f'  <object id="{oid}" type="model" name="{escape(p.name)}">\n{mesh_xml(p.solid)}\n  </object>')
        parent = next_id
        comps = "\n".join(f'    <component objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>' for oid, _ in comp_ids)
        oname = object_name or parts[0].name
        objs.append(f'  <object id="{parent}" type="model" name="{escape(oname)}">\n   <components>\n{comps}\n   </components>\n  </object>')
        build.append(f'  <item objectid="{parent}" transform="{xf}" printable="1"/>')
        parts_cfg = "\n".join(part_cfg(oid, p) for oid, p in comp_ids)
        cfg.append(f'  <object id="{parent}">\n    <metadata key="name" value="{escape(oname)}"/>\n'
                   f'    <metadata key="extruder" value="{parts[0].filament}"/>\n{parts_cfg}\n  </object>')

    model = (f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {ns}>\n'
             f' <metadata name="Application">p1s.py</metadata>\n <resources>\n' + "\n".join(objs) +
             '\n </resources>\n <build>\n' + "\n".join(build) + '\n </build>\n</model>\n')
    config = '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + "\n".join(cfg) + '\n</config>\n'
    content_types = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
                     ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
                     ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
                     ' <Default Extension="config" ContentType="text/xml"/>\n</Types>\n')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            ' <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
            '</Relationships>\n')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)
        if bambu_config:
            z.writestr("Metadata/model_settings.config", config)
    return path


def preview(path, parts, colors=None, elev=28, azim=-55, size=900):
    """
    Render a shaded PNG of one or more Manifolds / Parts with a small numpy
    z-buffer (no OpenGL needed). Use it to eyeball every model before export.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    items = [p.solid if isinstance(p, Part) else p for p in (parts if isinstance(parts, (list, tuple)) else [parts])]
    colors = colors or ["#3b82f6", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#6b7280"]
    e, a = math.radians(elev), math.radians(azim)
    # camera basis: right, up, forward(view dir into screen)
    fwd = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])  # points to camera
    right = np.cross([0, 0, 1], fwd); right /= np.linalg.norm(right)
    up = np.cross(fwd, right)
    light = 0.6 * fwd + 0.5 * up + 0.3 * right; light /= np.linalg.norm(light)

    meshes = [_tri(m) for m in items]
    allv = np.vstack([v for v, _ in meshes])
    ctr = (allv.min(0) + allv.max(0)) / 2
    proj = lambda v: np.stack([(v - ctr) @ right, (v - ctr) @ up, (v - ctr) @ fwd], 1)  # noqa: E731
    pv = proj(allv)
    span = max(np.ptp(pv[:, 0]), np.ptp(pv[:, 1])) * 1.08
    sc = size / span
    img = np.ones((size, size, 3))
    zb = np.full((size, size), -np.inf)
    for i, (v, f) in enumerate(meshes):
        P = proj(v)
        X = P[:, 0] * sc + size / 2
        Y = size / 2 - P[:, 1] * sc
        Z = P[:, 2]
        base = np.array(matplotlib.colors.to_rgb(colors[i % len(colors)]))
        tri = v[f]
        nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
        shade = 0.30 + 0.70 * np.clip(nrm @ light, 0, 1)
        facing = nrm @ fwd > 0
        for k in np.nonzero(facing)[0]:
            ia, ib, ic = f[k]
            xs, ys = np.array([X[ia], X[ib], X[ic]]), np.array([Y[ia], Y[ib], Y[ic]])
            x0, x1 = max(int(xs.min()), 0), min(int(xs.max()) + 1, size - 1)
            y0, y1 = max(int(ys.min()), 0), min(int(ys.max()) + 1, size - 1)
            if x1 < x0 or y1 < y0:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            d = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
            if abs(d) < 1e-12:
                continue
            w0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d
            w1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d
            w2 = 1 - w0 - w1
            inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not inside.any():
                continue
            z = w0 * Z[ia] + w1 * Z[ib] + w2 * Z[ic]
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            win = inside & (z > sub)
            sub[win] = z[win]
            img[y0:y1 + 1, x0:x1 + 1][win] = base * shade[k]
    plt.imsave(path, np.clip(img, 0, 1))
    return path


__all__ = [n for n in dir() if not n.startswith("_")]
