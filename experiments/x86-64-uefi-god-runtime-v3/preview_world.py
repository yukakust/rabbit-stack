#!/usr/bin/env python3
"""Preview exact signed-package pixels in a local HTML canvas (no network)."""
import argparse
import json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from compile_world import compile_world
from package import decode_package


def preview(world, counter):
    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    package = compile_world(world, counter, private)
    decoded = decode_package(package, private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw))
    data = {"palette": decoded["palette"], "sprites": [{**s, "pixels": list(s["pixels"])} for s in decoded["sprites"]], "objects": decoded["objects"]}
    # All names/intent are absent; this payload contains only validated numeric fields.
    return '''<!doctype html><meta charset="utf-8"><title>Rabbit graphics v3 preview</title>
<style>body{background:#121826;color:#eee;font:16px system-ui;margin:32px}canvas{width:960px;max-width:100%;border:1px solid #485268}p{max-width:65ch}</style>
<h1>Rabbit graphics v3 — package preview</h1><p>Exact decoded asset pixels. Static preview; not physical Dell evidence or a VM simulation.</p>
<canvas id="scene" width="480" height="270"></canvas><script>
const world=''' + json.dumps(data) + ''';
const ctx=document.getElementById('scene').getContext('2d');ctx.fillStyle='#121826';ctx.fillRect(0,0,480,270);
for(const o of world.objects){const s=world.sprites.find(s=>s.id===o.sprite);
 const image=ctx.createImageData(s.width,s.height);
 for(let i=0;i<s.width*s.height;i++){const c=world.palette[s.pixels[i]];image.data.set(c,i*4);}
 const layer=document.createElement('canvas');layer.width=s.width;layer.height=s.height;
 layer.getContext('2d').putImageData(image,0,0);ctx.imageSmoothingEnabled=false;
 ctx.drawImage(layer,o.x*3,o.y*3,s.display_width*3,s.display_height*3);
}</script>'''


def main():
    parser=argparse.ArgumentParser();parser.add_argument("world",type=Path);parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(preview(args.world,1))
    print(f"PREVIEW: {args.output}")


if __name__=="__main__":main()
