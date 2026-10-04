"""Strict cached boot trial observation; never write authority or attestation."""
import json,struct,sys
NAMES=('phase','error','plan_phase','plan_error','submitted','completed','board_address','calibration_result','offset','ready_bytes','credit_count','credit_size','max_endpoints','boot_round','ram_phase','ram_error','asset_ready','asset_pinned','native_stage','native_error','adapter_phase','cleanup_slots','dma_users','bmi_version','bmi_type','board_phase','board_error','board_result','asset_bitmap','boot_attempted')
def decode(o):
 raw=bytes.fromhex(o['raw_hex'])
 if o.get('format')!='QWBT1' or len(raw)!=160 or raw[:8]!=b'QWBT0001' or raw[128:].hex()!='8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01':raise ValueError('invalid exact boot envelope')
 d=dict(zip(NAMES,struct.unpack_from('<30I',raw,8)))
 if d['phase']>6 or d['plan_phase']>22 or d['submitted']>4000 or d['completed']>d['submitted'] or d['offset']>727125 or d['ready_bytes']>256 or d['max_endpoints']>9 or d['native_stage']>20 or d['adapter_phase']>13 or d['cleanup_slots']>14 or d['dma_users']>14 or d['board_phase']>6 or d['ram_phase']>6 or d['asset_bitmap']>4095:raise ValueError('boot bounds mismatch')
 if any(d[k]>1 for k in ('boot_round','asset_ready','asset_pinned','boot_attempted')):raise ValueError('invalid boot boolean')
 if d['phase']==5:
  if d['error'] or d['plan_error'] or d['plan_phase']!=20 or d['submitted']!=d['completed'] or d['submitted']<3000 or d['calibration_result'] or d['ready_bytes'] not in (16,20) or not d['credit_count'] or not d['credit_size'] or not d['max_endpoints'] or d['board_phase']!=5 or d['board_error'] or d['board_result'] or d['bmi_version']!=0x05020001 or d['bmi_type']!=8 or d['asset_bitmap']!=4095 or not d['asset_ready']:raise ValueError('false main/HTC success')
 closed=d['native_stage'] in (5,6) and d['adapter_phase']==12 and d['cleanup_slots']==14 and not d['dma_users'] and not d['asset_pinned']
 d.update(format='QWBT1',device_attestation=False,htc_ready_observed=d['phase']==5,all_loader_resources_released=closed,physical_trial_complete=d['phase']==5 and closed and not d['native_error'],wifi_connected=False)
 return d
if __name__=='__main__':print(json.dumps(decode(json.load(open(sys.argv[1]))),indent=2))
