import contextlib,http.client,io,socket,threading,unittest
from http.server import HTTPServer
from probe import Handler,Nonces
class Tests(unittest.TestCase):
 def setUp(self):
  self.server=HTTPServer(('127.0.0.1',0),Handler);self.server.nonces=Nonces();self.port=self.server.server_port
  self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
 def tearDown(self):self.server.shutdown();self.server.server_close();self.thread.join()
 def request(self,method,path,body,headers=None):
  connection=http.client.HTTPConnection('127.0.0.1',self.port,timeout=3)
  try:
   connection.request(method,path,body,headers or {});response=connection.getresponse();return response.status,response.read()
  finally:connection.close()
 def test_roundtrip_repeat_and_no_file_path(self):
  body=b'{"nonce":"'+b'ab'*32+b'"}'
  with contextlib.redirect_stdout(io.StringIO()) as log:status,response=self.request('POST','/probe',body)
  self.assertEqual(status,200);self.assertIn(b'ab'*32,response);self.assertIn('request_sha256',log.getvalue())
  self.assertEqual(self.request('POST','/probe',body)[0],400)
  self.assertEqual(self.request('GET','/../../etc/passwd',b'')[0],404)
 def test_bounds_wrong_type_and_transfer_encoding(self):
  for body in (b'x'*129,b'{"nonce":1}',b'{"nonce":1,"nonce":2}',b'{"nonce":"'+b'ab'*32+b'","extra":1}'):
   self.assertEqual(self.request('POST','/probe',body)[0],400)
  self.assertEqual(self.request('POST','/probe',b'0\r\n\r\n',{'Transfer-Encoding':'chunked'})[0],400)
 def test_duplicate_lengths(self):
  with socket.create_connection(('127.0.0.1',self.port),timeout=3) as s:
   s.sendall(b'POST /probe HTTP/1.0\r\nContent-Length: 2\r\nContent-Length: 2\r\n\r\n{}')
   self.assertIn(b'400',s.recv(1024).split(b'\r\n')[0])
if __name__=='__main__':unittest.main()
