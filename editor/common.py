"""Shared helpers: project loading, work folders, pause trimming and source->edit time mapping."""
import importlib.util, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITOR = os.path.join(REPO, "editor")
FPS = 30000 / 1001
HALF = 0.5 / FPS
SR = 48000
snap = lambda x: round(x * FPS) / FPS


def load_project(name):
    """projects/<name>/project.py must define PROJECT (a dict). See projects/_template/project.py."""
    path = os.path.join(REPO, "projects", name, "project.py")
    spec = importlib.util.spec_from_file_location(f"project_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    p = mod.PROJECT
    p["name"] = name
    p["dir"] = os.path.dirname(path)
    w = os.environ.get("EDIT_WORK") or os.path.join(REPO, "work", name)
    p["work"] = w
    for sub in ("src", "analysis", "el", "out", "cards"):
        os.makedirs(os.path.join(w, sub), exist_ok=True)
    return p


def src_path(p, key):
    return os.path.join(p["work"], "src", p["sources"][key]["file"])


def analysis(p, key, kind):
    """kind: wav | sil | words | f0"""
    ext = {"wav": ".wav", "sil": "_sil.tsv", "words": "_words.json", "f0": "_f0.npy"}[kind]
    return os.path.join(p["work"], "analysis", key + ext)


def silences(p, key):
    return [tuple(map(float, l.split())) for l in open(analysis(p, key, "sil")) if len(l.split()) == 2]


def tighten(lo, hi, sils, pad=0.12, protect=(), min_cut=0.25):
    """Keep ranges of [lo,hi] after removing every pause (from silencedetect) except inside `protect` windows."""
    cuts = []
    for a, b in sils:
        a2, b2 = max(a + pad, lo), min(b - pad, hi)
        if b2 - a2 < min_cut:
            continue
        if any(not (b2 < x or a2 > y) for x, y in protect):
            continue
        cuts.append((a2, b2))
    keep, t = [], lo
    for a, b in cuts:
        if a > t:
            keep.append((t, a))
        t = max(t, b)
    if hi > t:
        keep.append((t, hi))
    keep = [(snap(a), snap(b)) for a, b in keep]
    return [(a, b) for a, b in keep if b - a > 0.2]


class Timeline:
    """Ordered pieces of source clips -> one continuous edit. Times in project files are always SOURCE times
    of a named source; Timeline.at(src, t) converts them to edit (output) time."""

    def __init__(self, p, pieces, pad=0.12):
        self.chains = []  # (src_key, keep_ranges)
        for piece in pieces:
            key, lo, hi = piece[0], piece[1], piece[2]
            protect = list(piece[3]) if len(piece) > 3 else []
            protect += [tuple(w) for w in p.get("protect", {}).get(key, [])]
            self.chains.append((key, tighten(lo, hi, silences(p, key), pad, protect)))
        self.segs = []  # (chain_idx, src_key, a, b, out_start)
        o = 0.0
        for ci, (key, keep) in enumerate(self.chains):
            for a, b in keep:
                self.segs.append((ci, key, a, b, o))
                o += b - a
        self.total = o
        self.chain_start = {}
        for ci, key, a, b, os_ in self.segs:
            self.chain_start.setdefault(ci, os_)

    def chain_of(self, key, t):
        for ci, (k, keep) in enumerate(self.chains):
            if k == key and keep and keep[0][0] - 0.5 <= t <= keep[-1][1] + 0.5:
                return ci
        return None

    def at(self, key, t):
        """source time -> edit time (snaps forward into the next kept range if t was cut)."""
        ci = self.chain_of(key, t)
        if ci is None:
            return None
        for c, s, a, b, os_ in self.segs:
            if c != ci:
                continue
            if t < a:
                return os_
            if t <= b:
                return os_ + t - a
        return None

    def words(self, words_by_src):
        """map transcribed words (with .a .b .w .spk on source time) onto the edit timeline."""
        ow = []
        for ci, (key, keep) in enumerate(self.chains):
            if not keep:
                continue
            lo, hi = keep[0][0], keep[-1][1]
            segs = [(a, b, os_) for c, s, a, b, os_ in self.segs if c == ci]
            for x in words_by_src.get(key, []):
                mid = (x["a"] + x["b"]) / 2
                if not (lo - 0.05 <= mid <= hi + 0.05):
                    continue
                for a, b, os_ in segs:
                    if a - 0.08 <= mid <= b + 0.08:
                        oa = os_ + max(x["a"], a) - a
                        ob = os_ + min(x["b"], b) - a
                        ow.append(dict(oa=oa, ob=max(ob, oa + 0.08), w=x["w"], spk=x["spk"]))
                        break
        ow.sort(key=lambda x: x["oa"])
        return ow

    def report(self):
        out = [f"edit length {int(self.total//60)}:{self.total%60:04.1f}  ({len(self.segs)} jump cuts)"]
        for ci, (key, keep) in enumerate(self.chains):
            out.append(f"  piece {ci}: {key:<10} {sum(b-a for a,b in keep):6.1f}s kept in {len(keep)} segments, starts at {self.chain_start.get(ci,0):.1f}s")
        return "\n".join(out)


def card_image(p, set_id, number):
    """Official card scan from images.pokemontcg.io, cached in work/<project>/cards/."""
    import subprocess
    path = os.path.join(p["work"], "cards", f"{set_id}_{number}.png")
    if not os.path.exists(path):
        subprocess.run(["curl", "-sSL", "-m", "60", "-o", path, f"https://images.pokemontcg.io/{set_id}/{number}_hires.png"], check=True)
    return path


def resolve(p, rel):
    """a path given in a project file: relative to the project folder unless absolute."""
    return rel if os.path.isabs(rel) else os.path.join(p["dir"], rel)
