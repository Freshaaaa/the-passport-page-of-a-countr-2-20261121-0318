#!/usr/bin/env python3
"""Build the invented passport spread for the make.fun competition
'The Passport Page of a Country That Isn't There'.

Draws a 1024x724 landscape spread (data page left, visas page right) for the
invented Republic of Meridia. PIL only, no network, no randomness, no clock:
running it twice produces a byte-identical PNG.
"""

import hashlib
import os
import random
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1024, 724
CREAM = (246, 241, 227)
CREAM_BAND = (238, 231, 212)
NAVY = (27, 42, 74)
NAVY_SOFT = (74, 88, 122)
GREY = (110, 108, 96)
RED = (139, 30, 45)
GREEN = (31, 92, 61)
GOLD = (180, 141, 38)
SKIN = (227, 185, 143)
SKIN_DARK = (205, 160, 118)
HAIR = (43, 35, 32)
BLAZER = (42, 58, 85)
PORTRAIT_BG = (185, 196, 206)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
MONO = os.path.join(FONT_DIR, "DejaVuSansMono.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def text(draw, xy, s, fnt, fill=NAVY, anchor="la"):
    draw.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def tracked(draw, cx, y, s, fnt, fill=NAVY, tracking=2):
    """Draw text centred at cx with manual letter tracking."""
    widths = [draw.textlength(ch, font=fnt) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2.0
    for ch, w in zip(s, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def wrap(draw, s, fnt, max_w):
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def lighthouse(draw, cx, top, scale=1.0):
    """Small navy lighthouse coat of arms with waves, centred at cx."""
    # light beams (gold, thin wedges radiating up and out from the lamp)
    draw.polygon([(cx - 4, top + 12), (cx - 36, top - 8), (cx - 28, top + 2)], fill=GOLD)
    draw.polygon([(cx + 4, top + 12), (cx + 36, top - 8), (cx + 28, top + 2)], fill=GOLD)
    # lamp room
    draw.rectangle([cx - 5, top + 8, cx + 5, top + 16], fill=NAVY)
    draw.polygon([(cx - 7, top + 8), (cx + 7, top + 8), (cx, top + 1)], fill=NAVY)
    # gallery
    draw.rectangle([cx - 9, top + 16, cx + 9, top + 19], fill=NAVY)
    # tower (slightly tapered)
    draw.polygon([(cx - 8, top + 48), (cx + 8, top + 48),
                  (cx + 5, top + 19), (cx - 5, top + 19)], fill=NAVY)
    # tower stripe
    draw.polygon([(cx - 7, top + 34), (cx + 7, top + 34),
                  (cx + 6, top + 28), (cx - 6, top + 28)], fill=CREAM)
    # waves
    for i, wy in enumerate((top + 52, top + 58)):
        draw.arc([cx - 26 + i * 3, wy, cx + 26 - i * 3, wy + 12], 180, 360, fill=NAVY, width=2)
    draw.line([cx - 30, top + 52, cx + 30, top + 52], fill=NAVY, width=1)


def portrait():
    """Passport portrait from the photorealistic photo (fictional person):
    loads portrait.png (240x300, centre-cropped 4:5), resizes it to the
    120x150 box and adds the same navy frame as before."""
    pw, ph = 120, 150
    here = os.path.dirname(os.path.abspath(__file__))
    photo = Image.open(os.path.join(here, "portrait.png")).convert("RGB")
    # portrait.png is already 4:5; resize to the box, then frame it
    img = photo.resize((pw, ph), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, pw - 1, ph - 1], outline=NAVY, width=2)
    return img


def field(draw, x, y, label, value, label_size=10, value_size=14, width=200):
    text(draw, (x, y), label, font(SANS, label_size), fill=GREY)
    text(draw, (x, y + 14), value, font(SANS_BOLD, value_size), fill=NAVY)


def _jittered_rect(draw, x0, y0, x1, y1, radius, rng, fill, width,
                   jitter=1.3, gaps=0):
    """Rounded-rectangle border with a hand-stamped wobble: every perimeter
    point is jittered a touch, and optionally a few short stretches are
    erased where the ink skipped. Deterministic (uses the caller's rng)."""
    import math
    pts = []

    def arc(cx, cy, r, a0, a1):
        n = max(2, int(abs(a1 - a0) * r / 6))
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    def edge(xa, ya, xb, yb):
        n = max(2, int(math.hypot(xb - xa, yb - ya) / 6))
        for i in range(n + 1):
            pts.append((xa + (xb - xa) * i / n, ya + (yb - ya) * i / n))

    edge(x0 + radius, y0, x1 - radius, y0)              # top
    arc(x1 - radius, y0 + radius, radius, -90, 0)       # top-right corner
    edge(x1, y0 + radius, x1, y1 - radius)              # right
    arc(x1 - radius, y1 - radius, radius, 0, 90)        # bottom-right corner
    edge(x1 - radius, y1, x0 + radius, y1)              # bottom
    arc(x0 + radius, y1 - radius, radius, 90, 180)      # bottom-left corner
    edge(x0, y1 - radius, x0, y0 + radius)              # left
    arc(x0 + radius, y0 + radius, radius, 180, 270)     # top-left corner
    jpts = [(px + rng.uniform(-jitter, jitter),
             py + rng.uniform(-jitter, jitter)) for px, py in pts]
    draw.line(jpts + [jpts[0]], fill=fill, width=width, joint="curve")
    for _ in range(gaps):
        i = rng.randrange(4, len(jpts) - 8)
        draw.line(jpts[i:i + 5], fill=(0, 0, 0, 0), width=width + 1)


def stamp(text_lines, border, accent, rotate_deg, emblem="anchor"):
    """One entry/exit stamp on its own layer, slightly rotated.
    Irregular, uneven ink like a real rubber stamp: a wobbling border with
    a few gaps where the ink skipped, a faint double impression (the stamp
    bounced when it hit the page), and deterministic faded patches, coarse
    dry areas and fine grain where it was pressed unevenly. All randomness
    uses one fixed seed per country, so every run produces the same image."""
    sw, sh = 410, 104
    layer = Image.new("RGBA", (sw + 24, sh + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0 = 12, 12
    ink = tuple(border) + (255,)
    # Fixed seed per country so each stamp wears differently, yet every run
    # produces the same image. (The rng is created here so the border wobble,
    # the ink gaps and the masks below all draw from one sequence.)
    seed = 20261121 + sum(ord(c) for c in text_lines[0])
    rng = random.Random(seed)
    # double impression: ghost of the whole frame, offset (2,1), faint —
    # the stamp bounced a touch when it hit the page
    _jittered_rect(d, x0 + 2, y0 + 1, x0 + sw + 2, y0 + sh + 1, 10,
                   rng, tuple(border) + (55,), 3, jitter=1.0)
    # main outer border: wobbles like a hand-pressed stamp, with a few
    # short gaps where the ink skipped
    _jittered_rect(d, x0, y0, x0 + sw, y0 + sh, 10,
                   rng, tuple(border) + (215,), 3, gaps=3)
    # inner border, lightly wobbled too
    _jittered_rect(d, x0 + 4, y0 + 4, x0 + sw - 4, y0 + sh - 4, 8,
                   rng, ink, 1, jitter=0.8)
    # emblem: circle with a small anchor
    ex, ey, er = x0 + 16, y0 + sh // 2, 26
    d.ellipse([ex, ey - er, ex + 2 * er, ey + er], outline=ink, width=2)
    d.line([ex + er, ey - 14, ex + er, ey + 12], fill=ink, width=2)
    d.arc([ex + er - 8, ey + 4, ex + er + 8, ey + 18], 0, 180, fill=ink, width=2)
    d.line([ex + er - 10, ey - 4, ex + er + 10, ey - 4], fill=ink, width=2)
    d.ellipse([ex + er - 3, ey - 17, ex + er + 3, ey - 11], outline=ink, width=2)
    # country + entry/exit
    tx = x0 + 84
    text(d, (tx, y0 + 10), text_lines[0], font(SANS_BOLD, 17), fill=ink)
    text(d, (tx, y0 + 38), text_lines[1], font(SANS, 13), fill=ink)
    text(d, (tx, y0 + 60), text_lines[2], font(SANS, 13), fill=ink)
    # uneven ink: deterministic faded patches (pressed unevenly).
    mask = Image.new("L", layer.size, 255)
    md = ImageDraw.Draw(mask)
    for _ in range(52):
        x = rng.randint(0, layer.width - 1)
        y = rng.randint(0, layer.height - 1)
        r = rng.randint(3, 10)
        md.ellipse([x - r, y - r, x + r, y + r], fill=rng.randint(170, 235))
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    # coarse uneven ink: a few larger faded areas where the stamp pad was
    # dry or the page was pressed unevenly (kept light so text stays legible)
    coarse = Image.new("L", layer.size, 255)
    cd = ImageDraw.Draw(coarse)
    for _ in range(16):
        x = rng.randint(0, layer.width - 1)
        y = rng.randint(0, layer.height - 1)
        r = rng.randint(10, 24)
        cd.ellipse([x - r, y - r, x + r, y + r], fill=rng.randint(160, 210))
    coarse = coarse.filter(ImageFilter.GaussianBlur(6))
    mask = ImageChops.multiply(mask, coarse)
    # fine grain: the paper's tooth showing through thin ink
    grain = Image.new("L", layer.size, 255)
    gd = ImageDraw.Draw(grain)
    for _ in range(500):
        x = rng.randint(0, layer.width - 1)
        y = rng.randint(0, layer.height - 1)
        gd.point((x, y), fill=rng.randint(180, 240))
    grain = grain.filter(ImageFilter.GaussianBlur(0.5))
    mask = ImageChops.multiply(mask, grain)
    r_, g_, b_, a_ = layer.split()
    layer = Image.merge("RGBA", (r_, g_, b_, ImageChops.multiply(a_, mask)))
    # slight ink bleed into the paper fibres
    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    return layer.rotate(rotate_deg, resample=Image.BICUBIC, expand=False)


def _bezier(p0, p1, p2, p3, n=20):
    """Sample a cubic bezier curve (deterministic, no randomness)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1.0 - t
        pts.append((
            mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0]
            + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
            mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1]
            + 3 * mt * t * t * p2[1] + t ** 3 * p3[1],
        ))
    return pts


def signature(draw, x, y, w):
    """A flowing handwritten signature: an initial loop, a scrawled body
    with pen lifts, and a long underline flourish — a quick cursive
    signature, not readable text and not a zigzag. Drawn in a 170x16 box
    above the rule; a softer wide pass under a crisp narrow pass gives
    the stroke pen pressure."""
    loop = (
        ((10, 13), (5, 3), (16, 0), (24, 5)),
        ((24, 5), (29, 11), (21, 15), (14, 13)),
    )
    body = (
        ((18, 11), (26, 9), (31, 5), (38, 5)),
        ((38, 5), (46, 5), (48, 11), (53, 13)),
        ((53, 13), (57, 6), (65, 3), (73, 6)),
        ((73, 6), (79, 10), (81, 13), (87, 12)),
        ((87, 12), (89, 3), (99, 2), (103, 8)),
        ((103, 8), (105, 13), (99, 15), (92, 13)),
    )
    flourish = (
        ((98, 10), (112, 7), (128, 6), (146, 10)),
        ((146, 10), (156, 14), (166, 12), (170, 5)),
    )
    for stroke in (loop, body, flourish):
        pts = []
        for seg in stroke:
            pts.extend(_bezier(*seg))
        pts = [(x + px, y + py) for px, py in pts]
        draw.line(pts, fill=(70, 88, 125), width=3, joint="curve")
        draw.line(pts, fill=NAVY, width=2, joint="curve")
    draw.line([x, y + 20, x + w, y + 20], fill=NAVY, width=1)
    text(draw, (x, y + 26), "HOLDER'S SIGNATURE", font(SANS, 9), fill=GREY)


def _mrz_check_digit(field):
    """ICAO 9303 check digit: weights 7,3,1 repeating; A=10..Z=35, '<'=0."""
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(field):
        if ch == "<":
            value = 0
        elif ch.isdigit():
            value = int(ch)
        else:
            value = ord(ch) - 55  # A=10, B=11, ..., Z=35
        total += value * weights[i % 3]
    return str(total % 10)


def mrz_lines():
    # Data page fields (must agree with the printed data above the MRZ band).
    doc_number = "M20417783"   # passport M-2041-7783
    nationality = "MER"
    birth = "920314"           # 14 MAR 1992
    sex = "F"
    expiry = "340602"          # 02 JUN 2034
    personal = "<" * 14         # no personal number on this document

    # Line 1: type + issuing state + surname + separator + given names.
    line1_base = "P<MER" + "VOSS<<ELENA<MARA"
    line1 = line1_base + "<" * (44 - len(line1_base))

    # Line 2 (TD3): doc number + check, nationality, birth + check, sex,
    # expiry + check, personal number + check, composite check.
    core = (
        doc_number + _mrz_check_digit(doc_number)
        + nationality
        + birth + _mrz_check_digit(birth)
        + sex
        + expiry + _mrz_check_digit(expiry)
        + personal + _mrz_check_digit(personal)
    )
    line2 = core + _mrz_check_digit(core)
    assert len(line1) == 44 and len(line2) == 44
    return line1, line2


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # outer border + centre gutter
    d.rectangle([14, 14, W - 15, H - 15], outline=NAVY, width=2)
    d.line([W // 2, 22, W // 2, H - 22], fill=(190, 184, 164), width=1)

    # ---------------- LEFT PAGE: data page ----------------
    lx, lw = 36, 448
    cx = lx + lw // 2

    lighthouse(d, cx, 34)
    tracked(d, cx, 100, "REPUBLIC OF MERIDIA", font(SANS_BOLD, 20), fill=NAVY, tracking=2)
    tracked(d, cx, 128, "PASSPORT  ·  PASAPORTA", font(SANS, 12), fill=NAVY_SOFT, tracking=1)
    d.line([lx + 8, 152, lx + lw - 8, 152], fill=NAVY, width=1)

    # portrait + fields beside it
    img.paste(portrait(), (lx + 12, 170))
    fx = lx + 152
    field(d, fx, 170, "SURNAME / SURNAM", "VOSS")
    field(d, fx, 208, "GIVEN NAMES", "ELENA MARA")
    field(d, fx, 246, "NATIONALITY", "MERIDIAN")
    field(d, fx, 284, "DATE OF BIRTH", "14 MAR 1992")

    # second field grid
    col2 = lx + 240
    field(d, lx + 12, 348, "PLACE OF BIRTH / PLAS NASK", "PORT MERIDIAN")
    field(d, col2, 348, "PASSPORT NO.", "M-2041-7783")
    field(d, lx + 12, 396, "SEX", "F")
    field(d, col2, 396, "DATE OF ISSUE", "03 JUN 2024")
    field(d, lx + 12, 444, "TYPE", "P")
    field(d, col2, 444, "DATE OF EXPIRY", "02 JUN 2034")
    field(d, lx + 12, 492, "AUTHORITY", "PORT MERIDIAN")
    field(d, col2, 492, "COUNTRY CODE", "MER")

    # signature
    signature(d, lx + 12, 536, 170)

    # MRZ band
    d.rectangle([lx + 8, 596, lx + lw - 8, 668], fill=CREAM_BAND, outline=NAVY, width=1)
    l1, l2 = mrz_lines()
    mono = font(MONO, 14)
    text(d, (lx + 20, 606), l1, mono, fill=NAVY)
    text(d, (lx + 20, 632), l2, mono, fill=NAVY)
    text(d, (cx, 686), "1", font(SANS, 10), fill=GREY, anchor="ma")

    # ---------------- RIGHT PAGE: visas ----------------
    rx, rw = 540, 448
    text(d, (rx, 34), "VISAS", font(SANS_BOLD, 16), fill=NAVY)
    d.line([rx, 60, rx + rw - 8, 60], fill=NAVY, width=1)

    stamps = [
        (["CALDORIA", "ENTRY   12 SEP 2024", "EXIT      20 SEP 2024"], RED, -2.0),
        (["VESPER ISLES", "ENTRY   05 FEB 2025", "EXIT      11 FEB 2025"], NAVY, 1.5),
        (["NORDMARK", "ENTRY   18 JUL 2025", "EXIT      02 AUG 2025"], GREEN, -1.0),
    ]
    y = 76
    for lines, colour, rot in stamps:
        s = stamp(lines, colour, colour, rot)
        img.paste(s, (rx - 4, y), s)
        y += 116

    # condition box — the telling detail
    by = 428
    d.rectangle([rx, by, rx + rw - 8, by + 92], outline=NAVY, width=2)
    text(d, (rx + 14, by + 12), "CONDITION", font(SANS_BOLD, 12), fill=NAVY)
    cond = ("Holder must report to the Harbour Master "
            "within 24 hours of arrival.")
    lines = wrap(d, cond, font(SANS, 12), rw - 36)
    cy = by + 34
    for ln in lines:
        text(d, (rx + 14, cy), ln, font(SANS, 12), fill=NAVY)
        cy += 17
    text(d, (rx + 14, by + 72), "Harbour Master's Office, Port Meridian",
         font(SANS, 10), fill=GREY)

    # harbour fee stamp
    fee = Image.new("RGBA", (300, 64), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fee)
    fd.rounded_rectangle([4, 4, 296, 60], radius=8, outline=RED, width=3)
    text(fd, (150, 12), "HARBOUR FEE PAID", font(SANS_BOLD, 15), fill=RED, anchor="ma")
    text(fd, (150, 34), "12 CROWNS", font(SANS_BOLD, 13), fill=RED, anchor="ma")
    fee = fee.rotate(-4, resample=Image.BICUBIC, expand=False)
    img.paste(fee, (rx + 120, 548), fee)

    text(d, (rx + rw - 8, 686), "2", font(SANS, 10), fill=GREY, anchor="ma")
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = build()
    img.save(out, format="PNG", optimize=True)
    data = open(out, "rb").read()
    print("entry.png:", len(data), "bytes,",
          hashlib.sha256(data).hexdigest(), "size", img.size)


if __name__ == "__main__":
    main()
