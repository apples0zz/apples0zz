"""Remove the engraved logo from the card holder's backplate.

The backplate is a 2 mm slab tilted 20° back. The logo is engraved 0.5-1.0 mm into its front
face. Rotate so that face points straight up, fill a slab from below the engraving up to the
face, but only over the logo area, rotate back, and union with the original. Nothing else changes.
Run: python3 models/card_holder/generate.py
"""
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude/skills/bambu-p1s/scripts"))
from p1s import *  # noqa: E402,F403
from manifold3d import Mesh  # noqa: E402

HERE = Path(__file__).resolve().parent
t = trimesh.load(HERE / "original.stl")
m = Manifold(Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))

# front face normal of the backplate (found by grouping face normals): (-0.94, 0, 0.342)
nf = np.array([-0.94, 0.0, 0.342]); nf /= np.linalg.norm(nf)
FRONT, GROOVE_BOTTOM = -2.0, -3.0           # nf·x of the face and of the deepest engraving

# rotation that turns nf into +Z (about the Y axis)
th = np.arctan2(-nf[0], nf[2])
Rm = np.array([[np.cos(th), 0, np.sin(th)], [0, 1, 0], [-np.sin(th), 0, np.cos(th)]])
assert np.allclose(Rm @ nf, [0, 0, 1], atol=1e-6)
A = np.eye(4); A[:3, :3] = Rm
Ainv = np.linalg.inv(A)
rot = m.transform(A[:3, :].tolist())

# logo area = where front-facing faces sit below the face plane (the engraving floors and walls)
n = t.face_normals; c = t.triangles_center
off = c @ nf
floor_ = (n @ nf > 0.999) & (off < FRONT - 0.2) & (off > GROOVE_BOTTOM - 0.2)   # engraving floors
wall_ = (np.abs(n @ nf) < 0.02) & (off < FRONT - 0.05) & (off > GROOVE_BOTTOM + 0.05)  # engraving side walls
groove = floor_   # floors alone outline the logo (side walls also match the plate edges)
pts = (Rm @ t.vertices[np.unique(t.faces[groove])].T).T
x0, y0 = pts[:, 0].min() - 1.0, pts[:, 1].min() - 1.0
x1, y1 = pts[:, 0].max() + 1.0, pts[:, 1].max() + 1.0
print(f"logo area on the plate: {x1 - x0:.1f} x {y1 - y0:.1f} mm")

zc = GROOVE_BOTTOM - 0.4                    # inside the plate, just below the engraving
section = rot.slice(zc) ^ CrossSection.square((x1 - x0, y1 - y0)).translate((x0, y0))
filler = extrude(section, FRONT - zc).translate((0, 0, zc))   # up to the face, never past it
fixed = (rot + filler).transform(Ainv[:3, :].tolist())

report(m, name="original", quiet=False)
report(fixed, name="no logo", quiet=False)
print(f"added {fixed.volume() - m.volume():.1f} mm³ (the engraving's volume)")
export_stl(HERE / "card_holder_no_logo.stl", fixed)
export_3mf(HERE / "card_holder_no_logo.3mf", [Part("card holder", fixed, 1)])
preview(HERE / "preview.png", fixed, elev=25, azim=120)
