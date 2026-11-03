"""Video 1 (Nov 2026): ripping a possibly-resealed Scarlet & Violet base booster box.
Reference for how a finished edit is set up. All times are SOURCE times (seconds into that clip).
Note: the published version also had light "reaction" caption pills -- those are banned now and left out here.
"""
PROJECT = {
    "title": "Is our Scarlet & Violet booster box RESEALED?",
    "sources": {
        # key: Google Drive file id, local file name, where punch-in zooms aim (x, y as fractions of the frame)
        "intro":  {"drive": "1iQqTsuIX0QGy6vbkC-zazzzUSOYaCyRg", "file": "intro.mov",  "zoom_center": (0.5, 0.42)},
        "extra1": {"drive": "1KXT8qg41F1VazxzgGX-hJqRzZCVJvUI5", "file": "extra1.mov", "zoom_center": (0.5, 0.40)},
        "extra2": {"drive": "1I36llYrruJOMhCttA5_ViR9y7wKUUTbG", "file": "extra2.mov", "zoom_center": (0.5, 0.45)},
        "full":   {"drive": "1lKCekYZ8Hv3pVe5M7yCdGyXP9Z4uM8v9", "file": "full.mov",   "zoom_center": (0.62, 0.38)},
    },
    # order of the edit: (source, from, to[, extra no-cut windows])
    "timeline": [
        ("intro", 0.0, 14.35),    # "...might have been a resealed booster box."
        ("extra1", 0.0, 30.2),    # Editor Sophie backstory, up to "complete Pokedex binder"
        ("extra2", 2.0, 43.6),    # pack stash + Pokedex binder tour
        ("extra1", 30.3, 73.0),   # backstory continued ("zero hits", convincer/okayer)
        ("intro", 15.15, 22.45),  # "So instead of slowly opening it... let's get to it"
        ("full", 0.0, 891.6),     # the rip
    ],
    "main_section_starts": 5,      # timeline piece where the pack-opening music starts
    # never jump-cut inside these windows (card reveals, the hits lineup, price check)
    "protect": {"full": [(141, 151), (266, 283), (311, 331), (578, 590), (664, 694), (832, 842), (869, 880)]},
    "speakers": {"solo": {"extra1": "Sophie", "extra2": "Sophie"}},
    "music": {"intro": [480, 135], "main": [738, 282, 970, 132, 400]},
    "cards": {
        "gold":     dict(set="sv1", num=258, name="GOLD FIGHTING ENERGY", rarity="HYPER RARE  258/198", big=True),
        "treads":   dict(set="sv1", num=248, name="IRON TREADS ex", rarity="SPECIAL ILLUSTRATION RARE  248/198", big=True),
        "gard":     dict(set="sv1", num=86,  name="GARDEVOIR ex", rarity="DOUBLE RARE  086/198", big=True),
        "ralts":    dict(set="sv1", num=211, name="RALTS", rarity="ILLUSTRATION RARE  211/198"),
        "wiglett":  dict(set="sv1", num=206, name="WIGLETT", rarity="ILLUSTRATION RARE  206/198"),
        "dondozo":  dict(set="sv1", num=207, name="DONDOZO", rarity="ILLUSTRATION RARE  207/198"),
        "arcanine": dict(set="sv1", num=224, name="ARCANINE ex", rarity="ULTRA RARE  224/198"),
        "miraidon": dict(set="sv1", num=227, name="MIRAIDON ex", rarity="ULTRA RARE  227/198"),
    },
    "card_pops": [("full", 144.6, 3.2, "gold"), ("full", 269.3, 3.6, "treads"), ("full", 584.5, 3.2, "gard")],
    "montage": ("full", 668.0, 1.6, ["ralts", "wiglett", "dondozo", "arcanine", "miraidon"]),  # "THE HITS" run
    "images": [("full", 109.6, 116.0, "aura_binder.jpg")],   # "chat, insert a picture of the aura binder"
    # big sticker captions (hype only). (source, from, to, text)
    "captions": [
        ("intro", 9.3, 14.3, "RESEALED BOX?!"),
        ("extra2", 2.1, 9.5, "THE PACK STASH"),
        ("extra1", 30.3, 41.0, "ZERO HITS"),
        ("intro", 20.4, 22.45, "LET'S GET TO IT!"),
        ("full", 103.6, 109.5, "AURA BINDER CARD!"),
        ("full", 109.6, 116.0, "AIDEN'S AURA BINDER"),
        ("full", 144.6, 147.8, "OUR FIRST GOLD CARD!"),
        ("full", 269.3, 276.5, "IRON TREADS SIR!"),
        ("full", 313.0, 319.5, "OH MY GOSH!!"),
        ("full", 584.5, 587.6, "GARDEVOIR ex!"),
        ("full", 592.6, 595.5, "LAST PACK!"),
        ("full", 666.0, 676.0, "THE HITS"),
        ("full", 788.1, 792.8, "$15?!"),
        ("full", 834.0, 836.6, "$33 PULL?!"),
        ("full", 871.9, 878.0, "OVER $100 TOTAL!"),
        ("full", 884.0, 891.6, "SUBSCRIBE FOR MORE RIPS!"),
    ],
    "tags": [("extra1", 0.2, 5.4, "EDITOR SOPHIE  -  CONTEXT TIME")],
    "big_zooms": [("full", 143.4, 148.0), ("full", 269.0, 276.5), ("full", 312.8, 322.0), ("full", 579.4, 587.4)],
    # big pulls: sparkle burst + music drops out + sound ("thump" default, "ding" for gold)
    "big_moments": [("full", 144.6, "ding"), ("full", 269.3), ("full", 313.0), ("full", 584.5)],
    "extra_bursts": [("full", 666.0), ("full", 871.9)],
    "extra_sfx": [("full", 313.0, "sparkle", 0.25), ("full", 666.0, "riser", 0.25), ("full", 871.9, "sparkle", 0.3),
                  ("full", 834.0, "thump", 0.5)],
    "bleeps": [("full", 407.75, 408.08)],
    "shorts": {
        "short1_resealed": {
            "title": "RESEALED BOOSTER BOX?!", "music": 282,
            "parts": [dict(src="intro", **{"from": 9.2, "to": 14.35}, layout="wide"),
                      dict(src="full", **{"from": 8.8, "to": 16.6}),
                      dict(src="full", **{"from": 139.6, "to": 151.0}, no_cuts=True),
                      dict(src="full", **{"from": 152.2, "to": 156.2}, no_cuts=True)],
            "captions": [("full", 144.6, 151.0, "FIRST GOLD CARD!")],
            "cards": [("full", 144.6, 4.0, "gold")],
            "zooms": [("full", 143.4, 148.0)],
            "big_moments": [("full", 144.6, "ding")],
        },
        "short2_sir": {
            "title": "QUICK OPEN = SIR?!", "music": 738,
            "parts": [dict(src="full", **{"from": 262.4, "to": 283.7}, no_cuts=True),
                      dict(src="full", **{"from": 833.2, "to": 840.3}, no_cuts=True, x=0.40),
                      dict(src="full", **{"from": 871.8, "to": 877.2}, no_cuts=True, x=0.66)],
            "captions": [("full", 269.1, 277.5, "IRON TREADS SIR!"), ("full", 833.3, 836.6, "$33 PULL?!"),
                         ("full", 836.7, 840.3, "$4 FOR AN SIR??"), ("full", 871.9, 877.2, "OVER $100 TOTAL!")],
            "cards": [("full", 269.3, 5.0, "treads")],
            "zooms": [("full", 269.0, 276.5)],
            "big_moments": [("full", 269.3)],
        },
    },
}
