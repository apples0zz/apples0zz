"""Follow-the-action camera for vertical Shorts.

The 9:16 window pans to wherever the hands and cards are moving (frame differencing on a small grey copy),
smoothed heavily so it glides like a camera operator instead of jittering. No shake, ever.
"""
import json, os, subprocess
import numpy as np
import common as C

GW, GH, GFPS = 240, 135, 10          # analysis size and rate
HALF_W = 0.5 * (1080 * 9 / 16) / 1920  # half the crop width, as a fraction of the frame width


def track(p, src, lo, hi, default=(0.5, 0.5)):
    """smoothed (times, cx, cy) in source seconds / frame fractions for [lo, hi] of a source. Cached."""
    out = os.path.join(p["work"], "analysis", f"{src}_follow2_{lo:.2f}_{hi:.2f}.json")
    if os.path.exists(out):
        d = json.load(open(out)); return np.array(d["t"]), np.array(d["x"]), np.array(d["y"])
    ia = C.input_args(p, src)
    cmd = ["ffmpeg", "-v", "error"] + ia[:-2] + ["-ss", f"{lo:.3f}", "-t", f"{hi - lo:.3f}"] + ia[-2:] + [
        "-vf", f"{C.flip_filter(p, src)}fps={GFPS},scale={GW}:{GH},format=gray", "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, GH, GW).astype(np.float32)
    xs, ys = np.arange(GW)[None, :], np.arange(GH)[:, None]
    cx, cy = [], []
    px, py = default
    for k in range(len(fr)):
        if k == 0:
            cx.append(px); cy.append(py); continue
        d = np.abs(fr[k] - fr[k - 1])
        d[: int(GH * 0.06)] = 0; d[-int(GH * 0.04):] = 0       # ignore the very edges (people leaning in)
        d = np.where(d > 18, d, 0)
        wsum = d.sum()
        if wsum > 2500:                                          # enough movement to be worth following
            px = float((d * xs).sum() / wsum / GW); py = float((d * ys).sum() / wsum / GH)
        cx.append(px); cy.append(py)
    t = lo + np.arange(len(cx)) / GFPS
    cx, cy = smooth(np.array(cx)), smooth(np.array(cy))
    cx = np.clip(cx, HALF_W, 1 - HALF_W); cy = np.clip(cy, 0.3, 1.0)   # pulls happen right at the bottom edge
    json.dump(dict(t=t.tolist(), x=cx.tolist(), y=cy.tolist()), open(out, "w"))
    return t, cx, cy


def smooth(v, sigma_s=0.9):
    """gaussian smoothing (about a second), edge-padded so the start and end don't drift"""
    s = sigma_s * GFPS
    k = np.exp(-0.5 * (np.arange(-int(3 * s), int(3 * s) + 1) / s) ** 2); k /= k.sum()
    pad = len(k) // 2
    return np.convolve(np.pad(v, pad, mode="edge"), k, mode="valid")


def expr(times, vals, t0, t1, step=0.3):
    """piecewise-linear ffmpeg expression of a track over source window [t0, t1], in the input's own t (0 at t0).
    Written as a flat sum of ramps (nested if()s hit ffmpeg's expression depth limit on long clips)."""
    keys = np.arange(t0, t1 + step, step)
    v = np.interp(keys, times, vals)
    loc = keys - t0
    terms = [f"{v[0]:.4f}"]
    for i in range(len(keys) - 1):
        dv = v[i + 1] - v[i]
        if abs(dv) > 1e-4:
            terms.append(f"{dv / step:+.4f}*min(max(t-{loc[i]:.2f},0),{step})")
    return "(" + "".join(terms) + ")"
