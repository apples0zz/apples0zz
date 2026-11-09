# apples0zz

3D-printing workspace for a **Bambu Lab P1S** sliced in **Bambu Studio**.

- For any request to design, model, fix or print something, use the `bambu-p1s` skill
  (`.claude/skills/bambu-p1s/SKILL.md`). It has the printer specs, design rules, tolerances,
  materials, slicer settings, and the `p1s.py` modeling toolkit.
- Install the toolkit's dependencies with `pip install -r .claude/skills/bambu-p1s/requirements.txt`.
- Each model lives in `models/<name>/` with its generator script, `.3mf` (open this in
  Bambu Studio), `.stl` and `preview.png`.
- Every model must pass `report()` (watertight, fits the bed, sits on the bed, no unplanned
  overhangs) before it is handed over.
