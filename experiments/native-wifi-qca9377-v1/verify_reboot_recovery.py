"""Yukabox native/UEFI/world preflight, no owner private key and no physical writes."""
import argparse
from pathlib import Path
import reboot_recovery as recovery

flow = recovery.flow
profile = recovery.profile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--world', type=Path, required=True)
    p.add_argument('--counter', type=int, required=True)
    p.add_argument('--owner-public', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--ble-recovery', action='store_true')
    a = p.parse_args(); out = a.output
    out.mkdir(parents=True, exist_ok=False)
    world = flow.read_json(a.world); flow.save(out / 'world.json', world)
    restored = flow.compile_world(out / 'world.json', a.counter, flow.CREATOR)
    (out / 'world.rup').write_bytes(restored)
    owner = a.owner_public.read_bytes()
    _, _, crypto = recovery.engine.prepare(out, owner)
    builder = profile.build_city.compile_city_driver
    transform = None
    if a.ble_recovery:
        import ble_recovery_build, verify_ble_recovery
        builder = ble_recovery_build.compile_driver
        transform = verify_ble_recovery.fixture
    payload = builder(out, crypto)
    if builder(out, crypto) != payload:
        raise ValueError('two native builds differ')
    (out / 'payload.efi').write_bytes(payload)
    checks = flow.actors_module('actors_check').check_city(out / 'world.rup', out / 'world-check', sanitizers=True, roof_cat_timing=True)
    actors_gate = flow.actors_module('actors_gate')
    gates = [actors_gate.qemu_gate(out, payload), actors_gate.qemu_gate(out, payload, True, test_transform=transform)]
    # Bind all established native15 build dependencies too; this is conservative
    # and leaves the existing signed native15 packet and source snapshot intact.
    baseline = flow.read_json(recovery.REPO / 'experiments/native-wifi-qca9377-v1/runs/bmi-profile/reproduction.json', 8 * 1024 * 1024)
    names = set(baseline['inputs'])
    for folder in ('x86-64-uefi-connected-supervisor-v1','x86-64-uefi-wireless-supervisor-v1',
        'x86-64-uefi-runtime-supervisor-v1','x86-64-uefi-god-runtime-v1','x86-64-uefi-god-runtime-v2',
        'x86-64-uefi-god-runtime-v3','x86-64-uefi-city-v1','x86-64-uefi-city-v2',
        'runtime-update-contract-v1','ble-connected-file-transfer-v1'):
        base = recovery.REPO / 'experiments' / folder
        for source in base.rglob('*'):
            if source.is_file() and source.suffix in ('.c','.h','.py','.json') and not set(source.relative_to(base).parts).intersection(('runs','evidence','__pycache__')):
                names.add(str(source.relative_to(recovery.REPO)))
    names.update('experiments/native-wifi-qca9377-v1/' + n for n in
        ('reboot_recovery.py','verify_reboot_recovery.py','test_reboot_recovery.py'))
    if a.ble_recovery:
        names.update('experiments/native-wifi-qca9377-v1/' + n for n in
            ('ble_recovery_build.py','test_ble_recovery.c','verify_ble_recovery.py'))
    inputs = {n:flow.sha((recovery.REPO / n).read_bytes()) for n in sorted(names)}
    evidence = ('actors-qemu/report.json','actors-qemu/observed.log',
        'actors-empty-boot-qemu/report.json','actors-empty-boot-qemu/observed.log','world-check/city-check.c')
    report = {'status':'CITY-REBOOT-RECOVERY-PREFLIGHT-PASS','build_host':'yukabox',
        'payload_sha256':flow.sha(payload),'owner_public_sha256':flow.sha(owner),
        'world_sha256':flow.sha(flow.canonical(world)), 'restored_package_sha256':flow.sha(restored),
        'inputs':inputs,'evidence':recovery.hashes(out,evidence),'gates':gates,'host_world_checks':checks,
        'native_builds':2,'ble_unknown_disconnect_recovery':a.ble_recovery,'physical_reboot':False,'physical_bluetooth_transfer':False,
        'physical_city_restore':False,'owner_signing':False,'wifi_probe_enabled':False}
    flow.save(out / 'recovery-gate.json', report)
    print(report['status'], report['payload_sha256'])


if __name__ == '__main__':
    main()
