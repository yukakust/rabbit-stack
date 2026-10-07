#!/usr/bin/env python3
"""Pure public QPFX0001 decoder; values are telemetry, never device attestation."""
import argparse,json,struct
from pathlib import Path
FIELDS='''generation prefix_phase prefix_reason stop_calls prefix_released
stop_offset stop_submitted stop_completed stop_plan stop_io
boot_phase boot_error plan_phase plan_error plan_offset plan_submitted plan_completed io_phase
stage failed adapter_phase cleanup_slot held dma_users claimed access_count bus_owned
boot_owns_pin asset_pinned irq_owned link_owned wake_owned reset_owned
ble_state pending connected credits inflight stream_used stream_goal usb_polls usb_reads usb_timeouts usb_observation
last_usb_status_lo last_usb_status_hi last_usb_result last_usb_bytes
raw_count raw_overflow usb_fault frames max_poll_us max_qca_us
started_lo started_hi last_lo last_hi'''.split()
assert len(FIELDS)==58

def decode(raw,expected_generation):
 if type(raw) is not bytes or len(raw)!=240 or raw[:8]!=b'QPFX0001':raise ValueError('exact 240-byte QPFX0001 required')
 if type(expected_generation) is not int or not 1<=expected_generation<=0xffffffff:raise ValueError('explicit bounded generation required')
 values=struct.unpack('<58I',raw[8:])
 if values[0]!=expected_generation:raise ValueError('signed asset generation mismatch')
 return {'fields':dict(zip(FIELDS,values)),'device_attestation':False,'physical_owner_release_proven':False}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('raw',type=Path);p.add_argument('--generation',type=int,required=True);a=p.parse_args();print(json.dumps(decode(a.raw.read_bytes(),a.generation),indent=2))
