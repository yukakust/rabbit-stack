"""Full mapped warm initialization then fixed read-only CE7 exchange."""
import struct
import init_build as base
ROOT,CITY,actors,one=base.ROOT,base.CITY,base.actors,base.one
EXTRA=('full_read.c','full_read.h')
def sources(directory):
 base.sources(directory)
 p=directory/'pci_collect.h';p.write_text(one(p.read_text(),'888u','924u'))
 p=directory/'pci_collect.c';p.write_text(one(p.read_text(),'qca_diagnostic[3]=15;','qca_diagnostic[3]=16;'))
 p=directory/'diagnostic_gatt.c';s=p.read_text().replace('p[7]==10?8:0','p[7]==11?8:0').replace('start==1?1:10','start==1?1:11').replace('handle==1?1:10','handle==1?1:11')
 s=one(s,'i<172;i++)value[36+i]=qca_diagnostic[716+i];length=208;','i<208;i++)value[36+i]=qca_diagnostic[716+i];length=244;');p.write_text(s)
 for n in EXTRA:(directory/n).write_bytes((ROOT/n).read_bytes())
 p=directory/'init_probe.c';s=p.read_text().replace('#include "init_adapter.h"','#include "init_adapter.h"\n#include "full_read.h"').replace('static QcaInitAdapter adapter;','static QcaInitAdapter adapter;\nstatic QcaFullRead full_read;')
 s=one(s,' record(880,adapter.warm.second_rom_polls,4);record(884,adapter.warm.last_reset_read,4);',' record(880,adapter.warm.second_rom_polls,4);record(884,adapter.warm.last_reset_read,4);\n record(888,full_read.exchange.phase,4);record(892,full_read.error,4);record(896,full_read.exchange.value,4);\n record(900,full_read.exchange.bytes,4);record(904,full_read.exchange.tx_done,4);record(908,full_read.exchange.rx_done,4);\n record(912,full_read.exchange.mask,4);record(916,full_read.exchange.polls,4);record(920,full_read.exchange.last_elapsed,4);')
 old='''  if(cancelled)qca_init_adapter_cancel(&adapter);
  int rc=qca_init_adapter_poll(&adapter,now);
  if(rc==1&&stage==18){succeeded=1;if(qca_init_adapter_close(&adapter)){succeeded=0;failed=0x601;}stage=19;}'''
 new='''  if(cancelled)qca_init_adapter_cancel(&adapter);
  int rc=0;
  if(stage==18&&full_read.started){
   rc=cancelled?-1:qca_full_read_poll(&full_read,now);
   if(rc){
    succeeded=rc>0;
    if(!succeeded&&!failed)failed=0x2000|(full_read.error?full_read.error:0x100);
    if(qca_init_adapter_close(&adapter)){succeeded=0;if(!failed)failed=0x601;}
    stage=19;
   }
  }else{
   rc=qca_init_adapter_poll(&adapter,now);
   if(rc==1&&stage==18){
    if(qca_full_read_begin(&full_read,&adapter,chip,bar,now)){
     failed=0x2000|(full_read.error?full_read.error:0x101);succeeded=0;
     (void)qca_init_adapter_close(&adapter);stage=19;
    }
   }
  }'''
 s=one(s,old,new);p.write_text(s)
def compile_driver(directory,crypto):
 sources(directory)
 (directory/'ble_recovery_link.c').write_text(base.base.ble.link_source())
 names=('init_probe.c','init_adapter.c','warm_core.c','channels_core.c','boot_irq_mapped.c','full_read.c','diag_ce.c',
        'reset_core.c','power_core.c','uefi_port.c','wake_core.c','rom_ready.c','ce_ring.c',
        'ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c')
 payload=actors.compile_efi(directory,'full-read-driver',[directory/'driver.c',directory/'city_core.c',directory/'pci_collect.c',
  directory/'pci_identity.c',*[directory/n for n in names],actors.LINK/'usb_port.c',directory/'ble_recovery_link.c',
  directory/'diagnostic_gatt.c',actors.LINK/'file_core.c',actors.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1',))
 offset=struct.unpack_from('<I',payload,60)[0]
 if struct.unpack_from('<I',payload,offset+80)[0]>4*1024*1024:raise ValueError('mapped full read profile exceeds root bound')
 return payload
