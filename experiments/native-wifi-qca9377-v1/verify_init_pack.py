#!/usr/bin/env python3
"""Independent checks against pinned upstream chip parameters; no hardware I/O."""
import argparse,copy,hashlib,json,re,struct
from pathlib import Path
from init_tables import PIPES,SERVICES,describe_tables,table_bytes,validate_host_resources

def check_table_contents(sources):
 """Independently parse the pinned upstream data, not our candidate constants."""
 pci=sources['pci.c'];ce=sources['ce.h'];htc=sources['htc.h']
 symbols={n:int(v) for n,v in re.findall(r'#define\s+(PIPEDIR_\w+|CE_ATTR_FLAGS)\s+(\d+)',ce)}
 groups={n:int(v) for n,v in re.findall(r'(ATH10K_HTC_SVC_GRP_\w+|ATH10K_LOG_SERVICE_GROUP)\s*=\s*(\d+)',htc)}
 for name,group,index in re.findall(r'(ATH10K_HTC_SVC_ID_\w+)\s*=\s*SVC\((\w+),\s*(\d+)\)',htc):
  symbols[name]=(groups[group]<<8)|int(index)
 def value(token):
  token=token.strip()
  return symbols[token] if token in symbols else int(token,0)
 pipe_table=re.search(r'pci_target_ce_config_wlan\[\] = \{(.*?)\n\};',pci,re.S).group(1)
 fields=('pipenum','pipedir','nentries','nbytes_max','flags','reserved')
 rows=[]
 for body in re.findall(r'\{([^{}]+)\}',pipe_table)[:7]:
  found={n:value(v) for n,v in re.findall(r'\.(\w+)\s*=\s*__cpu_to_le32\(([^()]*)\)',body)}
  rows.append([found[n] for n in fields])
 rows=rows[:7];rows[5][1]=symbols['PIPEDIR_OUT'];rows[5][3]=2048
 assert tuple(map(tuple,rows))==PIPES,'candidate pipe table differs from upstream'
 services=re.search(r'pci_target_service_to_ce_map_wlan\[\] = \{(.*?)\n\};',pci,re.S).group(1)
 numbers=[value(v) for v in re.findall(r'__cpu_to_le32\(([^()]*)\)',services)]
 service_rows=[numbers[i:i+3] for i in range(0,len(numbers),3)]
 service_rows[15][2]=1
 assert not any(row[2]==5 for row in service_rows[:-1]), 'host-disabled CE5 service reference'
 assert re.search(r'attr = &ar_pci->attr\[5\];\s*attr->src_sz_max = 0;\s*attr->dest_nentries = 0;',pci)
 assert tuple(map(tuple,service_rows))==SERVICES,'candidate service map differs from upstream'
 expected=(b''.join(struct.pack('<6I',*row) for row in rows),b''.join(struct.pack('<3I',*row) for row in service_rows))
 assert expected==table_bytes()
 return describe_tables()

def resource_checks():
 # A fixture only: no live DMA mapping is asserted by this synthetic positive.
 resources=[{'pipe':p,'direction':d,'max_transfer':n,'owned':True,'mapped':True,
             'ring_entries':32,'receive_capacity':n if d&1 else 0}
            for p,d,n in ((0,2,256),(1,1,2048),(2,1,2048),(3,2,2048),(4,2,256),(7,3,2048))]
 assert validate_host_resources(resources)
 cases=[resources[:2],resources[:-1],resources+[resources[0]],None]
 for i in range(6):
  for name,val in (('owned',False),('mapped',False),('direction',0),('ring_entries',3),('max_transfer',65536)):
   bad=copy.deepcopy(resources);bad[i][name]=val;cases.append(bad)
 for name,val in (('receive_capacity',0),('receive_capacity',8192),('pipe',0),('pipe',6),('pipe',True),('owned',1)):
  bad=copy.deepcopy(resources);bad[1][name]=val;cases.append(bad)
 bad=copy.deepcopy(resources);bad[0]['receive_capacity']=1;cases.append(bad)
 bad=copy.deepcopy(resources);bad[0]['extra']=0;cases.append(bad)
 for bad in cases:
  try:validate_host_resources(bad)
  except ValueError:pass
  else:raise AssertionError('unsafe host resource inventory accepted')
 return len(cases)

def check_warm_sequence(sources):
 pci=sources['pci.c'];hw=sources['hw.c'];header=sources['hw.h']
 def function(name):
  return re.search(r'static (?:int|void) '+name+r'\(struct ath10k \*ar\)\n\{(.*?)\n\}',pci,re.S).group(1)
 body=function('ath10k_pci_warm_reset')
 calls=re.findall(r'(ath10k_pci_\w+)\(ar\)',body)
 expected=['irq_disable','warm_reset_si0','warm_reset_cpu','init_pipes','wait_for_target_init',
           'warm_reset_clear_lf','warm_reset_ce','warm_reset_cpu','init_pipes','wait_for_target_init']
 assert calls==['ath10k_pci_'+name for name in expected], 'warm reset ordering changed'
 cold=function('ath10k_pci_qca6174_chip_reset')
 assert re.findall(r'(ath10k_pci_\w+)\(ar\)',cold)==[
  'ath10k_pci_cold_reset','ath10k_pci_wait_for_target_init','ath10k_pci_warm_reset']
 regs=re.search(r'const struct ath10k_hw_regs qca6174_regs = \{(.*?)\};',hw,re.S).group(1)
 values={n:int(v,16) for n,v in re.findall(r'\.(\w+)\s*=\s*(0x[0-9a-fA-F]+)',regs)}
 assert values['rtc_soc_base_address']==0x800 and values['fw_indicator_address']==0x3a028
 assert values['soc_reset_control_ce_rst_mask']==1 and values['soc_reset_control_si0_rst_mask']==0
 macros={n:int(v,16) for n,v in re.findall(r'#define\s+(SOC_\w+)\s+(0x[0-9a-fA-F]+)',header)}
 assert macros['SOC_RESET_CONTROL_ADDRESS']==0 and macros['SOC_RESET_CONTROL_CPU_WARM_RST_MASK']==0x40
 assert macros['SOC_LF_TIMER_CONTROL0_ADDRESS']==0x50 and macros['SOC_LF_TIMER_CONTROL0_ENABLE_MASK']==4
 assert function('ath10k_pci_warm_reset_si0').count('msleep(10)')==2
 assert function('ath10k_pci_warm_reset_ce').count('msleep(10)')==1
 return {'upstream_order':expected,'soc_reset_address':'00000800','lf_timer_address':'00000850',
         'cpu_reset_mask':'00000040','ce_reset_mask':'00000001','si0_reset_mask':'00000000',
         'firmware_indicator_address':'0003a028','native_implementation_verified':False,
         'physical_sequence_executed':False}
def main():
 if not __debug__:raise SystemExit('optimized Python is forbidden: verification assertions must be enabled')
 p=argparse.ArgumentParser();p.add_argument('--pack',type=Path,required=True);p.add_argument('--vendor',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();pack=json.loads(a.pack.read_text());sources={}
 for n,h in pack['reference_sha256'].items():
  data=(a.vendor/n).read_bytes();assert hashlib.sha256(data).hexdigest()==h,n;sources[n]=data.decode()
 core=sources['core.c'];assert re.search(r'case ATH10K_HW_QCA6174:\s*case ATH10K_HW_QCA9377:.*?ar->hw_values = &qca6174_values;',core,re.S)
 values=re.search(r'const struct ath10k_hw_values qca6174_values = \{(.*?)\};',sources['hw.c'],re.S).group(1)
 count=int(re.search(r'\.ce_count\s*=\s*(\d+)',values).group(1));records=int(re.search(r'\.num_target_ce_config_wlan\s*=\s*(\d+)',values).group(1))
 assert count==pack['ce_count']==8 and records==pack['target_pipe_records']==7
 ce=sources['ce.h'];sizes={}
 for n in ('ce_pipe_config','ce_service_to_pipe'):
  body=re.search(r'struct '+n+r' \{(.*?)\};',ce,re.S).group(1);sizes[n]=4*len(re.findall(r'__le32\s+\w+;',body))
 assert sizes['ce_pipe_config']==pack['target_pipe_record_bytes']==24 and records*24==pack['target_pipe_bytes']==168
 assert sizes['ce_service_to_pipe']==pack['service_record_bytes']==12
 table=re.search(r'pci_target_service_to_ce_map_wlan\[\] = \{(.*?)\n\};',sources['pci.c'],re.S).group(1);services=table.count('__cpu_to_le32(')//3
 assert services==pack['service_map_records']==17 and services*12==pack['service_map_bytes']==204
 assert '#define NUM_TARGET_CE_CONFIG_WLAN ar->hw_values->num_target_ce_config_wlan' in sources['hw.h']
 assert re.search(r'case QCA9377_1_0_DEVICE_ID:\s*return 9;',sources['pci.c']) and pack['early_alloc_iram_banks']==9
 assert re.search(r'config->pipedir = __cpu_to_le32\(PIPEDIR_OUT\);.*?config->nbytes_max = __cpu_to_le32\(2048\);.*?serv_to_pipe\[15\].pipenum = __cpu_to_le32\(1\);',sources['pci.c'],re.S)
 native=(Path(__file__).parent/'init_tables_native.h').read_text()
 for name,data in zip(('qca_setup_pipes','qca_setup_services'),table_bytes()):
  body=re.search(name+r'\[\d+\]=\{(.*?)\};',native,re.S).group(1)
  assert bytes(int(v) for v in re.findall(r'\d+',body))==data,'native table bytes differ'
 tables=check_table_contents(sources);negative=resource_checks();warm=check_warm_sequence(sources)
 out={'status':'PINNED-QCA9377-INITIAL-CONFIG-PARAMETERS-PASS','pack_sha256':hashlib.sha256(a.pack.read_bytes()).hexdigest(),'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'table_builder_sha256':hashlib.sha256(Path(__file__).with_name('init_tables.py').read_bytes()).hexdigest(),'reference_sha256':pack['reference_sha256'],'ce_count':count,'target_pipe_records':records,'target_pipe_bytes':records*24,'service_map_records':services,'service_map_bytes':services*12,'tables':tables,'warm_reset_reference':warm,'resource_negative_cases':negative,'live_host_resources_verified':False,'native_write_gate_integrated':False,'physical_target_writes':False,'firmware_compatibility_verified':False};a.output.write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
