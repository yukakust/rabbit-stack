"""Bounded real CE0/1/2 control candidate, not physically admitted yet."""
import sys,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'native-wifi-qca9377-v1';SESSION=ROOT.parent/'native-wifi-qca9377-session-v1'
sys.path.insert(0,str(BASE));sys.path.insert(0,str(SESSION))
import boot_build as prior
one=prior.one
EXTRA=('operating.c','operating.h','operating_gatt.c')
PROTOCOL=('htc_wire.c','htc_wire.h','htc_session.c','htc_session.h','htc_credit.c','htc_credit.h','htc_control.c','htc_control.h','wmi_boot_info.c','wmi_boot_info.h','wmi_scan.c','wmi_scan.h')
def policy():
 old=prior.POLICY
 try:prior.POLICY=ROOT/'receiver-policy.json';return prior.policy()
 finally:prior.POLICY=old
def sources(directory):
 old=prior.POLICY
 try:prior.POLICY=ROOT/'receiver-policy.json';prior.sources(directory)
 finally:prior.POLICY=old
 for n in EXTRA:(directory/n).write_bytes((ROOT/n).read_bytes())
 for n in PROTOCOL:(directory/n).write_bytes((SESSION/n).read_bytes())
 # Preserve semantics while making the already verified protocol code compile
 # under both strict GCC and Clang; actual native fixture uses these exact bytes.
 for name,old,new in (
  ('htc_session.c','if(bytes)s->prepared=bytes;return bytes;','if(bytes)s->prepared=bytes;\n return bytes;'),
  ('wmi_scan.c','for(unsigned i=0;i<count;i++)put32(p+base+4*i,freq[i]);base+=4*count;','for(unsigned i=0;i<count;i++)put32(p+base+4*i,freq[i]);\n base+=4*count;')):
  q=directory/name;q.write_text(one(q.read_text(),old,new))
 p=directory/'init_probe.c';s=p.read_text()
 s=one(s,'#include "boot_native.h"','#include "boot_native.h"\n#include "operating.h"')
 s=one(s,'static unsigned boot_round,board_once,boot_once;','static unsigned boot_round,board_once,boot_once;\nstatic QcaOperating operating;')
 s=one(s,'    else rc=qca_boot_native_poll(&boot,now);','''    else {
     rc=qca_boot_native_poll(&boot,now);
     if(rc==1){
      if(!operating.phase)rc=qca_operating_begin(&operating,&boot,now);
      else rc=qca_operating_poll(&operating,now);
     }
    }''')
 s+='\nconst QcaOperating*qca_operating_view(void){return &operating;}\n'
 s+="""
void qca_operating_status(uint8_t out[208]){
 for(unsigned i=0;i<208;i++)out[i]=0;
 const uint8_t magic[8]={'Q','W','O','P','0','0','0','2'};for(unsigned i=0;i<8;i++)out[i]=magic[i];
 const QcaOperating*s=&operating;const QcaHtcSession*h=&s->control.session;const QcaWmiServiceInfo*w=&s->service;
 uint32_t fields[22]={s->phase,s->error,h->phase,s->control.posted,s->control.deferred_bytes,s->tx_count,s->rx_count,s->service_bytes,s->service_valid,h->wmi.endpoint,h->htt.endpoint,w->build,w->abi_minor,w->chains,w->memory_count,w->regdomain,w->low2,w->high2,w->low5,w->high5,s->control.credit.available,s->control.credit.outstanding};
 for(unsigned j=0;j<22;j++)for(unsigned i=0;i<4;i++)out[8+j*4+i]=(uint8_t)(fields[j]>>(8*i));
 for(unsigned j=0;j<10;j++)for(unsigned i=0;i<4;i++)out[96+j*4+i]=(uint8_t)(s->rx_diagnostic[j]>>(8*i));
 for(unsigned i=0;i<8;i++)out[136+i]=s->rx_descriptor[i];
 for(unsigned i=0;i<64;i++)out[144+i]=s->rx_prefix[i];
}
"""
 p.write_text(s)
 p=directory/'diagnostic_gatt.c';s=p.read_text()
 s=one(s,'size_t qca_boot_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);','size_t qca_boot_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);\nsize_t qca_operating_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);')
 s=one(s,'if(s){size_t boot=qca_boot_att','if(s){size_t op=qca_operating_att(s->mtu,p,n,r,capacity);if(op!=SIZE_MAX)return op;}\n if(s){size_t boot=qca_boot_att')
 p.write_text(s)
def compile_driver(directory,crypto):
 # Same actual driver/city/USB code generation as prior; isolated directory.
 sources(directory);prior.bt_usb_build.sources(directory)
 (directory/'ble_recovery_link.c').write_text(prior.prior.ble.link_source())
 names=('init_probe.c','init_adapter.c','warm_core.c','channels_core.c','boot_irq_mapped.c','full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','reset_core.c','power_core.c','uefi_port.c','wake_core.c','rom_ready.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','boot_gatt.c','operating.c','operating_gatt.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c')
 a=prior.actors
 payload=a.compile_efi(directory,'operating-driver',[directory/'driver.c',directory/'city_core.c',directory/'pci_collect.c',directory/'pci_identity.c',*[directory/n for n in names],directory/'usb_port.c',directory/'bt_event_stream.c',directory/'ble_recovery_link.c',directory/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'))
 off=struct.unpack_from('<I',payload,60)[0]
 if len(payload)>262144 or struct.unpack_from('<I',payload,off+80)[0]>4*1024*1024:raise ValueError('installed wire/mapped bounds')
 return payload
