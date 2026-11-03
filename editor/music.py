"""Music: Mixkit tracks (free for monetized YouTube, no credit needed). Lofi only -- see CLAUDE.md.

Tracks are referred to by Mixkit id and downloaded/normalized on first use into work/_music/.
"""
import os, subprocess, wave
import numpy as np
import common as C

LOFI = {  # id: title (all checked on mixkit.co, Nov 2026)
    480: "Curiosity (chillout) - backstory/intro",
    135: "Sleepy Cat (chillout) - backstory/intro",
    738: "Hip Hop 02 (lofi hip hop)",
    282: "Sweet September (hip hop)",
    970: "Night Sky Hip Hop",
    132: "Hazy After Hours (electronica)",
    400: "C.B.P.D (hip hop)",
    250: "Island Beat (R&B)",
}
DIR = os.path.join(C.REPO, "work", "_music")


def track(tid):
    os.makedirs(DIR, exist_ok=True)
    mp3, wav_ = os.path.join(DIR, f"{tid}.mp3"), os.path.join(DIR, f"mk_{tid}.wav")
    if not os.path.exists(wav_):
        if not os.path.exists(mp3):
            subprocess.run(["curl", "-sSL", "-m", "120", "-o", mp3, f"https://assets.mixkit.co/music/{tid}/{tid}.mp3"], check=True)
        # normalize every track to the same loudness so the bed level is predictable
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-af", "loudnorm=I=-24:TP=-3,aresample=48000", "-ac", "2", wav_], check=True)
    return wav_


def read_wav(path):
    w = wave.open(path)
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768


def write_wav(path, stereo):
    w = wave.open(path, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(C.SR)
    w.writeframes((np.clip(stereo, -1, 1) * 32000).astype(np.int16).tobytes()); w.close()


def bed(path, total, sections, drops=(), xf=1.5, drop_len=2.4):
    """sections: [(start, end, [mixkit ids...]), ...] played back to back with crossfades.
    drops: edit times where the music cuts out for a moment (big pulls) so the reaction hits harder."""
    SR = C.SR
    N = int((total + 1) * SR)
    mus = np.zeros((N, 2), np.float32)
    for start, end, ids in sections:
        if not ids or end <= start: continue
        t, k = start, 0
        while t < end:
            a = read_wav(track(ids[k % len(ids)])); k += 1
            i = int(t * SR); j = min(N, i + len(a), int(end * SR))
            seg = a[: j - i].copy(); nf = int(xf * SR)
            if len(seg) > 2 * nf:
                seg[:nf] *= np.linspace(0, 1, nf)[:, None]; seg[-nf:] *= np.linspace(1, 0, nf)[:, None]
            mus[i:j] += seg
            t += len(a) / SR - xf
    gain = np.ones(N, np.float32); r = int(0.05 * SR)
    for d in drops:
        i, j = int((d - 0.08) * SR), int((d - 0.08 + drop_len) * SR)
        gain[i:j] = 0; gain[max(0, i - r):i] = np.linspace(1, 0, i - max(0, i - r)); gain[j:j + r] = np.linspace(0, 1, len(gain[j:j + r]))
    mus *= gain[:, None]
    fo = int(3 * SR); mus[int(total * SR) - fo:int(total * SR)] *= np.linspace(1, 0, fo)[:, None]
    write_wav(path, mus)
