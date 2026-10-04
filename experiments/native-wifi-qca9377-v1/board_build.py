"""Fresh setup plus exact RAM helper/board query; no main-image startup."""
import hashlib,json,struct,re
from pathlib import Path
import setup_build as prior
import ble_recovery_build as ble
from firmware_preflight import container
ROOT,CITY,actors,one=prior.ROOT,prior.CITY,prior.actors,prior.one
POLICY=ROOT/'board-query-policy.json'
VENDOR=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin')
EXTRA=('bmi_loader.c','bmi_loader.h','board_query.c','board_query.h','board_smbios.c','board_smbios.h','board_gatt.c')
def policy():
 p=json.loads(POLICY.read_text())
 if p['helper_bytes']!=24193 or p['helper_sha256']!='fac7edbbddb4e1b1a3d846cd55f83c607c31b7a07b0ceee73dc7ec154e8e6988' or p['patch_load_address']!=0x1234 or p['execute_parameter']!=0x10 or p['physical_type']!=8 or p['physical_version']!=0x05020001 or p['permanent_otp_programming'] or p['main_firmware_execution']:raise ValueError('exact board-query-only policy required')
 return p
def sources(directory):
 prior.sources(directory)
 for n in EXTRA:(directory/n).write_bytes((ROOT/n).read_bytes())
 p=policy();data=VENDOR.read_bytes()
 if hashlib.sha256(data).hexdigest()!=p['container_sha256']:raise ValueError('container changed')
 helper=dict(container(data,b'QCA-ATH10K'))[4]
 if len(helper)!=p['helper_bytes'] or hashlib.sha256(helper).hexdigest()!=p['helper_sha256']:raise ValueError('helper changed')
 array=lambda x:'{'+','.join(str(b) for b in x)+'}'
 (directory/'board_helper.h').write_text('static const uint8_t board_helper[]='+array(helper)+';\nstatic const uint8_t board_helper_digest[32]='+array(bytes.fromhex(p['helper_sha256']))+';\n')
 q=directory/'init_probe.c';s=q.read_text();s=one(s,'#include "config_setup.h"','#include "config_setup.h"\n#include "board_query.h"\n#include "board_smbios.h"\n#include "board_helper.h"')
 s=one(s,'static QcaConfigSetup setup;','static QcaConfigSetup setup;\nstatic QcaBoardQuery board;static QcaBoardSmbios smbios;static unsigned board_once;')
 s=one(s,' if(stage){telemetry();return;}',' if(stage){telemetry();return;}\n (void)qca_board_smbios_collect(&smbios,st);')
 s=one(s,'rc=cancelled?-1:qca_config_setup_poll(&setup,now);', '''rc=cancelled?-1:qca_config_setup_poll(&setup,now);
   if(cancelled&&board.phase&&board.phase<5){board.phase=6;board.error=4;}
   if(rc==1){
    if(!board_once){board_once=1;if(smbios.state==4||qca_board_begin(&board,&setup,board_helper,sizeof(board_helper),board_helper_digest)){board.phase=6;board.error=3;rc=-1;}else rc=0;}
    else rc=qca_board_poll(&board,now);
   }''')
 s+='''
void qca_board_status(uint8_t out[160]){
 for(unsigned i=0;i<160;i++)out[i]=0;
 const uint8_t magic[8]={'Q','B','D','I','0','0','0','1'};for(unsigned i=0;i<8;i++)out[i]=magic[i];
 uint32_t fields[15]={board.phase,board.error,board.submitted,board.offset,board.polls,board.result,board.helper_bytes,board.board_id,board.chip_id,board.extended,
  board.phase==5&&!(board.result&255)&&board.board_id,smbios.state,smbios.error,smbios.structures,smbios.bytes};
 for(unsigned j=0;j<15;j++)for(unsigned i=0;i<4;i++)out[8+j*4+i]=(uint8_t)(fields[j]>>(8*i));
 for(unsigned i=0;i<32;i++)out[68+i]=(uint8_t)smbios.variant[i];
 uint32_t tail[7]={setup.bmi.version,setup.bmi.type,stage,failed,adapter.phase,adapter.channels.cleanup_slot,port.dma_users};
 for(unsigned j=0;j<7;j++)for(unsigned i=0;i<4;i++)out[100+j*4+i]=(uint8_t)(tail[j]>>(8*i));
 for(unsigned i=0;i<32;i++)out[128+i]=board_helper_digest[i];
}
''';q.write_text(s)
 q=directory/'diagnostic_gatt.c';s=q.read_text();s=one(s,'#include "pci_collect.h"','#include "pci_collect.h"\nsize_t qca_board_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);');m=re.search(r'size_t rg_att\([^{}]*\)\{',s)
 if not m:raise ValueError('ATT dispatcher changed')
 q.write_text(s[:m.end()]+'\n if(s){size_t b=qca_board_att(s->mtu,p,n,r,capacity);if(b!=SIZE_MAX)return b;}'+s[m.end():])
def compile_driver(directory,crypto):
 sources(directory);(directory/'ble_recovery_link.c').write_text(ble.link_source())
 names=('init_probe.c','init_adapter.c','warm_core.c','channels_core.c','boot_irq_mapped.c','full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','reset_core.c','power_core.c','uefi_port.c','wake_core.c','rom_ready.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c','bmi_loader.c','board_query.c','board_smbios.c','board_gatt.c')
 payload=actors.compile_efi(directory,'board-query-driver',[directory/'driver.c',directory/'city_core.c',directory/'pci_collect.c',directory/'pci_identity.c',*[directory/n for n in names],actors.LINK/'usb_port.c',directory/'ble_recovery_link.c',directory/'diagnostic_gatt.c',actors.LINK/'file_core.c',actors.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1'))
 offset=struct.unpack_from('<I',payload,60)[0]
 if struct.unpack_from('<I',payload,offset+80)[0]>4*1024*1024:raise ValueError('mapped driver exceeds root bound')
 return payload
