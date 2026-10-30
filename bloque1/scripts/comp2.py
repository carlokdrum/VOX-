import numpy as np, subprocess, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

D = '/tmp/claude-0/-home-claude/151a5d7d-95d0-53f2-9876-b0845c8abc48/scratchpad/'
O = D + 'b1v2/'
W, H, FPS = 1080, 1920, 24
DUR = 10.6
N = int(DUR * FPS)
rng = random.Random(11)

def clamp(x, a=0, b=1): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a))
def eo(x): return 1 - (1 - x) ** 3
def eb(x, s=1.9):
    x -= 1; return x * x * ((s + 1) * x + s) + 1
def twos(t): return math.floor(t * 12) / 12   # stop-motion on twos

# ---------- keying ----------
def key_green(path, border=7):
    im = Image.open(path).convert('RGB')
    a = np.array(im).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    gm = (g > r + 30) & (g > b + 30)
    alpha = np.where(gm, 0, 255).astype(np.uint8)
    am = Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert('RGBA'); out.putalpha(am)
    # despill
    arr = np.array(out); g2 = arr[..., 1].astype(np.int16); m = np.maximum(arr[..., 0], arr[..., 2]).astype(np.int16)
    arr[..., 1] = np.minimum(g2, m + 10).astype(np.uint8)
    out = Image.fromarray(arr)
    bb = out.getbbox(); return out.crop(bb)

def paper_shadow(layer, off=(9, 12), blur=7, op=140):
    pad = 40
    s = Image.new('RGBA', (layer.width + pad * 2, layer.height + pad * 2), (0, 0, 0, 0))
    a = layer.split()[3].point(lambda v: v * op // 255)
    blk = Image.new('RGBA', layer.size, (25, 15, 5, 255)); blk.putalpha(a)
    s.alpha_composite(blk, (pad + off[0], pad + off[1]))
    s = s.filter(ImageFilter.GaussianBlur(blur))
    s.alpha_composite(layer, (pad, pad))
    return s

def fit(im, h): return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)

palmas = paper_shadow(fit(key_green(O + 'palmas.png'), 1750))
luna = paper_shadow(fit(key_green(O + 'luna.png'), 560))
reloj = paper_shadow(fit(key_green(O + 'reloj.png'), 620))
familia = paper_shadow(fit(key_green(O + 'familia.png'), 760))
bg = Image.open(O + 'bg.png').convert('RGB').resize((int(W * 1.25), int(H * 1.25)), Image.LANCZOS)
revista = np.array(Image.open(O + 'revista.png').convert('RGB'))

# ---------- fire clip (cobalt keyed out) ----------
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', D + 'b1/fuego.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                     capture_output=True).stdout
src = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3); NS = len(src)
CAL = np.zeros((H, W, 3), np.float32); CALM = np.zeros((H, W), np.float32)
_c = np.array(Image.open(O + 'calendario.png').convert('RGB')).astype(np.float32)
CAL[295:295 + _c.shape[0], 255:255 + _c.shape[1]] = _c; CALM[295:295 + _c.shape[0], 255:255 + _c.shape[1]] = 1
def fire_frame(i):
    f0 = src[min(i, NS - 1)].astype(np.float32)
    r_, g_, b_ = f0[..., 0], f0[..., 1], f0[..., 2]
    paper = ((r_ > 150) & (g_ > 140) & (b_ > 100) & (r_ - b_ < 80)).astype(np.float32) * CALM
    paper = np.array(Image.fromarray((paper * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32) / 255
    shade = np.clip(f0.mean(axis=2) / 225.0, 0.4, 1.15)[..., None]
    f0 = f0 * (1 - paper[..., None]) + CAL * shade * paper[..., None]
    f = f0.clip(0, 255).astype(np.int16)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    blue = np.clip(((b - np.maximum(r, g)) - 40) / 50.0, 0, 1)
    a = (1 - blue)
    am = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    c = f.copy()
    c[..., 2] = np.minimum(c[..., 2], np.maximum(c[..., 0], c[..., 1]) + 5)
    im = Image.fromarray(c.astype(np.uint8)).convert('RGBA'); im.putalpha(am.filter(ImageFilter.MinFilter(3)))
    return im

# ---------- ransom letters ----------
FONTS = ['/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
         '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf',
         '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf']
FONTS = [f for f in FONTS if __import__('os').path.exists(f)]
INKS = [(15, 15, 15), (250, 248, 240), (200, 25, 30), (20, 40, 160), (250, 200, 30)]

def letter(ch, size, seed):
    r = random.Random(seed)
    f = ImageFont.truetype(r.choice(FONTS), int(size * r.uniform(0.85, 1.15)))
    bb = f.getbbox(ch); lw, lh = bb[2] - bb[0], bb[3] - bb[1]
    pw, ph = int(lw + size * r.uniform(0.25, 0.45)), int(lh + size * r.uniform(0.3, 0.5))
    # paper scrap from magazine texture
    x0 = r.randint(0, revista.shape[1] - pw - 1); y0 = r.randint(0, revista.shape[0] - ph - 1)
    patch = Image.fromarray(revista[y0:y0 + ph, x0:x0 + pw]).convert('RGBA')
    pm = np.array(patch)[..., :3].mean()
    ink = (15, 15, 15) if pm > 140 else (250, 248, 240)
    if r.random() < 0.3: ink = r.choice(INKS)
    if abs(np.mean(ink) - pm) < 60: ink = (15, 15, 15) if pm > 128 else (250, 248, 240)
    d = ImageDraw.Draw(patch)
    d.text(((pw - lw) / 2 - bb[0], (ph - lh) / 2 - bb[1]), ch, font=f, fill=ink + (255,))
    # irregular scissor polygon
    j = size * 0.06
    poly = [(r.uniform(0, j), r.uniform(0, j)), (pw - r.uniform(0, j), r.uniform(0, j)),
            (pw - r.uniform(0, j), ph - r.uniform(0, j)), (r.uniform(0, j), ph - r.uniform(0, j))]
    m = Image.new('L', (pw, ph), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
    patch.putalpha(m)
    # paper grain
    a = np.array(patch).astype(np.int16); a[..., :3] += np.random.default_rng(seed).integers(-12, 12, (ph, pw, 1))
    patch = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    return paper_shadow(patch, off=(5, 7), blur=4, op=150), r.uniform(-9, 9)

def word(txt, size, seed):
    return [(letter(c, size, seed * 100 + k) if c != ' ' else None) for k, c in enumerate(txt)]

WORDS = {
    'UN': word('UN VIERNES', 120, 1),
    'QUE': word('QUE NUNCA', 105, 2),
    'EXI': word('EXISTIÓ', 150, 3),
    'ERR': word('NO FUE UN ERROR', 120, 4),
    'Y11': word('2011', 300, 5),
    'JUE': word('JUEVES', 135, 6),
    'SAB': word('SÁBADO', 160, 7),
}

def place_word(canvas, key, cx, cy, t0, t, step=0.06, out_t=None, mode='drop', heat=0.0, maxw=960):
    letters = WORDS[key]
    widths = [(l[0].width - 40) if l else 50 for l in letters]
    total = sum(widths) * 0.92
    fitk = min(1.0, maxw / total)
    widths = [w * fitk for w in widths]; total *= fitk
    x = cx - total / 2
    for k, l in enumerate(letters):
        w = widths[k]
        if l is None: x += w * 0.92; continue
        im, rot = l
        p = seg(twos(t), t0 + k * step, t0 + k * step + 0.17)
        if p <= 0: x += w * 0.92; continue
        lx, ly = x + w / 2, cy
        sc = fitk
        if mode == 'drop': ly -= 260 * (1 - eb(p)); sc = fitk * (1.6 - 0.6 * eo(p))
        if mode == 'slam': sc = fitk * (2.4 - 1.4 * eb(p))
        r = rot + 25 * (1 - p)
        if out_t is not None and t > out_t:
            q = seg(t, out_t + k * 0.03, out_t + k * 0.03 + 0.6)
            ly -= 900 * q ** 1.6 * (1 + 0.3 * math.sin(k)); lx += 140 * math.sin(k * 2.1) * q
            r += 220 * q * (1 if k % 2 else -1); sc *= 1 + 0.4 * q
            if q >= 1: x += w * 0.92; continue
        if heat > 0:
            ly += 5 * math.sin(t * 40 + k); lx += 4 * math.cos(t * 33 + k)
        li = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR).rotate(r, Image.BICUBIC, expand=True)
        if out_t is not None and t > out_t:
            # burning: darken + orange edge
            q = seg(t, out_t + k * 0.03, out_t + k * 0.03 + 0.6)
            a = np.array(li).astype(np.float32)
            a[..., :3] = a[..., :3] * (1 - 0.7 * q) + np.array([255, 110, 20]) * 0.5 * q
            a[..., 3] *= (1 - q ** 2)
            li = Image.fromarray(a.clip(0, 255).astype(np.uint8))
        canvas.alpha_composite(li, (int(lx - li.width / 2), int(ly - li.height / 2)))
        x += w * 0.92

# ---------- camera ----------
def camz(t):
    if t < 0.45: z = 1.5 - 0.5 * eo(t / 0.45)
    elif t < 3.0: z = 1.0 + 0.06 * seg(t, 0.45, 3.0)
    elif t < 3.35: z = 1.06 + 0.14 * eb(seg(t, 3.0, 3.35))
    elif t < 9.1: z = 1.2 + 0.35 * (seg(t, 3.35, 9.1) ** 1.6)
    else: z = 1.55 + 1.7 * (seg(t, 9.1, DUR) ** 2)
    sx = sy = 0
    for hit, amp in ((3.05, 26), (4.75, 34), (9.2, 22)):
        if hit <= t < hit + 0.45:
            k = (1 - (t - hit) / 0.45) ** 2; sx += amp * k * math.sin(t * 90); sy += amp * k * math.cos(t * 77)
    rot = -1.5 * seg(t, 3.35, 9.1)
    return z, sx, sy, rot

def place(canvas, layer, cx, cy, sc=1.0, rot=0.0, alpha=1.0):
    if alpha <= 0.01: return
    l = layer.resize((max(1, int(layer.width * sc)), max(1, int(layer.height * sc))), Image.BILINEAR)
    if rot: l = l.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 1:
        a = np.array(l); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); l = Image.fromarray(a)
    canvas.alpha_composite(l, (int(cx - l.width / 2), int(cy - l.height / 2)))

def depth_view(layer_canvas, z, d, sx, sy, rot):
    zz = 1 + (z - 1) * d
    if zz < 1:
        pad = Image.new('RGBA', (int(W / zz) + 2, int(H / zz) + 2), (0, 0, 0, 0))
        pad.alpha_composite(layer_canvas, ((pad.width - W) // 2, (pad.height - H) // 2))
        src_ = pad; cx, cy = pad.width / 2, pad.height / 2
    else:
        src_ = layer_canvas; cx, cy = W / 2, H / 2
    cx += sx * d / zz; cy += sy * d / zz
    cw, ch = W / zz, H / zz
    v = src_.rotate(rot * d, Image.BICUBIC, center=(cx, cy))
    return v.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BILINEAR)

pipe = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                         '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', O + 'mudo.mp4'],
                        stdin=subprocess.PIPE)
grain_rng = np.random.default_rng(3)
prev = None
for i in range(N):
    t = i / FPS
    ts = twos(t)
    z, sx, sy, rot = camz(t)
    # stop-motion jitter for cutouts
    jr = random.Random(int(ts * 12))
    jx, jy, jrot = jr.uniform(-4, 4), jr.uniform(-4, 4), jr.uniform(-1.2, 1.2)
    heat = seg(t, 3.2, 4.5)

    # L0 background newspaper (parallax 0.55, slow drift)
    L0 = Image.new('RGBA', (W, H))
    bx = -(bg.width - W) / 2 + 30 * math.sin(t * 0.4); by = -(bg.height - H) / 2 - 40 * t / DUR
    L0.paste(bg, (int(bx), int(by)))
    # scorch the newspaper around the fire as it grows
    if t > 3.2:
        sc_ = Image.new('L', (W, H), 0)
        rr = 120 + 600 * seg(t, 3.2, 9.5)
        ImageDraw.Draw(sc_).ellipse((540 - rr, 880 - rr * 1.2, 540 + rr, 880 + rr * 1.2), fill=int(170 * seg(t, 3.2, 5)))
        sc_ = sc_.filter(ImageFilter.GaussianBlur(120))
        dark = Image.new('RGBA', (W, H), (30, 12, 0, 255)); dark.putalpha(sc_)
        L0.alpha_composite(dark)
    V = depth_view(L0, z, 0.55, sx, sy, rot)

    # L1 mid cutouts (parallax 0.8): palms, moon, clock, family
    L1 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lift = seg(t, 4.0, 8.0)  # hot air lifts them
    burn = lift
    p = eb(seg(ts, 0.15, 0.6))
    place(L1, palmas, 930 + 400 * (1 - p) + jx, 1000 - 700 * lift ** 1.5 + jy, 0.95, 4 * math.sin(ts * 2.4) + jrot + 30 * lift, 1 - burn ** 3)
    p = eb(seg(ts, 0.35, 0.8))
    place(L1, luna, 190 + jx, 380 + 500 * (1 - p) - 400 * lift + jy, 1.0, 360 * eo(seg(ts, 0.5, 2.0)) + jrot - 60 * lift, p * (1 - burn ** 3))
    p = eb(seg(ts, 0.55, 1.0))
    clock_rot = 8 * math.sin(ts * 9) if ts < 3 else 0
    place(L1, reloj, 880 + 500 * (1 - p) + jx, 420 - 500 * lift + jy, 1.0, clock_rot + jrot + 80 * lift, p * (1 - burn ** 3))
    p = eb(seg(ts, 0.8, 1.4))
    place(L1, familia, 470 - 900 * (1 - p) + jx, 1620 - 300 * lift + jy, 1.25, jrot * 0.5 - 20 * lift, 1 - burn ** 3)
    if burn > 0:
        a = np.array(L1).astype(np.float32)
        a[..., :3] = a[..., :3] * (1 - 0.6 * burn) + np.array([255, 90, 10]) * 0.35 * burn
        L1 = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    V.alpha_composite(depth_view(L1, z, 0.8, sx, sy, rot))

    # L2 fire clip (hero, parallax 1.0) — stop motion before fire, fluid after
    fi = (i // 2) * 2 if t < 3.0 else i
    F = fire_frame(fi)
    Fl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    place(Fl, F, 540, 900, 0.78)
    V.alpha_composite(depth_view(Fl, z, 1.0, sx, sy, rot))

    # 2011 inside the burnt hole
    if 4.6 < t < 9.3:
        T = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        place_word(T, 'Y11', 540, 880, 4.74, t, step=0.07, mode='slam', maxw=520)
        Tv = depth_view(T, z, 1.0, sx, sy, rot)
        base = np.array(V).astype(np.float32)
        lum = base[..., :3].mean(axis=2)
        hole = np.clip((90 - lum) / 55, 0, 1)
        hm = np.array(Image.fromarray((hole * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255
        ta = np.array(Tv).astype(np.float32)
        a = ta[..., 3:] / 255 * hm[..., None] * (1 - seg(t, 8.8, 9.3))
        base[..., :3] = base[..., :3] * (1 - a) + ta[..., :3] * a * (0.9 + 0.1 * math.sin(t * 31))
        V = Image.fromarray(base.clip(0, 255).astype(np.uint8))

    # foreground ransom words (screen space, follow camera lightly)
    T = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if t < 3.6:
        place_word(T, 'QUE', 540, 1440, 1.0, t, step=0.05, out_t=3.1)
        place_word(T, 'EXI', 540, 1600, 1.45, t, step=0.06, mode='slam', out_t=3.15)
    if 3.1 < t < 4.9:
        place_word(T, 'ERR', 540, 1520, 3.15, t, step=0.035, out_t=4.3, heat=heat, maxw=1000)
    if 7.0 < t < 9.4:
        place_word(T, 'JUE', 540, 1560, 7.0, t, step=0.05, out_t=8.55)
    V.alpha_composite(depth_view(T, z, 0.35, sx, sy, rot * 0.3))
    if t > 9.1:
        S = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        place_word(S, 'SAB', 540, 960, 9.15, t, step=0.045, mode='slam', maxw=900)
        V.alpha_composite(S)

    arr = np.array(V.convert('RGB')).astype(np.float32)
    if (t < 0.45 or 3.0 < t < 3.35 or t > 9.4) and prev is not None:
        arr = arr * 0.55 + prev * 0.45
    prev = arr
    # warm fire light spill after ignition
    if t > 3.1:
        arr = arr * (1 + 0.08 * heat * (0.8 + 0.2 * math.sin(t * 23)) * np.array([1.0, 0.85, 0.6]))
    arr += grain_rng.normal(0, 6, (H, W, 1))
    pipe.stdin.write(arr.clip(0, 255).astype(np.uint8).tobytes())
    if i % 48 == 0: print(i, flush=True)
pipe.stdin.close(); pipe.wait()
