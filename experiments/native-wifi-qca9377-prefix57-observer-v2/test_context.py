"""HOST-only context rejection/session model. No signatures created or BLE."""
import base64,json,tempfile,unittest
from pathlib import Path
from context import verify_context,verify_session
from decode_prefix import sha
class ContextTests(unittest.TestCase):
 def test_saved_transport_exact(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'session.json';packet=b'HOST-PUBLIC-PACKET-FIXTURE';stream=bytes(range(32))+packet
   s={'kind':2,'counter':57,'sha256':sha(packet),'package_bytes':len(packet),'stream_base64':base64.b64encode(stream).decode(),'session_base64':base64.b64encode(stream[:8]).decode()}
   p.write_text(json.dumps(s));verify_session(p,packet,2,57)
   for k,v in [('counter',56),('kind',1),('sha256','00'*32),('package_bytes',1),('session_base64','AAAA'),('stream_base64',base64.b64encode(stream[:-1]).decode())]:
    bad={**s,k:v};p.write_text(json.dumps(bad))
    with self.assertRaises(ValueError):verify_session(p,packet,2,57)
 def test_context_fails_before_any_device_call(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'ctx.json'
   for value in ({},{'format':'PREFIX57-PUBLIC-CONTEXT-2','inputs':{}},{'format':'HOST-FIXTURE','inputs':{}}):
    p.write_text(json.dumps(value))
    with self.assertRaises(ValueError):verify_context(p)
if __name__=='__main__':unittest.main()
