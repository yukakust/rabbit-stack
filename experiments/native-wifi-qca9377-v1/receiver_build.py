"""Native33 setup plus signed RAM-only firmware staging; no image execution."""
import json,struct
import setup_build as prior
import ble_recovery_build as ble
ROOT,CITY,actors,one=prior.ROOT,prior.CITY,prior.actors,prior.one
EXTRA=('firmware_port.c','firmware_port.h','firmware_channel.c','firmware_channel.h','firmware_gatt.c','firmware_chunks.c','firmware_chunks.h')
POLICY=ROOT/'receiver-policy.json'
def policy():
 p=json.loads(POLICY.read_text())
 if set(p)!={'owner','target','digest','total','type','version','kind','generation'}:raise ValueError('exact receiver policy required')
 for k in ('owner','target','digest'):
  raw=bytes.fromhex(p[k])
  if len(raw)!=32 or not any(raw) or raw.hex()!=p[k]:raise ValueError('canonical nonzero policy hash required')
 if p['total']!=751436 or p['digest']!='8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01' or p['type']!=8 or p['version']!=0x05020001 or p['kind']!=1 or not 0<p['generation']<2**64:raise ValueError('reviewed QCA9377 RAM container policy required')
 return p
def sources(directory):
 prior.sources(directory)
 for n in EXTRA:(directory/n).write_bytes((ROOT/n).read_bytes())
 p=policy();array=lambda h:'{'+','.join(str(n) for n in bytes.fromhex(h))+'}'
 constant='static const QcaFirmwarePolicy ram_policy={'+','.join('.'+k+'='+array(p[k]) for k in ('owner','target','digest'))+','+','.join('.'+k+'='+str(p[k])+'ull' for k in ('total','type','version','kind','generation'))+'};\n'
 q=directory/'init_probe.c';s=q.read_text().replace('#include "config_setup.h"','#include "config_setup.h"\n#include "firmware_port.h"')
 s=one(s,'static QcaConfigSetup setup;','static QcaConfigSetup setup;\nstatic QcaFirmwarePort ram;static SystemTable*ram_system;static unsigned ram_attempted,ram_closing;\n'+constant)
 s=one(s,'int qca_stop(void){','static int qca_hardware_stop(void){')
 s=one(s,'void qca_start(SystemTable*st,uint64_t ms){','void qca_start(SystemTable*st,uint64_t ms){\n ram_system=st;')
 s=one(s,'void qca_poll(uint64_t ms){','static void qca_hardware_poll(uint64_t ms){')
 s+='''
/* The hardware owner closes FIRST. RAM assets never borrow DMA mappings. */
void qca_poll(uint64_t ms){
 qca_hardware_poll(ms);
 if(ram_closing){(void)qca_fwp_close(&ram);return;}
 if(stage!=5||failed||cancelled)return;
 if(!ram_attempted){ram_attempted=1;if(qca_fwp_start_setup(&ram,ram_system,&ram_policy,&setup)){ram.phase=6;ram.error=0x100;return;}}
 if(ram.phase>0&&ram.phase<4)(void)qca_fwp_step(&ram);
}
int qca_stop(void){
 ram_closing=1;int hardware=qca_hardware_stop();int result=qca_fwp_close(&ram);
 /* Resident close is a single-call ABI. Two bounded pool releases complete
  * unpinned RAM teardown; faults/pins retain ownership and still refuse close. */
 if(result==1)result=qca_fwp_close(&ram);
 return hardware||qca_fwp_owned(&ram)||result<0;
}
const QcaFirmwarePort*qca_ram_view(void){return &ram;}
size_t qca_ram_att(uint16_t mtu,const uint8_t*p,size_t n,uint8_t*r,size_t capacity){
 return qca_fwp_att(&ram,mtu,p,n,r,capacity);
}
''';q.write_text(s)
 q=directory/'diagnostic_gatt.c';s=q.read_text();s=one(s,'#include "pci_collect.h"','#include "pci_collect.h"\nsize_t qca_ram_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);');m=__import__('re').search(r'size_t rg_att\([^{}]*\)\{',s)
 if not m:raise ValueError('ATT dispatcher signature changed')
 s=s[:m.end()]+'\n if(s){size_t asset=qca_ram_att(s->mtu,p,n,r,capacity);if(asset!=SIZE_MAX)return asset;}'+s[m.end():];q.write_text(s)
def compile_driver(directory,crypto):
 sources(directory)
 (directory/'ble_recovery_link.c').write_text(ble.link_source())
 names=('init_probe.c','init_adapter.c','warm_core.c','channels_core.c','boot_irq_mapped.c','full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','reset_core.c','power_core.c','uefi_port.c','wake_core.c','rom_ready.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c')
 payload=actors.compile_efi(directory,'ram-receiver-driver',[directory/'driver.c',directory/'city_core.c',directory/'pci_collect.c',directory/'pci_identity.c',*[directory/n for n in names],actors.LINK/'usb_port.c',directory/'ble_recovery_link.c',directory/'diagnostic_gatt.c',actors.LINK/'file_core.c',actors.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'))
 offset=struct.unpack_from('<I',payload,60)[0]
 if struct.unpack_from('<I',payload,offset+80)[0]>4*1024*1024:raise ValueError('mapped receiver exceeds root bound')
 return payload
