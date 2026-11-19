"""Video 3 (Nov 2026): two 30th Celebration Ultra-Premium Collections (Day / Espeon and Night / Umbreon) + Delta Reign
promos, 60 packs as a "who gets the better box" battle, Classic Collection war and trades. BIG energy edit.
Clips from Drive folder 1YzBWPUGxdue6nSZJU-b63J4MM5dX7Cty. All times are SOURCE times. Style rules: CLAUDE.md.

Top hits: Pikachu ex SIR #150 + classic Lugia in one pack (c6250 ~3:02, "what a double opening", ~$130),
Sylveon ex SIR #153, Gengar Prime (classic), Mew ex SIR #152, Greninja BREAK (classic), Articuno/Zapdos/Moltres IRs.
Card images: api.pokemontcg.io data, scans hosted on images.scrydex.com.
"""
IMG = "https://images.scrydex.com/pokemon/{}-{}/large"
DIR = "../../work/2026-11-video3/cards/{}_{}.png"

def card(set_id, num, name, rarity, big=False):
    label = f"{rarity}  {num}/128" if set_id == "me55" else f"CLASSIC COLLECTION  {rarity}"
    return dict(image=DIR.format(set_id, num), url=IMG.format(set_id, num), name=name, rarity=label, big=big)

PROJECT = {
    "title": "Opening TWO 30th Celebration Ultra-Premium Collections!",
    "sources": {
        "c6244": {"drive": "1Uqaxz4qfq2psm7Oa2AWeIY4yo2P5Fu_2", "file": "IMG_6244.mov", "zoom_center": (0.5, 0.45)},
        "c6245": {"drive": "1JMFyya0YLt98ITN56_XfloElbu-aEJga", "file": "IMG_6245.mov", "zoom_center": (0.5, 0.55), "flip": True},
        "c6246": {"drive": "1DmU6dJKAAxbpa2_Okr8mqQWZg8uk90P9", "file": "IMG_6246.mov", "zoom_center": (0.5, 0.55), "flip": True},
        "c6248": {"drive": "1mL1ngzGVIpW04JqsYjbF1oIKYHgXxaM6", "file": "IMG_6248.mov", "zoom_center": (0.5, 0.6), "ignore_rotation": True, "flip": True},
        "c6250": {"drive": "1MXqX7prNvLjg64nhDN8IlG8lg_6UYUqX", "file": "IMG_6250.mov", "zoom_center": (0.5, 0.6), "ignore_rotation": True, "flip": True},
    },
    "timeline": [
        ("c6250", 182.2, 199.5, {"teaser": "WAIT FOR IT..."}),   # cold open: the double opening
        ("c6244", 4.5, 30.0),                    # what's in the box? Delta Reign Pokemon Center ETB promos
        ("c6244", 30.0, 50.0, {"speed": 2}),
        ("c6244", 50.0, 83.0),                   # the 30th Celebration UPCs, day vs night
        ("c6245", 6.0, 36.0, {"speed": 2}),      # top-down: unboxing
        ("c6245", 36.0, 57.0),                   # sleeves, Kyogre promo
        ("c6245", 57.0, 90.0, {"speed": 2}),     # sleeving the boosters
        ("c6245", 90.0, 131.5),                  # the Pokemon-product photo tradition
        ("c6245", 176.0, 208.5),                 # Ninetales promo
        ("c6246", 1.0, 30.0),                    # the 30th Celebration master set binder
        ("c6246", 30.0, 70.0, {"speed": 2}),
        ("c6246", 82.0, 200.0),                  # 60 packs!, PSA graded promos
        ("c6246", 200.0, 250.0, {"speed": 2}),
        ("c6248", 15.0, 54.0),                   # the promos ("we're cutting that out" bit skipped)
        ("c6248", 67.0, 113.0, {"speed": 2}),    # sleeves, coin, dice, deck box
        ("c6248", 113.0, 183.0),                 # playmats
        ("c6248", 196.0, 215.0),                 # classic collection first? the battle setup
        ("c6248", 241.0, 325.0),                 # the rip begins
        ("c6248", 325.0, 352.0, {"speed": 2}),
        ("c6248", 352.0, 428.0),                 # Sylveon SIR, Gengar Prime
        ("c6248", 428.0, 492.0, {"speed": 2}),
        ("c6248", 492.0, 575.6),                 # Mew ex, Articuno IR, Mew SIR
        ("c6250", 0.0, 70.0),
        ("c6250", 181.0, 300.0),                 # THE double opening, $130, max win
        ("c6250", 300.0, 337.0),                 # hits so far, three legendary birds
        ("c6250", 402.0, 440.0),                 # Greninja BREAK
        ("c6250", 490.0, 500.0),                 # Greninja ex
        ("c6250", 632.0, 700.0),                 # Maushold IR, Meowth
        ("c6250", 736.0, 748.5),                 # "Charizard, if you can hear me"
        ("c6250", 860.0, 925.0),                 # last pack magic, the tally
        ("c6250", 925.0, 960.0, {"speed": 2}),
        ("c6250", 960.0, 1014.5),                # Classic Collection war
        ("c6250", 1026.0, 1100.0),               # trade time
        ("c6250", 1129.0, 1166.5),               # the hits photo, "holy hits"
    ],
    "main_section_starts": 17,       # lofi hip hop from the first pack
    "energy": "big",
    "pause_min": 0.35,
    "pause_pad": 0.08,
    "auto_bleep": True,              # bleep every swear the transcript finds
    "protect": {"c6250": [(182, 200), (293, 335), (404, 422), (1145, 1160)],
                "c6248": [(266, 272), (352, 362), (402, 416), (520, 530), (552, 562)]},
    "speakers": {"solo": {}},
    "music": {"intro": [480, 135], "main": [738, 282, 970, 132, 400, 250]},
    "vocab": "30th Celebration, Ultra-Premium Collection, Espeon, Umbreon, Sylveon, Salamence, Gengar Prime, Lugia, Greninja BREAK, Morpeko, Articuno, Zapdos, Moltres, Maushold, Ninetales, Kyogre, PSA",
    "subtitle_fixes": {"Delta Rainy TV": "Delta Reign ETB", "Delta Rain": "Delta Reign", "Delta Ram": "Delta Reign",
                       "Esteeon": "Espeon", "Mouse Hold": "Maushold", "Mouse hold": "Maushold", "Salomons": "Salamence",
                       "Hobbiesville": "Hobbiesville", "ore binder": "aura binder", "Cherubal": "Chimchar", "Payoder": "Pyroar"},
    "cards": {
        "pika_sir":  card("me55", 150, "PIKACHU ex", "SPECIAL ILLUSTRATION RARE", big=True),
        "lugia":     card("me55c", 149, "LUGIA", "SECRET RARE", big=True),
        "sylveon":   card("me55", 153, "SYLVEON ex", "SPECIAL ILLUSTRATION RARE", big=True),
        "gengar":    card("me55c", 94, "GENGAR PRIME", "RARE PRIME", big=True),
        "mew_sir":   card("me55", 152, "MEW ex", "SPECIAL ILLUSTRATION RARE", big=True),
        "greninja":  card("me55c", 41, "GRENINJA BREAK", "RARE BREAK", big=True),
        "articuno":  card("me55", 132, "ARTICUNO", "ILLUSTRATION RARE"),
        "zapdos":    card("me55", 133, "ZAPDOS", "ILLUSTRATION RARE"),
        "moltres":   card("me55", 130, "MOLTRES", "ILLUSTRATION RARE"),
        "morpeko":   card("me55", 135, "MORPEKO", "ILLUSTRATION RARE"),
        "salamence": card("me55", 109, "SALAMENCE ex", "DOUBLE RARE"),
        "maushold":  card("me55", 146, "MAUSHOLD", "ILLUSTRATION RARE"),
        "kommoo":    card("me55", 143, "KOMMO-O", "ILLUSTRATION RARE"),
        "solgaleo":  card("me55c", 89, "SOLGALEO-GX", "RARE HOLO GX"),
    },
    "card_pops": [
        ("c6248", 269.2, 2.6, "salamence"), ("c6248", 295.6, 2.8, "morpeko"),
        ("c6248", 355.6, 4.0, "sylveon"), ("c6248", 404.3, 4.0, "gengar"),
        ("c6248", 523.9, 3.0, "articuno"), ("c6248", 553.9, 4.0, "mew_sir"),
        ("c6250", 182.5, 3.4, "pika_sir"), ("c6250", 186.2, 4.2, "lugia"),
        ("c6250", 324.1, 2.8, "solgaleo"), ("c6250", 406.7, 4.0, "greninja"),
        ("c6250", 638.8, 3.0, "maushold"), ("c6250", 883.5, 3.0, "kommoo"),
    ],
    "montage": ("c6250", 296.1, 1.6, ["moltres", "morpeko", "articuno", "gengar", "zapdos"]),   # "what I've gotten so far"
    "images": [],
    "captions": [
        ("c6244", 50.7, 56.0, "30TH CELEBRATION UPCs!"),
        ("c6246", 94.7, 99.5, "60 PACKS!!"),
        ("c6246", 127.5, 133.0, "GRADED PROMOS!"),
        ("c6248", 120.3, 126.0, "PLAYMAT TIME!"),
        ("c6248", 212.8, 218.0, "LET THE BATTLE BEGIN!"),
        ("c6248", 355.6, 360.5, "SYLVEON SIR!"),
        ("c6248", 404.3, 409.5, "GENGAR PRIME!"),
        ("c6248", 523.9, 527.0, "ARTICUNO IR!"),
        ("c6248", 553.9, 559.0, "MEW SIR!"),
        ("c6250", 182.5, 186.0, "PIKACHU ex SIR!"),
        ("c6250", 190.4, 195.0, "DOUBLE OPENING!!"),
        ("c6250", 221.5, 224.5, "$130 CARD?!"),
        ("c6250", 241.3, 244.3, "MAX WIN!"),
        ("c6250", 296.1, 304.1, "THE HITS SO FAR"),
        ("c6250", 320.4, 324.0, "ALL 3 LEGENDARY BIRDS!"),
        ("c6250", 406.7, 411.0, "GRENINJA BREAK!"),
        ("c6250", 870.1, 873.4, "LAST PACK MAGIC?"),
        ("c6250", 904.9, 909.0, "30 PACKS, 12 HITS!"),
        ("c6250", 977.5, 981.0, "CLASSIC COLLECTION WAR!"),
        ("c6250", 1026.8, 1030.0, "TRADE TIME!"),
        ("c6250", 1158.6, 1166.5, "SUBSCRIBE FOR MORE RIPS!"),
    ],
    "tags": [],
    "big_zooms": [("c6248", 355.0, 360.5), ("c6248", 403.8, 409.5), ("c6248", 553.4, 559.0),
                  ("c6250", 182.3, 189.0), ("c6250", 406.2, 411.0)],
    # where the card is being held during each big zoom (source fractions x, y), so the zoom lands on it
    "focus": [("c6248", 355.0, 0.68, 0.85), ("c6248", 356.6, 0.5, 0.66), ("c6248", 360.5, 0.5, 0.66),
              ("c6248", 403.8, 0.62, 0.84), ("c6248", 406.0, 0.57, 0.78), ("c6248", 409.5, 0.57, 0.78),
              ("c6248", 553.4, 0.63, 0.85), ("c6248", 559.0, 0.63, 0.85),
              ("c6250", 182.3, 0.2, 0.88), ("c6250", 186.0, 0.25, 0.9), ("c6250", 189.0, 0.32, 0.9),
              ("c6250", 406.2, 0.72, 0.86), ("c6250", 411.0, 0.73, 0.86)],
    "big_moments": [("c6248", 355.6), ("c6248", 404.3), ("c6248", 553.9), ("c6250", 182.5), ("c6250", 406.7)],
    "extra_bursts": [("c6250", 190.4), ("c6250", 241.3), ("c6250", 1147.3)],
    "extra_sfx": [("c6250", 221.5, "kaching", 0.45), ("c6250", 241.3, "tada", 0.4), ("c6250", 296.1, "riser", 0.25),
                  ("c6250", 883.5, "boing", 0.4), ("c6250", 977.5, "drumroll", 0.3)],
    "bleeps": [],
    "shorts": {
        "short1_double": {
            "title": "WHAT A DOUBLE OPENING!", "music": 282,
            "parts": [dict(src="c6250", **{"from": 176.0, "to": 214.0}, no_cuts=False)],
            "captions": [("c6250", 182.5, 186.0, "PIKACHU ex SIR!"), ("c6250", 190.4, 195.0, "+ CLASSIC LUGIA!"),
                         ("c6250", 221.5, 224.5, "$130?!")],
            "cards": [("c6250", 182.5, 3.4, "pika_sir"), ("c6250", 186.2, 4.4, "lugia")],
            "zooms": [("c6250", 182.3, 192.5)],
            "zoom": 0.3,
            # where the cards are held during the reveal (source fractions x, y): Lugia bottom-left, Pikachu ex next to it
            "focus": [("c6250", 182.3, 0.17, 0.8), ("c6250", 186.0, 0.22, 0.8), ("c6250", 188.5, 0.3, 0.82), ("c6250", 192.0, 0.36, 0.82)],
            "big_moments": [("c6250", 182.5)],
        },
        "short2_battle": {
            "title": "WHO PULLED BETTER?", "music": 738,
            "parts": [dict(src="c6248", **{"from": 350.0, "to": 362.0}),
                      dict(src="c6248", **{"from": 402.0, "to": 414.0}),
                      dict(src="c6248", **{"from": 551.5, "to": 562.0})],
            "captions": [("c6248", 355.6, 360.5, "SYLVEON SIR!"), ("c6248", 404.3, 409.5, "GENGAR PRIME!"),
                         ("c6248", 553.9, 559.0, "MEW SIR!")],
            "cards": [("c6248", 355.6, 4.0, "sylveon"), ("c6248", 404.3, 4.0, "gengar"), ("c6248", 553.9, 4.0, "mew_sir")],
            "zooms": [("c6248", 355.0, 360.5), ("c6248", 403.8, 409.5), ("c6248", 553.4, 559.0)],
            # where each card is held up: Sylveon (Aiden lifts it to the middle), Gengar, Mew
            "focus": [("c6248", 355.0, 0.68, 0.88), ("c6248", 356.6, 0.5, 0.66), ("c6248", 360.5, 0.5, 0.66),
                      ("c6248", 403.8, 0.62, 0.86), ("c6248", 406.0, 0.57, 0.78), ("c6248", 409.5, 0.57, 0.78),
                      ("c6248", 553.4, 0.63, 0.9), ("c6248", 559.0, 0.63, 0.88)],
            "big_moments": [("c6248", 355.6), ("c6248", 404.3), ("c6248", 553.9)],
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
