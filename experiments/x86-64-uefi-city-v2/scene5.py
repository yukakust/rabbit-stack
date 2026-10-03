"""Generic bounded 3D actors, coloured primitives, sine motion and timed visibility."""
import copy
import struct
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'x86-64-uefi-city-v1'))
import city_world
flow=city_world.flow
from llm_world import obj,array,integer,validate_schema
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
VECTOR=obj({axis:integer(-1000,1000) for axis in ('x','y','z')})
SIZE=obj({axis:integer(1,1000) for axis in ('width','height','depth')})
MOTION=obj({**{axis:integer(-500,500) for axis in ('x','y','z')},'period_ms':integer(100,60000),'phase_ms':integer(0,59999)})
VISIBILITY=obj({'mode':{'type':'string','enum':['always','inside','outside']},'period_ms':integer(100,60000),
                'duration_ms':integer(1,60000),'delay_ms':integer(0,60000)})
PART=obj({'shape':{'type':'string','enum':['ellipsoid','box','cone']},'position':VECTOR,'size':SIZE,
          'color':city_world.RGB,'motion':MOTION,'visibility':VISIBILITY})
ACTOR=obj({'id':integer(1,65535),'name':{'type':'string','maxLength':80},
           'position':obj({'x':integer(-20000,20000),'y':integer(0,7000),'z':integer(-20000,20000)}),
           'yaw':integer(0,255),'parts':array(PART,1,48)})
SCHEMA=obj({**city_world.SCHEMA['properties'],'schema_version':integer(5,5),'actors':array(ACTOR,0,4)})

def validate(world):
    validate_schema(world,SCHEMA)
    base=copy.deepcopy(world);base.pop('actors');base['schema_version']=4;city_world.validate(base)
    ids=[a['id'] for a in world['actors']]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate actor id')
    if sum(len(a['parts']) for a in world['actors'])>96:raise ValueError('global actor geometry budget exceeded')
    for a in world['actors']:
        for p in a['parts']:
            if p['motion']['phase_ms']>=p['motion']['period_ms']:raise ValueError('motion phase exceeds period')
            if p['visibility']['duration_ms']>p['visibility']['period_ms']:raise ValueError('visibility duration exceeds period')
    return world

def compile_scene(world,counter,private=flow.CREATOR):
    validate(world)
    base=copy.deepcopy(world);actors=base.pop('actors');base['schema_version']=4
    body=bytearray(city_world.compile_city(base,counter,private)[:-64]);body[:5]=b'RUP5\x05';body[13]=len(actors)
    for a in actors:
        p=a['position'];body+=struct.pack('<HBBhHh6x',a['id'],a['yaw'],len(a['parts']),p['x'],p['y'],p['z'])
        for part in a['parts']:
            p=part['position'];s=part['size'];m=part['motion'];v=part['visibility']
            body+=struct.pack('<BBHhhhHHHIhhhHHHHH12x',['ellipsoid','box','cone'].index(part['shape'])+1,
                              ['always','inside','outside'].index(v['mode']),0,p['x'],p['y'],p['z'],s['width'],s['height'],s['depth'],int(part['color'],16),
                              m['x'],m['y'],m['z'],m['period_ms'],m['phase_ms'],v['period_ms'],v['duration_ms'],v['delay_ms'])
    struct.pack_into('<H',body,6,len(body)+64)
    return bytes(body)+private.sign(bytes(body))

def decode_scene(packet,public=flow.PUBLIC):
    if type(packet)!=bytes or not 128<=len(packet)<=6816 or packet[:6]!=b'RUP5\x05\x00' or struct.unpack_from('<H',packet,6)[0]!=len(packet):raise ValueError('actor packet header/budget differs')
    Ed25519PublicKey.from_public_bytes(public).verify(packet[-64:],packet[:-64])
    count,actors=packet[12:14]
    if not 1<=count<=64 or actors>4:raise ValueError('actor/building count differs')
    end=32+count*32
    # Reconstruct legacy portion for its independently reviewed validation.
    legacy=bytearray(packet[:end]);legacy[:5]=b'RUP4\x04';legacy[13]=0;struct.pack_into('<H',legacy,6,end+64)
    # Parsing is independent of the supplied public key; never re-sign untrusted
    # input into a deliverable. This temporary packet exists only for V4 validation.
    legacy=bytes(legacy)+flow.CREATOR.sign(bytes(legacy))
    world,counter=city_world.decode_city(legacy,flow.PUBLIC);world['schema_version']=5;world['actors']=[]
    offset=end
    for _ in range(actors):
        if offset+16>len(packet)-64:raise ValueError('truncated actor')
        identity,yaw,parts,x,y,z=struct.unpack_from('<HBBhHh',packet,offset)
        if any(packet[offset+10:offset+16]) or not 1<=parts<=48:raise ValueError('actor header differs')
        offset+=16;a={'id':identity,'name':f'Actor {identity}','position':dict(x=x,y=y,z=z),'yaw':yaw,'parts':[]}
        for _ in range(parts):
            if offset+48>len(packet)-64:raise ValueError('truncated actor geometry')
            shape,mode,reserved,x,y,z,w,h,d,color,mx,my,mz,period,phase,vperiod,duration,delay=struct.unpack_from('<BBHhhhHHHIhhhHHHHH',packet,offset)
            if shape not in (1,2,3) or mode not in (0,1,2) or reserved or any(packet[offset+36:offset+48]) or color>0xffffff:raise ValueError('actor primitive differs')
            a['parts'].append({'shape':['ellipsoid','box','cone'][shape-1],'position':dict(x=x,y=y,z=z),
                              'size':dict(width=w,height=h,depth=d),'color':f'{color:06x}','motion':dict(x=mx,y=my,z=mz,period_ms=period,phase_ms=phase),
                              'visibility':dict(mode=['always','inside','outside'][mode],period_ms=vperiod,duration_ms=duration,delay_ms=delay)})
            offset+=48
        world['actors'].append(a)
    if offset!=len(packet)-64:raise ValueError('actor packet trailing bytes')
    validate(world);return world,counter

def models():
    return {'rabbit.actor.roof-cat-v1':flow.read_json(ROOT/'models/roof-cat.json')}
