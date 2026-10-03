"""Bounded vector data -> antialiased indexed RGBA; no scripts, XML or external resource inputs."""
from llm_world import obj, array, integer, validate_schema

COLOR = {'anyOf': [{'type': 'string', 'pattern': '^[0-9a-f]{8}$'}, {'type': 'null'}]}
COMMAND = obj({'op': {'type': 'string', 'enum': ['M', 'L', 'C', 'Q', 'Z']}, 'points': array(integer(0, 512), 0, 6)})
SHAPE = obj({'kind': {'type': 'string', 'enum': ['ellipse', 'rect', 'path']},
             'fill': COLOR, 'stroke': COLOR, 'stroke_width': integer(0, 24),
             'geometry': array(integer(0, 512), 0, 4), 'commands': array(COMMAND, 0, 64)})
DRAWING = obj({'id': integer(1, 254), 'name': {'type': 'string', 'maxLength': 64},
               'width': integer(32, 128), 'height': integer(32, 128),
               'display_width': integer(1, 64), 'display_height': integer(1, 64),
               'frames': array(array(SHAPE, 1, 64), 1, 4)})


def render(source):
    validate_schema(source, DRAWING)
    from PIL import Image, ImageDraw
    images = []
    scale_x = source['width'] * 3 / 512; scale_y = source['height'] * 3 / 512
    point = lambda p: (p[0] * scale_x, p[1] * scale_y)
    color = lambda c: tuple(bytes.fromhex(c)) if c is not None else None
    for frame in source['frames']:
        image = Image.new('RGBA', (source['width'] * 3, source['height'] * 3))
        for shape in frame:
            overlay = Image.new('RGBA', image.size); draw = ImageDraw.Draw(overlay)
            fill = color(shape['fill']); stroke = color(shape['stroke'])
            width = max(1, round(shape['stroke_width'] * min(scale_x, scale_y)))
            if shape['stroke_width'] == 0: stroke = None
            geometry = shape['geometry']; commands = shape['commands']
            if shape['kind'] in ('ellipse', 'rect'):
                if len(geometry) != 4 or commands: raise ValueError('shape geometry requires four coordinates and no commands')
                a, b, c, d = geometry
                if c == 0 or d == 0: raise ValueError('shape has zero extent')
                box = [point((a-c,b-d)), point((a+c,b+d))] if shape['kind'] == 'ellipse' else [point((a,b)),point((a+c,b+d))]
                function = draw.ellipse if shape['kind'] == 'ellipse' else draw.rectangle
                function(box, fill=fill, outline=stroke, width=width)
            else:
                if geometry or not commands or commands[0]['op'] != 'M': raise ValueError('path requires initial M and no geometry')
                paths = []; points = []; current = None
                for command in commands:
                    op = command['op']; values = command['points']
                    if len(values) != {'M': 2, 'L': 2, 'C': 6, 'Q': 4, 'Z': 0}[op]:
                        raise ValueError('path command coordinate count differs')
                    if op == 'M':
                        if points: paths.append(points)
                        current = tuple(values); points = [current]
                    elif op == 'L': current = tuple(values); points.append(current)
                    elif op == 'Z': points.append(points[0]); current = points[0]
                    else:
                        controls = [current] + [tuple(values[i:i+2]) for i in range(0,len(values),2)]
                        # Fixed sampling bounds CPU cost; supersampling smooths edges.
                        for step in range(1,33):
                            t = step/32; layer = controls
                            while len(layer)>1:
                                layer = [tuple((1-t)*a+t*b for a,b in zip(layer[i],layer[i+1])) for i in range(len(layer)-1)]
                            points.append(layer[0])
                        current = controls[-1]
                if points: paths.append(points)
                for path in paths:
                    scaled = [point(p) for p in path]
                    if fill is not None and len(path)>=3: draw.polygon(scaled, fill=fill)
                    if stroke is not None and len(path)>=2:
                        draw.line(scaled, fill=stroke, width=width, joint='curve')
                        for x,y in [scaled[0],scaled[-1]]: draw.ellipse((x-width/2,y-width/2,x+width/2,y+width/2),fill=stroke)
            image.alpha_composite(overlay)
        images.append(image.resize((source['width'], source['height']), Image.Resampling.LANCZOS))
    atlas = Image.new('RGBA', (source['width'], source['height'] * len(images)))
    for i, image in enumerate(images): atlas.paste(image, (0, source['height'] * i))
    quantized = atlas.quantize(colors=255, method=Image.Quantize.FASTOCTREE).convert('RGBA')
    colors = ['00000000']; lookup = {}; indexes = []
    pixels = quantized.get_flattened_data() if hasattr(quantized, 'get_flattened_data') else quantized.getdata()
    for pixel in pixels:
        if pixel[3] == 0: indexes.append(0); continue
        color = bytes(pixel).hex()
        if color not in lookup: lookup[color] = len(colors); colors.append(color)
        indexes.append(lookup[color])
    area = source['width'] * source['height']
    return {'width': source['width'], 'height': source['height'], 'palette': colors,
            'frames': [bytes(indexes[i*area:(i+1)*area]).hex() for i in range(len(images))]}
