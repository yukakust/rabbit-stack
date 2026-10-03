"""Portable signed RUP4 city: centimetres, camera and bounded procedural buildings."""
import json
import struct
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CONNECTED=ROOT.parent/'x86-64-uefi-connected-supervisor-v1'
sys.path.insert(0,str(CONNECTED))
import ask_connected_world as flow
from llm_world import obj,array,integer,validate_schema
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

RGB={'type':'string','pattern':'^[0-9a-f]{6}$'}
POSITION=obj({'x':integer(-20000,20000),'y':integer(0,3000),'z':integer(-20000,20000)})
BUILDING=obj({'id':integer(1,65535),'name':{'type':'string','maxLength':80},
 'kind':{'type':'string','enum':['house','box','road']},'position':POSITION,
 'size':obj({'width':integer(1,3000),'height':integer(1,3000),'depth':integer(1,3000)}),'wall':RGB,'roof':RGB})
SCHEMA=obj({'schema_version':integer(4,4),'world_id':{'type':'string','maxLength':80},
 'camera':obj({'x':integer(-20000,20000),'y':integer(50,3000),'z':integer(-20000,20000),'yaw':integer(0,255)}),
 'sky':RGB,'ground':RGB,'buildings':array(BUILDING,1,64)})

def validate(world):
 validate_schema(world,SCHEMA)
 ids=[b['id'] for b in world['buildings']]
 if len(ids)!=len(set(ids)):raise ValueError('duplicate building id')
 return world

def compile_city(world,counter,private=flow.CREATOR):
 validate(world)
 if type(counter)!=int or not 1<=counter<=0xffffffff:raise ValueError('invalid city counter')
 n=96+32*len(world['buildings']);body=bytearray(n-64);body[:4]=b'RUP4';body[4]=4
 struct.pack_into('<HI',body,6,n,counter);body[12]=len(world['buildings']);struct.pack_into('<H',body,14,32)
 c=world['camera'];struct.pack_into('<hHhB',body,16,c['x'],c['y'],c['z'],c['yaw']);struct.pack_into('<II',body,24,int(world['sky'],16),int(world['ground'],16))
 for i,b in enumerate(world['buildings']):
  p=b['position'];s=b['size'];struct.pack_into('<HBBhhhHHHII',body,32+i*32,b['id'],['house','box','road'].index(b['kind'])+1,0,
   p['x'],p['y'],p['z'],s['width'],s['height'],s['depth'],int(b['wall'],16),int(b['roof'],16))
 return bytes(body)+private.sign(bytes(body))

def decode_city(packet,public=flow.PUBLIC):
 if not isinstance(packet,bytes) or len(packet)<96 or len(packet)>2144:raise ValueError('city packet size differs')
 if packet[:6]!=b'RUP4\x04\x00' or struct.unpack_from('<H',packet,6)[0]!=len(packet):raise ValueError('city header differs')
 count=packet[12];counter=struct.unpack_from('<I',packet,8)[0]
 if not 1<=count<=64 or not counter or len(packet)!=96+count*32 or packet[13] or packet[14:16]!=b'\x20\x00' or packet[23]:raise ValueError('city shape/counter differs')
 Ed25519PublicKey.from_public_bytes(public).verify(packet[-64:],packet[:-64])
 x,y,z,yaw=struct.unpack_from('<hHhB',packet,16);sky,ground=struct.unpack_from('<II',packet,24)
 if sky>0xffffff or ground>0xffffff:raise ValueError('city RGB differs')
 world={'schema_version':4,'world_id':'city-v1','camera':dict(x=x,y=y,z=z,yaw=yaw),'sky':f'{sky:06x}','ground':f'{ground:06x}','buildings':[]}
 for i in range(count):
  offset=32+i*32;identity,kind,reserved,x,y,z,w,h,d,wall,roof=struct.unpack_from('<HBBhhhHHHII',packet,offset)
  if kind not in (1,2,3) or reserved or any(packet[offset+24:offset+32]) or wall>0xffffff or roof>0xffffff:raise ValueError('city record differs')
  world['buildings'].append({'id':identity,'name':f'Building {identity}','kind':['house','box','road'][kind-1],
   'position':dict(x=x,y=y,z=z),'size':dict(width=w,height=h,depth=d),'wall':f'{wall:06x}','roof':f'{roof:06x}'})
 validate(world)
 return world,counter

def initial_city():
 buildings=[]
 for i,(x,z,wall) in enumerate([(-800,700,'ddbd8d'),(800,900,'dab09a'),(-800,1800,'acd0c1'),(800,2100,'dfd0a5'),(-800,3000,'b5c4dd')],1):
  buildings.append({'id':i,'name':f'Дом {i}','kind':'house','position':dict(x=x,y=0,z=z),
   'size':dict(width=600,height=450,depth=600),'wall':wall,'roof':'a35740'})
 buildings.append({'id':6,'name':'Улица','kind':'road','position':dict(x=0,y=0,z=1800),
  'size':dict(width=700,height=1,depth=3000),'wall':'65717a','roof':'65717a'})
 buildings.append({'id':7,'name':'Начало улицы','kind':'road','position':dict(x=0,y=0,z=0),
  'size':dict(width=700,height=1,depth=3000),'wall':'65717a','roof':'65717a'})
 return {'schema_version':4,'world_id':'first-street-v1','camera':dict(x=0,y=250,z=-1200,yaw=0),
  'sky':'8fc3e0','ground':'76915c','buildings':buildings}
