"""Step 2: build the main (landscape) video for a project in the house style (see CLAUDE.md).

    python3 editor/build_main.py <project> --plan     # print the timeline, write graphics + filtergraph, no render
    python3 editor/build_main.py <project> --test 40  # render the first 40 s to check the look
    python3 editor/build_main.py <project>            # full render + 1080p (<400 MB) and 720p delivery copies
"""
import json, os, subprocess, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import sfxlib, music, subs

SR, FPS, HALF, snap = C.SR, C.FPS, C.HALF, C.snap
GRADE = "eq=saturation=1.1:brightness=0.025:gamma=1.03,colorbalance=rs=0.03:bs=0.04:rm=0.02"


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
    for i, (src, sa, sb, txt) in enumerate(p.get("tags", [])):
        a, b = at(src, sa), at(src, sb)
        jobs.append(("tag", (f"{EL}/tag{i}.mov", txt, b - a), {}, a, "0", "H-h-50"))
    piece_starts = [T.chain_start[ci] for ci in range(1, len(T.chains)) if p["timeline"][ci][0] != p["timeline"][ci - 1][0]]
    big = [(src, t, snd) for src, t, *rest in p.get("big_moments", []) for snd in [rest[0] if rest else "thump"]]
    bursts = [t - 0.15 for t in piece_starts] + [at(src, t) - 0.05 for src, t, _ in big if at(src, t) is not None]
    bursts += [at(*x) - 0.05 for x in p.get("extra_bursts", [])]
    for i, t in enumerate(bursts):
        jobs.append(("sparkle_burst", (f"{EL}/burst{i}.mov", 1.0), dict(seed=i + 3), t, "0", "0"))

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
    mute = []
    for src, a, b in p.get("bleeps", []):
        oa, ob = at(src, a), at(src, b)
        place(oa, sfxlib.bleep(ob - oa), 0.22); mute.append((oa, ob))
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
        args += ["-i", C.src_path(p, key)]
        sel = "+".join(f"between(t,{a-HALF:.4f},{b-HALF:.4f})" for a, b in keep)
        asel = "+".join(f"between(t,{a:.4f},{b:.4f})" for a, b in keep)
        blocks = []
        for a, b in keep:  # alternate normal / 1.12x punch-in every ~3.5 s
            n = max(1, int((b - a) // 3.5))
            blocks += [(a + (b - a) * j / n, a + (b - a) * (j + 1) / n) for j in range(n)]
        alt = "+".join(f"between(t,{snap(a)-HALF:.4f},{snap(b)-HALF:.4f})" for i, (a, b) in enumerate(blocks) if i % 2) or "0"
        cx, cy = p["sources"][key].get("zoom_center", (0.5, 0.42))
        bz = "+".join(f"between(t,{a},{b})" for s, a, b in p.get("big_zooms", []) if s == key and T.chain_of(key, a) == ci) or "0"
        fc += [f"[{ci}:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30000/1001,setsar=1,split=3[c{ci}b][c{ci}z][c{ci}y]",
               f"[c{ci}z]crop=iw/1.12:ih/1.12:(iw-ow)/2:(ih-oh)*0.45,scale=1920:1080[c{ci}zz]",
               f"[c{ci}y]crop=iw/1.5:ih/1.5:iw*{cx}-ow/2:ih*{cy}-oh/2,scale=1968:1108[c{ci}yy]",
               f"[c{ci}b][c{ci}zz]overlay=enable='{alt}'[c{ci}o1]",
               f"[c{ci}o1][c{ci}yy]overlay=x=-24:y=-14:enable='{bz}'[c{ci}o2]",
               f"[c{ci}o2]select='{sel}',setpts=N/FRAME_RATE/TB[v{ci}]",
               f"[{ci}:a]aresample={SR},aformat=channel_layouts=stereo,asetnsamples=n=48,aselect='{asel}',asetpts=N/SR/TB[a{ci}]"]
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
    import anim
    getattr(anim, j[0])(*j[1], **j[2])


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
