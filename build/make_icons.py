"""Generate raster favicon variants (.ico and apple-touch-icon.png).

Run from project root:
    python build/make_icons.py

Outputs:
    assets/favicon.ico       - multi-size 16/32/48 for legacy browsers
    assets/favicon-32.png    - 32x32 PNG fallback
    assets/apple-touch-icon.png - 180x180 for iOS home screen
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

ORANGE = (204, 119, 82, 255)        # #cc7752
WHITE = (255, 255, 255, 255)


def find_bold_font(target_size: int) -> ImageFont.FreeTypeFont:
    """Find a bold sans-serif font that exists on this OS."""
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",     # Segoe UI Bold (Windows)
        "C:/Windows/Fonts/arialbd.ttf",      # Arial Bold (Windows)
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, target_size)
    return ImageFont.load_default()


def render_icon(size: int) -> Image.Image:
    """Render a square LC monogram on a rounded orange background."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    radius = max(2, round(size * 0.22))
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=ORANGE)

    font_size = round(size * 0.5)
    font = find_bold_font(font_size)
    text = "LC"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # textbbox returns (left, top, right, bottom) — top can be non-zero, account for it
    tx = (size - tw) / 2 - bbox[0]
    ty = (size - th) / 2 - bbox[1]
    draw.text((tx, ty), text, font=font, fill=WHITE)
    return img


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    icon_180 = render_icon(180)
    icon_180.save(OUT / "apple-touch-icon.png", format="PNG", optimize=True)
    print(f"wrote {OUT / 'apple-touch-icon.png'} (180x180)")

    icon_32 = render_icon(32)
    icon_32.save(OUT / "favicon-32.png", format="PNG", optimize=True)
    print(f"wrote {OUT / 'favicon-32.png'} (32x32)")

    icon_16 = render_icon(16)
    icon_48 = render_icon(48)
    icon_16.save(
        OUT / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=[icon_32, icon_48],
    )
    print(f"wrote {OUT / 'favicon.ico'} (multi-size)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
