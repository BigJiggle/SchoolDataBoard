"""Draws the app icon (graphite tile with the SchoolBoard mark) as icon.png, icon.ico and icon.icns.

    python desktop/make_icon.py
"""

import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 1024


def draw() -> Image.Image:
    k = 4  # draw at 4x and scale down for smooth edges
    n = SIZE * k
    pad, radius = 92 * k, 200 * k
    # Tile: a soft vertical graphite gradient.
    grad = Image.new("RGBA", (1, n))
    for y in range(n):
        t = y / n
        c = int(46 - 18 * t)
        grad.putpixel((0, y), (c, c + 2, c + 6, 255))
    tile = grad.resize((n, n))
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).rounded_rectangle([pad, pad, n - pad, n - pad], radius=radius, fill=255)
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    img.paste(tile, (0, 0), mask)
    # The mark: an open cup ("U") with rounded ends, like the sidebar logo.
    w = 76 * k
    left, right, top, bottom = 318 * k, 706 * k, 300 * k, 724 * k
    u = Image.new("L", (n, n), 0)
    du = ImageDraw.Draw(u)
    du.rounded_rectangle([left, top - 400 * k, right, bottom], radius=(right - left) // 2, fill=255)
    du.rounded_rectangle([left + w, top - 400 * k, right - w, bottom - w], radius=(right - left - 2 * w) // 2, fill=0)
    du.rectangle([0, 0, n, top], fill=0)
    for x in (left + w // 2, right - w // 2):
        du.ellipse([x - w // 2, top - w // 2, x + w // 2, top + w // 2], fill=255)
    img.paste((255, 255, 255, 255), (0, 0), u)
    return img.resize((SIZE, SIZE), Image.LANCZOS)


if __name__ == "__main__":
    img = draw()
    img.save(os.path.join(HERE, "icon.png"))
    img.save(os.path.join(HERE, "icon.ico"), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    img.save(os.path.join(HERE, "icon.icns"))
    print("wrote icon.png, icon.ico, icon.icns")
