#!/usr/bin/env python3
"""Generate placeholder TRX pose cards (colored background + line-art figure)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "assets" / "illustrations"
W, H = 480, 640
INK = (28, 25, 23, 255)
STRAP = (245, 245, 245, 220)

CARDS: dict[str, tuple[tuple[int, int, int], str]] = {
    "row": ((47, 106, 107), "row"),
    "press": ((196, 92, 78), "press"),
    "squat": ((196, 149, 58), "squat"),
    "lunge": ((106, 127, 70), "lunge"),
    "plank": ((52, 73, 102), "plank"),
    "twist": ((122, 79, 140), "twist"),
    "curl": ((166, 86, 57), "curl"),
    "pull": ((62, 110, 88), "pull"),
    "chest-fly": ((70, 130, 168), "chest-fly"),
    "core-crunch": ((186, 110, 54), "core-crunch"),
    "hinge": ((130, 96, 70), "hinge"),
    "jump": ((90, 140, 92), "jump"),
    "stretch": ((140, 118, 168), "stretch"),
    "default": ((110, 110, 118), "default"),
}


def line(draw: ImageDraw.ImageDraw, a, b, width=9, fill=INK):
    draw.line([a, b], fill=fill, width=width)
    r = width // 2
    for p in (a, b):
        draw.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fill)


def head(draw: ImageDraw.ImageDraw, cx, cy, r=28):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=INK, width=8)


def straps(draw: ImageDraw.ImageDraw, anchors):
    for x, y in anchors:
        line(draw, (x, 70), (x, y), width=7, fill=STRAP)
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=STRAP)


def figure(draw: ImageDraw.ImageDraw, slug: str):
    cx, cy = W // 2, H // 2 + 20

    if slug == "row":
        straps(draw, [(cx - 70, 250), (cx + 70, 250)])
        head(draw, cx, 210)
        line(draw, (cx, 240), (cx, 360))
        line(draw, (cx, 270), (cx - 70, 250))
        line(draw, (cx, 270), (cx + 70, 250))
        line(draw, (cx, 360), (cx - 40, 500))
        line(draw, (cx, 360), (cx + 50, 500))
    elif slug == "press":
        straps(draw, [(cx - 80, 280), (cx + 80, 280)])
        head(draw, cx, 200)
        line(draw, (cx, 230), (cx, 370))
        line(draw, (cx, 270), (cx - 80, 280))
        line(draw, (cx, 270), (cx + 80, 280))
        line(draw, (cx, 370), (cx - 35, 510))
        line(draw, (cx, 370), (cx + 45, 510))
    elif slug == "squat":
        straps(draw, [(cx - 55, 300), (cx + 55, 300)])
        head(draw, cx, 190)
        line(draw, (cx, 220), (cx, 340))
        line(draw, (cx, 260), (cx - 55, 300))
        line(draw, (cx, 260), (cx + 55, 300))
        line(draw, (cx, 340), (cx - 70, 430))
        line(draw, (cx, 340), (cx + 70, 430))
        line(draw, (cx - 70, 430), (cx - 55, 520))
        line(draw, (cx + 70, 430), (cx + 55, 520))
    elif slug == "lunge":
        straps(draw, [(cx - 20, 290)])
        head(draw, cx - 10, 185)
        line(draw, (cx - 10, 215), (cx, 350))
        line(draw, (cx - 10, 250), (cx - 20, 290))
        line(draw, (cx - 10, 250), (cx + 50, 310))
        line(draw, (cx, 350), (cx - 80, 520))
        line(draw, (cx, 350), (cx + 90, 430))
        line(draw, (cx + 90, 430), (cx + 70, 520))
    elif slug == "plank":
        straps(draw, [(160, 300), (320, 300)])
        head(draw, 130, 250)
        line(draw, (155, 270), (360, 280))
        line(draw, (200, 275), (160, 300))
        line(draw, (280, 278), (320, 300))
        line(draw, (360, 280), (390, 360))
        line(draw, (360, 280), (400, 300))
    elif slug == "twist":
        straps(draw, [(cx + 40, 270)])
        head(draw, cx - 10, 195)
        line(draw, (cx - 10, 225), (cx + 10, 360))
        line(draw, (cx, 260), (cx - 90, 300))
        line(draw, (cx, 260), (cx + 40, 270))
        line(draw, (cx + 10, 360), (cx - 50, 510))
        line(draw, (cx + 10, 360), (cx + 70, 510))
    elif slug == "curl":
        straps(draw, [(cx - 50, 320), (cx + 50, 320)])
        head(draw, cx, 185)
        line(draw, (cx, 215), (cx, 360))
        line(draw, (cx, 255), (cx - 50, 250))
        line(draw, (cx - 50, 250), (cx - 50, 320))
        line(draw, (cx, 255), (cx + 50, 250))
        line(draw, (cx + 50, 250), (cx + 50, 320))
        line(draw, (cx, 360), (cx - 40, 510))
        line(draw, (cx, 360), (cx + 40, 510))
    elif slug == "pull":
        straps(draw, [(cx - 40, 230), (cx + 40, 230)])
        head(draw, cx, 280)
        line(draw, (cx, 310), (cx, 400))
        line(draw, (cx, 330), (cx - 40, 230))
        line(draw, (cx, 330), (cx + 40, 230))
        line(draw, (cx, 400), (cx - 35, 520))
        line(draw, (cx, 400), (cx + 40, 520))
    elif slug == "chest-fly":
        straps(draw, [(cx - 110, 270), (cx + 110, 270)])
        head(draw, cx, 195)
        line(draw, (cx, 225), (cx, 365))
        line(draw, (cx, 260), (cx - 110, 270))
        line(draw, (cx, 260), (cx + 110, 270))
        line(draw, (cx, 365), (cx - 40, 510))
        line(draw, (cx, 365), (cx + 45, 510))
    elif slug == "core-crunch":
        straps(draw, [(cx + 30, 250)])
        head(draw, cx - 40, 250)
        line(draw, (cx - 20, 270), (cx + 80, 330))
        line(draw, (cx + 10, 290), (cx + 30, 250))
        line(draw, (cx + 80, 330), (cx + 40, 430))
        line(draw, (cx + 80, 330), (cx + 130, 420))
        line(draw, (cx + 40, 430), (cx - 20, 500))
        line(draw, (cx + 130, 420), (cx + 90, 510))
    elif slug == "hinge":
        straps(draw, [(cx - 10, 280)])
        head(draw, cx - 70, 250)
        line(draw, (cx - 50, 270), (cx + 40, 320))
        line(draw, (cx, 295), (cx - 10, 280))
        line(draw, (cx + 40, 320), (cx + 20, 510))
        line(draw, (cx + 40, 320), (cx + 90, 510))
    elif slug == "jump":
        straps(draw, [(cx - 30, 240), (cx + 30, 240)])
        head(draw, cx, 160)
        line(draw, (cx, 190), (cx, 320))
        line(draw, (cx, 230), (cx - 70, 200))
        line(draw, (cx, 230), (cx + 70, 200))
        line(draw, (cx, 320), (cx - 55, 430))
        line(draw, (cx, 320), (cx + 55, 430))
        line(draw, (cx - 70, 500), (cx + 70, 500), width=6, fill=(255, 255, 255, 160))
    elif slug == "stretch":
        straps(draw, [(cx - 20, 180)])
        head(draw, cx, 230)
        line(draw, (cx, 260), (cx, 390))
        line(draw, (cx, 280), (cx - 70, 200))
        line(draw, (cx, 280), (cx + 20, 180))
        line(draw, (cx, 390), (cx - 45, 520))
        line(draw, (cx, 390), (cx + 40, 520))
    else:
        head(draw, cx, 190)
        line(draw, (cx, 220), (cx, 370))
        line(draw, (cx, 260), (cx - 70, 320))
        line(draw, (cx, 260), (cx + 70, 320))
        line(draw, (cx, 370), (cx - 40, 520))
        line(draw, (cx, 370), (cx + 40, 520))


def render(slug: str, color: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGBA", (W, H), (*color, 255))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((18, 18, W - 18, H - 18), radius=36, outline=(255, 255, 255, 70), width=4)
    figure(draw, slug)
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, (color, _) in CARDS.items():
        render(slug, color).save(OUT / f"{slug}.png", "PNG")
        print(f"wrote {slug}.png")


if __name__ == "__main__":
    main()
