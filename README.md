# apples0zz — Bambu P1S models

Parametric, print-checked models for a Bambu Lab P1S. Open the `.3mf` files in Bambu Studio:
parts, AMS filament slots and per-part settings come pre-assigned.

| Model | Files | Notes |
|---|---|---|
| Box with slide-on lid | `models/box_with_lid/` | 80×60×40 mm, 0.25 mm/side lid fit, no supports |
| Two-colour hex coaster | `models/two_color_coaster/` | AMS: base = slot 1, inlay = slot 2 (top 3 layers only) |
| Phone stand | `models/phone_stand/` | Prints on its side, no supports, cable pass-through |
| **Bathroom makeup organizer** | `models/makeup_organizer/` | 6 modules for two 8.75"×22.5" shelves: stick slot blocks and side-standing compact racks. See its README |

Regenerate or customise (e.g. a 120×80×50 box):

```bash
pip install -r .claude/skills/bambu-p1s/requirements.txt
python3 .claude/skills/bambu-p1s/examples/box_with_lid.py 120 80 50
```

The design knowledge and toolkit live in `.claude/skills/bambu-p1s/`.
