"""Separately gated city profile for reversible QCA wake/chip-ID telemetry."""
import struct
import diagnostic_build as base
ROOT,CITY,actors,one=base.ROOT,base.CITY,base.actors,base.one
def sources(directory):
 base.sources(directory)
 header=(directory/'pci_collect.h').read_text().replace('128u','160u')
 (directory/'pci_collect.h').write_text(header)
 collector=(directory/'pci_collect.c').read_text()
 collector=one(collector,'uint8_t qca_diagnostic[QCA_DIAGNOSTIC_SIZE];','uint8_t qca_diagnostic[QCA_DIAGNOSTIC_SIZE];\nvoid*qca_controller;')
 collector=one(collector,' qca_diagnostic[0]=', ' qca_controller=0;\n qca_diagnostic[0]=')
 collector=one(collector,"qca_diagnostic[3]=1;","qca_diagnostic[3]=2;")
 collector=one(collector,'   flags|=2;','   flags|=2;qca_controller=handles[i];')
 collector=one(collector,' put(4,flags,4);',' if(flags!=15||targets!=1)qca_controller=0;\n put(4,flags,4);')
 (directory/'pci_collect.c').write_text(collector)
 driver=(directory/'driver.c').read_text()
 driver=one(driver,'void qca_collect(SystemTable*);','void qca_collect(SystemTable*);\n#include "bringup.h"')
 driver=one(driver,' qca_collect(st);',' qca_collect(st);qca_start(st,city_clock_ms());')
 driver=one(driver,'static int EFIAPI poll_radio(void){','static int EFIAPI poll_radio(void){\n qca_poll(city_clock_ms());')
 driver=one(driver,'static int EFIAPI close_radio(void){','static int EFIAPI close_radio(void){\n if(qca_stop())return 1;')
 driver=one(driver,'return radio_port.bound?EFI_ERROR(6):0;', 'return radio_port.bound||qca_stop()?EFI_ERROR(6):0;')
 driver=one(driver,'Status EFIAPI module_entry(void*h,SystemTable*st){','Status EFIAPI module_entry(void*h,SystemTable*st){\n qca_image=h;')
 (directory/'driver.c').write_text(driver)
 for name in ('bringup.h','bringup.c','uefi_port.c','uefi_port.h','wake_core.c','wake_core.h'):
  (directory/name).write_bytes((ROOT/name).read_bytes())
def compile_driver(directory,crypto):
 sources(directory)
 payload=actors.compile_efi(directory,'bringup-driver',[directory/'driver.c',directory/'city_core.c',
  directory/'pci_collect.c',directory/'pci_identity.c',directory/'bringup.c',directory/'uefi_port.c',directory/'wake_core.c',
  actors.LINK/'usb_port.c',actors.LINK/'hci_link.c',directory/'diagnostic_gatt.c',actors.LINK/'file_core.c',
  actors.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1',))
 offset=struct.unpack_from('<I',payload,60)[0]
 if struct.unpack_from('<I',payload,offset+80)[0]>4*1024*1024:raise ValueError('mapped bringup profile exceeds root bound')
 return payload
