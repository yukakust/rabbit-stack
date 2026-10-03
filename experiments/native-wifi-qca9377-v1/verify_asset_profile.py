#!/usr/bin/env python3
"""Actual UEFI city + disabled-policy asset ATT integration, QCA absent."""
import hashlib,json,sys
from pathlib import Path
import asset_build as build
import verify_bmi_profile as bmi
sys.path.insert(0,str(build.base.CITY))
import actors_gate
ROOT=build.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(source):
    source=bmi.fixture(source)
    return build.one(source,'say("ONE-SHOT WIFI RESET PROBE TARGET ABSENT; CLEAN CLOSE AND CITY RETAINED");',r'''
 uint8_t asset_service[23]={6,1,0,255,255,0,0x28,7,0,0,0,0,0,0,0x80,0x49,0x46,0x54,0x49,0x42,0x42,0x41,0x52};
 if(att(asset_service,23,7)||diagnostic_reply_size!=5||diagnostic_reply[1]!=11||diagnostic_reply[3]!=17)return 1;
 uint8_t asset_read[3]={0x0a,17,0};
 if(att(asset_read,3,0x0b)||diagnostic_reply_size!=65||!same(diagnostic_reply+1,(const uint8_t*)"RFCS0001",8))return 1;
 for(unsigned i=9;i<65;i++)if(diagnostic_reply[i])return 1;
 uint8_t asset_blob[5]={0x0c,17,0,64,0};if(att(asset_blob,5,0x0d)||diagnostic_reply_size!=1)return 1;
 asset_blob[3]=65;if(att(asset_blob,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;
 uint8_t denied_begin[47]={0x12,13,0,'R','F','C','1',1};denied_begin[11]=225;
 if(att(denied_begin,47,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=0x80)return 1;
 if(att(asset_read,3,0x0b)||diagnostic_reply_size!=65)return 1;
 for(unsigned i=9;i<65;i++)if(diagnostic_reply[i])return 1;
 say("ACTUAL UEFI ASSET SERVICE DISCOVERY/READ/BLOB/WRITE-DENIAL PASS; NO POLICY/ALLOCATION/FIRMWARE");
 say("ONE-SHOT WIFI RESET PROBE TARGET ABSENT; CLEAN CLOSE AND CITY RETAINED");
 ''')
def main():
    baseline=ROOT/'runs/bmi-profile/report.json';old=json.loads(baseline.read_text())
    for name,expected in old['source_sha256'].items():
        if sha((ROOT.parent.parent/name).read_bytes())!=expected:raise ValueError('frozen native15 baseline changed')
    port=ROOT/'runs/firmware-port/report.json';gate=json.loads(port.read_text())
    for name,expected in gate['source_sha256'].items():
        if sha((ROOT.parent.parent/name).read_bytes())!=expected:raise ValueError('RAM port gate source changed')
    out=ROOT/'runs/asset-profile';out.mkdir(parents=True,exist_ok=False)
    public=bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7')
    _,_,crypto=build.actors.engine.prepare(out,public)
    payload=build.compile_driver(out,crypto);assert payload==build.compile_driver(out,crypto)
    (out/'payload.efi').write_bytes(payload)
    gates=[actors_gate.qemu_gate(out,payload,test_transform=fixture),actors_gate.qemu_gate(out,payload,True,test_transform=fixture)]
    names=('asset_build.py','verify_asset_profile.py','firmware_port.c','firmware_port.h','firmware_channel.c','firmware_channel.h','firmware_gatt.c','firmware_chunks.c','firmware_chunks.h')
    report={'status':'FIRMWARE-ASSET-DISABLED-NATIVE-UEFI-CITY-GATES-PASS','build_host':'yukabox','payload_sha256':sha(payload),'source_sha256':{str((ROOT/n).relative_to(ROOT.parent.parent)):sha((ROOT/n).read_bytes()) for n in names},'native15_baseline_gate_sha256':sha(baseline.read_bytes()),'ram_port_gate_sha256':sha(port.read_bytes()),'gates':gates,'asset_policy_enabled':False,'actual_uefi_att_execution':True,'actual_uefi_ram_allocation':False,'physical_bluetooth_transfer':False,'owner_signing':False,'firmware_upload':False,'wifi_association':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['payload_sha256'])
if __name__=='__main__':main()
