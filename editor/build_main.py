"""Step 2: build the main (landscape) video for a project in the house style (see CLAUDE.md).

    python3 editor/build_main.py <project> --plan     # print the timeline, write graphics + filtergraph, no render
    python3 editor/build_main.py <project> --test 40  # render the first 40 s to check the look
    python3 editor/build_main.py <project>            # full render + 1080p (<400 MB) and 720p delivery copies
"""
import json, os, re, subprocess, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import sfxlib, music, subs

SR, FPS, HALF, snap = C.SR, C.FPS, C.HALF, C.snap
GRADE = "eq=saturation=1.1:brightness=0.025:gamma=1.03,colorbalance=rs=0.03:bs=0.04:rm=0.02"


HYPE_WORDS = {"wow", "whoa", "omg", "yes", "yay", "no", "wait", "what", "holy", "dude", "nice", "oh", "let's", "lets", "ooh", "look", "babe"}


def pop_zoom_times(p, T, ci, key):
    """BIG energy: quick zoom bumps on excited moments (an exclamation word that starts a phrase), every ~6 s at most."""
    if p.get("energy") != "big" or T.speed[ci] != 1:
        return []
    keep = T.chains[ci][1]
    if not keep or not os.path.exists(C.analysis(p, key, "words")):
        return []
    lo, hi = keep[0][0], keep[-1][1]
    words = json.load(open(C.analysis(p, key, "words")))
    big = [(a - 1.0, b + 1.0) for s, a, b in p.get("big_zooms", []) if s == key]
    out, last, prev_end = [], -99, -99
    for a, b, w, prob in words:
        k = w.lower().strip(".,!?")
        if lo <= a <= hi and k in HYPE_WORDS and a - prev_end > 0.35 and a - last > 6 and not any(x <= a <= y for x, y in big):
            out.append(a); last = a
        prev_end = b
    return out + [t for s, t in p.get("pop_zooms", []) if s == key]


def zoom_windows(p, T, ci, key, keep, extra):
    """(start, end, amount, ramp_in, ramp_out) on SOURCE time: alternating punch-ins + big zooms + pop zooms."""
    big_e = p.get("energy") == "big"
    step = 2.6 if big_e else 3.5
    amt = 0.15 if big_e else 0.12
    wins = []
    for a, b in keep:
        n = max(1, int((b - a) // step))
        blk = [(a + (b - a) * j / n, a + (b - a) * (j + 1) / n) for j in range(n)]
        wins += [(x, y, amt, 0.06, 0.06) for i, (x, y) in enumerate(blk) if i % 2]
    bigz = [(a, b) for s, a, b in p.get("big_zooms", []) if s == key and keep and keep[0][0] - 0.5 <= a <= keep[-1][1] + 0.5]
    wins = [w for w in wins if not any(not (w[1] < x or w[0] > y) for x, y in bigz)]
    wins += [(a, b, 0.6 if big_e else 0.5, 0.35, 0.35) for a, b in bigz]
    for t in pop_zoom_times(p, T, ci, key):
        wins = [w for w in wins if not (w[0] - 0.2 <= t <= w[1] + 0.2 and w[2] <= 0.15)]
        wins.append((t - 0.05, t + 1.1, 0.28, 0.12, 0.45))
    return wins


def zoom_expr(wins):
    """1 + sum of eased bumps; t is the source clip's own time."""
    terms = []
    for a, b, amt, ri, ro in wins:
        u = f"min(1,max(0,(t-{a:.3f})/{ri}))*min(1,max(0,({b:.3f}-t)/{ro}))"
        terms.append(f"{amt}*({u})*({u})*(3-2*({u}))")
    return "1+" + "+".join(terms) if terms else "1"


def plan(p):
    T = C.Timeline(p, p["timeline"])
    W = p["work"]; EL = os.path.join(W, "el"); OUT = os.path.join(W, "out")
    at = T.at

    # ---------------- graphics jobs (source times -> edit times) ----------------
    cards = p.get("cards", {})
    pops = list(p.get("card_pops", []))
    if p.get("montage"):
        src, t0, step, keys = p["montage"]
        pops += [(src, t0 + i * step, step, k) for i, k in enumerate(keys)]
    jobs, card_windows = [], []
    for i, (src, t, d, k) in enumerate(pops):
        c = cards[k]; a = at(src, t)
        if a is None: continue
        png = C.card_image(p, c["set"], c["num"]) if "set" in c else C.resolve(p, c["image"])
        big = c.get("big", False) and not (p.get("montage") and k in p["montage"][3])
        label = c["rarity"] if big else f'{c["name"]}  -  {c["rarity"].split("  ")[0]}'
        jobs.append(("card", (f"{EL}/card{i}.mov", png, label, d), dict(sparkle=True, quick=not big), a, "1090", "20"))
        card_windows.append((a, a + d))
    for i, (src, sa, sb, img) in enumerate(p.get("images", [])):
        a, b = at(src, sa), at(src, sb)
        jobs.append(("image_pop", (f"{EL}/img{i}.mov", C.resolve(p, img), b - a), dict(height=690), a, "(W-w)/2", "150"))
    for i, (src, sa, sb, txt) in enumerate(p.get("captions", [])):
        a, b = at(src, sa), at(src, sb)
        if b is None: b = T.total
        if a is None or b - a < 0.4: continue
        busy = any(not (b < x or a > y) for x, y in card_windows)
        jobs.append(("hype", (f"{EL}/cap{i}.mov", txt, b - a), {}, a, "(W-w)/2-230" if busy else "(W-w)/2", "-10"))
    for ci, tz in enumerate(T.teaser):
        if tz and T.chains[ci][1]:
            a = T.chain_start[ci]
            d = sum(y - x for x, y in T.chains[ci][1])
            jobs.append(("hype", (f"{EL}/teaser{ci}.mov", tz if isinstance(tz, str) else "COMING UP...", min(d, 4.0)), {}, a, "(W-w)/2", "-10"))
    for i, (src, sa, sb, txt) in enumerate(p.get("tags", [])):
        a, b = at(src, sa), at(src, sb)
        jobs.append(("tag", (f"{EL}/tag{i}.mov", txt, b - a), {}, a, "0", "H-h-50"))
    piece_starts = [T.chain_start[ci] for ci in range(1, len(T.chains)) if p["timeline"][ci][0] != p["timeline"][ci - 1][0]]
    big = [(src, t, snd) for src, t, *rest in p.get("big_moments", []) for snd in [rest[0] if rest else "thump"]]
    bursts = [t - 0.15 for t in piece_starts] + [at(src, t) - 0.05 for src, t, _ in big if at(src, t) is not None]
    bursts += [at(*x) - 0.05 for x in p.get("extra_bursts", [])]
    for i, t in enumerate(bursts):
        jobs.append(("sparkle_burst", (f"{EL}/burst{i}.mov", 1.0), dict(seed=i + 3), t, "0", "0"))
    pops_by_chain = {}
    ffwd = []  # fast-forwarded pieces get a bouncing pink "FAST FORWARD" badge
    for ci, sp in enumerate(T.speed):
        if sp != 1 and T.chains[ci][1]:
            a = T.chain_start[ci]
            d = sum(round((y - x) * FPS) / FPS for x, y in T.chains[ci][1]) / sp
            ffwd.append((a, d))
            jobs.append(("title_bar", (f"{EL}/ffwd{ci}.mov", f"FAST FORWARD  >>  {sp:g}X", d), dict(size=46), a, "40", "24"))

    # ---------------- sound effects track ----------------
    track = np.zeros(int((T.total + 2) * SR))
    def place(t, name, g):
        if t is None: return
        y = sfxlib.LIB[name] if isinstance(name, str) else name
        if isinstance(name, str) and "whoosh" in name: t -= 0.15
        i = int(t * SR)
        if i < 0: return
        j = min(len(track), i + len(y)); track[i:j] += g * y[: j - i]
    for src, t, d, k in pops:
        place(at(src, t), "softwhoosh", 0.45)
        place(at(src, t + 0.12), "sparkle", 0.28 if cards[k].get("big") else 0.16)
    for src, t, snd in big:
        place(at(src, t), snd, 0.7 if snd == "thump" else 0.45)
    for src, sa, sb, img in p.get("images", []):
        place(at(src, sa), "softwhoosh", 0.45); place(at(src, sa + 0.1), "sparkle", 0.22)
    for src, sa, sb, txt in p.get("captions", []) + p.get("tags", []):
        place(at(src, sa), "bubble_hi", 0.32)
    for t in piece_starts:
        place(t - 0.2, "softwhoosh", 0.4); place(t - 0.2, "sparkle", 0.18)
    for src, t, name, g in p.get("extra_sfx", []):
        place(at(src, t), name, g)
    if p.get("energy") == "big":
        for src, t, snd in big:                       # drumroll into every big reveal, ta-da on it
            ot = at(src, t)
            if ot is not None:
                place(ot - 1.4, "drumroll", 0.35); place(ot, "tada", 0.4)
        for ci, (key, keep) in enumerate(T.chains):   # zoom whoosh on every pop zoom
            for t in pop_zoom_times(p, T, ci, key):
                place(at(key, t), "zoomwhoosh", 0.35)
        for a, d in ffwd:
            place(a, "scratch", 0.3); place(a + d - 0.2, "scratch", 0.25)
        last = {"kaching": -99, "scratch": -99, "boing": -99}
        for ci, (key, keep) in enumerate(T.chains):   # word-triggered fun sounds
            if T.speed[ci] != 1 or not os.path.exists(C.analysis(p, key, "words")): continue
            lo, hi = keep[0][0], keep[-1][1]
            for a_, b_, w, prob in json.load(open(C.analysis(p, key, "words"))):
                if not lo <= a_ <= hi: continue
                k = w.lower().strip(".,!?")
                snd = ("kaching" if ("$" in w or k in ("dollars", "bucks", "worth")) else
                       "scratch" if k == "wait" else
                       "boing" if k in ("oops", "dropped", "fell", "falling", "farted", "whoops") else None)
                ot = at(key, a_)
                if snd and ot is not None and ot - last[snd] > (20 if snd == "scratch" else 8):
                    place(ot, snd, {"kaching": 0.4, "scratch": 0.28, "boing": 0.4}[snd]); last[snd] = ot
    mute = []
    bleeps = list(p.get("bleeps", []))
    if p.get("auto_bleep"):   # every swear in the transcripts, padded a little
        for key in p["sources"]:
            if os.path.exists(C.analysis(p, key, "words")):
                for a_, b_, w, prob in json.load(open(C.analysis(p, key, "words"))):
                    if re.sub(r"[^a-z']", "", w.lower()) in subs.CENSOR:
                        bleeps.append((key, a_ - 0.03, b_ + 0.03))
    for src, a, b in bleeps:
        for ci, (k, keep) in enumerate(T.chains):
            if k != src: continue
            for c_, s_, x, y, os_ in T.segs:
                if c_ == ci and x <= a <= y:
                    oa = os_ + (a - x) / T.speed[ci]; ob = os_ + (min(b, y) - x) / T.speed[ci]
                    place(oa, sfxlib.bleep(max(0.05, ob - oa)), 0.22); mute.append((oa, ob))
    sfx_wav = os.path.join(W, "out", "sfx_track.wav")
    music.write_wav(sfx_wav, np.repeat(np.clip(track, -1, 1)[:, None], 2, axis=1))

    # ---------------- music bed (lofi, ducked under voices later) ----------------
    main_start = T.chain_start[p.get("main_section_starts", 0)]
    drops = [at(src, t) for src, t, _ in big if at(src, t) is not None]
    mus_wav = os.path.join(W, "out", "music_track.wav")
    music.bed(mus_wav, T.total, [(0.0, main_start - 0.3, p["music"].get("intro", [])), (main_start, T.total, p["music"]["main"])], drops)

    # ---------------- subtitles ----------------
    words = {k: subs.load_words(p, k) for k in p["sources"] if os.path.exists(C.analysis(p, k, "words"))}
    lines = subs.make_lines(T.words(words))
    ass = os.path.join(W, "out", "subs.ass")
    subs.write_ass(lines, ass)
    json.dump(lines, open(os.path.join(W, "out", "subs_lines.json"), "w"), indent=0)
    subs.write_srt(lines, os.path.join(W, "out", "subs.srt"))

    # ---------------- filtergraph ----------------
    fc, args = [], []
    for ci, (key, keep) in enumerate(T.chains):
        # seek each input close to its piece (decoding a long clip from 0 for every piece is slow) and put the
        # source timestamps back with setpts, so every t below is still source time
        ss = max(0.0, int(keep[0][0] - 3)) if keep else 0.0
        ia = C.input_args(p, key)
        dur = (keep[-1][1] - ss + 1.0) if keep else 1.0   # and stop decoding just after its last kept frame
        args += ia[:-2] + (["-ss", f"{ss:.3f}"] if ss else []) + ["-t", f"{dur:.3f}"] + ia[-2:]
        back = f"setpts=PTS+{ss:.3f}/TB," if ss else ""
        sel = "+".join(f"between(t,{a-HALF:.4f},{b-HALF:.4f})" for a, b in keep)
        asel = "+".join(f"between(t,{a:.4f},{b:.4f})" for a, b in keep)
        cx, cy = p["sources"][key].get("zoom_center", (0.5, 0.42))
        zoom = zoom_expr(zoom_windows(p, T, ci, key, keep, pops_by_chain.get(ci, [])))
        sp = T.speed[ci]
        vsp = f",setpts=N/({sp}*FRAME_RATE)/TB,fps=30000/1001" if sp != 1 else ""
        asp = f",atempo={sp}" if sp != 1 else ""
        # select the kept frames first, so the (expensive) scaling and zoom only run on frames that are used
        fc += [f"[{ci}:v]{back}fps=30000/1001,select='{sel}',{C.flip_filter(p, key)}scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,"
               f"scale=w='trunc(1920*({zoom})/2)*2':h=-2:eval=frame:flags=bicubic,crop=1920:1080:x='(iw-ow)*{cx}':y='(ih-oh)*{cy}',setsar=1,"
               f"setpts=N/FRAME_RATE/TB{vsp}[v{ci}]",
               f"[{ci}:a]{back.replace('setpts', 'asetpts')}aresample={SR},aformat=channel_layouts=stereo,asetnsamples=n=48,aselect='{asel}',asetpts=N/SR/TB{asp}[a{ci}]"]
    n = len(T.chains)
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca]")
    fc.append(f"[cv]{GRADE}[g]")
    cur, idx = "g", n
    for j in jobs:
        args += ["-i", j[1][0]]
        fc.append(f"[{idx}:v]setpts=PTS+{j[3]:.3f}/TB[e{idx}]")
        fc.append(f"[{cur}][e{idx}]overlay=x={j[4]}:y={j[5]}:eof_action=pass[o{idx}]")
        cur, idx = f"o{idx}", idx + 1
    fc.append(f"[{cur}]subtitles={ass}:fontsdir={subs.FONTSDIR},format=yuv420p[v]")
    args += ["-i", sfx_wav, "-i", mus_wav]
    si, mi = idx, idx + 1
    mutex = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in mute) or "0"
    fc += [f"[ca]volume=0:enable='{mutex}',highpass=f=70,acompressor=threshold=-22dB:ratio=3.5:attack=8:release=180:makeup=2,asplit=2[voice][sc]",
           f"[{mi}:a]volume=0.5,atrim=duration={T.total:.2f}[mus0]",
           "[mus0][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[mus]",
           f"[voice][{si}:a][mus]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"]
    fcp = os.path.join(OUT, "main_fc.txt")
    open(fcp, "w").write(";\n".join(fc))
    return T, jobs, args, fcp, lines


def make_graphics(jobs):
    import anim
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(os.cpu_count() or 4) as ex:
        list(ex.map(_one, jobs))

def _one(j):
    """draw one graphic, unless the same graphic (same settings) was already drawn by an earlier run"""
    import anim
    key = repr((j[0], j[1], sorted(j[2].items())))
    stamp = j[1][0] + ".job"
    if os.path.exists(j[1][0]) and os.path.exists(stamp) and open(stamp).read() == key:
        return
    getattr(anim, j[0])(*j[1], **j[2])
    open(stamp, "w").write(key)


def render(p, args, fcp, out, extra=()):
    cmd = ["ffmpeg", "-hide_banner", "-y"] + args + ["-filter_complex_script", fcp, "-map", "[v]", "-map", "[a]", *extra,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True, stderr=open(out + ".log", "w"))


def deliver(master, total):
    """1080p copy that fits the 400 MB send limit, plus a 720p phone preview."""
    base = master.replace("_master.mp4", "")
    vb = int(min(6000, (380 * 8 * 1024) / total - 200))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", master, "-c:v", "libx264", "-preset", "medium", "-b:v", f"{vb}k",
                    "-maxrate", "6000k", "-bufsize", "8000k", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
                    base + "_1080p.mp4"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", master, "-vf", "scale=-2:720", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "26", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", base + "_preview720.mp4"], check=True)
    return base + "_1080p.mp4", base + "_preview720.mp4"


if __name__ == "__main__":
    p = C.load_project(sys.argv[1])
    T, jobs, args, fcp, lines = plan(p)
    print(T.report()); print(f"{len(jobs)} animated graphics, {len(lines)} subtitle lines")
    if "--plan" in sys.argv:
        sys.exit(0)
    make_graphics(jobs)
    out = os.path.join(p["work"], "out", f"{p['name']}_main_master.mp4")
    if "--test" in sys.argv:
        secs = sys.argv[sys.argv.index("--test") + 1]
        render(p, args, fcp, out.replace("_master", "_test"), extra=("-t", secs))
        print("test ->", out.replace("_master", "_test")); sys.exit(0)
    render(p, args, fcp, out)
    print("master ->", out)
    for f in deliver(out, T.total):
        print("deliver ->", f)
