"""Speaker-colored, animated subtitles (ASS, burned in with libass).

Speakers are told apart by voice pitch: Sophie (higher) vs Aiden (lower), split at ~140 Hz.
Clips with only one person talking are listed in PROJECT["speakers"]["solo"].
"""
import json, os, re
import numpy as np
import common as C

SOPHIE, AIDEN = "Sophie", "Aiden"
F0_SPLIT = 140.0
CENSOR = {"fuck": "f***", "fucking": "f***ing", "shit": "sh*t"}
FIX = {"Kirk Lee": "Kirlia", "Where candy": "Rare Candy", "where candy": "Rare Candy"}
FONTSDIR = os.path.join(C.EDITOR, "fonts", "ass")

def load_words(p, name):
    SOLO = p.get("speakers", {}).get("solo", {})
    split = p.get("speakers", {}).get("split_hz", F0_SPLIT)
    FIX.update(p.get("subtitle_fixes", {}))
    words = json.load(open(C.analysis(p, name, "words")))
    f0, rms = np.load(C.analysis(p, name, "f0"))
    thr = np.percentile(rms, 55)
    out = []
    for a, b, w, p in words:
        i, j = int(a * 50), int(b * 50) + 1
        seg = f0[i:j][(rms[i:j] > thr) & (f0[i:j] > 75) & (f0[i:j] < 380)]
        out.append(dict(a=a, b=b, w=w, f0=float(np.median(seg)) if len(seg) >= 2 else None, src=name))
    # speaker per utterance (words separated by < 0.5s), by median pitch
    if name in SOLO:
        for x in out: x["spk"] = SOLO[name]
        return out
    # per-word label from pitch, then smooth with a +-2 word majority inside each utterance
    lab = [None if x["f0"] is None else (1 if x["f0"] >= split else 0) for x in out]
    for i in range(len(out)):
        if lab[i] is None or (x := out[i]["f0"]) is not None and abs(x - split) < 6:
            # fill from nearest labeled neighbour in time
            best, bd = None, 9
            for j in range(max(0, i - 4), min(len(out), i + 5)):
                if j != i and lab[j] is not None and out[j]["f0"] is not None and abs(out[j]["f0"] - split) >= 6:
                    d = abs(out[j]["a"] - out[i]["a"])
                    if d < bd: best, bd = lab[j], d
            if best is not None: lab[i] = best
    lab = [1 if v is None else v for v in lab]
    sm = []
    for i in range(len(out)):
        win = [lab[j] for j in range(max(0, i - 2), min(len(out), i + 3)) if abs(out[j]["a"] - out[i]["a"]) < 1.6]
        sm.append(1 if sum(win) * 2 >= len(win) else 0)
    for x, v in zip(out, sm):
        x["spk"] = SOPHIE if v else AIDEN
    return out

def clean(w):
    k = re.sub(r"[^\w']", "", w).lower()
    if k in CENSOR:
        return re.sub(re.escape(re.sub(r"[^\w']", "", w)), CENSOR[k], w, flags=re.I)
    return w

def make_lines(ow, max_chars=34, max_dur=2.8, gap=0.55):
    """ow: list of dicts with oa, ob, w, spk (output timeline), sorted."""
    # lone-word speaker flips -> take the neighbours' speaker
    for i in range(len(ow)):
        p = ow[i - 1] if i > 0 else None; n = ow[i + 1] if i + 1 < len(ow) else None
        if p and p["spk"] != ow[i]["spk"] and ow[i]["oa"] - p["ob"] < 0.4 and (n is None or n["spk"] == p["spk"] or n["oa"] - ow[i]["ob"] > 0.6):
            ow[i]["spk"] = p["spk"]
    lines, cur = [], []
    def flush():
        if cur:
            lines.append(dict(a=cur[0]["oa"], b=cur[-1]["ob"], spk=cur[0]["spk"], text=" ".join(clean(x["w"]) for x in cur)))
    for x in ow:
        if cur:
            text_len = len(" ".join(y["w"] for y in cur)) + 1 + len(x["w"])
            brk = (x["spk"] != cur[0]["spk"] or x["oa"] - cur[-1]["ob"] > gap or text_len > max_chars
                   or x["ob"] - cur[0]["oa"] > max_dur
                   or (cur[-1]["w"][-1:] in ".?!" and len(" ".join(y["w"] for y in cur)) > 10))
            if brk:
                flush(); cur = []
        cur.append(x)
    flush()
    for i, l in enumerate(lines):
        nxt = lines[i + 1]["a"] if i + 1 < len(lines) else l["b"] + 1
        l["b"] = min(max(l["b"] + 0.3, l["a"] + 0.7), nxt - 0.02)
        t = l["text"]
        for k, v in FIX.items(): t = t.replace(k, v)
        l["text"] = t
    return [l for l in lines if l["b"] - l["a"] > 0.15]

def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def write_ass(lines, path, w=1920, h=1080, size=70, margin_v=24, outline=5, shadow=3):
    # colors &HAABBGGRR
    pink, blue = "&H00C88FFF", "&H00FFC97A"
    plum = "&H0040222B"
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sophie,FredokaSubs,{size},{pink},{pink},{plum},&H6040222B,-1,0,0,0,100,100,1,0,1,{outline},{shadow},2,60,60,{margin_v},1
Style: Aiden,FredokaSubs,{size},{blue},{blue},{plum},&H6040222B,-1,0,0,0,100,100,1,0,1,{outline},{shadow},2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for l in lines:
        anim = r"{\fad(70,90)\fscx78\fscy78\t(0,110,\fscx107\fscy107)\t(110,190,\fscx100\fscy100)\blur0.6}"
        txt = l["text"].replace("{", "(").replace("}", ")")
        ev.append(f"Dialogue: 0,{ts(l['a'])},{ts(l['b'])},{l['spk']},,0,0,0,,{anim}{txt}")
    open(path, "w").write(hdr + "\n".join(ev) + "\n")


def write_srt(lines, path):
    """plain captions file for YouTube closed captions (upload it in YouTube Studio > Subtitles)."""
    def t(x):
        x = max(0, x); return f"{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d},{int(round((x%1)*1000)):03d}".replace(",1000", ",999")
    with open(path, "w") as f:
        for i, l in enumerate(lines, 1):
            f.write(f"{i}\n{t(l['a'])} --> {t(l['b'])}\n{l['spk']}: {l['text']}\n\n")
