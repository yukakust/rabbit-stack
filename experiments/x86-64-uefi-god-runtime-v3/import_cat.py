#!/usr/bin/env python3
"""Export generated 2x2 walk-sheet to a data-only RUP3 world.

No painting, keying, or alpha synthesis: retain the generated transparency,
crop equal cells, resize and quantize all poses using ONE shared RGBA palette.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def import_cat(source, width=128):
    from PIL import Image
    if type(width) is not int or not 64 <= width <= 128:
        raise ValueError('source width must be 64..128')
    with Image.open(source) as original:
        if original.width > 4096 or original.height > 4096:
            raise ValueError('image exceeds host input budget')
        if original.width % 2 or original.height % 2 or original.mode != 'RGBA':
            raise ValueError('expected an even-sized RGBA 2x2 sheet')
        rgba = original.copy()
    if rgba.getchannel('A').getextrema()[0] != 0:
        raise ValueError('sheet must contain genuine transparency')
    cw, ch = rgba.width//2, rgba.height//2
    height = round(width*ch/cw)
    poses = [rgba.crop((x*cw,y*ch,(x+1)*cw,(y+1)*ch)).resize(
        (width,height),Image.Resampling.LANCZOS) for y in range(2) for x in range(2)]
    atlas = Image.new('RGBA',(width,height*4))
    for i,pose in enumerate(poses):
        atlas.paste(pose,(0,i*height))
    indexed = atlas.quantize(colors=255,method=Image.Quantize.FASTOCTREE)
    colors = indexed.convert('RGBA')
    raw = indexed.tobytes()
    pixels = list(colors.get_flattened_data()) if hasattr(colors,'get_flattened_data') else list(colors.getdata())
    slots = {}
    for index,pixel in zip(raw,pixels):
        slots[index] = pixel
    palette = ['00000000'] + [''.join(f'{v:02x}' for v in slots.get(i,(0,0,0,0))) for i in range(255)]
    mapped = bytes(0 if pixels[i][3]==0 else index+1 for i,index in enumerate(raw))
    frame_size = width*height
    world = {
        'schema_version':3,'world_id':'ginger-cat-walk-v1','palette':palette,
        'sprites':[{'id':1,'name':'ginger-cat-four-step-walk-v1','width':width,'height':height,
                    'display_width':64,'display_height':43,
                    'frames':[mapped[i*frame_size:(i+1)*frame_size].hex() for i in range(4)]}],
        'objects':[{'id':1,'sprite':1,'program':1,'x':8,'y':40,'vx':1,'vy':0,'target':1}],
        'programs':[{'id':1,'name':'walk-bounce-four-pose-loop','code':[1,2,5,4,0]}]
    }
    return world


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,default=ROOT/'assets/cat-walk-source-v1.png')
    parser.add_argument('--width',type=int,default=128)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--preview',type=Path,help='export a walk-loop GIF using exact indexed world pixels')
    args=parser.parse_args()
    world=import_cat(args.source,args.width)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(world,indent=2)+'\n')
    if args.preview:
        export_preview(world,args.preview)
    print(f'WORLD: {args.output}; four poses; source SHA256={hashlib.sha256(args.source.read_bytes()).hexdigest()}')


def export_preview(world,path):
    """Format export, not generated art: actual v3 nearest sampling and alpha.

    This small MOVE/BOUNCE/ANIMATE model previews this world's exact program only;
    the freestanding C VM is separately tested. No direction-dependent flip.
    """
    from PIL import Image
    sprite=world['sprites'][0]
    palette=[tuple(bytes.fromhex(c)) for c in world['palette']]
    layers=[]
    for frame in sprite['frames']:
        pixels=bytes.fromhex(frame)
        # Match C floor mapping, not Pillow's pixel-centre nearest mapping.
        w,h=sprite['width'],sprite['height']
        dw,dh=sprite['display_width']*3,sprite['display_height']*3
        layer=Image.new('RGBA',(dw,dh))
        layer.putdata([palette[pixels[(y*h//dh)*w+x*w//dw]] for y in range(dh) for x in range(dw)])
        layers.append(layer)
    images=[]
    x=world['objects'][0]['x'];vx=world['objects'][0]['vx']
    for tick in range(240):
        x+=vx
        if x<0 or x>96:
            x=max(0,min(x,96));vx=-vx
        if tick%4==3:
            image=Image.new('RGBA',(480,270),(18,24,38,255))
            image.alpha_composite(layers[((tick+1)//4)%4],(x*3,120))
            images.append(image.convert('RGB'))
    path.parent.mkdir(parents=True,exist_ok=True)
    images[0].save(path,save_all=True,append_images=images[1:],duration=132,loop=0)
    images[0].save(path.with_suffix('.png'))
    print(f'LOCAL MODEL PREVIEW (not Dell evidence): {path}')


if __name__=='__main__':main()
