"""Exact native warm/full-channel profile; no target RAM/firmware writes."""
import struct
import bmi_build as base
ROOT,CITY,actors,one=base.ROOT,base.CITY,base.actors,base.one
CORE=('init_probe.c','init_adapter.c','init_adapter.h','warm_core.c','warm_core.h',
      'channels_core.c','channels_core.h','boot_irq_mapped.c','boot_irq_mapped.h')
def sources(directory):
 base.sources(directory)
 h=directory/'pci_collect.h';h.write_text(one(h.read_text(),'800u','888u'))
 c=directory/'pci_collect.c';c.write_text(one(c.read_text(),'qca_diagnostic[3]=13;','qca_diagnostic[3]=15;'))
 g=directory/'diagnostic_gatt.c';s=g.read_text().replace('p[7]==8?8:0','p[7]==10?8:0').replace('start==1?1:8','start==1?1:10').replace('handle==1?1:8','handle==1?1:10')
 s=one(s,'for(unsigned i=0;i<84;i++)value[36+i]=qca_diagnostic[716+i];length=120;',
         'for(unsigned i=0;i<172;i++)value[36+i]=qca_diagnostic[716+i];length=208;')
 g.write_text(s)
 for name in CORE:(directory/name).write_bytes((ROOT/name).read_bytes())
def compile_driver(directory,crypto):
 sources(directory)
 (directory/'ble_recovery_link.c').write_text(base.ble.link_source())
 names=('init_probe.c','init_adapter.c','warm_core.c','channels_core.c','boot_irq_mapped.c',
        'reset_core.c','power_core.c','uefi_port.c','wake_core.c','rom_ready.c','ce_ring.c',
        'ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c')
 payload=actors.compile_efi(directory,'init-driver',[directory/'driver.c',directory/'city_core.c',
  directory/'pci_collect.c',directory/'pci_identity.c',*[directory/n for n in names],
  actors.LINK/'usb_port.c',directory/'ble_recovery_link.c',directory/'diagnostic_gatt.c',actors.LINK/'file_core.c',
  actors.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1',))
 offset=struct.unpack_from('<I',payload,60)[0]
 if struct.unpack_from('<I',payload,offset+80)[0]>4*1024*1024:raise ValueError('mapped native init profile exceeds root bound')
 return payload
