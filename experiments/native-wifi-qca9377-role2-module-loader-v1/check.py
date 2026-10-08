"""Read-only software closure; never device/signing/entropy admission."""
from pathlib import Path
import json,hashlib,struct
R=Path(__file__).resolve().parent;REPO=R.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(x,msg):
 if not x:raise ValueError(msg)
def checked(root=R):
 r=Path(root);f=json.loads((r/'evidence/freeze.json').read_text())
 for name,h in f['source_sha256'].items():need(sha(r/name)==h,'source '+name)
 for name,h in f['artifact_sha256'].items():need(sha(r/name)==h,'artifact '+name)
 for filename,key in [('inputs.json','original_frozen_sources_sha256'),('parent-inputs.json','original_frozen_parent_sources_sha256'),('child-inputs.json','frozen_child_inputs_sha256')]:
  for name,h in json.loads((r/filename).read_text())[key].items():need(sha(REPO/name)==h,'frozen source preserved '+name)
 child=(r/'runs/child/supplicant.efi').read_bytes();pe=struct.unpack_from('<I',child,60)[0];need(struct.unpack_from('<H',child,pe+24+68)[0]==11,'real boot-service child')
 model=json.loads((r/'runs/checked/report.json').read_text());need(model['physical_admission'] is False and model['synthetic_firmware'] is True and model['coff_units']==6,'model provenance')
 q=json.loads((r/'runs/qemu/report.json').read_text());need(q['status']=='ACTUAL-QEMU-UEFI-SIGNED-RSN-CHILD-LOAD-START-OPTIONS-UNLOAD-PASS' and q['physical_admission'] is False and q['qemu_only'] is True and q['child_payload_sha256']==sha(r/'runs/child/supplicant.efi'),'actual OVMF child')
 log=(r/'runs/qemu/debug.log').read_text();need('MODULE CHILD QEMU PASS ROLE2 NO PHYSICAL NIC ENTROPY AUTH CLAIM' in log and 'MATURE SUPPLICANT OPEN AND UNLOAD REFUSAL PASS SYNTHETIC PROVIDERS' in log,'actual child lifecycle')
 p=r/'parent-projection';native=json.loads((p/'runs/native-projection/report.json').read_text());need(native['physical_admission'] is False and native['epoch_unreserved'] is True and native['fits'] is True and native['file_bytes']<=262144 and native['aggregate_mapped_bytes']<=4194304 and native['entropy_approved'] is False and native['GetRNG_calls']==0,'unsigned mapped/file caps')
 need(native['child_payload_sha256']==q['child_payload_sha256'],'same selected child')
 b=(p/'runs/native-projection/payload.efi').read_bytes();need(hashlib.sha256(b).hexdigest()==native['payload_sha256'] and len(b)==native['file_bytes'],'whole parent payload')
 pe=struct.unpack_from('<I',b,60)[0];need(struct.unpack_from('<I',b,pe+80)[0]==native['mapped_bytes'],'whole actual mapped')
 reproduction=json.loads((p/'runs/native-projection/reproduction.json').read_text());need(reproduction['payload_sha256']==[native['payload_sha256']]*3,'three actual equal builds')
 city=json.loads((p/'runs/native-projection/qemu-report.json').read_text());need(city['payload_sha256']==native['payload_sha256'] and city['world19_sha256']=='89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7' and len(city['gates'])==2,'world19 normal EMPTY')
 for i,g in enumerate(city['gates']):need(g['physical_verified'] is False and g['empty_boot'] is bool(i) and g['status']=='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS','actual city gate')
 return {'status':'ROLE2-SIGNED-MODULE-PARENT-OVMF-SOFTWARE-CLOSURE-PASS','physical_admission':False,'entropy_approved':False,'provider_authority':False,'payload_sha256':native['payload_sha256'],'child_payload_sha256':q['child_payload_sha256'],'aggregate_mapped_bytes':native['aggregate_mapped_bytes'],'global_external_pool_budget_not_implemented':True}
if __name__=='__main__':print(json.dumps(checked(),indent=2))
