#!/usr/bin/env python3
"""Loopback-only QEMU fixture, converts a real UE frame with FFmpeg.

The all-zero signing seed is PUBLIC TEST material, never an owner's key.
This server has no write/control API and cannot be used as a production service.
"""
import argparse
import ctypes
import hashlib
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import struct
import subprocess
import time

def encode(rgb,w,h,sequence,lib):
    runs=bytearray(); i=0
    while i<len(rgb):
        color=rgb[i:i+3]; count=1
        while count<65535 and i+count*3<len(rgb) and rgb[i+count*3:i+(count+1)*3]==color:
            count+=1
        runs+=struct.pack('<H',count)+color; i+=count*3
    codec,body=(2,bytes(runs)) if len(runs)<len(rgb) else (1,rgb)
    message=struct.pack('<4sBBHHHIQ16s24s',b'RPF1',1,codec,64,w,h,len(body),sequence,bytes(16),bytes(24))+body
    secret=ctypes.create_string_buffer(64); public=ctypes.create_string_buffer(32)
    seed=ctypes.create_string_buffer(bytes(32),32)
    lib.crypto_ed25519_key_pair(secret,public,seed)
    signature=ctypes.create_string_buffer(64)
    lib.crypto_ed25519_sign(signature,secret,message,ctypes.c_size_t(len(message)))
    return message+signature.raw,public.raw

def main():
    p=argparse.ArgumentParser(); p.add_argument('--image',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    root=Path(__file__).resolve().parent
    subprocess.run(['gcc','-shared','-fPIC','-O2',str(root/'monocypher.c'),
                    str(root/'monocypher-ed25519.c'),'-o',str(root/'fixture-crypto.so')],check=True)
    rgb=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(a.image),
         '-vf','scale=640:360','-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
    if len(rgb)!=640*360*3:raise SystemExit('wrong RGB length')
    lib=ctypes.CDLL(str(root/'fixture-crypto.so'))
    first,public=encode(rgb,640,360,1,lib); second,_=encode(rgb,640,360,2,lib)
    damaged=bytearray(first);damaged[-1]^=1
    (root/'fixture_public.h').write_text('static const unsigned char fixture_public[32]={'+','.join(str(x) for x in public)+'};\n')
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/'input.json').write_text(json.dumps({'input_sha256':hashlib.sha256(a.image.read_bytes()).hexdigest(),
        'rgb_sha256':hashlib.sha256(rgb).hexdigest(),'first_wire_sha256':hashlib.sha256(first).hexdigest(),
        'wire_bytes':len(first),'codec':first[5],'dimensions':[640,360],
        'fixture_key_public':True,'bind':'127.0.0.1:9783','physical_dell':False},indent=2)+'\n')
    frames={'/first.rpf':first,'/second.rpf':second,'/invalid.rpf':bytes(damaged),
            '/oversize.rpf':b'0'*(64+640*360*5+65)}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            data=first if self.path=='/slow.rpf' else frames.get(self.path)
            if data is None:self.send_error(404);return
            self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers()
            try:
                if self.path=='/slow.rpf':
                    self.wfile.write(data[:64]);self.wfile.flush();time.sleep(3)
                    self.wfile.write(data[64:])
                else:self.wfile.write(data)
            except (ConnectionResetError,BrokenPipeError):pass
        def log_message(self,fmt,*args):
            with (a.output/'requests.log').open('a') as f:f.write(fmt%args+'\n')
    print('FIXTURE READY 127.0.0.1:9783',flush=True)
    ThreadingHTTPServer(('127.0.0.1',9783),Handler).serve_forever()
if __name__=='__main__':main()
