"""Separate reviewed actor profile with a read-only PCI characteristic.

Installed bootstrap and legacy actor source bytes remain unchanged.
"""
import sys,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CITY=ROOT.parent/'x86-64-uefi-city-v2'
sys.path.insert(0,str(CITY))
import actors_build as actors
one=actors.one

def sources(directory):
 actors.sources(directory)
 driver=(directory/'driver.c').read_text()
 driver=one(driver,'#include "actor_clock.c"','#include "actor_clock.c"\nvoid qca_collect(SystemTable*);')
 driver=one(driver,' if(city_display_bind(st)||city_clock_bind(st))return 1;',
     ' if(city_display_bind(st)||city_clock_bind(st))return 1;\n qca_collect(st);')
 (directory/'driver.c').write_text(driver)
 gatt=(actors.LINK/'gatt_core.c').read_text()
 gatt=one(gatt,'#include "gatt_core.h"','#include "gatt_core.h"\n#include "pci_collect.h"')
 gatt=one(gatt,'w16(r+3,7);return 5;','w16(r+3,9);return 5;')
 gatt=one(gatt,'w16(r+4,7);uuid','w16(r+4,9);uuid')
 gatt=one(gatt,'handle<=6?6:0','handle<=6?6:handle<=8?8:0')
 gatt=one(gatt,'declaration==6?2:8','declaration>=6?2:8')
 gatt=one(gatt,'if(handle>7)','if(handle>9)')
 gatt=one(gatt,'handle==4||handle==6','handle==4||handle==6||handle==8')
 gatt=one(gatt,'uint8_t value[RF_STATUS_SIZE];','uint8_t value[QCA_DIAGNOSTIC_SIZE];')
 gatt=one(gatt,'if(handle==7){','if(handle==9){for(unsigned i=0;i<QCA_DIAGNOSTIC_SIZE;i++)value[i]=qca_diagnostic[i];length=QCA_DIAGNOSTIC_SIZE;}\n  else if(handle==7){')
 gatt=gatt.replace('handle<=7?','handle<=9?')
 (directory/'diagnostic_gatt.c').write_text(gatt)
 for name in ('pci_collect.h','pci_collect.c','pci_identity.h','pci_identity.c'):
  (directory/name).write_bytes((ROOT/name).read_bytes())

def compile_driver(directory,crypto):
 sources(directory)
 payload=actors.compile_efi(directory,'diagnostic-driver',[directory/'driver.c',directory/'city_core.c',
  directory/'pci_collect.c',directory/'pci_identity.c',actors.LINK/'usb_port.c',actors.LINK/'hci_link.c',
  directory/'diagnostic_gatt.c',actors.LINK/'file_core.c',actors.NATIVE/'sha256.c',*crypto],
  driver=True,definitions=('SCENE_REVISION=1',))
 offset=struct.unpack_from('<I',payload,60)[0]
 if struct.unpack_from('<I',payload,offset+24+56)[0]>4*1024*1024:
  raise ValueError('mapped diagnostic profile exceeds installed4MiB bound')
 return payload
