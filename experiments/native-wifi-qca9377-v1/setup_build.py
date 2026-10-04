import struct
import config_read_build as prior
ROOT,CITY,actors,one=prior.ROOT,prior.CITY,prior.actors,prior.one
EXTRA=('config_setup.c','config_setup.h','init_tables_native.h')
def sources(directory):
 prior.sources(directory)
 for n in EXTRA:(directory/n).write_bytes((ROOT/n).read_bytes())
 p=directory/'pci_collect.c';p.write_text(one(p.read_text(),'qca_diagnostic[3]=17;','qca_diagnostic[3]=18;'))
 p=directory/'diagnostic_gatt.c';p.write_text(p.read_text().replace('p[7]==12?8:0','p[7]==13?8:0').replace('start==1?1:12','start==1?1:13').replace('handle==1?1:12','handle==1?1:13'))
 p=directory/'init_probe.c';s=p.read_text().replace('#include "config_read.h"','#include "config_setup.h"').replace('static QcaConfigRead config_read;','static QcaConfigSetup setup;\n#define config_read setup.read').replace('qca_config_read_poll(&config_read,now)','qca_config_setup_poll(&setup,now)')
 s=one(s,' record(716,config_read.phase,4);',' record(280,setup.phase,4);record(284,setup.error,4);record(288,setup.op,4);\n record(292,setup.write_mask,4);record(296,setup.readback_mask,4);record(300,setup.write_attempts,4);\n record(304,setup.cpu_attempted,4);record(308,setup.cpu_before,4);record(312,setup.cpu_readback,4);\n record(316,setup.bmi.phase,4);record(320,setup.bmi.error,4);record(324,setup.bmi.version,4);\n record(328,setup.bmi.type,4);record(332,setup.bmi.info_length,4);record(336,setup.bmi.bytes,4);\n record(340,setup.bmi.tx_done,4);record(344,setup.bmi.rx_done,4);record(348,setup.bmi_polls,4);\n record(352,setup.bmi.last>=setup.bmi.started?setup.bmi.last-setup.bmi.started:0,4);\n record(716,config_read.phase,4);');p.write_text(s)
def compile_driver(directory,crypto):
 sources(directory)
 (directory/'ble_recovery_link.c').write_text(prior.prior.base.base.ble.link_source())
 names=('init_probe.c','init_adapter.c','warm_core.c','channels_core.c','boot_irq_mapped.c','full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c',
        'reset_core.c','power_core.c','uefi_port.c','wake_core.c','rom_ready.c','ce_ring.c',
        'ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c')
 payload=actors.compile_efi(directory,'full-read-driver',[directory/'driver.c',directory/'city_core.c',directory/'pci_collect.c',
  directory/'pci_identity.c',*[directory/n for n in names],actors.LINK/'usb_port.c',directory/'ble_recovery_link.c',
  directory/'diagnostic_gatt.c',actors.LINK/'file_core.c',actors.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1'))
 offset=struct.unpack_from('<I',payload,60)[0]
 if struct.unpack_from('<I',payload,offset+80)[0]>4*1024*1024:raise ValueError('mapped full read profile exceeds root bound')
 return payload
