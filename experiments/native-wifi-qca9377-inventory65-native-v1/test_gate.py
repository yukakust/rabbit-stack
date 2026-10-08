"""Meaningful corruption cases on copied public proofs; no live state/hardware."""
from pathlib import Path
import tempfile,shutil,json,unittest
from gate import checked,R
class Test(unittest.TestCase):
 def test_actual_and_corruption(self):
  self.assertFalse(checked()['physical_admission'])
  owned=Path('/home/yuka/rabbit-world/i65-gate');owned.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(prefix='inventory65-gate-',dir=owned) as t:
   clone=Path(t)/'copy';shutil.copytree(R,clone,ignore=shutil.ignore_patterns('*.img','*.fd','*.ppm','tmp','__pycache__','evidence','gate-tmp'))
   f=clone/'runs/checked-candidate/report.json';saved=f.read_bytes();self.assertFalse(checked(clone)['physical_admission'])
   for field,value in [('native_counter',64),('generation_reserved',True),('physical_admission',True),('entropy_approved',True),('GetRNG_RDSEED_MSR_calls',True),('base64_report_sha256','00'*32),('world_package_sha256','00'*32)]:
    d=json.loads(saved);d[field]=value;f.write_text(json.dumps(d))
    with self.assertRaises((ValueError,AssertionError),msg=field):checked(clone)
    f.write_bytes(saved)
   p=clone/'runs/checked-candidate/driver.c';original=p.read_bytes();p.write_bytes(original+b'\n/* source corruption */')
   with self.assertRaises(ValueError):checked(clone)
   p.write_bytes(original)
   p=clone/'runs/checked-candidate/payload.efi';original=p.read_bytes();p.write_bytes(original[:-1]+bytes([original[-1]^1]))
   with self.assertRaises(ValueError):checked(clone)
if __name__=='__main__':unittest.main()
