#!/usr/bin/env python3
"""Interpret a bounded read-only PCI report; never infers BMI/firmware support."""
import argparse,json,struct,hashlib
from pathlib import Path
def combine_qpd13(prefix,extension):
 if len(prefix)!=716 or prefix[:4]!=b'QPD'+bytes([13]) or len(extension)!=120 or extension[:4]!=b'QIC'+bytes([1]):raise ValueError('invalid split diagnostic envelope')
 if hashlib.sha256(prefix).digest()!=extension[4:36]:raise ValueError('split diagnostic hash mismatch')
 if struct.unpack_from('<I',prefix,128)[0] not in (5,6,7):raise ValueError('probe still active')
 return {'format':'QPD13','raw_hex':(prefix+extension[36:]).hex(),'read_strategy':'split_sha256'}
def combine_qpd14(prefix,extension):
 if len(prefix)!=716 or prefix[:4]!=b'QPD'+bytes([14]) or len(extension)!=184 or extension[:4]!=b'QIC'+bytes([1]):raise ValueError('invalid QPD14 split envelope')
 if hashlib.sha256(prefix).digest()!=extension[4:36]:raise ValueError('split diagnostic hash mismatch')
 if struct.unpack_from('<I',prefix,128)[0] not in (5,6,7,20):raise ValueError('init probe still active')
 result={'format':'QPD14','raw_hex':(prefix+extension[36:]).hex(),'read_strategy':'split_sha256'}
 decode(result)
 return result
def combine_qpd15(prefix,extension):
 if len(prefix)!=716 or prefix[:4]!=b'QPD'+bytes([15]) or len(extension)!=208 or extension[:4]!=b'QIC'+bytes([1]):raise ValueError('invalid QPD15 split envelope')
 if hashlib.sha256(prefix).digest()!=extension[4:36]:raise ValueError('split diagnostic hash mismatch')
 if struct.unpack_from('<I',prefix,128)[0] not in (5,6,7,20):raise ValueError('init probe still active')
 result={'format':'QPD15','raw_hex':(prefix+extension[36:]).hex(),'read_strategy':'split_sha256'}
 decode(result)
 return result
def combine_qpd16(prefix,extension):
 if len(prefix)!=716 or prefix[:4]!=b'QPD'+bytes([16]) or len(extension)!=244 or extension[:4]!=b'QIC'+bytes([1]):raise ValueError('invalid QPD16 split envelope')
 if hashlib.sha256(prefix).digest()!=extension[4:36]:raise ValueError('split diagnostic hash mismatch')
 if struct.unpack_from('<I',prefix,128)[0] not in (5,6,7,20):raise ValueError('init probe still active')
 result={'format':'QPD16','raw_hex':(prefix+extension[36:]).hex(),'read_strategy':'split_sha256'}
 decode(result)
 return result
def combine_qpd17(prefix,extension):
 if len(prefix)!=716 or prefix[:4]!=b'QPD'+bytes([17]) or len(extension)!=244 or extension[:4]!=b'QIC'+bytes([1]):raise ValueError('invalid QPD17 split envelope')
 if hashlib.sha256(prefix).digest()!=extension[4:36]:raise ValueError('split diagnostic hash mismatch')
 if struct.unpack_from('<I',prefix,128)[0] not in (5,6,7,20):raise ValueError('probe still active')
 result={'format':'QPD17','raw_hex':(prefix+extension[36:]).hex(),'read_strategy':'split_sha256'}
 decode(result)
 return result
def combine_qpd18(prefix,extension):
 if len(prefix)!=716 or prefix[:4]!=b'QPD'+bytes([18]) or len(extension)!=244 or extension[:4]!=b'QIC'+bytes([1]):raise ValueError('invalid QPD18 split envelope')
 if hashlib.sha256(prefix).digest()!=extension[4:36]:raise ValueError('split diagnostic hash mismatch')
 if struct.unpack_from('<I',prefix,128)[0] not in (5,6,7,20):raise ValueError('probe still active')
 result={'format':'QPD18','raw_hex':(prefix+extension[36:]).hex(),'read_strategy':'split_sha256'}
 decode(result)
 return result
def decode(value):
 version=1 if value.get('format')=='QPD1' else 2 if value.get('format')=='QPD2' else 3 if value.get('format')=='QPD3' else 4 if value.get('format')=='QPD4' else 5 if value.get('format')=='QPD5' else 6 if value.get('format')=='QPD6' else 7 if value.get('format')=='QPD7' else 8 if value.get('format')=='QPD8' else 9 if value.get('format')=='QPD9' else 10 if value.get('format')=='QPD10' else 11 if value.get('format')=='QPD11' else 12 if value.get('format')=='QPD12' else 13 if value.get('format')=='QPD13' else 14 if value.get('format')=='QPD14' else 15 if value.get('format')=='QPD15' else 16 if value.get('format')=='QPD16' else 17 if value.get('format')=='QPD17' else 18 if value.get('format')=='QPD18' else 0
 length=128 if version==1 else 160 if version==2 else 144 if version==3 else 196 if version==4 else 240 if version==5 else 246 if version==6 else 280 if version==7 else 356 if version==8 else 620 if version==9 else 700 if version==10 else 716 if version==11 else 924 if version>=16 else 888 if version==15 else 864 if version==14 else 800
 if not version or not isinstance(value.get('raw_hex'),str) or len(value['raw_hex'])!=length*2:
  raise ValueError('bounded QPD1 envelope required')
 raw=bytes.fromhex(value['raw_hex'])
 if len(raw)!=length or raw[:4]!=b'QPD'+bytes([version]):raise ValueError('invalid QPD bytes')
 flags,count,targets=struct.unpack_from('<I',raw,4)[0],struct.unpack_from('<I',raw,16)[0],struct.unpack_from('<I',raw,20)[0]
 enum_status,read_status,location_status=struct.unpack_from('<Q',raw,8)[0],struct.unpack_from('<Q',raw,24)[0],struct.unpack_from('<Q',raw,32)[0]
 if flags&~63 or any(raw[60:64]):raise ValueError('unknown flags/reserved bytes')
 config=list(struct.unpack_from('<16I',raw,64));bdf=list(struct.unpack_from('<4I',raw,40))
 result={'format':'QPD'+str(version),'device_attestation':False,'flags':flags,'enum_status':f'{enum_status:016x}',
  'handle_count':count,'target_count':targets,'read_status':f'{read_status:016x}',
  'location_status':f'{location_status:016x}','bdf':bdf,'config_words':[f'{n:08x}' for n in config],
  'physical_identity_usable':False,'wifi_association_verified':False,'bmi_target_version':None}
 if flags&2:
  result.update(vendor=f'{config[0]&65535:04x}',device=f'{config[0]>>16:04x}',
   subsystem_vendor=f'{config[11]&65535:04x}',subsystem_device=f'{config[11]>>16:04x}',
   pci_revision=config[2]&255,command=f'{config[1]&65535:04x}',bar0_raw=f'{config[4]:08x}')
  usable=(flags==15 and not enum_status and targets==1 and count<=64 and config[0]==0x0042168c
   and config[2]>>16==0x0280 and (config[3]>>16)&127==0 and not location_status
   and bdf[0]<=65535 and bdf[1]<=255 and bdf[2]<=31 and bdf[3]<=7)
  result['physical_identity_usable']=usable
  if usable:
   result['board_catalog_candidate']=f'bus=pci,vendor=168c,device=0042,subsystem-vendor={config[11]&65535:04x},subsystem-device={config[11]>>16:04x}'
   result['bar0']=f'{((config[5]<<32) if config[4]&6==4 else 0)|(config[4]&0xfffffff0):016x}'
 if version==2:
  stage,chip,error,cleanup,extent,attributes=struct.unpack_from('<IIIIQQ',raw,128)
  if stage>4 or cleanup not in (1,2):raise ValueError('invalid bringup state')
  result['wake_probe']={'stage':stage,'chip_id':f'{chip:08x}','error':error,'cleanup_completed':cleanup==1,
   'bar_extent':extent,'original_attributes':f'{attributes:016x}',
   'chip_revision':(chip>>8)&15 if stage==2 else None,
   'probe_succeeded':stage==2 and not error and cleanup==1,'dma_enabled':False,'firmware_uploaded':False}
 if version>=4:
  stage,chip,error,cleanup,extent,attrs,phase,reset_error,owned,firmware,original,actual,pm,reserved,initial,readback,revalidation=struct.unpack_from('<IIIIQQIIIIHHHHIII',raw,128)
  if stage>(20 if version>=14 else 16 if version>=10 else 13 if version>=9 else 12 if version>=5 else 7) or cleanup not in (1,2) or phase>4 or owned>1 or (reserved and version<6):raise ValueError('invalid reset telemetry')
  result['reset_probe']={'stage':stage,'chip_id':f'{chip:08x}','error':error,'cleanup_completed':cleanup==1,'bar_extent':extent,'original_attributes':f'{attrs:016x}','reset_phase':phase,'reset_error':reset_error,'reset_owned':bool(owned),'fw_indicator':f'{firmware:08x}','fw_initialized_seen':bool(firmware&2),'original_command':f'{original:04x}','active_command_snapshot':f'{actual:04x}','pmcsr':f'{pm:04x}','global_reset_initial':f'{initial:08x}','global_reset_readback':f'{readback:08x}','revalidation_error':revalidation,'chip_revision':(chip>>8)&15 if stage==5 and chip else None,'identity_probe_succeeded':stage==5 and not error and cleanup==1,'dma_enabled':False,'firmware_uploaded':False}
 if version>=5:
  rom_error,indicator,bmi_error,version_word,type_word,info_length,users,bus_phase,bus_error,bus_owned,held=struct.unpack_from('<11I',raw,196)
  if users>(14 if version>=14 else 4) or bus_phase>4 or bus_owned>1 or held>(0x3fff if version>=14 else 15):raise ValueError('invalid DMA/BMI telemetry')
  received=bmi_error==0 and version_word not in (0,0xffffffff) and type_word not in (0,0xffffffff)
  released=cleanup==1 and not users and not held and not bus_owned
  result['reset_probe'].update(cleanup_completed=released,dma_enabled=bus_phase==2,chip_revision=(chip>>8)&15 if chip else None)
  result['bmi_probe']={'stage':stage,'rom_error':rom_error,'rom_indicator':f'{indicator:08x}','rom_ready_seen':indicator!=0xffffffff and not(indicator&1) and bool(indicator&2),'bmi_error':bmi_error,'reply_received':received,'target_version_raw':f'{version_word:08x}','target_type_raw':type_word,'reply_length_field':info_length,'dma_buffers_held':users,'dma_hold_mask':held,'bus_phase':bus_phase,'bus_error':bus_error,'bus_owned':bool(bus_owned),'cleanup_completed':released,'query_and_cleanup_succeeded':stage==5 and not error and received and released,'firmware_compatibility_verified':False,'firmware_uploaded':False}
  if received:result['bmi_target_version']=f'{version_word:08x}'
 if version>=6:
  original,readback,owned,link_error=struct.unpack_from('<HHBB',raw,240)
  if owned>1 or link_error>7:raise ValueError('invalid PCIe lifecycle telemetry')
  result['pcie_link']={'original_control':f'{original:04x}','active_control_snapshot':f'{reserved:04x}','last_readback':f'{readback:04x}','owned':bool(owned),'error':link_error,'restore_completed':not owned and original==readback}
 if version>=7:
  orig,cmd,owned,err,en0,en,core0,core,writes,link,status,cause=struct.unpack_from('<HHBBIIIIIHHI',raw,246)
  if owned>1 or err>12 or status:raise ValueError('invalid boot IRQ telemetry')
  restored=not owned and cmd==orig and en==en0 and not((core^core0)&0x800) and not(cause&0x7fc00)
  result['boot_irq']={'original_command':f'{orig:04x}','command_readback':f'{cmd:04x}','owned':bool(owned),'error':err,'original_enable':f'{en0:08x}','last_enable':f'{en:08x}','original_core_control':f'{core0:08x}','last_core_control':f'{core:08x}','mmio_writes':writes,'post_reset_link_control':f'{link:04x}','pending_after_clear':f'{cause:08x}','host_irq_handler_installed':False,'restore_completed':restored}
  if owned:
   result['bmi_probe'].update(cleanup_completed=False,query_and_cleanup_succeeded=False)
   result['reset_probe']['cleanup_completed']=False
 if 8<=version<18:
  flags,mask,seed_tx,seed_rx,last_tx,last_rx,tx_read,tx_write,rx_read,rx_write,req,resp=struct.unpack_from('<II8HQQ',raw,280)
  nbytes=struct.unpack_from('<I',raw,352)[0]
  if flags&~127 or mask&~3 or any(i>=8 for i in (seed_tx,seed_rx,last_tx,last_rx,tx_read,tx_write,rx_read,rx_write)) or nbytes>12:
   raise ValueError('invalid pre-cleanup CE snapshot')
  if (not flags and any(raw[280:356])) or (flags and not flags&1) or (mask and not flags&1):
   raise ValueError('inconsistent pre-cleanup CE snapshot')
  for valid,address in ((flags&8,req),(flags&16,resp)):
   if (not valid and address) or (valid and (not address or address>0xffffffff)):
    raise ValueError('invalid snapshot DMA address')
  result['ce_exchange_snapshot']={'captured_before_cleanup':bool(flags&1),
   'tx_completed':bool(flags&2),'rx_completed':bool(flags&4),'last_observed_hardware_indices':
    {'tx':last_tx if mask&1 else None,'rx':last_rx if mask&2 else None},
   'initial_indices':{'tx':seed_tx,'rx':seed_rx},'software_indices':{'tx_read':tx_read,'tx_write':tx_write,'rx_read':rx_read,'rx_write':rx_write},
   'request_dma_address':f'{req:016x}' if flags&8 else None,'response_dma_address':f'{resp:016x}' if flags&16 else None,
   'tx_descriptor_hex':raw[320:328].hex() if flags&32 else None,'rx_descriptor_hex':raw[328:336].hex() if flags&64 else None,
   'response_hex':raw[336:348].hex() if flags&16 else None,'request_hex':raw[348:352].hex() if flags&8 else None,
   'received_bytes':nbytes,'basis':'last existing BMI poll + mapped memory before stop; not a fresh MMIO snapshot or device attestation'}
 if 9<=version<18:
  valid,failed_mask=struct.unpack_from('<II',raw,356)
  if valid&~255 or failed_mask&~255 or valid&failed_mask:raise ValueError('invalid pre-halt CE masks')
  engines=[]
  for i in range(8):
   words=struct.unpack_from('<8I',raw,364+i*32)
   if valid&(1<<i) and 0xffffffff in words:raise ValueError('invalid available pre-halt CE register')
   if not((valid|failed_mask)&(1<<i)) and any(words):raise ValueError('uncaptured CE register data')
   engines.append({'engine':i,'available':bool(valid&(1<<i)),'read_failed_or_all_ones':bool(failed_mask&(1<<i)),
    **{name:f'{word:08x}' for name,word in zip(('source_base','source_size','destination_base','destination_size','control','command','source_read','destination_read'),words)}})
  result['ce_before_first_halt']={'valid_mask':valid,'failed_mask':failed_mask,'complete':(valid|failed_mask)==255,'all_available':valid==255,'engines':engines,'basis':'bounded read-only registers after ROM-ready, before first halt; bus mastering off; addresses not dereferenced'}
 if 10<=version<18:
  phase,error,flags,target,ce,core=struct.unpack_from('<6I',raw,620)
  command,itx,irx,otx,orx,mask,tr,tw,rr,rw=struct.unpack_from('<10H',raw,644)
  address=struct.unpack_from('<Q',raw,664)[0];value,nbytes,reserved=struct.unpack_from('<III',raw,688)
  if phase>3 or flags&~15 or mask&~3 or any(i>=8 for i in (itx,irx,otx,orx,tr,tw,rr,rw)) or nbytes>4 or reserved:
   raise ValueError('invalid CE7 diagnostic snapshot')
  if not flags and any(raw[620:700]):raise ValueError('uncaptured CE7 data')
  if flags and not flags&1:raise ValueError('unlatched CE7 data')
  if flags&8 and (not address or address>0xffffffff):raise ValueError('invalid CE7 response address')
  if not flags&8 and (address or value):raise ValueError('unavailable CE7 response data')
  if target and (target!=0x004008f8 or ce!=((core&0x7ff)<<21)|0x1008f8):raise ValueError('invalid fixed CE7 target')
  if flags and (phase==0 or (phase==3 and not 1<=error<=11)):raise ValueError('invalid captured CE7 phase')
  if phase in (1,2) and target!=0x004008f8:raise ValueError('missing fixed CE7 target')
  if phase==2 and (error or flags!=15 or nbytes!=4 or mask!=3 or command&6!=6):raise ValueError('invalid completed CE7 read')
  result['ce7_diagnostic']={'captured_before_cleanup':bool(flags&1),'phase':phase,'error':error,
   'tx_completed':bool(flags&2),'rx_completed':bool(flags&4),'read_completed':phase==2 and not error,
   'target_address':f'{target:08x}','ce_address':f'{ce:08x}','core_control':f'{core:08x}',
   'active_command':f'{command:04x}','initial_indices':[itx,irx],
   'last_observed_indices':[otx if mask&1 else None,orx if mask&2 else None],
   'software_indices':[tr,tw,rr,rw],'response_dma_address':f'{address:016x}' if flags&8 else None,
   'tx_descriptor_hex':raw[672:680].hex(),'rx_descriptor_hex':raw[680:688].hex(),
   'response_word':f'{value:08x}' if flags&8 else None,'received_bytes':nbytes,
   'target_pointer_used':False,'target_config_written':False,'firmware_uploaded':False}
 if 11<=version<18:
  first,last,polls,budget=struct.unpack_from('<4I',raw,700)
  ce7=result['ce7_diagnostic']
  if (not ce7['captured_before_cleanup'] and any(raw[700:716])) or (ce7['captured_before_cleanup'] and budget!=3000000):raise ValueError('invalid CE7 polling budget')
  if (not polls and (first or last)) or (polls and (last<first)):raise ValueError('invalid CE7 polling time')
  ce7.update(first_poll_elapsed_us=first if polls else None,last_poll_elapsed_us=last if polls else None,poll_count=polls,wait_budget_us=budget if budget else None,
   completion_observed_after_wait_budget=bool(ce7['read_completed'] and last>=budget),device_completion_timestamp_known=False)
 if version>=12:
  phase,error,mask,address,target,nbytes=struct.unpack_from('<6I',raw,716)
  words=list(struct.unpack_from('<11I',raw,740));first,last,polls,reserved=struct.unpack_from('<4I',raw,784)
  if phase>5 or mask&~7 or reserved or (polls and last<first) or (not polls and (first or last)):raise ValueError('invalid configuration snapshot')
  if phase==0 and any(raw[716:800]):raise ValueError('unstarted configuration data')
  preflight_rejected=phase==5 and error==1 and mask==0 and target==0 and nbytes==0 and not any(words) and not any((first,last,polls))
  if phase and ((version<17 and (not result['ce7_diagnostic']['read_completed'] or f'{address:08x}'!=result['ce7_diagnostic']['response_word'])) or (not preflight_rejected and address!=0x00401ee0)):raise ValueError('configuration read lacks validated fixed state address')
  if target not in (0,0x00401ee0,0x00400900,0x004008cc) or nbytes not in (0,4,36):raise ValueError('configuration address/length outside Target Pack')
  if (not mask&1 and any(words[:9])) or (not mask&2 and words[9]) or (not mask&4 and words[10]):raise ValueError('unread configuration fields')
  if phase==4 and (error or mask!=7 or target!=0x004008cc or nbytes!=4):raise ValueError('incomplete configuration snapshot')
  if version>=17 and phase in (1,2,3) and mask==7:raise ValueError('completed config with active phase')
  if version>=17 and phase in (1,2,3) and error:raise ValueError('active config with fault')
  if phase==5 and not error:raise ValueError('configuration fault missing error')
  result['initial_config_read']={'phase':phase,'error':error,'read_mask':mask,'read_completed':phase==4 and mask==7,
   'interconnect_word_value':f'{address:08x}' if phase else None,'fixed_state_address':'00401ee0' if phase and not preflight_rejected else None,'last_target_address':f'{target:08x}',
   'state_words':[f'{n:08x}' for n in words[:9]],'pipe_config_address':f'{words[0]:08x}' if mask&1 else None,
   'service_map_address':f'{words[1]:08x}' if mask&1 else None,'early_alloc':f'{words[9]:08x}' if mask&2 else None,
   'option_flag2':f'{words[10]:08x}' if mask&4 else None,'first_poll_elapsed_us':first if polls else None,
   'last_poll_elapsed_us':last if polls else None,'poll_count':polls,'target_config_written':False,'pointers_followed':False,
   'device_completion_timestamp_known':False,'configuration_compatibility_verified':False}
 if version>=14:
  a,ae,w,we,wo,co,cpu,pipes,c,allocated,cursor,verified,recovery,ro,ri,me=struct.unpack_from('<16I',raw,800)
  if a>13 or w>13 or c>7 or recovery>4 or max(wo,co,verified,ro)>1 or cpu>2 or pipes>2 or allocated>14 or cursor>14:
   raise ValueError('invalid native init bounds')
  if bus_phase==2 or actual&4 or users>held.bit_count():raise ValueError('unexpected active DMA/native held inventory')
  if stage not in (0,1,2,3,4,5,6,7,18,19,20):raise ValueError('unknown native init stage')
  if any(raw[204:220]) or (any(raw[356:716]) if version==18 else any(raw[280:716 if version>=17 else 800])):raise ValueError('unexpected legacy BMI/CE7 data in init profile')
  if stage==7 and any(raw[800:]):raise ValueError('absent target with init data')
  if verified and (recovery!=3 or ro or ri!=2 or wo or co):raise ValueError('unverified cold recovery claimed')
  full_release=(result['reset_probe']['cleanup_completed'] and result['pcie_link']['restore_completed'] and result['boot_irq']['restore_completed'] and not result['reset_probe']['reset_owned'] and not wo and not co and not ro)
  if a==12 and (wo or co or ro or users or held or bus_owned or c not in (0,6)):
   raise ValueError('closed adapter still owns resources')
  if stage==5 and (result['reset_probe']['error'] or not full_release or a!=12 or ae or w!=12 or we or cpu!=2 or pipes!=2 or c!=6 or allocated!=14 or cursor!=14 or verified or me):
   raise ValueError('success lacks exact warm/channel/restore proof')
  if stage==20 and (a!=13 or not result['reset_probe']['error'] or not ae or cleanup!=2):raise ValueError('invalid retained adapter')
  result['native_init']={'adapter_phase':a,'adapter_error':ae,'warm_phase':w,'warm_error':we,
   'warm_owned':bool(wo),'ce_reset_owned':bool(co),'cpu_resets':cpu,'pipe_initializations':pipes,
   'channels_phase':c,'allocated_pages':allocated,'cleanup_cursor':cursor,
   'cold_recovery_verified':bool(verified),'cold_recovery_phase':recovery,'cold_recovery_owned':bool(ro),
   'cold_recovery_indicator':f'{ri:08x}','mapped_guard_error':me,
   'warm_and_channels_verified':stage==5,'all_resources_restored':full_release,
   'retained':stage==20,'bus_master_enabled_during_probe':False,'target_ram_written':False,'firmware_uploaded':False}
 if version>=15:
  fp,indicator,elapsed,first,second,reset_read=struct.unpack_from('<6I',raw,864)
  if fp>12 or first>300 or second>300:raise ValueError('invalid warm failure bounds')
  if bool(fp)!=bool(we) or (w==13)!=bool(fp):raise ValueError('warm failure phase/error mismatch')
  if not fp and elapsed:raise ValueError('elapsed failure without failure')
  if stage==5 and (fp or indicator!=2 or not first or not second):raise ValueError('warm success lacks ROM observations')
  result['native_init']['warm_failure']={'phase':fp,'last_indicator':f'{indicator:08x}',
   'phase_elapsed_us':elapsed,'first_rom_polls':first,'second_rom_polls':second,
   'last_reset_control_read':f'{reset_read:08x}','additional_mmio_operations':0,
   'basis':'cached warm operations before cleanup; polling times are host observations'}
 if version>=16:
  phase,error,value,bytes_read,tx,rx,mask,polls,elapsed=struct.unpack_from('<9I',raw,888)
  if phase>3 or tx>1 or rx>1 or mask>3 or bytes_read not in (0,4):raise ValueError('invalid full CE7 bounds')
  complete=phase==2 and not error and value==0x00401ee0 and bytes_read==4 and tx==rx==1 and mask==3 and polls>0
  if stage==5 and not complete:raise ValueError('success lacks fixed full-channel CE7 read')
  if phase==0 and any(raw[888:]):raise ValueError('unstarted full CE7 with data')
  if version>=17 and result['initial_config_read']['phase'] and not complete:raise ValueError('config lacks full-channel interconnect proof')
  if version>=17 and stage==5 and not result['initial_config_read']['read_completed']:raise ValueError('success lacks config read')
  result['native_init']['warm_sequence_verified']=w==12 and not we and cpu==pipes==2
  result['native_init']['bus_master_enabled_during_probe']=True if phase==2 or mask or polls else None
  result['reset_probe']['dma_enabled']=result['native_init']['bus_master_enabled_during_probe']
  result['native_init']['terminal_dma_released']=full_release
  result['full_channel_read']={'phase':phase,'error':error,'interconnect_word':f'{value:08x}' if complete else None,
   'bytes':bytes_read,'tx_completed':bool(tx),'rx_completed':bool(rx),'observed_mask':mask,'polls':polls,
   'last_poll_elapsed_us':elapsed,'read_verified':complete,'target_address':'004008f8',
   'target_ram_written':False,'firmware_uploaded':False,'basis':'fixed CE7 read using retained full14 mapping inventory'}
 if version==18:
  sp,se,op,wm,rm,attempts,ca,cb,cr,bp,be,bv,bt,bl,bb,tx,rx,np,elapsed=struct.unpack_from('<19I',raw,280)
  if sp>5 or op>10 or wm>31 or rm>31 or rm&~wm or attempts>5 or ca>1 or bp>3 or tx>1 or rx>1 or bb>12:raise ValueError('invalid setup bounds')
  if sp==0 and any(raw[280:356]):raise ValueError('unstarted setup with data')
  if sp!=5 and se:raise ValueError('non-fault setup with error')
  if sp==1 and op>=10:raise ValueError('active setup with completed operation count')
  if sp==5 and not se:raise ValueError('setup fault without error')
  if (wm or attempts or sp) and not result['initial_config_read']['read_completed']:raise ValueError('setup lacks config proof')
  if wm&16 and (wm!=31 or rm&15!=15):raise ValueError('config-done posted before previous readbacks')
  if ca and (op!=10 or wm!=31 or rm!=31):raise ValueError('CPU wake before complete readbacks')
  complete=sp==4 and not se and op==10 and wm==rm==31 and attempts==5 and ca and bp==2 and not be and bv not in (0,0xffffffff) and bt not in (0,0xffffffff) and bb==12 and tx==rx==1 and np>0
  if stage==5 and not complete:raise ValueError('setup success lacks config/BMI proof')
  result['config_setup']={'phase':sp,'error':se,'operation':op,'write_mask':wm,'readback_mask':rm,'write_attempts':attempts,'target_ram_write_attempted':bool(attempts),'cpu_wake_attempted':bool(ca),'cpu_before':f'{cb:08x}','cpu_readback':f'{cr:08x}','bmi_phase':bp,'bmi_error':be,'bmi_version':f'{bv:08x}','bmi_type':bt,'bmi_length_field':bl,'bmi_bytes':bb,'bmi_tx_completed':bool(tx),'bmi_rx_completed':bool(rx),'bmi_polls':np,'bmi_last_elapsed_us':elapsed,'setup_and_bmi_verified':bool(complete),'firmware_uploaded':False}
  result['bmi_probe'].update(reply_received=bp==2 and not be,target_version_raw=f'{bv:08x}',target_type_raw=bt,reply_length_field=bl,bmi_error=be,query_and_cleanup_succeeded=bool(complete and full_release),basis='native-owned post-config BMI telemetry')
  if bp==2 and not be:result['bmi_target_version']=f'{bv:08x}'
  result['native_init']['target_ram_written']=bool(attempts)
  result['initial_config_read']['target_config_written']=bool(attempts)
 if version==3:
  pm,csr,pcie,link,status,reserved=struct.unpack_from('<HHHHII',raw,128)
  if status>3 or reserved:raise ValueError('invalid power-capability snapshot')
  result['pci_power']={'status':status,'pm_capability_offset':pm,'pmcsr':f'{csr:04x}','power_state':csr&3 if status==1 else None,'pcie_capability_offset':pcie,'link_control':f'{link:04x}','aspm_enabled':bool(link&3) if pcie else None,'writes':0}
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
 if a.input.stat().st_size>4096:raise ValueError('oversized report')
 result=decode(json.loads(a.input.read_text()));text=json.dumps(result,indent=2)+'\n'
 if a.output:a.output.write_text(text)
 print(text,end='')
if __name__=='__main__':main()
