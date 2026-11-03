"""Video 2 (Nov 2026): pack opening on the playmat, top-down camera. Edit plan in progress.
All times are SOURCE times. Style rules: CLAUDE.md."""
PROJECT = {
    "title": "",
    "sources": {
        "main": {"drive": "154eqNaLYWHcYx7hlcUJPaVkXk_mAaadZ", "file": "main.mov", "zoom_center": (0.5, 0.45)},
    },
    "timeline": [
        # ("intro", 0.0, 20.0),
        # ("main", 0.0, 900.0),
    ],
    "main_section_starts": 0,        # timeline piece where the pack-opening (lofi hip hop) music starts
    "protect": {},                   # {"main": [(from, to), ...]}  no jump cuts inside (reveals, hits lineup)
    "speakers": {"solo": {}},        # {"extra1": "Sophie"} for clips where only one of us talks
    "music": {"intro": [480, 135], "main": [738, 282, 970, 132, 400]},   # Mixkit ids, see editor/music.py
    "cards": {},                     # "key": dict(set="sv1", num=248, name="IRON TREADS ex", rarity="SPECIAL ILLUSTRATION RARE  248/198", big=True)
    "card_pops": [],                 # (source, t, seconds, "key")
    "montage": None,                 # (source, t, seconds_each, ["key", ...])  "THE HITS" run
    "images": [],                    # (source, from, to, "file.jpg")  e.g. "chat, insert a picture"
    "captions": [],                  # (source, from, to, "HYPE TEXT!")  sticker captions only, never reaction pills
    "tags": [],                      # (source, from, to, "EDITOR SOPHIE  -  CONTEXT TIME")
    "big_zooms": [],                 # (source, from, to)
    "big_moments": [],               # (source, t[, "ding"])  thump/ding + sparkle burst + music drop
    "extra_bursts": [],              # (source, t)
    "extra_sfx": [],                 # (source, t, "sparkle"|"thump"|"riser"|"ding"|"softwhoosh"|"bubble_hi", gain)
    "bleeps": [],                    # (source, from, to)
    "vocab": "",                     # extra words to help the transcription (card names in this set)
    "shorts": {},                    # see the example project
}
