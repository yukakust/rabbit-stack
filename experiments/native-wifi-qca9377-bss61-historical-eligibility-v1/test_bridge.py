"""Pure host fixtures; no radio, credential or physical authority."""
from pathlib import Path
import importlib.util,sys,struct,hashlib,copy,unittest
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'native-wifi-qca9377-scan61-observer-v1'))
import fixtures
import bridge
class Translation(unittest.TestCase):
 def fixture(self):
  c=fixtures.capture(True);b=bytearray.fromhex(c['status_hex'][0]);struct.pack_into('<I',b,8+24*4,0);c['status_hex']=[b.hex()]*3
  return c,{'generation':61,'epoch':42,'status_sha256':hashlib.sha256(b).hexdigest()}
 def mutate(self,c,r,index,value):
  b=bytearray.fromhex(c['status_hex'][0]);struct.pack_into('<I',b,8+4*index,value);c['status_hex']=[b.hex()]*3;r['status_sha256']=hashlib.sha256(b).hexdigest()
 def test_historical_zero_preserved(self):
  c,r=self.fixture();b=bridge.translate(c,r)
  self.assertEqual((b['live_frequency'],b['observed_frequency']),(0,2437));self.assertEqual(b['native_capabilities'],'UNKNOWN');self.assertEqual(b['native_basic_rate_compatibility'],'UNRESOLVED');self.assertTrue(b['fresh_live_BSS_revalidation_required']);self.assertFalse(b['association_authority']);self.assertFalse(b['controlled_port_authority']);self.assertFalse(b['physical_verified']);self.assertEqual(b['completion'],25)
 def test_root_wrong_generation_epoch_status(self):
  for name,value in [('generation',60),('epoch',43),('status_sha256','0'*64)]:
   c,r=self.fixture();r[name]=value
   with self.assertRaises(ValueError):bridge.translate(c,r)
 def test_quiescence_live_owners_watermarks(self):
  for index,value in [(3,0),(4,0),(24,2437),(26,0),(23,25),(28,25),(44,1)]:
   c,r=self.fixture();self.mutate(c,r,index,value)
   with self.assertRaises(ValueError):bridge.translate(c,r)
 def test_reviewed_policy_exact(self):
  c,r=self.fixture();b=bytearray.fromhex(c['status_hex'][0]);b[264]^=1;c['status_hex']=[b.hex()]*3;r['status_sha256']=hashlib.sha256(b).hexdigest()
  with self.assertRaises(ValueError):bridge.translate(c,r)
 def test_wrong_beacon_channel(self):
  c,r=self.fixture();pages=c['pages_hex'][0];blob=bytearray.fromhex(''.join(pages[80:85]));struct.pack_into('<I',blob,44+8,7);altered=[blob[j:j+512].hex() for j in range(0,2084,512)];pages[80:85]=altered;c['pages_hex'][1]=pages.copy()
  with self.assertRaises(ValueError):bridge.translate(c,r)
 def test_two_immutable_passes(self):
  c,r=self.fixture();c['pages_hex'][1][0]='00'
  with self.assertRaises(ValueError):bridge.translate(c,r)
if __name__=='__main__':unittest.main()
