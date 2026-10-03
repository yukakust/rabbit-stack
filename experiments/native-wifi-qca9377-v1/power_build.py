"""Read-only power-capability profile, preserving city and file service."""
import struct
import diagnostic_build as base
ROOT,CITY,actors,one=base.ROOT,base.CITY,base.actors,base.one
def sources(directory):
 base.sources(directory)
 p=directory/'pci_collect.h';p.write_text(p.read_text().replace('128u','144u'))
 p=directory/'pci_collect.c';s=p.read_text().replace('#include "pci_identity.h"','#include "pci_identity.h"\n#include "power_core.h"')
 s=one(s,'qca_diagnostic[3]=1;','qca_diagnostic[3]=3;')
 s=one(s,'uint32_t config[16]={0};','uint32_t config[64]={0};')
 s=one(s,'(pci,2,0,16,config)','(pci,2,0,64,config)')
 s=one(s,'   flags|=2;','   flags|=2;\n   qca_power_decode((const uint8_t*)config,qca_diagnostic+128);')
 p.write_text(s)
 for name in ('power_core.h','power_core.c'):(directory/name).write_bytes((ROOT/name).read_bytes())
def compile_driver(directory,crypto):
 sources(directory)
 payload=actors.compile_efi(directory,'power-driver',[directory/'driver.c',directory/'city_core.c',directory/'pci_collect.c',directory/'pci_identity.c',directory/'power_core.c',actors.LINK/'usb_port.c',actors.LINK/'hci_link.c',directory/'diagnostic_gatt.c',actors.LINK/'file_core.c',actors.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1',))
 offset=struct.unpack_from('<I',payload,60)[0]
 if struct.unpack_from('<I',payload,offset+80)[0]>4*1024*1024:raise ValueError('mapped power profile exceeds immutable bound')
 return payload
