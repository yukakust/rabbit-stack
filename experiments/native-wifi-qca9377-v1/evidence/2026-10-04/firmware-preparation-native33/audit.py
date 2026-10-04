import hashlib,json,re
from pathlib import Path
repo=Path('/home/yuka/rabbit-world/wifi-reset-v1/source');r=repo/'experiments/native-wifi-qca9377-v1';vendor=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/linux/drivers/net/wireless/ath/ath10k')
i=json.loads(Path('/tmp/rabbit-native33-public-identity.json').read_text());assert i['native_counter']==33 and i['receiver_reported_applied'] and i['config_write_mask']==i['config_readback_mask']==31 and i['all_host_resources_restored']
pack=json.loads((r/'init-target.json').read_text());source={}
for n in ('core.c','hw.h'):
 data=(vendor/n).read_bytes();assert hashlib.sha256(data).hexdigest()==pack['reference_sha256'][n];source[n]=data.decode()
versions=dict((n,int(v,16)) for n,v in re.findall(r'#define\s+(QCA9377_HW_\d_\d_DEV_VERSION)\s+(0x[0-9a-fA-F]+)',source['hw.h']))
matches=[n for n,v in versions.items() if v==int(i['physical_bmi_version'],16)];assert len(matches)==1
symbol=matches[0];start=source['core.c'].index('.id = '+symbol);end=source['core.c'].index('\n\t},',start);record=source['core.c'][start:end]
name=re.search(r'\.name = "([^"]+)"',record).group(1);directory_symbol=re.search(r'\.dir = (\w+)',record).group(1)
assert directory_symbol=='QCA9377_HW_1_0_FW_DIR' and '.dev_id = QCA9377_1_0_DEVICE_ID' in record and '.bus = ATH10K_BUS_PCI' in record
assert re.search(r'#define\s+QCA9377_HW_1_0_FW_DIR\s+ATH10K_FW_DIR "/QCA9377/hw1.0"',source['hw.h'])
out={'status':'FRESH-PHYSICAL-BMI-HARDWARE-AND-FIRMWARE-DIRECTORY-MATCH-PASS','native_counter':33,'physical_identity_sha256':hashlib.sha256(Path('/tmp/rabbit-native33-public-identity.json').read_bytes()).hexdigest(),'physical_bmi_version':i['physical_bmi_version'],'physical_bmi_type':i['physical_bmi_type'],'hardware_name':name,'version_symbol':symbol,'firmware_directory':'ath10k/QCA9377/hw1.0','board_calibration_bytes':int(re.search(r'\.cal_data_len = (\d+)',record).group(1)),'linux_commit':pack['linux_commit'],'reference_sha256':{n:pack['reference_sha256'][n] for n in source},'firmware_uploaded':False,'fresh_board_variant_pending':True,'signed_asset_receiver_live_policy_integration_pending':True,'firmware_startup_verified':False,'wifi_association_verified':False,'upload_authorized':False}
Path('/tmp/rabbit-native33-hardware-match.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],name,out['firmware_directory'])
