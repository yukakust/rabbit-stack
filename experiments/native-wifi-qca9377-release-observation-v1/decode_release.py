"""Exact53 controlled-stop with genuine RAM release, not legacy boot decoder."""
import json,sys,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
sys.path.insert(0,str(ROOT.parent/'native-wifi-qca9377-persistent-admission-v1'));import route
sys.path.insert(0,str(route.PROFILE));from decode_profile import decode as profile_decode
sys.path.insert(0,str(route.V5));from read_startup import decode as startup_decode
NAMES='phase error plan_phase plan_error submitted completed board_address calibration_result offset ready_bytes credit_count credit_size max_endpoints boot_round ram_phase ram_error asset_ready asset_pinned native_stage native_error adapter_phase cleanup_slots dma_users bmi_version bmi_type board_phase board_error board_result asset_bitmap boot_attempted'.split()
VALUES=(5,0,20,0,3114,3114,4202432,3,0,20,2,1792,4,1,0,0,0,0,6,8448,12,14,0,84017153,8,5,0,0,0,1)
def decode(raw,startup,profile,assets):
 for o in (raw,startup,profile):
  if o.get('peripheral','').upper()!=route.PEER or o.get('writes')!=0:raise ValueError('known-peer zero-write required')
 b=bytes.fromhex(raw['raw_hex'])
 if raw.get('format')!='QWBT1' or len(b)!=160 or b[:8]!=b'QWBT0001' or b[128:].hex()!='8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01':raise ValueError('exact BOOT envelope required')
 values=struct.unpack('<30I',b[8:128])
 if values!=VALUES:raise ValueError('exact controlled-stop RAM-cleared tuple required')
 if assets['status']!='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' or assets['native_counter']!=53 or assets['native_payload_sha256']!=route.PAYLOAD_SHA or assets['completed_chunks']!=12 or len(assets['packets'])!=12:raise ValueError('exact prior12-chunk receipt required')
 receipt=assets['last_receipt']
 if receipt.get('peripheral','').upper()!=route.PEER or receipt['action']!=4 or receipt['error'] or receipt['bitmap']!=4095 or receipt['ready']!=1 or receipt['packet_sha256']!=assets['packets'][-1]['packet_sha256']:raise ValueError('correlated full RAM receipt required')
 w=startup_decode(startup);p=profile_decode(profile)
 if any(w[k]!=v for k,v in {'phase':2,'error':0,'transaction_phase':4,'ready_seen':1,'tx_complete':1,'abi_minor':574,'credit_available':2,'credit_outstanding':0,'memory_count':0,'reject_reason':0,'mac_hex':'c0b5d778c3fb'}.items()):raise ValueError('actual READY/MAC/INIT TX required')
 if not p['bounded_rx_trial_pass'] or p['rx_phase'] not in (1,3) or p['rx_error'] or p['polls']<1 or p['stop_latched']!=1 or p['cleanup_slots']!=14 or p['adapter_phase']!=12:raise ValueError('bounded RX and genuine all-owner clear required')
 # RX posted/queue fields are retained historical bookkeeping after the
 # actual lifecycle/PCI/DMA/map/pin inventory proves release. No RX clears
 # are fabricated and no claim about unseen queued payload bytes is made.
 d=dict(zip(NAMES,values));d.update(all_loader_resources_released=True,physical_trial_complete=True,controlled_stop=True,ram_assets_released=True,ready_observed=True,router_connected=False,device_attestation=False)
 return d,w,p
