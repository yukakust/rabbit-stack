"""Strict cached native board observation; not attestation/write authority."""
import json,struct,sys
from board_build import policy
def decode(observation):
 raw=bytes.fromhex(observation['raw_hex'])
 if observation.get('format')!='QBDI1' or len(raw)!=160 or raw[:8]!=b'QBDI0001':raise ValueError('invalid board envelope')
 fields=struct.unpack_from('<15I',raw,8)
 phase,error,submitted,offset,polls,result,helper_bytes,board,chip,extended,usable,sm_state,sm_error,structures,sm_bytes=fields
 version,kind,stage,root_error,adapter,cleanup,users=struct.unpack_from('<7I',raw,100)
 p=policy()
 if raw[128:].hex()!=p['helper_sha256'] or phase>6 or submitted>101 or offset>24196 or helper_bytes not in (0,24193) or board>31 or chip>3 or extended>1 or usable>1 or sm_state>4 or structures>4096 or sm_bytes>1048576 or users>14 or cleanup>14 or adapter>13 or stage>20:raise ValueError('board bounds/policy mismatch')
 if board!=(result&0x7c00)>>10 or chip!=(result&0x18000)>>15 or extended!=bool(result&0x40000) or usable!=bool(phase==5 and not result&255 and board):raise ValueError('board result contradicts cached IDs')
 try:variant=raw[68:100].split(b'\0',1)[0].decode('ascii')
 except UnicodeError as e:raise ValueError('non-ascii variant') from e
 if len(variant)>31 or any(ord(c)<32 or ord(c)>126 for c in variant) or raw[68+len(variant):100]!=bytes(32-len(variant)) or bool(variant)!=(sm_state==3):raise ValueError('invalid variant state/padding')
 if bool(sm_error)!=(sm_state==4) or (sm_state in (2,3) and (not structures or not sm_bytes)):raise ValueError('invalid SMBIOS completion')
 if phase==5 and (error or submitted!=101 or offset!=24196 or not polls or helper_bytes!=24193 or version!=p['physical_version'] or kind!=p['physical_type'] or sm_state not in (1,2,3)):raise ValueError('false helper success')
 if stage==5 and (phase!=5 or root_error or adapter!=12 or cleanup!=14 or users):raise ValueError('false closed board query')
 complete=phase==5 and stage==5 and not root_error and adapter==12 and cleanup==14 and not users
 return {'format':'QBDI1','device_attestation':False,'phase':phase,'error':error,'submitted':submitted,'padded_helper_bytes':offset,'polls':polls,'result_hex':f'{result:08x}','board_id':board,'chip_id':chip,'extended_board_supported':bool(extended),'bmi_ids_usable':bool(usable),'smbios_state':sm_state,'smbios_error':sm_error,'variant':variant,'bmi_version':f'{version:08x}','bmi_type':kind,'native_stage':stage,'native_error':root_error,'adapter_phase':adapter,'cleanup_slots':cleanup,'dma_users':users,'helper_query_and_cleanup_complete':complete,'exact_board_selected':False,'main_firmware_started':False,'wifi_association':False}
if __name__=='__main__':print(json.dumps(decode(json.load(open(sys.argv[1]))),indent=2))
