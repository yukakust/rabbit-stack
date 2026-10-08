"""Source-only63 progress ABI join; frozen candidate pins required for final admission."""
from pathlib import Path
import importlib.util,hashlib
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(pins=None,monitor=None):
 observer=REPO/'experiments/native-wifi-qca9377-filter64-observer-v1';spec=importlib.util.spec_from_file_location('_monitor63_native_source',observer/'native_binding.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r=m.check(pins);text=''.join((monitor or (ROOT/'collector.m').read_text()).split())
 for token in ('services[3]={0x22,0x2e,0x2a},values[3]={0x23,0x2f,0x2b},sizes[3]={160,544,416};','le32(b+8+59*4)!=64','le32(b+8+(self.index==1?44:4)*4)!=1','le32(b+8+55*4)!=12||le32(b+8+56*4)!=14||le32(b+8+57*4)!=4','n=self.index==1?45:44;n<=(self.index==1?54:52);n++','le32(b+8+60*4)!=64','le32(b+8+61*4)!=13'):
  if token not in text:raise ValueError('monitor actual native field/UUID '+token)
 return {'status':'SOURCE-PRODUCER63-PROGRESS-ABI-JOIN-DRAFT' if pins is None else 'ROOT-PINNED-FROZEN63-PROGRESS-ABI-JOIN-PASS','native':r,'monitor_source_sha256':sha(ROOT/'collector.m'),'physical_admission':False,'native_binding_frozen':pins is not None}
if __name__=='__main__':print(check()['status'])
