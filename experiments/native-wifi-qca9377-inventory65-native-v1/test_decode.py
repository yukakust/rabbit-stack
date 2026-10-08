from pathlib import Path
import json,hashlib,unittest
from decode import decode
R=Path(__file__).resolve().parent
class Test(unittest.TestCase):
 def setUp(self):
  report=json.loads((R/'runs/checked-candidate/report.json').read_text());self.code=report['rng_code_object_sha256'];self.cpu=hashlib.sha256((R/'inventory.c').read_bytes()).hexdigest();self.raw=(R/'runs/host-model/fixture-0.bin').read_bytes()
 def pair(self,raw):return raw[:512],b'QIC\2'+hashlib.sha256(raw[:512]).digest()+raw[512:]
 def test_actual_C_fixtures(self):
  for mode in range(5):
   raw=(R/f'runs/host-model/fixture-{mode}.bin').read_bytes();d=decode(*self.pair(raw),self.code,self.cpu);self.assertFalse(d['entropy_approved']);self.assertFalse(d['physical_admission']);self.assertEqual(d['GetInfo']['closed'],mode not in (3,4))
 def test_semantic_tamper(self):
  for offset in [0,7,8,12,16,20,24,28,32,36,40,71,72,79,80,88,92,96,104,116,316,320,336+8,336+12,336+16,336+20,656,687,696,700,704,708,923]:
   raw=bytearray(self.raw);raw[offset]^=0x80
   with self.assertRaises(ValueError,msg=str(offset)):decode(*self.pair(raw),self.code,self.cpu)
 def test_integrity_length_provenance(self):
  a,b=self.pair(self.raw)
  for first,second in [(a[:-1],b),(a,b[:-1]),(a,b[:4]+bytes(32)+b[36:]),(a,b'QIC\1'+b[4:])]:
   with self.assertRaises(ValueError):decode(first,second,self.code,self.cpu)
  with self.assertRaises(ValueError):decode(a,b,'00'*32,self.cpu)
  with self.assertRaises(ValueError):decode(a,b,self.code,'00'*32)
if __name__=='__main__':unittest.main()
