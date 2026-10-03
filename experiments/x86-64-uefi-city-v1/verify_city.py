#!/usr/bin/env python3
"""Reproduce city host + exact UEFI gates. No owner signing, radio or hardware writes."""
import json
import tempfile
from pathlib import Path
import build_city
import city_gate
import city_world
import check_city

def verify():
    root=Path(__file__).resolve().parent; (root/'runs').mkdir(exist_ok=True)
    directory=Path(tempfile.mkdtemp(prefix='verified-',dir=root/'runs'))
    # PUBLIC fixture authority only, never the real owner's private key.
    _,_,crypto=build_city.engine.prepare(directory,build_city.engine.old.TEST_OWNER)
    payload=build_city.compile_city_driver(directory,crypto)
    if build_city.compile_city_driver(directory,crypto)!=payload:raise ValueError('city build nondeterministic')
    (directory/'payload.efi').write_bytes(payload)
    (directory/'world.rup').write_bytes(city_world.compile_city(city_world.initial_city(),9))
    report={'directory':str(directory),'payload_sha256':city_world.flow.sha(payload),
            'profile_sources':city_world.flow.city_module('city_native').source_hashes(),
            'host':check_city.check_city(directory/'world.rup',directory/'host',sanitizers=True),
            'qemu':city_gate.qemu_gate(directory,payload),
            'empty_boot_qemu':city_gate.qemu_gate(directory,payload,empty_boot=True),
            'physical_verified':False,'bluetooth_verified':False}
    city_world.flow.save(directory/'verification.json',report)
    return report

if __name__=='__main__':print(json.dumps(verify(),indent=2))
