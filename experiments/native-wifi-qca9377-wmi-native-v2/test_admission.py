"""Current-world/component corruption rejection; no secret/radio calls."""
import copy,json,shutil,tempfile
from pathlib import Path
from unittest.mock import patch
import startup_route as r
ROOT=r.ROOT

def main():
 source=ROOT/'runs/checked-candidate';world=(ROOT/'runs/current-world.rup').read_bytes();checks=0
 with tempfile.TemporaryDirectory(prefix='rabbit-init-gates-') as t:
  d=Path(t)/'checked';shutil.copytree(source,d,symlinks=True);payload=(d/'payload.efi').read_bytes()
  with patch.object(r.engine,'load_private',side_effect=AssertionError('no secret')) as secret,patch.object(r.flow,'sender_step',side_effect=AssertionError('no radio')) as radio:
   r.gates(d,payload,world);checks+=1
   with patch.object(r.prior,"gates",r.gates):r.gates(d,payload,world);checks+=1
   for filename,key,value in [('report.json','payload_sha256','00'*32),('report.json','scan',True),('report.json','memory_requests_supported',1),('report.json','build_host','mac'),('report.json','receiver_policy_sha256','00'*32),('report.json','layout_report_sha256','00'*32),('report.json','available_report_sha256','00'*32),('report.json','response_report_sha256','00'*32),('report.json','operating_report_sha256','00'*32),('report.json','initial_report_sha256','00'*32),('reproduction.json','world_package_sha256','00'*32),('reproduction.json','status','unknown'),('operating-report.json','scenarios',21),('initial-report.json','scenarios',64)]:
    p=d/filename;before=p.read_bytes();data=json.loads(before);data[key]=value;p.write_text(json.dumps(data,indent=2)+'\n')
    try:r.gates(d,payload,world)
    except (ValueError,KeyError):pass
    else:raise AssertionError('mutation admitted '+key)
    p.write_bytes(before);checks+=1
   for data,wrong_world in [(payload[:-1]+bytes([payload[-1]^1]),world),(payload,(d/'legacy-world.rup').read_bytes())]:
    try:r.gates(d,data,wrong_world)
    except ValueError:pass
    else:raise AssertionError('wrong payload/world admitted')
    checks+=1
   for component in ['layout','available','response','operating','initial']:
    p=d/(component+'-host.log');before=p.read_bytes();p.write_bytes(before+b'corrupted')
    try:r.gates(d,payload,world)
    except ValueError:pass
    else:raise AssertionError('changed log admitted')
    p.write_bytes(before);checks+=1
   p=d/'reproduction.json';before=p.read_bytes();data=json.loads(before);data['inputs'].pop('experiments/native-wifi-qca9377-wmi-native-v2/startup.c');p.write_text(json.dumps(data,indent=2)+'\n')
   try:r.gates(d,payload,world)
   except ValueError:pass
   else:raise AssertionError('omitted startup source admitted')
   p.write_bytes(before);checks+=1
   secret.assert_not_called();radio.assert_not_called()
 print(f'INIT49 ADMISSION checks={checks} PASS; no secret loads/radio writes')
if __name__=='__main__':main()
