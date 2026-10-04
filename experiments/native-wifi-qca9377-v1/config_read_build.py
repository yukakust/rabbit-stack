import struct
"""Full warm initialization and four finite read-only CE7 operations."""
import full_read_build as prior
ROOT,CITY,actors,one=prior.ROOT,prior.CITY,prior.actors,prior.one
EXTRA=('config_read.c','config_read.h')
def sources(directory):
 prior.sources(directory)
 for n in EXTRA:(directory/n).write_bytes((ROOT/n).read_bytes())
 p=directory/'pci_collect.c';p.write_text(one(p.read_text(),'qca_diagnostic[3]=16;','qca_diagnostic[3]=17;'))
 p=directory/'diagnostic_gatt.c';p.write_text(p.read_text().replace('p[7]==11?8:0','p[7]==12?8:0').replace('start==1?1:11','start==1?1:12').replace('handle==1?1:11','handle==1?1:12'))
 p=directory/'init_probe.c';s=p.read_text().replace('#include "full_read.h"','#include "config_read.h"').replace('static QcaFullRead full_read;','static QcaConfigRead config_read;\n#define full_read config_read.full').replace('qca_full_read_poll(&full_read,now)','qca_config_read_poll(&config_read,now)')
 s=one(s,' record(888,full_read.exchange.phase,4);',''' record(716,config_read.phase,4);record(720,config_read.error,4);record(724,config_read.mask,4);
 if(config_read.phase)record(728,full_read.exchange.value,4);
 unsigned ci=config_read.slot<3?config_read.slot:2;QcaDiagExchange*cr=&config_read.reads[ci];
 record(732,cr->target,4);record(736,cr->bytes,4);
 for(unsigned j=0;j<11;j++)record(740+j*4,config_read.words[j],4);
 record(784,cr->first_elapsed,4);record(788,cr->last_elapsed,4);record(792,cr->polls,4);
 record(888,full_read.exchange.phase,4);''');p.write_text(s)
def compile_driver(directory,crypto):
 sources(directory)
 (directory/'ble_recovery_link.c').write_text(prior.base.base.ble.link_source())
 names=('init_probe.c','init_adapter.c','warm_core.c','channels_core.c','boot_irq_mapped.c','full_read.c','config_read.c','diag_ce.c',
        'reset_core.c','power_core.c','uefi_port.c','wake_core.c','rom_ready.c','ce_ring.c',
        'ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c')
 payload=actors.compile_efi(directory,'full-read-driver',[directory/'driver.c',directory/'city_core.c',directory/'pci_collect.c',
  directory/'pci_identity.c',*[directory/n for n in names],actors.LINK/'usb_port.c',directory/'ble_recovery_link.c',
  directory/'diagnostic_gatt.c',actors.LINK/'file_core.c',actors.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1',))
 offset=struct.unpack_from('<I',payload,60)[0]
 if struct.unpack_from('<I',payload,offset+80)[0]>4*1024*1024:raise ValueError('mapped full read profile exceeds root bound')
 return payload
