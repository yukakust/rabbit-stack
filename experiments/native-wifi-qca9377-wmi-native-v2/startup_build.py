"""Isolated WMI INIT candidate; no physical admission/signing route."""
import sys,struct,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LAYOUT=ROOT.parent/'native-wifi-qca9377-service-layout-v1'
sys.path.insert(0,str(LAYOUT));import operating_build as layout
BASE=layout.BASE;SESSION=layout.SESSION;AVAILABLE=layout.AVAILABLE;prior=layout.prior;one=layout.one
TXN=ROOT.parent/'native-wifi-qca9377-wmi-transaction-v1'
INIT=ROOT.parent/'native-wifi-qca9377-wmi-init-v1'
MEM=ROOT.parent/'native-wifi-qca9377-memory-v1'
RES=ROOT.parent/'native-wifi-qca9377-resources-v1'
EXTRA_FILES={ROOT:('startup.c','startup.h','startup_gatt.c'),TXN:('init_transaction.c','init_transaction.h'),INIT:('init_wire.c','init_wire.h'),MEM:('memory_plan.c','memory_plan.h'),RES:('resources.c','resources.h')}
def policy():
 old=prior.POLICY
 try:prior.POLICY=ROOT/'receiver-policy.json';return prior.policy()
 finally:prior.POLICY=old
def sources(directory):
 layout.sources(directory)
 for folder,names in EXTRA_FILES.items():
  for n in names:(directory/n).write_bytes((folder/n).read_bytes())
 p=directory/'init_transaction.h';p.write_text(p.read_text().replace('Current encoder ABI minor53 required.','Major/namespaces checked; minor preserved as firmware metadata.'))
 p=directory/'init_probe.c';s=p.read_text()
 s=one(s,'#include "operating.h"','#include "operating.h"\n#include "startup.h"')
 s=one(s,'static QcaOperating operating;','static QcaOperating operating;\nstatic QcaWmiStartup startup;')
 s=one(s,'.generation=47ull','.generation=49ull')
 s=one(s,'int qca_stop(void){','int qca_stop(void){\n qca_wmi_startup_cancel(&startup);')
 s=one(s,'else rc=qca_operating_poll(&operating,now);',"""else {
       rc=qca_operating_poll(&operating,now);
       if(rc==1){
        if(!startup.phase)rc=qca_wmi_startup_begin(&startup,&operating,now);
        else rc=qca_wmi_startup_poll(&startup,now);
       }
       else if(rc<0&&startup.phase==1)(void)qca_wmi_startup_poll(&startup,now);
      }""")
 s+='\nconst QcaWmiStartup*qca_wmi_startup_view(void){return &startup;}\n'
 s+="""
void qca_wmi_status(uint8_t out[96]){
 for(unsigned j=0;j<96;j++)out[j]=0;
 const uint8_t magic[8]={'Q','W','I','N','0','0','0','1'};for(unsigned j=0;j<8;j++)out[j]=magic[j];
 const QcaWmiStartup*s=&startup;const QcaWmiInitTransaction*t=&s->transaction;
 uint32_t fields[12]={s->phase,s->error,t->phase,s->tx_posted,s->tx_count,s->rx_count,t->ready_seen,t->tx_complete,t->ready.abi_minor,operating.control.credit.available,operating.control.credit.outstanding,operating.service.memory_count};
 for(unsigned j=0;j<12;j++)for(unsigned k=0;k<4;k++)out[8+4*j+k]=(uint8_t)(fields[j]>>(8*k));
 for(unsigned j=0;j<6;j++)out[56+j]=t->ready.mac[j];
 for(unsigned j=0;j<8;j++)for(unsigned k=0;k<4;k++)out[64+4*j+k]=(uint8_t)(s->diagnostic[j]>>(8*k));
}
"""
 p.write_text(s)
 p=directory/'diagnostic_gatt.c';s=p.read_text()
 s=one(s,'size_t qca_operating_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);','size_t qca_operating_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);\nsize_t qca_wmi_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);')
 s=one(s,'if(s){size_t op=qca_operating_att','if(s){size_t init=qca_wmi_att(s->mtu,p,n,r,capacity);if(init!=SIZE_MAX)return init;}\n if(s){size_t op=qca_operating_att')
 p.write_text(s)
def compile_driver(directory,crypto):
 # Same actual driver/city/USB code generation as prior; isolated directory.
 sources(directory);prior.bt_usb_build.sources(directory)
 (directory/'ble_recovery_link.c').write_text(prior.prior.ble.link_source())
 names=('init_probe.c','init_adapter.c','warm_core.c','channels_core.c','boot_irq_mapped.c','full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','reset_core.c','power_core.c','uefi_port.c','wake_core.c','rom_ready.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','boot_gatt.c','operating.c','operating_gatt.c','startup.c','startup_gatt.c','init_transaction.c','init_wire.c','memory_plan.c','resources.c','available.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c')
 a=prior.actors
 payload=a.compile_efi(directory,'operating-driver',[directory/'driver.c',directory/'city_core.c',directory/'pci_collect.c',directory/'pci_identity.c',*[directory/n for n in names],directory/'usb_port.c',directory/'bt_event_stream.c',directory/'ble_recovery_link.c',directory/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'))
 off=struct.unpack_from('<I',payload,60)[0]
 if len(payload)>262144 or struct.unpack_from('<I',payload,off+80)[0]>4*1024*1024:raise ValueError('installed wire/mapped bounds')
 return payload
