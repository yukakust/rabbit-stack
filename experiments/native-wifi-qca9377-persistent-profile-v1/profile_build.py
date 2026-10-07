"""Provisional53 bounded whole EFI, no signing or physical admission."""
import sys,struct,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RX=ROOT.parent/'native-wifi-qca9377-persistent-rx-v1'
sys.path.insert(0,str(RX));import rx_build as rx
checked=rx.checked;one=checked.one
def policy():return json.loads((ROOT/'receiver-policy.json').read_text())
def sources(directory):
 rx.sources(directory)
 for n in ('trial.h','trial.c','profile_gatt.c'):(directory/n).write_bytes((ROOT/n).read_bytes())
 p=directory/'init_probe.c';s=p.read_text()
 s=one(s,'.generation=52ull','.generation=53ull')
 s=one(s,'#include "persistent.h"','#include "persistent.h"\n#include "trial.h"')
 s=one(s,'static QcaPersistentNative persistent;','static QcaPersistentNative persistent;\nstatic QcaBoundedTrial trial;')
 s=one(s,' qca_hardware_poll(ms);',' qca_hardware_poll(ms);\n qca_profile_step(ms*1000);')
 s=one(s,'void qca_poll(uint64_t ms){','static void qca_profile_step(uint64_t);\nvoid qca_poll(uint64_t ms){')
 s+='''
static unsigned actual_released(void){
 return persistent.life.phase&&qca_init_adapter_released(&adapter)&&!port.claimed&&!port.dma_users
  &&!adapter.access.count&&!boot.owns_pin&&!ram.asset.pinned&&!irq.owned&&!link.owned&&!wake.owned;
}
static void qca_profile_step(uint64_t now){
 if(qca_trial_tick(&trial,qca_radio_accepts_work(&persistent.life),actual_released(),now))(void)qca_stop();
}
void qca_profile_status(uint8_t out[192]){
 for(unsigned j=0;j<192;j++)out[j]=0;
 const uint8_t magic[8]={'Q','W','R','X','0','0','0','1'};for(unsigned j=0;j<8;j++)out[j]=magic[j];
 const QcaPersistentNative*p=&persistent;const QcaPersistentRx*r=&p->rx;
 uint32_t held=0;for(unsigned j=0;j<14;j++)if(adapter.channels.buffers[j].allocated||adapter.channels.buffers[j].mapped||adapter.channels.buffers[j].allocation_uncertain)held++;
 uint32_t values[46]={trial.phase,trial.error,trial.expired,trial.stop_requested,actual_released(),
  p->life.phase,p->life.error,p->error,p->polls,r->phase,r->error,r->completed,r->posted_count,
  r->count,r->backpressure,r->posted[0],r->posted[1],held,port.dma_users,port.claimed,
  wake.owned,link.owned,irq.owned,boot.owns_pin,adapter.bus.owned,adapter.access.count,
  adapter.phase,adapter.channels.cleanup_slot,startup.phase,startup.error,startup.transaction.phase,
  startup.transaction.ready_seen,startup.transaction.tx_complete,operating.control.credit.available,
  operating.control.credit.outstanding,operating.control.credit.reserved,operating.control.credit.total,
  r->cookie[0],r->cookie[1],(uint32_t)trial.started,(uint32_t)(trial.started>>32),
  (uint32_t)trial.last,(uint32_t)(trial.last>>32),p->stop_latched,53,0};
 for(unsigned j=0;j<46;j++)for(unsigned k=0;k<4;k++)out[8+4*j+k]=(uint8_t)(values[j]>>(8*k));
}
'''
 p.write_text(s)
 p=directory/'diagnostic_gatt.c';s=p.read_text()
 s=one(s,'size_t qca_wmi_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);','size_t qca_wmi_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);\nsize_t qca_profile_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);')
 s=one(s,'if(s){size_t init=qca_wmi_att','if(s){size_t prof=qca_profile_att(s->mtu,p,n,r,capacity);if(prof!=SIZE_MAX)return prof;}\n if(s){size_t init=qca_wmi_att')
 p.write_text(s)
def compile_driver(directory,crypto):
 sources(directory);checked.prior.bt_usb_build.sources(directory)
 (directory/'ble_recovery_link.c').write_text(checked.prior.prior.ble.link_source())
 names=('init_probe.c','init_adapter.c','warm_core.c','channels_core.c','boot_irq_mapped.c','full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','reset_core.c','power_core.c','uefi_port.c','wake_core.c','rom_ready.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','boot_gatt.c','operating.c','operating_gatt.c','startup.c','startup_gatt.c','init_transaction.c','init_wire.c','memory_plan.c','resources.c','available.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c','persistent.c','lifecycle.c','rx.c','trial.c','profile_gatt.c')
 a=checked.prior.actors
 payload=a.compile_efi(directory,'persistent-profile',[directory/'driver.c',directory/'city_core.c',directory/'pci_collect.c',directory/'pci_identity.c',*[directory/n for n in names],directory/'usb_port.c',directory/'bt_event_stream.c',directory/'ble_recovery_link.c',directory/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'))
 off=struct.unpack_from('<I',payload,60)[0]
 if len(payload)>262144 or struct.unpack_from('<I',payload,off+80)[0]>4*1024*1024:raise ValueError('wire/mapped bound')
 return payload
