"""Separately gated city profile for reversible QCA wake/chip-ID telemetry."""
import struct
import diagnostic_build as base
import ble_recovery_build as ble
ROOT,CITY,actors,one=base.ROOT,base.CITY,base.actors,base.one
def sources(directory):
 base.sources(directory)
 header=(directory/'pci_collect.h').read_text().replace('128u','800u')
 (directory/'pci_collect.h').write_text(header)
 collector=(directory/'pci_collect.c').read_text()
 collector=one(collector,'uint8_t qca_diagnostic[QCA_DIAGNOSTIC_SIZE];','uint8_t qca_diagnostic[QCA_DIAGNOSTIC_SIZE];\nvoid*qca_controller;')
 collector=one(collector,' qca_diagnostic[0]=', ' qca_controller=0;\n qca_diagnostic[0]=')
 collector=one(collector,"qca_diagnostic[3]=1;","qca_diagnostic[3]=13;")
 collector=one(collector,'   flags|=2;','   flags|=2;qca_controller=handles[i];')
 collector=one(collector,' put(4,flags,4);',' if(flags!=15||targets!=1)qca_controller=0;\n put(4,flags,4);')
 (directory/'pci_collect.c').write_text(collector)
 # Separate bounded extension: physical CoreBluetooth stopped the800byte QPD12
 # at738bytes. Keep the main read716bytes and extension120bytes/hash-bound.
 gatt=(directory/'diagnostic_gatt.c').read_text()
 gatt=one(gatt,'#include "pci_collect.h"','#include "pci_collect.h"\n#include "sha256.h"')
 for old,new in [('p[7]==5?8:0','p[7]==8?8:0'),('start==1?7:10','start==1?7:12'),('start==1?1:5','start==1?1:8'),
  ('handle<=9?9:0','handle<=9?9:handle<=11?11:0'),('declaration==9?6:declaration/2+1','declaration==9?6:declaration==11?7:declaration/2+1'),
  ('handle>10','handle>12'),('||handle==9)','||handle==9||handle==11)'),('handle==10?6:(handle-1)/2+1','handle==10?6:handle==12?7:(handle-1)/2+1'),
  ('handle==1?1:5','handle==1?1:8'),('handle<=10?','handle<=12?')]:
  assert old in gatt,old
  gatt=gatt.replace(old,new)
 gatt=one(gatt,'if(handle==10){for(unsigned i=0;i<QCA_DIAGNOSTIC_SIZE;i++)value[i]=qca_diagnostic[i];length=QCA_DIAGNOSTIC_SIZE;}',
  "if(handle==10){for(unsigned i=0;i<716;i++)value[i]=qca_diagnostic[i];length=716;}\n  else if(handle==12){value[0]='Q';value[1]='I';value[2]='C';value[3]=1;rabbit_sha256(value+4,qca_diagnostic,716);for(unsigned i=0;i<84;i++)value[36+i]=qca_diagnostic[716+i];length=120;}")
 (directory/'diagnostic_gatt.c').write_text(gatt)
 driver=(directory/'driver.c').read_text()
 driver=one(driver,'void qca_collect(SystemTable*);','void qca_collect(SystemTable*);\n#include "bringup.h"')
 driver=one(driver,' qca_collect(st);',' qca_collect(st);qca_start(st,city_clock_ms());')
 driver=one(driver,'static int EFIAPI poll_radio(void){','static int EFIAPI poll_radio(void){\n qca_poll(city_clock_ms());')
 driver=one(driver,'static int EFIAPI close_radio(void){','static int EFIAPI close_radio(void){\n if(qca_stop())return 1;')
 driver=one(driver,'return radio_port.bound?EFI_ERROR(6):0;', 'return radio_port.bound||qca_stop()?EFI_ERROR(6):0;')
 driver=one(driver,'Status EFIAPI module_entry(void*h,SystemTable*st){','Status EFIAPI module_entry(void*h,SystemTable*st){\n qca_image=h;')
 (directory/'driver.c').write_text(driver)
 for name in ('bringup.h','bmi_probe.c','diag_ce.c','diag_ce.h','reset_core.c','reset_core.h','power_core.c','power_core.h','uefi_port.c','uefi_port.h','wake_core.c','wake_core.h','rom_ready.c','rom_ready.h','bmi_transport.c','bmi_transport.h','ce_ring.c','ce_ring.h','ce_hw.c','ce_hw.h','ce_uefi.c','ce_uefi.h','ce_bus.c','ce_bus.h','dma_buffer.c','dma_buffer.h','pcie_link.c','pcie_link.h','boot_irq.c','boot_irq.h'):
  (directory/name).write_bytes((ROOT/name).read_bytes())
def compile_driver(directory,crypto):
 sources(directory)
 (directory/'ble_recovery_link.c').write_text(ble.link_source())
 payload=actors.compile_efi(directory,'bmi-driver',[directory/'driver.c',directory/'city_core.c',
  directory/'pci_collect.c',directory/'pci_identity.c',directory/'bmi_probe.c',directory/'reset_core.c',directory/'power_core.c',directory/'uefi_port.c',directory/'wake_core.c',*[directory/n for n in ('diag_ce.c','rom_ready.c','bmi_transport.c','ce_ring.c','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c')],
  actors.LINK/'usb_port.c',directory/'ble_recovery_link.c',directory/'diagnostic_gatt.c',actors.LINK/'file_core.c',
  actors.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1',))
 offset=struct.unpack_from('<I',payload,60)[0]
 if struct.unpack_from('<I',payload,offset+80)[0]>4*1024*1024:raise ValueError('mapped bringup profile exceeds root bound')
 return payload
