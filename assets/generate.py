#!/usr/bin/env python3
"""Regenerate the Nexus page images from the source screenshot.

  assets/header-mod-warning-skip-1300x372.jpg   (dialog crop + title overlay, banner)
  assets/gallery-mod-warning-skip-1920x1080.jpg (screenshot with red X, gallery)

The header is a band cropped around the warning dialog, with the title
top-left over a darkened left edge (same layout as the bigger-inventory
header).

Usage: python3 assets/generate.py   (or: make assets)
Requires: Pillow (pip install Pillow). Typeface is vendored (see FONT).
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "warning.jpg")
HDR = os.path.join(HERE, "header-mod-warning-skip-1300x372.jpg")
GALLERY = os.path.join(HERE, "gallery-mod-warning-skip-1920x1080.jpg")

# In-game heading typeface, vendored (SIL OFL 1.1):
# https://github.com/NMSCD/No-Mans-Sky-Universal-Font
FONT = os.path.join(HERE, "fonts", "GeosansLight-NMS.ttf")

TITLE = ["MOD WARNING SKIP"]
SUBTITLE = "REMOVES THE MOD WARNING MESSAGE"

# Header crop, in source pixels: keeps the warning dialog centered in
# the frame and in the lower part, clear of the top-left title.
HDR_X = 0
HDR_Y = 155
HDR_W = 1820

# Header size in output pixels.
HDR_OUT_W = 1300
HDR_OUT_H = 372

# Title placement in the header.
TITLE_X = 48
TITLE_Y = 48
TITLE_SIZE = 50
TITLE_GAP = 62
SUBTITLE_SIZE = 30

X_RED = (255, 57, 0)


def text_shadowed(d, xy, s, font, fill):
    x, y = xy
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, -2), (-2, 2), (2, 2)):
        d.text((x + dx, y + dy), s, font=font, fill=(0, 0, 0))
    d.text((x, y), s, font=font, fill=fill)


def header():
    img = Image.open(SRC).convert("RGB")
    assert img.size[0] * 9 == img.size[1] * 16, f"source is not 16:9: {img.size}"
    assert img.size[0] >= HDR_X + HDR_W, f"crop too wide for source: {img.size}"

    band_h = int(HDR_W * HDR_OUT_H / HDR_OUT_W)
    band = img.crop((HDR_X, HDR_Y, HDR_X + HDR_W, HDR_Y + band_h))
    band = band.resize((HDR_OUT_W, HDR_OUT_H), Image.LANCZOS)
    d = ImageDraw.Draw(band, "RGBA")
    # left-weighted gradient: title sits on the left
    for x in range(HDR_OUT_W):
        a = int(205 * max(0.0, 1 - x / (HDR_OUT_W * 0.62)) ** 1.5)
        d.rectangle([x, 0, x + 1, HDR_OUT_H], fill=(0, 0, 0, a))
    band = band.convert("RGB")
    d = ImageDraw.Draw(band)
    fb = ImageFont.truetype(FONT, TITLE_SIZE)
    fs = ImageFont.truetype(FONT, SUBTITLE_SIZE)

    for i, line in enumerate(TITLE):
        text_shadowed(d, (TITLE_X, TITLE_Y + i * TITLE_GAP), line, fb, (255, 255, 255))
    text_shadowed(
        d,
        (TITLE_X + 2, TITLE_Y + len(TITLE) * TITLE_GAP + 8),
        SUBTITLE,
        fs,
        (255, 205, 130),
    )
    band.save(HDR, quality=92)
    print(f"wrote {HDR}")


def gallery():
    w, h = 1920, 1080
    src = Image.open(SRC).convert("RGB")
    scale = max(w / src.width, h / src.height)
    img = src.resize(
        (round(src.width * scale), round(src.height * scale)), Image.LANCZOS
    )
    left = (img.width - w) // 2
    top = (img.height - h) // 2
    img = img.crop((left, top, left + w, top + h))
    # The game draws the dialog left of center; recenter it horizontally
    # so the gallery reads cleanly. Kept vertically where it is so the
    # title stays clear of the X crossing. The backdrop is black, so the
    # shift is seamless.
    bbox = img.convert("L").point(lambda v: 255 if v > 60 else 0).getbbox()
    if bbox:
        dx = round(w / 2 - (bbox[0] + bbox[2]) / 2)
        canvas = Image.new("RGB", (w, h))
        canvas.paste(img, (dx, 0))
        img = canvas
    d = ImageDraw.Draw(img)
    d.line([(0, 0), (w, h)], fill=(0, 0, 0), width=30)
    d.line([(w, 0), (0, h)], fill=(0, 0, 0), width=30)
    d.line([(0, 0), (w, h)], fill=X_RED, width=22)
    d.line([(w, 0), (0, h)], fill=X_RED, width=22)
    img.save(GALLERY, quality=92)
    print(f"wrote {GALLERY}")


if __name__ == "__main__":
    header()
    gallery()
