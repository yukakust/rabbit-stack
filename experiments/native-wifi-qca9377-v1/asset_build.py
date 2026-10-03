"""Native asset-service integration, disabled until a reviewed BMI policy exists.

This builds plumbing/negative-path gates; it does not guess a firmware policy,
sign or replace the pending native15 candidate.
"""
import struct
import bmi_build as base
ROOT,actors,one=base.ROOT,base.actors,base.one
def sources(directory):
    base.sources(directory)
    driver=(directory/'driver.c').read_text()
    driver=one(driver,'#include "bringup.h"','#include "bringup.h"\n#include "pci_collect.h"\n#include "firmware_port.h"\nQcaFirmwarePort qca_assets;\nstatic SystemTable*asset_system;\nstatic unsigned asset_attempted;\n/* No physical BMI response yet: no firmware policy/allocations authorized. */\nstatic const QcaFirmwarePolicy asset_policy={0};')
    driver=one(driver,'qca_collect(st);qca_start(st,city_clock_ms());','qca_collect(st);qca_start(st,city_clock_ms());asset_system=st;')
    driver=one(driver,' qca_poll(city_clock_ms());',' qca_poll(city_clock_ms());\n if(asset_policy.total&&!asset_attempted&&qca_diagnostic[128]==5){asset_attempted=1;qca_fwp_start(&qca_assets,asset_system,&asset_policy,qca_diagnostic,280);}\n if(qca_assets.phase>=1&&qca_assets.phase<=3)qca_fwp_step(&qca_assets);')
    driver=one(driver,' if(qca_stop())return 1;',' if(qca_stop())return 1;\n if(qca_fwp_close(&qca_assets))return 1;')
    driver=one(driver,'return radio_port.bound||qca_stop()?EFI_ERROR(6):0;','return radio_port.bound||qca_fwp_owned(&qca_assets)||qca_stop()?EFI_ERROR(6):0;')
    (directory/'driver.c').write_text(driver)
    gatt=(directory/'diagnostic_gatt.c').read_text()
    gatt=one(gatt,'#include "pci_collect.h"','#include "pci_collect.h"\n#include "firmware_port.h"\nextern QcaFirmwarePort qca_assets;')
    anchor=' if(!s||!p||!r||!n||capacity<RG_MTU_MAX||n>s->mtu)return 0;'
    gatt=one(gatt,anchor,anchor+'\n size_t asset=qca_fwp_att(&qca_assets,s->mtu,p,n,r,capacity);if(asset!=SIZE_MAX)return asset;')
    (directory/'diagnostic_gatt.c').write_text(gatt)
    for name in ('firmware_port.c','firmware_port.h','firmware_channel.c','firmware_channel.h','firmware_gatt.c','firmware_chunks.c','firmware_chunks.h'):
        (directory/name).write_bytes((ROOT/name).read_bytes())
def compile_driver(directory,crypto):
    sources(directory)
    native=('bmi_probe.c','reset_core.c','power_core.c','uefi_port.c','wake_core.c','rom_ready.c','bmi_transport.c','ce_ring.c','ce_ring.h','ce_hw.c','ce_uefi.c','ce_bus.c','dma_buffer.c','pcie_link.c','boot_irq.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c')
    payload=actors.compile_efi(directory,'asset-driver',[directory/'driver.c',directory/'city_core.c',directory/'pci_collect.c',directory/'pci_identity.c',*[directory/n for n in native if n.endswith('.c')],actors.LINK/'usb_port.c',actors.LINK/'hci_link.c',directory/'diagnostic_gatt.c',actors.LINK/'file_core.c',actors.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1',))
    offset=struct.unpack_from('<I',payload,60)[0]
    if struct.unpack_from('<I',payload,offset+24+56)[0]>4*1024*1024:raise ValueError('asset native exceeds mapped4MiB bound')
    return payload
