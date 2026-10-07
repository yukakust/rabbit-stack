"""Exact installed55 zero-write BOOT capture; RAM release is not boot failure."""
import json,struct,subprocess
from pathlib import Path
import scan_route as r
S=r.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json';out=r.ROOT/'runs/control';out.mkdir(parents=True,exist_ok=True)
with r.flow.state_lock(S):
 s=r.flow.read_json(S)
 if any(s.get(k) for k in ('pending','native_pending','recovery_pending')) or s['engine']['native_counter']!=55 or s['engine']['payload_sha256']!=r.PAYLOAD_SHA:raise ValueError('exact installed55 idle transport required')
 run=subprocess.run([str(r.ROOT/'runs/control/boot-reader-v2'),'--read'],capture_output=True,text=True,timeout=130);(out/'boot55-v2.log').write_text(run.stderr)
 if run.returncode:raise RuntimeError(run.stderr)
 raw=json.loads(run.stdout);r.flow.save(out/'boot55.json',raw);b=bytes.fromhex(raw['raw_hex'])
 if raw.get('peripheral','').upper()!=r.PEER or raw.get('writes')!=0 or raw.get('format')!='QWBT1' or len(b)!=160 or b[:8]!=b'QWBT0001' or b[128:].hex()!='8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01':raise ValueError('exact known-peer BOOT required')
 names='phase error plan_phase plan_error submitted completed board_address calibration_result offset ready_bytes credit_count credit_size max_endpoints boot_round ram_phase ram_error asset_ready asset_pinned native_stage native_error adapter_phase cleanup_slots dma_users bmi_version bmi_type board_phase board_error board_result asset_bitmap boot_attempted'.split();d=dict(zip(names,struct.unpack('<30I',b[8:128])))
 if d['phase']>6 or d['plan_phase']>22 or d['submitted']>4000 or d['completed']>d['submitted'] or d['offset']>727125 or d['adapter_phase']>13 or d['cleanup_slots']>14 or d['dma_users']>14 or any(d[k]>1 for k in ('boot_round','asset_ready','asset_pinned','boot_attempted')):raise ValueError('BOOT bounds')
 d['all_loader_resources_released']=bool(d['native_stage'] in (5,6) and d['adapter_phase']==12 and d['cleanup_slots']==14 and not d['dma_users'] and not d['asset_pinned']);d['device_attestation']=False;d['wifi_connected']=False
 r.flow.save(out/'boot55.decoded.json',d);print(json.dumps(d))
