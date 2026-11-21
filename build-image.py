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


def stamp(text_lines, border, accent, rotate_deg, emblem="anchor"):
    """One entry/exit stamp on its own layer, slightly rotated.
    Irregular, uneven ink like a real rubber stamp: a faint ghost border
    (the stamp shifted a touch), a slightly fainter outer border, and
    deterministic faded patches where the stamp was pressed unevenly."""
    sw, sh = 410, 104
    layer = Image.new("RGBA", (sw + 24, sh + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0 = 12, 12
    ink = tuple(border) + (255,)
    faint = tuple(border) + (60,)
    # faint ghost border, offset 1px (the stamp shifted a touch on the page)
    d.rounded_rectangle([x0 + 1, y0 + 1, x0 + sw + 1, y0 + sh + 1], radius=10,
                        outline=faint, width=3)
    # outer border, slightly fainter than the inner one
    d.rounded_rectangle([x0, y0, x0 + sw, y0 + sh], radius=10,
                        outline=tuple(border) + (215,), width=3)
    d.rounded_rectangle([x0 + 4, y0 + 4, x0 + sw - 4, y0 + sh - 4], radius=8,
                        outline=ink, width=1)
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
    # Fixed seed per country so each stamp fades differently, yet every run
    # produces the same image.
    seed = 20261121 + sum(ord(c) for c in text_lines[0])
    rng = random.Random(seed)
    mask = Image.new("L", layer.size, 255)
    md = ImageDraw.Draw(mask)
    for _ in range(52):
        x = rng.randint(0, layer.width - 1)
        y = rng.randint(0, layer.height - 1)
        r = rng.randint(3, 10)
        md.ellipse([x - r, y - r, x + r, y + r], fill=rng.randint(170, 235))
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    r_, g_, b_, a_ = layer.split()
    layer = Image.merge("RGBA", (r_, g_, b_, ImageChops.multiply(a_, mask)))
    return layer.rotate(rotate_deg, resample=Image.BICUBIC, expand=False)


def signature(draw, x, y, w):
    """A restrained hand-drawn signature squiggle + rule."""
    pts = [(x + 4, y + 14), (x + 18, y + 4), (x + 30, y + 14), (x + 44, y + 6),
           (x + 58, y + 14), (x + 74, y + 8), (x + 92, y + 14), (x + 110, y + 6),
           (x + 128, y + 13)]
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
