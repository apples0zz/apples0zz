"""Step 1 for a new video: download clips, transcribe, find pauses and pitch (for speaker colors), contact sheets.

    python3 editor/prep.py <project>            # everything
    python3 editor/prep.py <project> --no-tx    # skip transcription (fast)
"""
import json, os, subprocess, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

PROMPT = ("Sophie and Aiden opening Pokemon booster packs. Pokedex binder, aura binder, SIR, special illustration rare, "
          "illustration rare, full art, reverse holo, ex, gold card, hyper rare, booster box, Scarlet and Violet, Mega Evolution.")


def sh(*cmd, **kw):
    return subprocess.run(list(cmd), check=True, **kw)


def download(p, key):
    s = p["sources"][key]
    dst = C.src_path(p, key)
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        return dst
    if "drive" in s:  # Google Drive file id (needs drive.usercontent.google.com allowed in the network settings)
        sh("curl", "-sSL", "-o", dst, f"https://drive.usercontent.google.com/download?id={s['drive']}&export=download&confirm=t")
    elif "path" in s:
        os.symlink(os.path.abspath(s["path"]), dst)
    return dst


def wav(p, key):
    out = C.analysis(p, key, "wav")
    if not os.path.exists(out):
        sh("ffmpeg", "-v", "error", "-y", "-i", C.src_path(p, key), "-vn", "-ac", "1", "-ar", "16000", out)
    return out


def silence(p, key):
    out = C.analysis(p, key, "sil")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", C.analysis(p, key, "wav"), "-af", "silencedetect=n=-36dB:d=0.5", "-f", "null", "-"],
                       capture_output=True, text=True)
    vals = [float(l.split(":")[1].split("|")[0]) for l in r.stderr.splitlines() if "silence_start" in l or "silence_end" in l]
    with open(out, "w") as f:
        for i in range(0, len(vals) - 1, 2):
            f.write(f"{vals[i]}\t{vals[i+1]}\n")


def transcribe(p, keys):
    import numpy as np
    from faster_whisper import WhisperModel
    m = WhisperModel("medium.en", device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)
    prompt = PROMPT + " " + p.get("vocab", "")
    for key in keys:
        out = C.analysis(p, key, "words")
        if os.path.exists(out):
            continue
        w = wave.open(C.analysis(p, key, "wav"))
        audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        segs, _ = m.transcribe(audio, word_timestamps=True, initial_prompt=prompt, beam_size=5, vad_filter=True,
                               vad_parameters=dict(min_silence_duration_ms=300))
        words = [[round(x.start, 3), round(x.end, 3), x.word.strip(), round(x.probability, 3)] for s in segs for x in s.words]
        json.dump(words, open(out, "w"))
        txt = os.path.join(p["work"], "analysis", key + "_transcript.txt")
        with open(txt, "w") as f:
            line, t0 = [], None
            for a, b, ww, _ in words:
                if t0 is None: t0 = a
                line.append(ww)
                if ww[-1:] in ".?!" or len(line) > 14:
                    f.write(f"[{t0:7.2f}] {' '.join(line)}\n"); line, t0 = [], None
            if line: f.write(f"[{t0:7.2f}] {' '.join(line)}\n")
        print(key, len(words), "words ->", txt, flush=True)


def pitch(p, key):
    import numpy as np, librosa
    out = C.analysis(p, key, "f0")
    if os.path.exists(out):
        return
    w = wave.open(C.analysis(p, key, "wav"))
    y = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    f0 = librosa.yin(y, fmin=70, fmax=400, sr=16000, frame_length=1024, hop_length=320)
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=320)[0]
    n = min(len(f0), len(rms))
    np.save(out, np.stack([f0[:n], rms[:n]]))


def sheets(p, key):
    out = os.path.join(p["work"], "analysis", key + "_sheet.jpg")
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", C.src_path(p, key)],
                               capture_output=True, text=True).stdout)
    step = max(2, dur / 30)
    sh("ffmpeg", "-v", "error", "-y", "-i", C.src_path(p, key), "-vf", f"fps=1/{step:.2f},scale=320:-1,tile=6x5", "-frames:v", "1", out)


if __name__ == "__main__":
    p = C.load_project(sys.argv[1])
    keys = list(p["sources"])
    for k in keys:
        download(p, k); wav(p, k); silence(p, k); sheets(p, k)
        print("prepped", k, flush=True)
    if "--no-tx" not in sys.argv:
        transcribe(p, keys)
        for k in keys: pitch(p, k)
    print("done ->", os.path.join(p["work"], "analysis"))
