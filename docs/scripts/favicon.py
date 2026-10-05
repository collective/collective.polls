"""Build ``docs/_static/favicon.ico`` from ``docs/_static/logo.svg``.

The icon holds one PNG image per size, rendered with ``rsvg-convert``
(librsvg). Run it with ``make favicon`` after changing the logo.
"""

import struct
import subprocess
from pathlib import Path

STATIC = Path(__file__).resolve().parent.parent / "docs" / "_static"
SIZES = (16, 32, 48)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def render(svg: Path, size: int) -> bytes:
    """Render the SVG as a square PNG.

    :param svg: The SVG file to render.
    :param size: Width and height of the PNG, in pixels.
    :returns: The PNG data.
    """
    png = subprocess.run(
        ["rsvg-convert", "-w", str(size), "-h", str(size), str(svg)],
        check=True,
        capture_output=True,
    ).stdout
    if not png.startswith(PNG_SIGNATURE):
        raise RuntimeError(f"rsvg-convert did not return a PNG for size {size}")
    return png


def build_ico(images: dict[int, bytes]) -> bytes:
    """Pack PNG images into an ICO file.

    :param images: PNG data per size, in pixels.
    :returns: The ICO data.
    """
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = len(header) + 16 * len(images)
    entries = b""
    for size, png in images.items():
        entries += struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(png), offset)
        offset += len(png)
    return header + entries + b"".join(images.values())


def main() -> None:
    """Write the favicon next to the logo."""
    images = {size: render(STATIC / "logo.svg", size) for size in SIZES}
    target = STATIC / "favicon.ico"
    target.write_bytes(build_ico(images))
    print(f"Wrote {target.name}: sizes {', '.join(map(str, SIZES))}")


if __name__ == "__main__":
    main()
