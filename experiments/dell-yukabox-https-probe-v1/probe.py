"""Temporary bounded loopback probe. Publication is a separate Root operation."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse,json,re,time,hashlib
class Nonces:
 def __init__(self):self.seen=set()
 def accept(self,nonce):
  if not isinstance(nonce,str) or re.fullmatch(r'[0-9a-f]{64}',nonce) is None:return False
  if nonce in self.seen or len(self.seen)>=1024:return False
  self.seen.add(nonce);return True
def unique_object(pairs):
 result={}
 for key,value in pairs:
  if key in result:raise ValueError('duplicate field')
  result[key]=value
 return result
class Handler(BaseHTTPRequestHandler):
 protocol_version='HTTP/1.0'
 def setup(self):super().setup();self.connection.settimeout(5)
 def log_message(self,*args):pass
 def answer(self,status,body):
  self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
 def do_POST(self):
  lengths=self.headers.get_all('Content-Length',[])
  if self.path!='/probe' or self.headers.get('Transfer-Encoding') is not None or len(lengths)!=1 or len(lengths[0])>3 or not lengths[0].isdigit() or not 0<int(lengths[0])<=128:
   self.answer(400,b'{"error":"request"}');return
  try:
   body=self.rfile.read(int(lengths[0]));value=json.loads(body,object_pairs_hook=unique_object)
   if not isinstance(value,dict) or set(value)!= {'nonce'} or not self.server.nonces.accept(value['nonce']):raise ValueError('nonce')
  except (ValueError,UnicodeError,TimeoutError):self.answer(400,b'{"error":"nonce"}');return
  nonce=value['nonce'];response=json.dumps({'nonce':nonce,'proof':'rabbit-dell-wan-v1'},separators=(',',':')).encode()
  print(json.dumps({'event':'probe','nonce':nonce,'request_sha256':hashlib.sha256(body).hexdigest(),'response_sha256':hashlib.sha256(response).hexdigest(),'timestamp_unix':time.time()}),flush=True)
  self.answer(200,response)
 def do_GET(self):self.answer(404,b'{"error":"path"}')
def main():
 p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=9784);a=p.parse_args()
 if a.port!=9784:raise ValueError('isolated fixed port required')
 server=HTTPServer(('127.0.0.1',9784),Handler);server.nonces=Nonces();server.serve_forever()
if __name__=='__main__':main()
