import sys,json,hashlib
from pathlib import Path
root=Path('/home/yuka/rabbit-world/wifi-reset-v1/source/experiments/native-wifi-qca9377-v1');sys.path.insert(0,str(root))
import firmware_preflight as pre
vendor=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware')
materials=json.loads((vendor.parent.parent/'materials.json').read_text())
for name in ('ath10k/QCA9377/hw1.0/firmware-6.bin','ath10k/QCA9377/hw1.0/board-2.bin','ath10k/QCA9377/hw1.0/notice_ath10k_firmware-6.txt','LICENSE.QualcommAtheros_ath10k','WHENCE'):
 data=(vendor/name).read_bytes();expected=materials['files']['firmware/'+name];assert len(data)==expected['bytes'] and pre.digest(data)==expected['sha256']
fw=pre.firmware((vendor/'ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes());records=pre.boards((vendor/'ath10k/QCA9377/hw1.0/board-2.bin').read_bytes())
identity='bus=pci,vendor=168c,device=0042,subsystem-vendor=1028,subsystem-device=1810'
match=pre.select_board(records,identity)
out={'status':'PINNED-FIRMWARE-CONTAINER-AND-PCI-BOARD-CANDIDATE-PREPARED','firmware_source':materials['sources']['firmware'],'firmware':fw,'pci_board_candidate':match,'source_materials_sha256':pre.digest((vendor.parent.parent/'materials.json').read_bytes()),'license_files_hash_checked':True,'physical_bmi_target_version_pending':True,'fresh_board_variant_pending':True,'initial_configuration_write_and_readback_pending':True,'upload_authorized':False,'upload_performed':False,'next_order':['fresh post-warm configuration reads and bounded span validation','gated exact config writes/readback; config-done LAST and CPU wake','fresh BMI target version/type and exact board-variant validation','native firmware asset receiver integration and signed chunk receipts','RAM upload and startup; WMI/HTT; scan/security; DHCP']}
Path('/tmp/rabbit-native32-firmware-preparation.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status']);print(fw['version'],match['bytes'])
