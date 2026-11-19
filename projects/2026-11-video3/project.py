"""Video 3 (Nov 2026): 5 clips from Drive folder 1YzBWPUGxdue6nSZJU-b63J4MM5dX7Cty (IMG_6244-6250). Edit plan in progress.
All times are SOURCE times. Style rules: CLAUDE.md."""
PROJECT = {
    "title": "",
    "sources": {
        "c6244": {"drive": "1Uqaxz4qfq2psm7Oa2AWeIY4yo2P5Fu_2", "file": "IMG_6244.mov", "zoom_center": (0.5, 0.45)},
        "c6245": {"drive": "1JMFyya0YLt98ITN56_XfloElbu-aEJga", "file": "IMG_6245.mov", "zoom_center": (0.5, 0.45)},
        "c6246": {"drive": "1DmU6dJKAAxbpa2_Okr8mqQWZg8uk90P9", "file": "IMG_6246.mov", "zoom_center": (0.5, 0.45)},
        "c6248": {"drive": "1mL1ngzGVIpW04JqsYjbF1oIKYHgXxaM6", "file": "IMG_6248.mov", "zoom_center": (0.5, 0.45), "ignore_rotation": True},
        "c6250": {"drive": "1MXqX7prNvLjg64nhDN8IlG8lg_6UYUqX", "file": "IMG_6250.mov", "zoom_center": (0.5, 0.45), "ignore_rotation": True},
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
