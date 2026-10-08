"""Pure synthetic callback/result joins only; never creates physical admission."""
import unittest,json,copy,sys
from pathlib import Path
import classify_scan61 as classify
sys.path.insert(0,str(classify.DECODER.parent))
import fixtures
class CaptureTests(unittest.TestCase):
 def fixture(self):
  raw=fixtures.capture(True);raw.pop('fixture_kind');raw['format']='QSCN1-QEXP1'
  row={'peripheral':classify.decode.PEER,'writes':0,'NSError_code':0,'NSError_domain':'','cached_value_possible':False}
  rows=[{**row,'stage':s} for s in ('services','characteristics','services','characteristics')]
  seq=[(0,0,0x2b,raw['status_hex'][0])]
  for stage,passnum in ((1,0),(3,1)):
   if stage==3:seq.append((2,0,0x2b,raw['status_hex'][1]))
   seq.extend((stage,page,0x80+page,h) for page,h in enumerate(raw['pages_hex'][passnum]))
  seq.append((4,0,0x2b,raw['status_hex'][2]))
  rows += [{**row,'stage':'read','capture_stage':s,'page':p,'expected':f'52414242-4954-4649-8000-{uid:012X}','raw_hex':h,'raw_bytes':len(bytes.fromhex(h))} for s,p,uid,h in seq]
  return raw,rows
 def join(self,raw,rows):return classify.capture_from_logs(json.dumps(raw),'\n'.join(map(json.dumps,rows)))
 def test_complete_fixture_is_only_pure_decode(self):
  raw,rows=self.fixture();d=classify.decode.decode_capture(self.join(raw,rows));self.assertTrue(d['raw_beacon_matches_status']);self.assertFalse(d['physical_ssid_discovered'])
 def test_malformed_joins_reject(self):
  for kind in ('partial','missing-page','error','fixture','wrong-UUID','swapped-pages','missing-discovery','duplicate-read','callback-data','wrong-peer'):
   with self.subTest(kind=kind):
    raw,rows=self.fixture()
    if kind=='partial':raw['format']='QSCN1-QEXP1-PARTIAL'
    elif kind=='missing-page':raw['pages_hex'][0].pop()
    elif kind=='error':rows[8]['NSError_domain']='CBErrorDomain';rows[8]['NSError_code']=6
    elif kind=='fixture':raw['fixture_kind']='SYNTHETIC'
    elif kind=='wrong-UUID':rows[4]['expected']='52414242-4954-4649-8000-00000000002C'
    elif kind=='swapped-pages':rows[8],rows[9]=rows[9],rows[8]
    elif kind=='missing-discovery':rows.pop(0)
    elif kind=='duplicate-read':rows.insert(8,copy.deepcopy(rows[8]))
    elif kind=='callback-data':rows[8]['raw_hex']='00';rows[8]['raw_bytes']=1
    elif kind=='wrong-peer':rows[8]['peripheral']='00000000-0000-0000-0000-000000000000'
    with self.assertRaises(ValueError):self.join(raw,rows)
if __name__=='__main__':unittest.main()
