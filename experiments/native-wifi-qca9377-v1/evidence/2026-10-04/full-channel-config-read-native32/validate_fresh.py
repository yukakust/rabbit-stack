import hashlib,json,sys
from pathlib import Path
repo=Path('/Users/yukakust/rabbit-stack');r=repo/'experiments/native-wifi-qca9377-v1';sys.path.insert(0,str(r))
from decode_diagnostic import decode
from init_preflight import checked_destinations,rejection_checks
p=r/'runs/mac-control';raw_path=p/'native32-pci.json';raw=json.loads(raw_path.read_text());d=decode(raw)
s=json.loads((repo/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json').read_text());receipt_path=Path(s['engine']['last_release_report']);receipt=json.loads(receipt_path.read_text())
assert raw['format']=='QPD17' and raw['peripheral']=='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF' and raw['writes']==0
assert receipt['status']=='EXACT-APPLIED-RECEIPT' and receipt['receiver_reported_applied'] and receipt['counter']==s['engine']['native_counter']==32 and receipt['payload_sha256']==s['engine']['payload_sha256']
assert s['counter']==14 and receipt['base_world_sha256']==s['world_sha256'] and not any(s.get(k) for k in ('pending','native_pending','recovery_pending'))
assert d['native_init']['warm_sequence_verified'] and d['native_init']['all_resources_restored'] and d['full_channel_read']['read_verified']
out=checked_destinations(d);out.update(negative_cases=rejection_checks(d),native_counter=32,world_counter=14,world_sha256=s['world_sha256'],payload_sha256=s['engine']['payload_sha256'],raw_sha256=hashlib.sha256(raw_path.read_bytes()).hexdigest(),receipt_sha256=hashlib.sha256(receipt_path.read_bytes()).hexdigest(),verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),fresh_warm_and_full_channel_ce7_proof=True)
(p/'native32-preflight.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status']);print(out['target_tables']);print(out['early_alloc'],out['option_flag2'])
