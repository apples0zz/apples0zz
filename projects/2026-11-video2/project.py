"""Video 2 (Nov 2026): ripping Delta Reign early (12 packs each), top-down playmat camera, no Editor Sophie cut-in.
All times are SOURCE times (seconds into main.mov). Style rules: CLAUDE.md.

Hits found in the footage/transcript:
  Tate & Liza's Training full art (#130, ~7:29), Electivire IR (#108, Aiden's chase, ~10:12),
  Azurill IR (#115, Sophie's "that's the one I wanted", ~12:56), exes: Wishiwashi, Heat Rotom, Mega Malamar,
  Meowscarada (Sophie, "queen of the exes"). Chases named at the start: Mega Rayquaza ex gold/SIR,
  Electivire IR, Groudon IR, Eevee IR.
Card images: Delta Reign isn't on pokemontcg.io yet, so scans come from serebii.net (see "image" paths).
"""
S = "https://www.serebii.net/card/deltareign/{}.jpg"
CARD_DIR = "../../work/2026-11-video2/cards/serebii/{}.jpg"   # downloaded by fetch_cards() below

def card(num, name, rarity, big=False):
    return dict(image=CARD_DIR.format(num), url=S.format(num), name=name, rarity=f"{rarity}  #{num}", big=big)

PROJECT = {
    "title": "Ripping Delta Reign EARLY!",
    "sources": {
        "main": {"drive": "154eqNaLYWHcYx7hlcUJPaVkXk_mAaadZ", "file": "main.mov", "zoom_center": (0.42, 0.45)},
    },
    "timeline": [
        ("main", 0.0, 1117.3),   # ends on "absolutely cooked" -- the thumbnail-posing bit after that is cut
    ],
    "main_section_starts": 0,
    "protect": {"main": [(26, 49), (445, 455), (598, 628), (764, 792), (1028, 1050)]},
    "speakers": {"solo": {}},
    "music": {"intro": [], "main": [738, 282, 970, 132, 400, 250]},
    "vocab": "Delta Reign, Electivire, Groudon, Eevee, Azurill, Mega Rayquaza, Wishiwashi, Heat Rotom, Meowscarada, Mega Malamar, Tate & Liza's Training, Kecleon, Enamorus, Greninja",
    "subtitle_fixes": {"selectifier": "Electivire", "Selectifier": "Electivire", "mousecardia": "Meowscarada",
                       "Mousecardia": "Meowscarada", "mega recrozza": "Mega Rayquaza", "mega rick was a": "Mega Rayquaza",
                       "tates and lisa's": "Tate & Liza's", "enamorous": "Enamorus", "grandinja": "Greninja",
                       "gueratina": "Giratina", "karatina": "Giratina", "kayogre": "Kyogre", "delta rain": "Delta Reign"},
    "cards": {
        "rayq_gold": card(141, "MEGA RAYQUAZA ex", "MEGA HYPER RARE"),
        "rayq_sir":  card(138, "MEGA RAYQUAZA ex", "SPECIAL ILLUSTRATION RARE"),
        "electivire": card(108, "ELECTIVIRE", "ILLUSTRATION RARE", big=True),
        "groudon":   card(111, "GROUDON", "ILLUSTRATION RARE"),
        "eevee":     card(114, "EEVEE", "ILLUSTRATION RARE"),
        "tateliza":  card(130, "TATE & LIZA'S TRAINING", "FULL ART", big=True),
        "azurill":   card(115, "AZURILL", "ILLUSTRATION RARE", big=True),
        "wishiwashi": card(29, "WISHIWASHI ex", "DOUBLE RARE"),
        "heatrotom": card(23, "HEAT ROTOM ex", "DOUBLE RARE"),
        "malamar":   card(69, "MEGA MALAMAR ex", "DOUBLE RARE"),
        "meowscarada": card(14, "MEOWSCARADA ex", "DOUBLE RARE"),
    },
    "card_pops": [
        # "our chases for today... we're going to put them up on the screen"
        ("main", 27.6, 1.8, "rayq_gold"), ("main", 29.5, 1.8, "rayq_sir"), ("main", 32.7, 1.6, "electivire"),
        ("main", 34.4, 1.9, "groudon"), ("main", 42.8, 5.2, "eevee"),
        # the pulls
        ("main", 449.0, 3.6, "tateliza"), ("main", 611.8, 4.0, "electivire"), ("main", 776.4, 3.8, "azurill"),
    ],
    "montage": ("main", 1036.0, 1.6, ["wishiwashi", "heatrotom", "malamar", "meowscarada"]),  # "I pulled five exes"
    "images": [],
    "captions": [
        ("main", 20.0, 36.5, "TODAY'S CHASES"),
        ("main", 84.5, 88.5, "LET'S RIP!"),
        ("main", 155.8, 159.0, "FIRST ex!"),
        ("main", 448.8, 453.0, "FIRST FULL ART!"),
        ("main", 611.8, 618.0, "ELECTIVIRE IR!"),
        ("main", 624.3, 627.2, "LAST PACK MAGIC!"),
        ("main", 776.4, 781.0, "AZURILL IR!"),
        ("main", 1034.0, 1043.0, "THE HITS"),
        ("main", 1097.9, 1117.3, "SUBSCRIBE FOR MORE RIPS!"),
    ],
    "tags": [],
    "big_zooms": [("main", 448.5, 453.5), ("main", 611.0, 617.0), ("main", 775.8, 781.5)],
    "big_moments": [("main", 449.0), ("main", 611.8), ("main", 776.4)],
    "extra_bursts": [("main", 1034.0)],
    "extra_sfx": [("main", 1034.0, "riser", 0.25), ("main", 20.0, "sparkle", 0.25)],
    "bleeps": [("main", 18.98, 19.34), ("main", 748.66, 748.88)],
    "shorts": {
        "short1_electivire": {
            "title": "HIS CHASE CARD?!", "music": 282,
            "parts": [dict(src="main", **{"from": 30.4, "to": 36.7}, no_cuts=True),
                      dict(src="main", **{"from": 598.0, "to": 628.0}, x=0.42)],
            "captions": [("main", 611.8, 618.0, "ELECTIVIRE IR!"), ("main", 624.3, 627.6, "LAST PACK MAGIC!")],
            "cards": [("main", 611.8, 4.5, "electivire")],
            "zooms": [("main", 611.0, 617.0)],
            "big_moments": [("main", 611.8)],
        },
        "short2_hits": {
            "title": "DELTA REIGN HITS!", "music": 738,
            "parts": [dict(src="main", **{"from": 440.5, "to": 455.0}, x=0.35),
                      dict(src="main", **{"from": 764.0, "to": 791.0}, x=0.30)],
            "captions": [("main", 448.8, 453.0, "FIRST FULL ART!"), ("main", 776.4, 781.0, "AZURILL IR!")],
            "cards": [("main", 449.0, 3.8, "tateliza"), ("main", 776.4, 4.2, "azurill")],
            "zooms": [("main", 448.5, 453.5), ("main", 775.8, 781.5)],
            "big_moments": [("main", 449.0), ("main", 776.4)],
        },
    },
}


def fetch_cards():
    import os, subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    for c in PROJECT["cards"].values():
        path = os.path.normpath(os.path.join(here, c["image"]))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            subprocess.run(["curl", "-sSL", "-m", "60", "-o", path, c["url"]], check=True)
