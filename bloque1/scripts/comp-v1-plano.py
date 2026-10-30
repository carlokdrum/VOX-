import numpy as np, subprocess, math, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = '/tmp/claude-0/-home-claude/151a5d7d-95d0-53f2-9876-b0845c8abc48/scratchpad/b1/'
W, H, FPS = 1080, 1920, 24
DUR = 10.6
N = int(DUR * FPS)
FONT = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
try:
    FONT_BLACK = '/usr/share/fonts/truetype/google-fonts/Poppins-Black.ttf'
    ImageFont.truetype(FONT_BLACK, 10)
except Exception:
    FONT_BLACK = FONT

# load source frames
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', D + 'fuego.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                     capture_output=True).stdout
src = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
NS = len(src)

def ease_out(x): return 1 - (1 - x) ** 3
def ease_back(x, s=1.9):
    x -= 1; return x * x * ((s + 1) * x + s) + 1
def clamp(x, a=0, b=1): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a))

def text_layer(txt, size, fill, font=FONT_BLACK, stroke=0, sfill=None, track=0):
    f = ImageFont.truetype(font, size)
    # tracking
    widths = [f.getbbox(c)[2] - f.getbbox(c)[0] for c in txt]
    tw = sum(widths) + track * (len(txt) - 1) + 2 * stroke + 40
    th = int(size * 1.4) + 2 * stroke
    im = Image.new('RGBA', (int(tw), th), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 20 + stroke
    for c, w in zip(txt, widths):
        d.text((x - f.getbbox(c)[0], stroke + int(size * 0.05)), c, font=f, fill=fill,
               stroke_width=stroke, stroke_fill=sfill)
        x += w + track
    return im

def paste_center(base, layer, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if alpha <= 0 or scale <= 0.01: return
    l = layer.copy()
    if scale != 1.0:
        l = l.resize((max(1, int(l.width * scale)), max(1, int(l.height * scale))), Image.LANCZOS)
    if rot: l = l.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = l.split()[3].point(lambda v: int(v * alpha)); l.putalpha(a)
    base.alpha_composite(l, (int(cx - l.width / 2), int(cy - l.height / 2)))

# pre-rendered type
T_VIERNES = text_layer('VIERNES', 128, (22, 30, 70, 255), track=6)
T_QUE = text_layer('QUE NUNCA', 120, (255, 255, 255, 255), track=2)
T_EXI = text_layer('EXISTIÓ', 190, (255, 255, 255, 255), track=2)
T_ERR = text_layer('NO FUE UN ERROR', 92, (255, 246, 225, 255), track=4)
T_2011 = text_layer('2011', 430, (255, 236, 200, 255), track=-10)
T_JUE = text_layer('JUEVES', 170, (255, 255, 255, 255), track=4)
T_SAB = text_layer('SÁBADO', 200, (255, 255, 255, 255), track=4)

def shadowed(layer, off=(10, 14), blur=10, op=110):
    sh = Image.new('RGBA', (layer.width + 80, layer.height + 80), (0, 0, 0, 0))
    a = layer.split()[3]
    blk = Image.new('RGBA', layer.size, (0, 0, 20, op)); blk.putalpha(a.point(lambda v: v * op // 255))
    sh.alpha_composite(blk, (40 + off[0], 40 + off[1]))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    sh.alpha_composite(layer, (40, 40))
    return sh
T_QUE_S, T_EXI_S, T_JUE_S, T_SAB_S = map(shadowed, (T_QUE, T_EXI, T_JUE, T_SAB))

def glow(layer, color=(255, 120, 20), r=28, strength=2):
    g = Image.new('RGBA', (layer.width + 160, layer.height + 160), (0, 0, 0, 0))
    a = layer.split()[3]
    c = Image.new('RGBA', layer.size, color + (255,)); c.putalpha(a)
    g.alpha_composite(c, (80, 80))
    g = g.filter(ImageFilter.GaussianBlur(r))
    out = Image.new('RGBA', g.size, (0, 0, 0, 0))
    for _ in range(strength): out.alpha_composite(g)
    out.alpha_composite(layer, (80, 80))
    return out
T_ERR_G = glow(T_ERR, r=22)
T_2011_G = glow(T_2011, r=40, strength=3)

rng = random.Random(7)
jit = [(rng.uniform(-6, 6), rng.uniform(-6, 6), rng.uniform(-0.6, 0.6)) for _ in range(N)]

def cam(t):
    # zoom, offset x, offset y, rotation
    if t < 0.45: z = 1.55 - 0.55 * ease_out(t / 0.45)       # crash zoom in from wide (reverse)
    elif t < 3.0: z = 1.0 + 0.06 * seg(t, 0.45, 3.0)
    elif t < 3.35: z = 1.06 + 0.16 * ease_back(seg(t, 3.0, 3.35))  # impact on tear
    elif t < 9.1: z = 1.22 + 0.33 * (seg(t, 3.35, 9.1) ** 1.6)
    else: z = 1.55 + 1.6 * (seg(t, 9.1, DUR) ** 2)         # fly through
    sx = sy = 0
    for hit, amp in ((3.05, 26), (4.75, 34), (9.2, 22)):
        if hit <= t < hit + 0.45:
            k = (1 - (t - hit) / 0.45) ** 2
            sx += amp * k * math.sin(t * 90); sy += amp * k * math.cos(t * 77)
    rot = -1.2 * seg(t, 3.35, 9.1) + (0.8 * math.sin(t * 60) * (1 - seg(t, 3.05, 3.4)) if 3.05 < t < 3.4 else 0)
    return z, sx, sy, rot

pipe = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                         '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                         '-pix_fmt', 'yuv420p', D + 'video_mudo.mp4'], stdin=subprocess.PIPE)

prev = None
for i in range(N):
    t = i / FPS
    # --- stop-motion hold: 12fps steps before the fire, fluid after
    if t < 3.0:
        si = (i // 2) * 2
        jx, jy, jr = jit[i // 2]
    else:
        si = i; jx = jy = jr = 0
    si = min(si, NS - 1)
    fr = src[si]
    # ---- text printed on the paper (clip space), burned away by the fire
    base = Image.fromarray(fr).convert('RGBA')
    if t < 6.0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        a_in = ease_out(seg(t, 0.25, 0.7))
        paste_center(lay, T_VIERNES, 560, 860, 1.0, 0, a_in)
        # paper mask: cream pixels only (excludes flame, hole, blue)
        f = fr.astype(np.int16)
        r, g, b = f[..., 0], f[..., 1], f[..., 2]
        paper = ((r > 175) & (g > 165) & (b > 120) & (r - b < 70)).astype(np.float32)
        pm = Image.fromarray((paper * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
        la = np.array(lay.split()[3]).astype(np.float32) * (np.array(pm).astype(np.float32) / 255)
        # ink multiply
        ink = np.array(lay)[..., :3].astype(np.float32) / 255
        k = (la / 255)[..., None] * 0.92
        out = fr.astype(np.float32) * (1 - k + k * ink)
        base = Image.fromarray(out.clip(0, 255).astype(np.uint8)).convert('RGBA')
    # ---- 2011 lives INSIDE the burnt hole (visible only in dark pixels)
    if 4.6 < t < 9.4:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        p = seg(t, 4.74, 5.05)
        sc = 0.6 + 0.4 * ease_back(p) + 0.12 * seg(t, 5.05, 9.4)
        alpha = p * (1 - seg(t, 8.9, 9.4))
        paste_center(lay, T_2011_G, 540, 900, sc, -4, alpha)
        f = np.array(base)[..., :3].astype(np.float32)
        lum = f.mean(axis=2)
        dark = np.clip((95 - lum) / 60, 0, 1)
        dm = Image.fromarray((dark * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))
        la = np.array(lay).astype(np.float32)
        a = la[..., 3:] / 255 * (np.array(dm).astype(np.float32)[..., None] / 255)
        # flicker with the fire
        a *= 0.85 + 0.15 * math.sin(t * 37)
        f = f * (1 - a) + la[..., :3] * a
        base = Image.fromarray(f.clip(0, 255).astype(np.uint8)).convert('RGBA')
    # ---- camera transform
    z, sx, sy, rot = cam(t)
    img = base
    cw, ch = W / z, H / z
    cx, cy = W / 2 + sx / z + jx, H / 2 + sy / z + jy
    if z < 1:
        canvas = Image.new('RGBA', (int(W / z) + 4, int(H / z) + 4), (8, 40, 220, 255))
        canvas.alpha_composite(img, ((canvas.width - W) // 2, (canvas.height - H) // 2))
        img = canvas; cx += (canvas.width - W) / 2; cy += (canvas.height - H) / 2
    img = img.rotate(rot + jr, resample=Image.BICUBIC, center=(cx, cy))
    img = img.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BICUBIC)
    # motion blur on fast camera moments (blend with previous frame)
    fast = t < 0.45 or 3.0 < t < 3.35 or t > 9.4
    arr = np.array(img.convert('RGB')).astype(np.float32)
    if fast and prev is not None:
        arr = arr * 0.55 + prev * 0.45
    prev = arr
    img = Image.fromarray(arr.astype(np.uint8)).convert('RGBA')
    # ---- screen-space hyper-motion type
    # QUE NUNCA / EXISTIÓ : slam with overshoot on blue, stop-motion steps
    if 0.9 < t < 3.1:
        tq = (math.floor(t * 12) / 12)
        p1 = seg(tq, 0.95, 1.2); p2 = seg(tq, 1.45, 1.7)
        out = seg(t, 2.75, 3.05)
        paste_center(img, T_QUE_S, 540 - 900 * out, 330, 0.3 + 0.7 * ease_back(p1), -3, p1)
        paste_center(img, T_EXI_S, 540 + 900 * out, 1560, 2.6 - 1.6 * ease_back(p2), 3, p2)
    # NO FUE UN ERROR : emerges from the flames, heat shake, letters glowing
    if 3.15 < t < 4.6:
        p = seg(t, 3.15, 3.45); o = seg(t, 4.25, 4.6)
        sh = 4 * math.sin(t * 80)
        paste_center(img, T_ERR_G, 540 + sh, 1500 - 80 * ease_out(p) - 200 * o, 0.8 + 0.2 * ease_out(p) + 0.4 * o, 0, p * (1 - o))
    # JUEVES drifts away into smoke, SÁBADO bursts out of the fire
    if 7.0 < t < 9.2:
        p = seg(t, 7.0, 7.3); o = seg(t, 8.5, 9.2)
        lay = T_JUE_S.filter(ImageFilter.GaussianBlur(14 * o)) if o > 0 else T_JUE_S
        paste_center(img, lay, 540, 1580 - 300 * o, 1.0 + 0.3 * o, 2 * math.sin(t * 3), p * (1 - o))
    if t > 9.15:
        p = seg(t, 9.15, 9.45)
        paste_center(img, T_SAB_S, 540, 960, 3.2 - 2.2 * ease_back(p), -2, p)
    # grain + vignette
    a = np.array(img.convert('RGB')).astype(np.float32)
    a += np.random.default_rng(i).normal(0, 5, (H, W, 1))
    pipe.stdin.write(a.clip(0, 255).astype(np.uint8).tobytes())
    if i % 48 == 0: print(i, flush=True)
pipe.stdin.close(); pipe.wait()
