#!/usr/bin/env python3
"""Generate Boop app icon - magic wand with sparkles"""

from PIL import Image, ImageDraw
from pathlib import Path
import subprocess
import tempfile
import math


def create_icon(size: int) -> Image.Image:
    """Create a magic wand icon with sparkles."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    padding = size // 8

    # Purple gradient-ish background (magic vibes)
    draw.rounded_rectangle(
        [padding, padding, size - padding, size - padding],
        radius=size // 5,
        fill=(138, 79, 255)  # Nice purple
    )

    # Magic wand (diagonal, bottom-left to top-right)
    wand_width = size // 12
    center = size // 2

    # Wand body (cream/white color)
    wand_length = size // 2.5
    angle = -45  # degrees

    # Calculate wand endpoints
    rad = math.radians(angle)
    x1 = center - math.cos(rad) * wand_length / 2
    y1 = center - math.sin(rad) * wand_length / 2
    x2 = center + math.cos(rad) * wand_length / 2
    y2 = center + math.sin(rad) * wand_length / 2

    # Draw wand body (slightly offset for thickness)
    for offset in range(-wand_width // 2, wand_width // 2 + 1):
        draw.line([(x1, y1 + offset), (x2, y2 + offset)], fill=(255, 248, 230), width=2)

    # Wand tip (star/sparkle)
    tip_x, tip_y = x2, y2
    star_size = size // 8

    # Draw a 4-point star at the tip
    def draw_star(cx, cy, outer_r, inner_r, points=4):
        coords = []
        for i in range(points * 2):
            angle = math.radians(i * 180 / points - 90)
            r = outer_r if i % 2 == 0 else inner_r
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            coords.append((x, y))
        return coords

    # Main star at wand tip
    star_coords = draw_star(tip_x - size//12, tip_y - size//12, star_size, star_size // 3)
    draw.polygon(star_coords, fill=(255, 255, 150))  # Yellow star

    # Small sparkles around
    sparkle_positions = [
        (tip_x - size//5, tip_y - size//4, size//16),
        (tip_x - size//20, tip_y - size//3.5, size//20),
        (tip_x - size//3.5, tip_y - size//10, size//18),
    ]

    for sx, sy, sr in sparkle_positions:
        small_star = draw_star(sx, sy, sr, sr // 2.5)
        draw.polygon(small_star, fill=(255, 255, 200))

    # Tiny dots for extra magic
    dot_positions = [
        (tip_x - size//4, tip_y - size//5),
        (tip_x - size//8, tip_y - size//2.5),
        (tip_x - size//2.8, tip_y - size//6),
    ]
    for dx, dy in dot_positions:
        r = size // 40
        draw.ellipse([dx - r, dy - r, dx + r, dy + r], fill=(255, 255, 255))

    return img


def main():
    output_dir = Path(__file__).parent

    with tempfile.TemporaryDirectory() as tmpdir:
        iconset = Path(tmpdir) / "AppIcon.iconset"
        iconset.mkdir()

        # Create all required sizes
        for s in [16, 32, 128, 256, 512]:
            create_icon(s).save(iconset / f"icon_{s}x{s}.png")
            create_icon(s * 2).save(iconset / f"icon_{s}x{s}@2x.png")

        # Convert to icns
        icns_path = output_dir / "AppIcon.icns"
        subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(icns_path)], check=True)
        print(f"Created {icns_path}")


if __name__ == "__main__":
    main()
