"""Animated overlay elements (RGBA qtrle .mov clips) drawn with PIL: sticker captions, card pop-ups,
image pop-ups, sparkle bursts, the Shorts title bar and the name tag."""
import math, os, random, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FPS = 30000 / 1001
HERE = os.path.dirname(os.path.abspath(__file__))
BOLD = os.path.join(HERE, "fonts/Fredoka-Bold.ttf")
SEMI = os.path.join(HERE, "fonts/Fredoka-SemiBold.ttf")
PLUM = (43, 34, 64)
CREAM = (255, 248, 231)
BUTTER = (255, 226, 122)
PINK = (255, 158, 199)
LAV = (185, 167, 255)

def ease_out_back(x, s=1.9):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1
def ease_out_cubic(x): return 1 - (1 - x) ** 3
def ease_in_cubic(x): return x ** 3
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))

def writer(path, w, h):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}",
                             "-r", "30000/1001", "-i", "-", "-c:v", "qtrle", path], stdin=subprocess.PIPE)

def text_sprite(text, font_path, size, fill, stroke, stroke_w, shadow=True, pad=40):
    f = ImageFont.truetype(font_path, size)
    l, t, r, b = f.getbbox(text, stroke_width=stroke_w)
    w, h = r - l + pad * 2, b - t + pad * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l + 6, pad - t + 9), text, font=f, fill=PLUM + (150,), stroke_width=stroke_w, stroke_fill=PLUM + (150,))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(7)))
    d = ImageDraw.Draw(img)
    d.text((pad - l, pad - t), text, font=f, fill=fill, stroke_width=stroke_w, stroke_fill=stroke)
    return img

def pill_sprite(text, font_path, size, fg, bg, padx=38, pady=20, shadow=True):
    f = ImageFont.truetype(font_path, size)
    l, t, r, b = f.getbbox(text)
    tw, th = r - l, b - t
    pw, ph = tw + padx * 2, th + pady * 2
    m = 24
    img = Image.new("RGBA", (pw + m * 2, ph + m * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((m, m + 8, m + pw, m + ph + 8), radius=ph // 2, fill=PLUM + (110,))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((m, m, m + pw, m + ph), radius=ph // 2, fill=bg)
    d.text((m + padx - l, m + pady - t), text, font=f, fill=fg)
    return img

def place(canvas, sprite, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    s = sprite
    if abs(scale - 1) > 1e-3:
        s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BICUBIC)
    if abs(rot) > 0.05:
        s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = s.getchannel("A").point(lambda v: int(v * alpha))
        s = s.copy(); s.putalpha(a)
    canvas.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))

def star(size, color):
    img = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size
    pts = []
    for i in range(8):
        r = size if i % 2 == 0 else size * 0.32
        a = math.pi / 2 + i * math.pi / 4
        pts.append((c + r * math.cos(a), c - r * math.sin(a)))
    d.polygon(pts, fill=color)
    glow = img.filter(ImageFilter.GaussianBlur(size * 0.25))
    return Image.alpha_composite(glow, img)

def render(path, w, h, dur, frame_fn):
    n = max(1, round(dur * FPS))
    p = writer(path, w, h)
    for i in range(n):
        t = i / FPS
        cv = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        frame_fn(cv, t, dur)
        p.stdin.write(cv.tobytes())
    p.stdin.close(); p.wait()

def anim_in_hold_out(t, dur, tin=0.35, tout=0.25):
    """returns (phase_in 0..1, phase_out 0..1)"""
    return clamp(t / tin), clamp((t - (dur - tout)) / tout)

# ---------------- elements ----------------
MINT = (150, 230, 200)
OUTLINES = [(255, 126, 182), (160, 130, 255), (90, 200, 170), (255, 170, 90)]

def heart(size, color):
    img = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size * 0.5
    d.ellipse((size - 2 * r + 2, size - r * 1.2, size + 2, size + r * 0.8 - 2), fill=color)
    d.ellipse((size - 2, size - r * 1.2, size + 2 * r - 2, size + r * 0.8 - 2), fill=color)
    d.polygon([(size - 2 * r + 4, size + 0.05 * r), (size + 2 * r - 4, size + 0.05 * r), (size, size + 1.5 * r)], fill=color)
    return Image.alpha_composite(img.filter(ImageFilter.GaussianBlur(size * 0.2)), img)

def sticker_text(text, size, outline, fill=CREAM):
    f = ImageFont.truetype(BOLD, size)
    l, t, r, b = f.getbbox(text, stroke_width=16)
    pad = 50
    w, h = r - l + pad * 2, b - t + pad * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((pad - l + 4, pad - t + 10), text, font=f, fill=PLUM + (120,), stroke_width=16, stroke_fill=PLUM + (120,))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(img)
    d.text((pad - l, pad - t), text, font=f, fill=CREAM, stroke_width=16, stroke_fill=CREAM)   # white sticker edge
    d.text((pad - l, pad - t), text, font=f, fill=outline + (255,), stroke_width=9, stroke_fill=outline + (255,))
    d.text((pad - l, pad - t), text, font=f, fill=fill)
    return img

def hype(path, text, dur, size=112, outline=None, w=1800, h=340):
    outline = outline or OUTLINES[hash(text) % len(OUTLINES)]
    spr = sticker_text(text, size, outline)
    if spr.width > w - 160:
        k = (w - 160) / spr.width
        spr = spr.resize((int(spr.width * k), int(spr.height * k)), Image.LANCZOS)
    deco = [star(22, BUTTER + (255,)), star(16, CREAM + (255,)), heart(18, PINK + (255,)), star(14, LAV + (255,))]
    rnd = random.Random(len(text) * 7 + ord(text[0]))
    spots = [(-spr.width / 2 + 30, -spr.height / 2 + 30), (spr.width / 2 - 25, -spr.height / 2 + 35),
             (spr.width / 2 - 10, spr.height / 2 - 30), (-spr.width / 2 + 10, spr.height / 2 - 35)]
    decos = [(x, y, deco[i % len(deco)], rnd.uniform(0, 1)) for i, (x, y) in enumerate(spots)]
    def fr(cv, t, d):
        pi, po = anim_in_hold_out(t, d, 0.4, 0.25)
        sc = 0.2 + 0.8 * ease_out_back(pi, 2.2) if pi < 1 else 1 + 0.03 * math.sin(2 * math.pi * t / 1.1)
        rot = -10 * (1 - ease_out_cubic(pi)) + 2.0 * math.sin(2 * math.pi * t / 1.6) * ease_out_cubic(pi)
        y = h / 2 + 7 * math.sin(2 * math.pi * t / 1.3)
        a = clamp(t / 0.1)
        if po > 0:
            sc *= 1 - 0.5 * ease_in_cubic(po); a *= 1 - po; y -= 20 * po
        place(cv, spr, w / 2, y, sc, rot, a)
        for x, yy, s, ph in decos:
            v = 0.5 + 0.5 * math.sin(2 * math.pi * (t * 1.3 + ph))
            pa = clamp((t - 0.25) / 0.2) * a
            place(cv, s, w / 2 + x * sc, y + yy * sc, (0.6 + 0.5 * v) * ease_out_back(clamp((t - 0.2) / 0.3), 2.5), t * 40 + ph * 90, pa)
    render(path, w, h, dur, fr)
    return w, h

def sparkle_burst(path, dur=1.0, w=1920, h=1080, seed=3):
    rnd = random.Random(seed)
    ss = [star(s, c) for s, c in [(40, BUTTER + (255,)), (28, CREAM + (255,)), (34, PINK + (255,)), (24, LAV + (255,)), (30, MINT + (255,))]]
    hs = [heart(30, PINK + (255,)), heart(22, CREAM + (255,))]
    parts = [(rnd.uniform(0, w), rnd.uniform(0, h), rnd.choice(ss + hs), rnd.uniform(0, 0.35), rnd.uniform(-60, 60)) for _ in range(34)]
    def fr(cv, t, d):
        for x, y, s, dl, drift in parts:
            u = clamp((t - dl) / 0.6)
            if 0 < u < 1:
                v = math.sin(math.pi * u)
                place(cv, s, x + drift * u, y - 40 * u, 0.3 + 1.0 * v, u * 120, v)
    render(path, w, h, dur, fr)
    return w, h

# NOTE: the light 'meme' caption pills were removed on purpose -- never add reaction text
# that comments on what we say (see CLAUDE.md).

def tag(path, text, dur):
    spr = pill_sprite(text, BOLD, 46, PLUM, BUTTER + (255,))
    w, h = spr.width + 260, spr.height + 40
    def fr(cv, t, d):
        pi, po = anim_in_hold_out(t, d, 0.45, 0.3)
        x = -spr.width / 2 + (spr.width / 2 + 40 + spr.width / 2) * ease_out_back(pi, 1.3)
        rot = 4 * (1 - ease_out_cubic(pi))
        a = 1.0
        if po > 0:
            x -= (spr.width + 60) * ease_in_cubic(po)
        place(cv, spr, x, h / 2, 1, rot, a)
    render(path, w, h, dur, fr)
    return w, h

def card(path, png, label, dur, sparkle=False, cw=440, quick=False):
    im = Image.open(png).convert("RGBA")
    k = cw / im.width
    im = im.resize((cw, int(im.height * k)), Image.LANCZOS)
    mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=22, fill=255)
    im.putalpha(mask)
    m = 50
    base = Image.new("RGBA", (im.width + m * 2, im.height + m * 2), (0, 0, 0, 0))
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((m - 6, m - 6, m + im.width + 6, m + im.height + 6), radius=28,
                                           fill=(BUTTER + (210,)) if sparkle else (CREAM + (170,)))
    base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(18)))
    base.alpha_composite(im, (m, m))
    lab = pill_sprite(label, BOLD, 34, PLUM, CREAM + (245,), padx=28, pady=14)
    stars = [star(s, c) for s, c in [(26, BUTTER + (255,)), (18, CREAM + (255,)), (22, PINK + (255,)), (16, LAV + (255,))]]
    rnd = random.Random(hash(label) & 0xffff)
    parts = [(rnd.uniform(0, 2 * math.pi), rnd.uniform(260, 430), rnd.choice(stars), rnd.uniform(-0.05, 0.15)) for _ in range(16)]
    twinkles = [(rnd.uniform(-300, 300), rnd.uniform(-420, 420), rnd.choice(stars), rnd.uniform(0, 2)) for _ in range(7)]
    w, h = 900, 1040
    cx, cy = w / 2, 470
    tin = 0.28 if quick else 0.42
    def fr(cv, t, d):
        pi, po = anim_in_hold_out(t, d, tin, 0.22 if quick else 0.28)
        if sparkle:
            for ang, dist, s, delay in parts:
                u = clamp((t - delay) / 0.9)
                if 0 < u < 1:
                    r = dist * ease_out_cubic(u)
                    place(cv, s, cx + r * math.cos(ang), cy + r * math.sin(ang) * 1.2, 0.6 + 0.6 * (1 - u), u * 180, 1 - u ** 2)
            for x, y, s, ph in twinkles:
                v = math.sin(2 * math.pi * (t * 0.9 + ph / 2))
                if v > 0 and t > 0.4 and po == 0:
                    place(cv, s, cx + x, cy + y, 0.4 + 0.5 * v, t * 60, v)
        e = ease_out_back(pi, 1.6)
        sc = 0.15 + 0.85 * e
        rot = 14 * (1 - ease_out_cubic(pi)) + 2.2 * math.sin(2 * math.pi * t / 2.2) * ease_out_cubic(pi)
        y = cy + 10 * math.sin(2 * math.pi * t / 1.7)
        x = cx
        a = clamp(t / 0.1)
        if po > 0:
            x += 700 * ease_in_cubic(po); rot -= 20 * po; a *= 1 - po * 0.5
        place(cv, base, x, y, sc, rot, a)
        la = clamp((t - tin * 0.7) / 0.2) * (1 - po)
        place(cv, lab, x, y + base.height / 2 * sc - 4, 0.9 + 0.1 * ease_out_back(clamp((t - tin * 0.7) / 0.25)), 0, la)
    render(path, w, h, dur, fr)
    return w, h

def image_pop(path, png, dur, height=700):
    im = Image.open(png).convert("RGBA")
    k = height / im.height
    im = im.resize((int(im.width * k), height), Image.LANCZOS)
    m = 50
    base = Image.new("RGBA", (im.width + m * 2, im.height + m * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((m, m + 12, m + im.width, m + im.height + 12), radius=24, fill=PLUM + (150,))
    base = Image.alpha_composite(base, sh.filter(ImageFilter.GaussianBlur(16)))
    mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=24, fill=255)
    im.putalpha(mask); base.alpha_composite(im, (m, m))
    w, h = base.width + 120, base.height + 120
    def fr(cv, t, d):
        pi, po = anim_in_hold_out(t, d, 0.45, 0.3)
        e = ease_out_back(pi, 1.5)
        sc = 0.2 + 0.8 * e
        rot = -10 * (1 - ease_out_cubic(pi)) + 1.2 * math.sin(2 * math.pi * t / 2.4)
        y = h / 2 + 8 * math.sin(2 * math.pi * t / 1.9)
        a = clamp(t / 0.1)
        if po > 0:
            sc *= 1 - 0.7 * ease_in_cubic(po); a *= 1 - po
        place(cv, base, w / 2, y, sc, rot, a)
    render(path, w, h, dur, fr)
    return w, h

def title_bar(path, text, dur, size=66):
    spr = pill_sprite(text, BOLD, size, CREAM, (255, 120, 178, 250), padx=40, pady=18)
    w, h = max(spr.width + 60, 200), spr.height + 80
    def fr(cv, t, d):
        pi = clamp(t / 0.5)
        sc = 0.3 + 0.7 * ease_out_back(pi, 1.6)
        rot = -1.2 * math.sin(2 * math.pi * t / 2.6) * ease_out_cubic(pi)
        place(cv, spr, w / 2, h / 2 + 4 * math.sin(2 * math.pi * t / 1.8), sc, rot, clamp(t / 0.1))
    render(path, w, h, dur, fr)
    return w, h
