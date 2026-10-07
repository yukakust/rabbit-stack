"""HOST FIXTURES ONLY. Independent struct oracle, never physical observations."""
import copy,struct,unittest
from decode_prefix import decode_capture,loads,PEER

def fixture(cc=1,rc=12,over=7):
 w=[0]*58;w[0]=57;w[1]=3;w[3]=1;w[4]=1;w[5]=32984;w[6]=w[7]=133;w[20]=12;w[21]=14;w[48]=cc+rc;w[54]=100;w[56]=200
 s=(b'QPFX0001'+struct.pack('<58I',*w)).hex();h=[57,cc+rc,0,1,3,4672,cc,rc,over%12 if rc==12 else rc,over,100,0,200,0]
 raw=bytearray(b'QPHCI001'+struct.pack('<14I',*h))
 for i in range(16):
  valid=i<cc if i<4 else i-4<rc
  r=bytearray(288)
  if valid:
   # Genuine cleanup event can be later than stored last tick200.
   e=bytes.fromhex('050400010013') if i<4 else bytes.fromhex('13050101000100')
   struct.pack_into('<Q4I',r,0,201+i,len(e),3,0,int(i<4));r[24:24+len(e)]=e
  raw+=r
 pp=[raw[i*512:(i+1)*512].hex() for i in range(10)]
 return {'format':'QPFX1-QPHCI1','peripheral':PEER,'writes':0,'device_attestation':False,'status_hex':[s]*3,'pages_hex':[pp,pp.copy()],'fixture_kind':'HOST-ONLY-NEVER-PHYSICAL'}

class Tests(unittest.TestCase):
 def reject(self,c):
  with self.assertRaises(ValueError):decode_capture(c)
 def raw_change(self,c,off,data):
  b=bytearray.fromhex(''.join(c['pages_hex'][0]));b[off:off+len(data)]=data;p=[b[i*512:(i+1)*512].hex() for i in range(10)];c['pages_hex']=[p,p.copy()]
 def test_real_shape_oracle(self):
  for cc in range(5):
   for rc in range(13):
    c=fixture(cc,rc,0 if rc<12 else 7);r=decode_capture(c);self.assertEqual(len(r['events']),cc+rc);self.assertFalse(r['device_attestation']);self.assertTrue(r['bounded_history_only'])
 def test_identity_release(self):
  for i,v in [(0,56),(1,2),(4,0),(20,13),(21,13),*[(i,1) for i in range(22,33)]]:
   c=fixture();b=bytearray.fromhex(c['status_hex'][0]);struct.pack_into('<I',b,8+4*i,v);c['status_hex']=[b.hex()]*3;self.reject(c)
 def test_partial_changed_lengths(self):
  for mutation in (lambda c:c.update(format='QPFX1-QPHCI1-PARTIAL'),lambda c:c['status_hex'].pop(),lambda c:c['pages_hex'][1].pop(),lambda c:c['pages_hex'][0].__setitem__(9,'00'*63),lambda c:c.update(writes=True),lambda c:c.update(device_attestation=True)):
   c=fixture();mutation(c);self.reject(c)
 def test_raw_corruption(self):
  for off,data in [(0,b'X'),(8,struct.pack('<I',56)),(20,bytes(4)),(32,struct.pack('<I',5)),(36,struct.pack('<I',13)),(40,struct.pack('<I',12)),(64+8,struct.pack('<I',258)),(64+20,bytes(4)),(64+24,b'\x13'),(64+30,b'X'),(64+288,b'X')]:
   c=fixture();self.raw_change(c,off,data);self.reject(c)
 def test_live_telemetry_frozen_proof(self):
  c=fixture();b=bytearray.fromhex(c['status_hex'][0]);struct.pack_into('<I',b,8+4*3,9);c['status_hex']=[b.hex()]*3;decode_capture(c)
  c=fixture();b=bytearray.fromhex(c['status_hex'][1]);struct.pack_into('<I',b,8+4*40,987);c['status_hex'][1]=b.hex();decode_capture(c)
  for index in (2,5,48,49,54,56,50):
   c=fixture();b=bytearray.fromhex(c['status_hex'][1]);struct.pack_into('<I',b,8+4*index,1);c['status_hex'][1]=b.hex();self.reject(c)
 def test_duplicate_json(self):
  with self.assertRaises(ValueError):loads(b'{"x":0,"x":1}')
  with self.assertRaises(ValueError):loads(b'{"x":NaN}')
 def test_snapshot_not_rf_success(self):
  c=fixture();r=decode_capture(c);self.assertFalse(r['wifi_connected_claimed']);self.assertFalse(r['context_verified'])
if __name__=='__main__':unittest.main()
