"""Candidate native receiver -> fresh setup/query -> exact main boot trial.

Not admitted to physical signing until actual entrypoint/lifetime/QEMU gates.
"""
import hashlib,json,struct
from pathlib import Path
import receiver_build as prior
import board_build
from firmware_preflight import container,elements
ROOT,CITY,actors,one=prior.ROOT,prior.CITY,prior.actors,prior.one
POLICY=ROOT/'boot-receiver-policy.json'
EXTRA=('bmi_loader.c','bmi_loader.h','board_query.c','board_query.h','board_smbios.c','board_smbios.h','boot_image.c','boot_image.h','boot_transport.c','boot_transport.h','boot_native.c','boot_native.h','boot_gatt.c')
def policy():
 old=prior.POLICY
 try:
  prior.POLICY=POLICY
  return prior.policy()
 finally:prior.POLICY=old
def sources(directory):
 old=prior.POLICY
 try:
  prior.POLICY=POLICY;prior.sources(directory)
 finally:prior.POLICY=old
 for name in EXTRA:(directory/name).write_bytes((ROOT/name).read_bytes())
 p=board_build.policy();v=board_build.VENDOR;blob=v.read_bytes()
 if hashlib.sha256(blob).hexdigest()!=p['container_sha256']:raise ValueError('exact helper container required')
 helper=dict(container(blob,b'QCA-ATH10K'))[4]
 catalog=(v.parent/'board-2.bin').read_bytes()
 if hashlib.sha256(catalog).hexdigest()!='0fdcc7838f478da81704de88f7b33e28862110c6d5decf7818543f8e37e6cd98':raise ValueError('exact board catalog required')
 identity=b'bus=pci,vendor=168c,device=0042,subsystem-vendor=1028,subsystem-device=1810';matches=[]
 for tag,body in container(catalog,b'QCA-ATH10K-BOARD'):
  items=elements(body)
  if tag==0 and (0,identity) in items:matches.extend(data for kind,data in items if kind==1)
 if len(matches)!=1 or len(matches[0])!=8124 or hashlib.sha256(matches[0]).hexdigest()!='b2713b77c725b0ff81af75c85c3aeba97885d0f40174f715b1e39d5a9d50f4e7':raise ValueError('unique exact Dell board required')
 array=lambda b:'{'+','.join(str(x) for x in b)+'}'
 (directory/'boot_assets.h').write_text('static const uint8_t boot_helper[]='+array(helper)+';\nstatic const uint8_t boot_helper_digest[32]='+array(bytes.fromhex(p['helper_sha256']))+';\nstatic const uint8_t boot_board[]='+array(matches[0])+';\n')
 q=directory/'init_probe.c';s=q.read_text()
 s=one(s,'#include "firmware_port.h"','#include "firmware_port.h"\n#include "boot_native.h"\n#include "boot_assets.h"')
 s=one(s,'static QcaConfigSetup setup;','static QcaConfigSetup setup;\nstatic QcaBoardQuery board;static QcaBoardSmbios smbios;static QcaBootNative boot;\nstatic unsigned boot_round,board_once,boot_once;')
 s=one(s,' ram_system=st;',' ram_system=st;\n if(!stage)(void)qca_board_smbios_collect(&smbios,st);')
 s=one(s,'rc=cancelled?-1:qca_config_setup_poll(&setup,now);','''rc=cancelled?-1:qca_config_setup_poll(&setup,now);
   if(rc==1&&boot_round){
    if(!board_once){board_once=1;if(smbios.state!=2||qca_board_begin(&board,&setup,boot_helper,sizeof(boot_helper),boot_helper_digest))rc=-1;else rc=0;}
    else if(board.phase!=5){rc=qca_board_poll(&board,now);if(rc>0)rc=0;}
    else if(!boot_once){boot_once=1;if(qca_boot_native_begin(&boot,&board,&smbios,&ram.asset,boot_board,sizeof(boot_board),now))rc=-1;else rc=0;}
    else rc=qca_boot_native_poll(&boot,now);
   }''')
 s=one(s,'if(ram_closing){(void)qca_fwp_close(&ram);return;}','if(ram_closing){if(boot_round&&qca_boot_native_close(&boot))return;(void)qca_fwp_close(&ram);return;}')
 s=one(s,' if(stage!=5||failed||cancelled)return;',''' if(boot_round){
  if(qca_init_adapter_released(&adapter)&&!port.claimed)(void)qca_boot_native_close(&boot);
  return;
 }
 if(stage!=5||failed||cancelled)return;''')
 s=one(s,' if(ram.phase>0&&ram.phase<4)(void)qca_fwp_step(&ram);',''' if(ram.phase>0&&ram.phase<4)(void)qca_fwp_step(&ram);
 if(ram.phase==4&&ram.asset.ready&&!ram.asset.poisoned&&!ram.asset.pinned){
  /* First hardware lifetime must be completely released before reuse. */
  if(!qca_init_adapter_released(&adapter)||port.claimed||port.dma_users||adapter.access.count||reset.owned||irq.owned||link.owned||wake.owned){failed=0x8001;return;}
  boot_round=1;
  clear(&port,sizeof(port));clear(&wake,sizeof(wake));clear(&reset,sizeof(reset));clear(&link,sizeof(link));clear(&irq,sizeof(irq));clear(&rom,sizeof(rom));clear(&adapter,sizeof(adapter));clear(&setup,sizeof(setup));clear(&smbios,sizeof(smbios));
  stage=failed=chip=succeeded=cancelled=recoveries=close_attempts=0;actual_command=pmcsr=post_reset_link=0;bar=last_now=0;
  qca_start(ram_system,ms);
 }''')
 s=one(s,'/* The hardware owner closes FIRST.', 'static void clear(void*p,size_t n){volatile uint8_t*b=p;while(n--)*b++=0;}\n/* The hardware owner closes FIRST.')
 # During a trial only normal polling can finish hardware cleanup. Resident
 # close must succeed in one call once telemetry says all owners released.
 s=one(s,'ram_closing=1;int hardware=qca_hardware_stop();int result=qca_fwp_close(&ram);','ram_closing=1;int hardware=qca_hardware_stop();\n if(boot_round&&qca_boot_native_close(&boot))return 1;\n int result=qca_fwp_close(&ram);')
 s=one(s,' return qca_fwp_att(&ram,mtu,p,n,r,capacity);',''' if(boot_round&&p&&n>=3&&(p[0]==0x12||p[0]==0x52)){
  unsigned handle=(unsigned)p[1]|((unsigned)p[2]<<8);
  /* Asset writes remain sealed. Legacy replacement is delegated only after
     every hardware owner and the firmware pin have actually been released. */
  if((handle>=13&&handle<=19)||!qca_init_adapter_released(&adapter)||port.claimed||port.dma_users||ram.asset.pinned){
   if(!r||capacity<5)return 0;
   r[0]=1;r[1]=p[0];r[2]=p[1];r[3]=p[2];r[4]=3;return p[0]==0x52?0:5;
  }
 }
 return qca_fwp_att(&ram,mtu,p,n,r,capacity);''')
 s+='''
const QcaBootNative*qca_boot_view(void){return &boot;}
unsigned qca_boot_round(void){return boot_round;}
void qca_boot_status(uint8_t out[160]){
 for(unsigned i=0;i<160;i++)out[i]=0;
 const uint8_t magic[8]={'Q','W','B','T','0','0','0','1'};for(unsigned i=0;i<8;i++)out[i]=magic[i];
 uint32_t fields[30]={boot.phase,boot.error,boot.plan.phase,boot.plan.error,boot.plan.submitted,boot.plan.completed,boot.plan.board_address,boot.plan.calibration_result,boot.plan.offset,boot.ready_bytes,boot.credit_count,boot.credit_size,boot.max_endpoints,boot_round,ram.phase,ram.error,ram.asset.ready,ram.asset.pinned,stage,failed,adapter.phase,adapter.channels.cleanup_slot,port.dma_users,setup.bmi.version,setup.bmi.type,board.phase,board.error,board.result,ram.asset.received,boot_once};
 for(unsigned j=0;j<30;j++)for(unsigned i=0;i<4;i++)out[8+j*4+i]=(uint8_t)(fields[j]>>(8*i));
 for(unsigned i=0;i<32;i++)out[128+i]=ram_policy.digest[i];
}
'''
 q.write_text(s)
 q=directory/'diagnostic_gatt.c';s=q.read_text();s=one(s,'#include "pci_collect.h"','#include "pci_collect.h"\nsize_t qca_boot_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);');s=one(s,'if(s){size_t asset=qca_ram_att','if(s){size_t boot=qca_boot_att(s->mtu,p,n,r,capacity);if(boot!=SIZE_MAX)return boot;}\n if(s){size_t asset=qca_ram_att');q.write_text(s)
def compile_driver(directory,crypto):
 sources(directory);(directory/'ble_recovery_link.c').write_text(prior.ble.link_source())
 names=('init_probe.c','init_adapter.c','warm_core.c','channels_core.c','boot_irq_mapped.c','full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','reset_core.c','power_core.c','uefi_port.c','wake_core.c','rom_ready.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','boot_gatt.c')
 payload=actors.compile_efi(directory,'boot-receiver-driver',[directory/'driver.c',directory/'city_core.c',directory/'pci_collect.c',directory/'pci_identity.c',*[directory/n for n in names],actors.LINK/'usb_port.c',directory/'ble_recovery_link.c',directory/'diagnostic_gatt.c',actors.LINK/'file_core.c',actors.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'))
 off=struct.unpack_from('<I',payload,60)[0]
 if struct.unpack_from('<I',payload,off+80)[0]>4*1024*1024:raise ValueError('mapped boot receiver exceeds installed root bound')
 return payload
