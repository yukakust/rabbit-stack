#!/usr/bin/env python3
"""Import PNG art into a portable 256-entry RGBA world, not firmware."""
import argparse
import hashlib
import json
from pathlib import Path

from package import LEGACY

ROOT = Path(__file__).resolve().parent


def import_mouse(source, base):
    from PIL import Image, ImageOps
    world = json.loads(base.read_text())
    if world["schema_version"] != 2:
        raise ValueError("this importer upgrades the reviewed v2 example")
    palette = ["00000000"] + [color + "ff" for color in world["palette"][1:]]
    if len(palette) > 16:
        raise ValueError("base palette exceeds v2 budget")
    for sprite in world["sprites"]:
        sprite["display_width"] = sprite["width"]
        sprite["display_height"] = sprite["height"]
        sprite["frames"] = ["".join(f"{int(c,16):02x}" for c in frame) for frame in sprite["frames"]]
    with Image.open(source) as original:
        if original.width > 4096 or original.height > 4096:
            raise ValueError("PNG exceeds host image input budget")
        rgba = original.convert("RGBA")
    small = ImageOps.contain(rgba, (128, 128), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    canvas.alpha_composite(small, ((128-small.width)//2, (128-small.height)//2))
    colors = 256 - len(palette)
    quantized = canvas.quantize(colors=colors, method=Image.Quantize.FASTOCTREE)
    rgba_quantized = quantized.convert("RGBA")
    slots = {}
    raw_indexes=quantized.tobytes();rgba_pixels=list(rgba_quantized.get_flattened_data()) if hasattr(rgba_quantized,"get_flattened_data") else list(rgba_quantized.getdata())
    for index, pixel in zip(raw_indexes, rgba_pixels):
        slots[index] = pixel
    first = len(palette)
    palette.extend("".join(f"{c:02x}" for c in slots.get(i, (0, 0, 0, 0))) for i in range(colors))
    pixels = bytes(0 if rgba_pixels[i][3] == 0 else first+index
                   for i, index in enumerate(raw_indexes))
    mouse_object = next(o for o in world["objects"] if o["id"] == 2)
    sprite = next(s for s in world["sprites"] if s["id"] == mouse_object["sprite"])
    sprite.update(name="smooth-brown-mouse-v1", width=128, height=128,
                  display_width=32, display_height=32, frames=[pixels.hex()])
    mouse_object.update(x=110, y=30)
    world.update(schema_version=3, world_id="cat-chases-smooth-mouse-v1", palette=palette)
    return world


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT/"assets/mouse-source-v1.png")
    parser.add_argument("--base", type=Path, default=LEGACY/"worlds/cat-chases-mouse.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    world = import_mouse(args.source, args.base)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(world, indent=2)+"\n")
    print(f"WORLD: {args.output}; palette={len(world['palette'])}; source_sha256={hashlib.sha256(args.source.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
