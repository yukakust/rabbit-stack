#!/usr/bin/env python3
"""Independent checks against pinned upstream chip parameters; no hardware I/O."""
import argparse,hashlib,json,re
from pathlib import Path
def main():
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
 out={'status':'PINNED-QCA9377-INITIAL-CONFIG-PARAMETERS-PASS','pack_sha256':hashlib.sha256(a.pack.read_bytes()).hexdigest(),'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'reference_sha256':pack['reference_sha256'],'ce_count':count,'target_pipe_records':records,'target_pipe_bytes':records*24,'service_map_records':services,'service_map_bytes':services*12,'physical_target_writes':False,'firmware_compatibility_verified':False};a.output.write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
