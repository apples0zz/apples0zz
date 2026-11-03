"""Step 3: vertical 1080x1920 Shorts from the same source clips, same cute style + subtitles.

    python3 editor/build_shorts.py <project>            # all shorts in PROJECT["shorts"]
    python3 editor/build_shorts.py <project> <short>    # one
"""
import os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import sfxlib, music, subs, anim

SR, FPS = C.SR, C.FPS
GRADE = "eq=saturation=1.1:brightness=0.025:gamma=1.03,colorbalance=rs=0.03:bs=0.04:rm=0.02"


def build(p, name, cfg):
    W = p["work"]; od = os.path.join(W, "el", name); os.makedirs(od, exist_ok=True)
    segs, o = [], 0.0  # (src, a, b, layout, out_start, cx)
    for part in cfg["parts"]:
        src, lo, hi = part["src"], part["from"], part["to"]
        for a, b in C.tighten(lo, hi, C.silences(p, src), 0.12, part.get("protect", [(lo, hi)] if part.get("no_cuts") else [])):
            segs.append((src, a, b, part.get("layout", "crop"), o, part.get("x", p["sources"][src].get("zoom_center", (0.62, 0.4))[0])))
            o += b - a
    total = o
    def at(src, t):
        for s, a, b, l, os_, cx in segs:
            if s == src and a - 0.01 <= t <= b + 0.01: return os_ + max(0, t - a)
        later = [os_ for s, a, b, l, os_, cx in segs if s == src and a > t]
        return min(later) if later else None

    args, fc = [], []
    zooms = cfg.get("zooms", [])
    for i, (src, a, b, layout, os_, cx) in enumerate(segs):
        args += ["-ss", f"{a:.4f}", "-t", f"{b-a:.4f}", "-i", C.src_path(p, src)]
        if layout == "wide":  # both faces: landscape strip over a blurred fill
            fc.append(f"[{i}:v]fps=30000/1001,scale=1920:1080,setsar=1,split[w{i}a][w{i}b];"
                      f"[w{i}a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.15[bg{i}];"
                      f"[w{i}b]crop=1500:1080:210:0,scale=1080:-2[fg{i}];[bg{i}][fg{i}]overlay=0:(H-h)/2,setsar=1[sv{i}]")
        else:  # 9:16 crop around the hands, tighter during zoom moments
            zoomed = any(s == src and not (b < za or a > zb) for s, za, zb in zooms)
            ch = 840 if zoomed else 1080; cw = int(ch * 9 / 16) // 2 * 2
            x = int(min(max(cx * 1920 - cw / 2, 0), 1920 - cw)); y = int(min(max((432 if zoomed else 540) - ch / 2, 0), 1080 - ch))
            fc.append(f"[{i}:v]fps=30000/1001,scale=1920:1080,setsar=1,crop={cw}:{ch}:{x}:{y},scale=1080:1920,setsar=1[sv{i}]")
        fc.append(f"[{i}:a]aresample={SR},aformat=channel_layouts=stereo,apad,atrim=duration={b-a:.4f}[sa{i}]")
    n = len(segs)
    fc.append("".join(f"[sv{i}][sa{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca]")

    cards = p.get("cards", {})
    jobs = []
    for k, (src, t, d, key) in enumerate(cfg.get("cards", [])):
        c = cards[key]; a = at(src, t); d = min(d, total - a)
        png = C.card_image(p, c["set"], c["num"]) if "set" in c else C.resolve(p, c["image"])
        jobs.append(((anim.card, (f"{od}/card{k}.mov", png, f'{c["name"]}', d), dict(sparkle=True, cw=560)), a, "(W-w)/2", "490"))
    jobs.append(((anim.title_bar, (f"{od}/title.mov", cfg["title"], total), dict(size=64)), 0.0, "(W-w)/2", "200"))
    for k, (src, sa, sb, txt) in enumerate(cfg.get("captions", [])):
        a, b = at(src, sa), at(src, sb)
        if b is None: b = total
        if a is None or b - a < 0.3: continue
        jobs.append(((anim.hype, (f"{od}/cap{k}.mov", txt, b - a), dict(size=96, w=1060, h=300)), a, "(W-w)/2", "290"))
    cuts = [segs[i][4] for i in range(1, n) if segs[i][0] != segs[i - 1][0] or segs[i][1] - segs[i - 1][2] > 5]
    big = [at(src, t) for src, t, *r in cfg.get("big_moments", [])]
    for k, t in enumerate([0.0] + cuts + big):
        jobs.append(((anim.sparkle_burst, (f"{od}/burst{k}.mov", 1.0), dict(w=1080, h=1920, seed=k + 11)), max(0, t - 0.05), "0", "0"))
    for (fn, fa, kw), *_ in jobs:
        fn(*fa, **kw)
    fc.append(f"[cv]{GRADE}[g]")
    cur, idx = "g", n
    for (fn, fa, kw), t0, xe, ye in jobs:
        args += ["-i", fa[0]]
        fc.append(f"[{idx}:v]setpts=PTS+{t0:.3f}/TB[e{idx}];[{cur}][e{idx}]overlay=x={xe}:y={ye}:eof_action=pass[o{idx}]")
        cur, idx = f"o{idx}", idx + 1

    # subtitles (bottom-middle, above the YouTube Shorts UI)
    words = {}
    for s in {x[0] for x in segs}:
        words[s] = subs.load_words(p, s)
    ow = []
    for s_, a_, b_, l_, os_, cx in segs:
        for x in words[s_]:
            mid = (x["a"] + x["b"]) / 2
            if a_ - 0.08 <= mid <= b_ + 0.08:
                oa = os_ + max(x["a"], a_) - a_; ob = os_ + min(x["b"], b_) - a_
                ow.append(dict(oa=oa, ob=max(ob, oa + 0.08), w=x["w"], spk=x["spk"]))
    ow.sort(key=lambda x: x["oa"])
    ass = f"{od}/subs.ass"
    subs.write_ass(subs.make_lines(ow, max_chars=22, max_dur=2.2), ass, w=1080, h=1920, size=72, margin_v=380)
    fc.append(f"[{cur}]subtitles={ass}:fontsdir={subs.FONTSDIR},format=yuv420p[v]")

    # sound effects + music
    N = int((total + 1) * SR); trk = np.zeros(N)
    def place(t, nm, g):
        if t is None: return
        y = sfxlib.LIB[nm]; t -= 0.15 if "whoosh" in nm else 0
        i = int(t * SR); j = min(N, i + len(y))
        if i >= 0: trk[i:j] += g * y[: j - i]
    for src, t, d, key in cfg.get("cards", []):
        place(at(src, t), "softwhoosh", 0.45); place(at(src, t + 0.1), "sparkle", 0.3)
    for src, t, *r in cfg.get("big_moments", []):
        place(at(src, t), r[0] if r else "thump", 0.7 if not r or r[0] == "thump" else 0.45)
    for src, sa, sb, txt in cfg.get("captions", []):
        place(at(src, sa), "bubble_hi", 0.3)
    for t in cuts:
        place(t, "softwhoosh", 0.4); place(t, "sparkle", 0.15)
    sfx_wav = f"{od}/sfx.wav"; music.write_wav(sfx_wav, np.repeat(np.clip(trk, -1, 1)[:, None], 2, axis=1))
    mus_wav = f"{od}/music.wav"; music.bed(mus_wav, total, [(0, total, [cfg.get("music", 282)])], [b for b in big if b is not None], drop_len=2.2)
    args += ["-i", sfx_wav, "-i", mus_wav]
    si, mi = idx, idx + 1
    fc += [f"[ca]highpass=f=70,acompressor=threshold=-22dB:ratio=3.5:attack=8:release=180:makeup=2,asplit=2[voice][sc]",
           f"[{mi}:a]volume=0.5[mus0];[mus0][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[mus]",
           f"[voice][{si}:a][mus]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"]
    fcp = f"{od}/fc.txt"; open(fcp, "w").write(";\n".join(fc))
    out = os.path.join(W, "out", f"{p['name']}_{name}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args + ["-filter_complex_script", fcp, "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    print(f"{name}: {total:.1f}s -> {out}")


if __name__ == "__main__":
    p = C.load_project(sys.argv[1])
    for k in (sys.argv[2:] or list(p.get("shorts", {}))):
        build(p, k, p["shorts"][k])
