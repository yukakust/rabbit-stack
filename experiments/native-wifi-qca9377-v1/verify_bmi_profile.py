#!/usr/bin/env python3
"""Yukabox exact one-shot probe gates. OVMF target absent, host MMIO fixtures."""
import hashlib,json,subprocess,sys,shutil,os
from pathlib import Path
import bmi_build as build
import verify_ce_hw,verify_bmi,verify_dma
import verify_reset
import verify_diagnostic as diagnostic
import verify_port
import verify_ble_recovery as ble_gate
from decode_diagnostic import decode,combine_qpd13
sys.path.insert(0,str(build.CITY))
import actors_gate
ROOT=build.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(source):
 source=diagnostic.fixture(source).replace('diagnostic_reply_size!=129','diagnostic_reply_size!=247').replace('"QPD\\1"','"QPD\\15"')
 return ble_gate.fixture(build.one(source,'say("ACTUAL UEFI PCI ENUMERATION READ THROUGH MOCK USB ATT; QCA ABSENT; NO WRITES");',r'''
 uint8_t joined_prefix[716];copy(joined_prefix,diagnostic_reply+1,246);
 if(le32(diagnostic_reply+129)!=7||le32(diagnostic_reply+141)!=1)return 1;
 uint8_t blob[5]={0x0c,10,0,246,0};
 if(att(blob,5,0x0d)||diagnostic_reply_size!=247)return 1;
 for(unsigned i=0;i<246;i++)if(diagnostic_reply[i+1])return 1;
 copy(joined_prefix+246,diagnostic_reply+1,246);
 uint8_t final_blob[5]={0x0c,10,0,236,1};
 if(att(final_blob,5,0x0d)||diagnostic_reply_size!=225)return 1;
 for(unsigned i=0;i<224;i++)if(diagnostic_reply[i+1])return 1;
 copy(joined_prefix+492,diagnostic_reply+1,224);
 uint8_t extension[3]={0x0a,12,0};if(att(extension,3,0x0b)||diagnostic_reply_size!=121)return 1;
 if(!same(diagnostic_reply+1,(const uint8_t*)"QIC\1",4))return 1;
 void rabbit_sha256(uint8_t*,const uint8_t*,size_t);uint8_t expected_hash[32];rabbit_sha256(expected_hash,joined_prefix,716);
 if(!same(diagnostic_reply+5,expected_hash,32))return 1;
 for(unsigned i=0;i<84;i++)if(diagnostic_reply[37+i])return 1;
 uint8_t bad_blob[5]={0x0c,10,0,205,2};if(att(bad_blob,5,1))return 1;
 uint8_t bad_extension[5]={0x0c,12,0,121,0};if(att(bad_extension,5,1))return 1;
 say("ACTUAL UEFI PCI ENUMERATION READ THROUGH MOCK USB ATT; QCA ABSENT; NO WRITES");
 say("LONG QPD13 READ/BLOB BOUNDS PASS; QCA ABSENT; NO IRQ WRITES");
 say("ONE-SHOT WIFI RESET PROBE TARGET ABSENT; CLEAN CLOSE AND CITY RETAINED");
 '''))
def main():
 target=json.loads((ROOT/'boot-irq-target.json').read_text())
 vendor=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/linux/drivers/net/wireless/ath/ath10k')
 for n,h in target['reference_sha256'].items():assert sha((vendor/n).read_bytes())==h,n
 diag_target=json.loads((ROOT/'diag-target.json').read_text())
 for n,h in diag_target['reference_sha256'].items():assert sha((vendor/n).read_bytes())==h,n
 assert diag_target['target_word']==0x004008f8 and diag_target['target_writes'] is False
 assert target['core_msi_firmware_mask']==0x800 and target['firmware_and_ce_mask']==0x7fc00
 out=ROOT/'runs/bmi-profile';out.mkdir(parents=True,exist_ok=False)
 verify_port.main()
 verify_reset.main()
 verify_ce_hw.main()
 verify_bmi.main()
 verify_dma.main()
 for component,run in [("ce","ce-hw"),("bmi","bmi"),("dma","dma")]:
  shutil.copyfile(ROOT/("runs/"+run+"/report.json"),out/(component+"-report.json"))
  shutil.copyfile(ROOT/("runs/"+run+"/host.log"),out/(component+"-host.log"))
 shutil.copyfile(ROOT/'runs/reset-core/report.json',out/'reset-report.json')
 shutil.copyfile(ROOT/'runs/reset-core/host.log',out/'reset-host.log')
 shutil.copyfile(ROOT/'runs/port/report.json',out/'port-report.json')
 shutil.copyfile(ROOT/'runs/port/host.log',out/'port-host.log')
 public=bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7')
 _,_,crypto=build.actors.engine.prepare(out,public)
 payload=build.compile_driver(out,crypto);assert payload==build.compile_driver(out,crypto)
 (out/'payload.efi').write_bytes(payload)
 exe=out/'bringup-test'
 subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
  *['-I'+str(p) for p in (ROOT,out,build.actors.OLD,build.actors.NATIVE)],
  str(ROOT/'bmi_probe_test.c'),*[str(out/n) for n in ('bmi_probe.c','diag_ce.c','reset_core.c','power_core.c','uefi_port.c','wake_core.c','pci_identity.c','rom_ready.c','bmi_transport.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c')],'-o',str(exe)],check=True)
 log=''
 for scenario in range(60):
  result=subprocess.run([str(exe),str(scenario)],capture_output=True,text=True,check=True,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'});log+=result.stdout+result.stderr
 for name,source,defs in [('ble-baseline',build.actors.LINK/'hci_link.c',['-DBASELINE']),('ble-fixed',out/'ble_recovery_link.c',[])]:
  test=out/name
  subprocess.run(['cc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',
   '-I'+str(build.actors.LINK),'-I'+str(build.actors.NATIVE),str(ROOT/'test_ble_recovery.c'),str(source),*defs,'-o',str(test)],check=True)
  result=subprocess.run([str(test)],capture_output=True,text=True,check=True)
  log+=name+': PASS\n'+result.stdout+result.stderr
 for line in log.splitlines():
  if not line.startswith('QPD13_MOCK='):continue
  raw=bytearray.fromhex(line.split('=',1)[1]);decoded=decode({'format':'QPD13','raw_hex':raw.hex()})
  prefix=bytes(raw[:716]);extension=b'QIC'+bytes([1])+hashlib.sha256(prefix).digest()+bytes(raw[716:])
  assert decode(combine_qpd13(prefix,extension))==decoded
  active=bytearray(prefix);active[128:132]=(17).to_bytes(4,'little');active_ext=b'QIC'+bytes([1])+hashlib.sha256(active).digest()+bytes(raw[716:])
  for a,b in ((prefix[:-1],extension),(prefix,extension[:-1]),(prefix,extension[:4]+bytes(32)+extension[36:]),(prefix,b'BAD!'+extension[4:]),(bytes(active),active_ext)):
   try:combine_qpd13(a,b)
   except ValueError:pass
   else:raise AssertionError('invalid split diagnostic accepted')
  assert decoded['ce_before_first_halt']['all_available']
  if not decoded['ce7_diagnostic']['read_completed']:
   assert not decoded['ce_exchange_snapshot']['captured_before_cleanup']
   continue
  if decoded['ce7_diagnostic']['response_word']!='00401ee0':
   assert decoded['initial_config_read']['phase']==5 and not decoded['ce_exchange_snapshot']['captured_before_cleanup'];continue
  if not decoded['initial_config_read']['read_completed']:
   assert not decoded['ce_exchange_snapshot']['captured_before_cleanup'];continue
  snapshot=decoded['ce_exchange_snapshot']
  assert snapshot['captured_before_cleanup'] and snapshot['request_hex']=='08000000'
  for offset,value in ((280,128),(284,4),(288,8),(304,0),(356,256),(360,1),(364,0xffffffff),(628,16),(648,8),(664,0),(632,0x400800),(632,0),(654,0),(644,0),(712,0),(708,0),(700,0xffffffff),(716,6),(724,8),(728,0),(732,0x400800),(736,5),(796,1),(724,0),(792,0)):
   bad=raw.copy();bad[offset:offset+4]=value.to_bytes(4,'little')
   try:decode({'format':'QPD13','raw_hex':bad.hex()})
   except ValueError:pass
   else:raise AssertionError('invalid CE snapshot accepted')
 log+='QPD13 actual host snapshots + invalid flags/indices/address decoding PASS\n'
 (out/'host.log').write_text(log)
 gates=[actors_gate.qemu_gate(out,payload,test_transform=fixture),actors_gate.qemu_gate(out,payload,True,test_transform=fixture)]
 files=('decode_diagnostic.py','read_pci.m','ble_recovery_build.py','test_ble_recovery.c','verify_ble_recovery.py','bmi_build.py','diag_ce.c','diag_ce.h','diag-target.json','bringup.h','bmi_probe.c','bmi_probe_test.c','verify_bmi_profile.py','reset_core.c','reset_core.h','reset_test.c','reset-target.json','verify_reset.py','power_core.c','power_core.h',
  'diagnostic_build.py','verify_diagnostic.py','pci_collect.c','pci_collect.h','pci_identity.c','pci_identity.h',
  'uefi_port.c','uefi_port.h','wake_core.c','wake_core.h','port_test.c','verify_port.py','wake-target.json','wake_test.c','rom_ready.c','rom_ready.h','bmi_transport.c','bmi_transport.h','ce_ring.c','ce_ring.h','ce_hw.c','ce_hw.h','ce_uefi.c','ce_uefi.h','ce_bus.c','ce_bus.h','dma_buffer.c','dma_buffer.h','ce_hw_test.c','ce_uefi_test.c','ce_bus_test.c','bmi_transport_test.c','verify_ce_hw.py','verify_bmi.py','ce-target.json','bmi-target.json','pcie_link.c','pcie_link.h','dma_buffer_test.c','verify_dma.py','boot_irq.c','boot_irq.h','boot-irq-target.json')
 paths=[ROOT/n for n in files]+[build.CITY/n for n in ('actors_build.py','city_core.c','city_core.h','city_display.c','actor_clock.c','actors_gate.py')]
 report={'status':'QCA-BOOTIRQ-PCIE-ROM-BMI-CITY-PROFILE-GATES-PASS','payload_sha256':sha(payload),
  'source_sha256':{str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in paths},
  'host_log_sha256':sha((out/'host.log').read_bytes()),'port_report_sha256':sha((out/'port-report.json').read_bytes()),
  'reset_report_sha256':sha((out/'reset-report.json').read_bytes()),'gates':gates,'physical_dell_verified':False,'dma':True,'ce_report_sha256':sha((out/'ce-report.json').read_bytes()),'bmi_report_sha256':sha((out/'bmi-report.json').read_bytes()),'dma_report_sha256':sha((out/'dma-report.json').read_bytes()),'pcie_aspm_reversible':True,'boot_irq_host_isolation':True,'ble_untracked_disconnect_recovery':True,'ce_snapshot_pre_cleanup':True,'ce_registers_before_first_halt':True,'fixed_ce7_read_only':True,'ce7_completion_before_timeout':True,'bounded_init_config_read':True,'hash_bound_split_diagnostic':True,'firmware_upload':False,
  'physical_operation':'reversible PCIe ASPM disable/restore + one-shot QCA reset + ROM-ready + four coherent DMA pages + fixed read-only CE7 target word + bounded fixed PCIe-state/earlyalloc/flag2 reads + halt/close/reuse + CE0/1 BMI target-info; verified all-eight halt, bus-master-off/Flush/Unmap/Free/PCI restore; no firmware upload'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('BRINGUP GATES PASS payload='+sha(payload))
if __name__=='__main__':main()
