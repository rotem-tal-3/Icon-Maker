"""
Icon Maker
-------------------
Generate Chrome extension icons from the given source image). Produces icon16/32/48/128/256/512.png.

Features
- Square export with two strategies:
  * contain (default): keep aspect ratio, pad to square with transparent or color bg
  * cover: center-crop to square before resizing
- Rounded edges
- Zips all outputs by default

Examples
--------
# Basic (contain-fit into square, transparent background)
python icon_maker_simple.py -i face.png -o ./icons

# Cover-crop to square first, then resize
python icon_maker_simple.py -i face.png -o ./icons --mode cover

# Use a solid background when padding (hex or css name understood by PIL)
python icon_maker_simple.py -i face.png -o ./icons --bg "#0f172a"

# Custom size set, no zip, make the images round
python icon_maker_simple.py -i face.png -o ./icons --sizes 16 32 48 128 256 512 --no-zip --round
"""

from PIL import Image, ImageDraw, ImageColor
import argparse
import sys
import os
import zipfile

LANCZOS = Image.LANCZOS

def parse_args():
    p = argparse.ArgumentParser(description="Generate Chrome extension icons from a single image.",
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("-i", "--input", required=True, help="Path to source image (PNG/JPG).")
    p.add_argument("-o", "--outdir", default="./icons_out", help="Directory to write outputs.")
    p.add_argument("--sizes", nargs="+", type=int, default=[16, 32, 48, 128],
                   help="Icon sizes to export (px).")
    p.add_argument("--mode", choices=["contain","cover"], default="contain",
                   help="Square handling: 'contain' pads to square; 'cover' center-crops to " +
                        "square.")
    p.add_argument("--bg", default="transparent",
                   help="Background when --mode=contain (e.g., '#0f172a' or 'transparent').")
    p.add_argument("--round", action="store_true",
                   help="Round the edges to create a circular icon.")
    p.add_argument("--zip", dest="make_zip", action="store_true",
                   help="Create a .zip with all outputs.")
    p.add_argument("--no-zip", dest="make_zip", action="store_false", help="Do not zip outputs.")
    p.set_defaults(make_zip=True)

    if len(sys.argv) == 1:
        p.print_help(sys.stderr)
        sys.exit(1)
    return p.parse_args()
def parse_bg(color_str):
    if color_str.lower() == "transparent":
        return None
    try:
        return ImageColor.getrgb(color_str)
    except ValueError:
        raise SystemExit(f"Invalid --bg color: {color_str}")

def square_contain(im, size, bg_rgb):
    """Fit image into size x size, preserving aspect. Pad with bg (or transparent)."""
    im = im.convert("RGBA")
    w, h = im.size
    scale = min(size / w, size / h)
    nw, nh = int(w * scale), int(h * scale)
    resized = im.resize((nw, nh), LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0,0,0,0) if bg_rgb is None else (*bg_rgb,255))
    x = (size - nw) // 2
    y = (size - nh) // 2
    canvas.paste(resized, (x, y), resized)
    return canvas

def square_cover(im):
    """Center-crop to square (min side) then return RGBA."""
    im = im.convert("RGBA")
    w, h = im.size
    side = min(w, h)
    x0 = (w - side) // 2
    y0 = (h - side) // 2
    return im.crop((x0, y0, x0+side, y0+side))

def make_round(im):
    """Circular mask of an image (assumes square)."""
    im = im.convert("RGBA")
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, w, h), fill=255)
    out = Image.new("RGBA", (w, h))
    out.paste(im, (0, 0), mask)
    return out

def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    src = Image.open(args.input)
    bg_rgb = parse_bg(args.bg)
    if args.mode == "cover":
        master_square = square_cover(src).resize((1024, 1024), LANCZOS)
    else:
        master_square = square_contain(src, 1024, bg_rgb)

    outputs = []
    for s in args.sizes:
        icon_sq = master_square.resize((s, s), LANCZOS)
        path_sq = os.path.join(args.outdir, f"icon{s}.png")
        icon_sq.save(path_sq, optimize=True)
        outputs.append(path_sq)

        if args.round:
            path_rd = os.path.join(args.outdir, f"icon{s}_round.png")
            make_round(icon_sq).save(path_rd, optimize=True)
            outputs.append(path_rd)

    if args.make_zip:
        zip_path = os.path.join(args.outdir, "icons_bundle.zip")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in outputs:
                zf.write(f, arcname=os.path.basename(f))
        print(zip_path)
    else:
        print(args.outdir)

if __name__ == "__main__":
    main()