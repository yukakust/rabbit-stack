#!/usr/bin/env python3
"""Prepare an existing gated driver-2 trial; explicit owner-local signing, NEVER send."""
import argparse
import json
from pathlib import Path
import struct
from build_image import ROOT,LINK,OLD,NATIVE,V3,old,digest
from release import pack,verify,UpdateError
from prepare_file import bundle

def checked_inputs(report_path,world_path,world_sha,owner_path):
    report=json.loads(report_path.read_text())
    if (report.get('status')!='OWNER-OBSERVED-EXACT-MAC-QEMU-NO-DEVICE' or
        not report.get('qemu_verified') or not report.get('mac_sender_compile_verified') or
        report.get('test_key_only') is not False):
        raise UpdateError('production owner-observed installation gate required')
    owner=owner_path.read_bytes()
    if len(owner)!=32 or owner==old.TEST_OWNER or digest(owner).hex()!=report['owner_public_sha256']:
        raise UpdateError('owner public key does not match installed gate')
    # Bind to the actual saved image, not a newly generated bootstrap.
    if digest((report_path.parent/'connected-supervisor.img').read_bytes()).hex()!=report['image_sha256']:
        raise UpdateError('saved installed image hash mismatch')
    production=[ROOT/'driver.c',ROOT/'loop.c',ROOT/'connected_abi.h',ROOT/'target.json',
        ROOT/'build_image.py',OLD/'supervisor.c',OLD/'scene_module.c',OLD/'scene_abi.h',
        OLD/'build_image.py',V3/'runtime_core.c']
    production += [LINK/name for name in ('usb_port.c','usb_port.h','hci_link.c','hci_link.h',
        'gatt_core.c','gatt_core.h','file_core.c','file_core.h')]
    production += [NATIVE/name for name in ('abi.h','verify_core.c','verify_core.h','sha256.c','sha256.h')]
    for path in production:
        name=str(path.relative_to(ROOT.parents[1]))
        if report['source_hashes'].get(name)!=digest(path.read_bytes()).hex():
            raise UpdateError('runtime source differs from installed gate: '+name)
    payload=report_path.parent/'driver-revision-2.efi'
    if digest(payload.read_bytes()).hex()!=report['module_hashes']['2']:
        raise UpdateError('saved driver-2 hash mismatch')
    world=world_path.read_bytes()
    if (not 12<=len(world)<=65535 or world[:4]!=b'RUP3' or
        struct.unpack_from('<I',world,8)[0]!=2 or digest(world).hex()!=world_sha.lower()):
        raise UpdateError('exact currently applied counter-2 world required')
    return report,owner,payload,world

def prepare_plan(report_path,world_path,world_sha,owner_path,output):
    report,owner,payload,world=checked_inputs(report_path,world_path,world_sha,owner_path)
    plan={'schema_version':1,'status':'REVIEWED-DRIVER-2-PREPARED-NOT-SIGNED-NOT-SENT',
        'installed_report':str(report_path.resolve()),'world_package':str(world_path.resolve()),
        'owner_public':str(owner_path.resolve()),'payload':str(payload.resolve()),
        'world_sha256':digest(world).hex(),'world_counter':2,'native_counter':1,
        'target_sha256':report['target_sha256'],'base_runtime_sha256':report['module_hashes']['1'],
        'payload_sha256':report['module_hashes']['2'],'owner_public_sha256':digest(owner).hex(),
        'installed_efi_sha256':report['efi_sha256'],
        'expected_effect':'same walking cat, engine-only blue bottom line; intentional reconnect',
        'assumption':'same Dell boot, baseline driver-1 still active, no native update yet',
        'recovery_scope':'failed health retains old driver/world; uncertain radio cleanup may watchdog reboot to empty bootstrap, NOT guaranteed native isolation'}
    with output.open('x') as out:json.dump(plan,out,indent=2,sort_keys=True)
    return plan

def sign_plan(path,private_path,reviewed_sha):
    raw=path.read_bytes()
    if digest(raw).hex()!=reviewed_sha.lower():raise UpdateError('reviewed plan SHA256 mismatch')
    plan=json.loads(raw)
    report,owner,payload,world=checked_inputs(Path(plan['installed_report']),Path(plan['world_package']),
        plan['world_sha256'],Path(plan['owner_public']))
    expected={'schema_version':1,'status':'REVIEWED-DRIVER-2-PREPARED-NOT-SIGNED-NOT-SENT',
        'world_counter':2,'native_counter':1,'target_sha256':report['target_sha256'],
        'base_runtime_sha256':report['module_hashes']['1'],'payload_sha256':report['module_hashes']['2'],
        'payload':str(payload.resolve()),'owner_public_sha256':digest(owner).hex(),
        'installed_efi_sha256':report['efi_sha256']}
    if any(plan.get(k)!=v for k,v in expected.items()):raise UpdateError('plan/gate identity mismatch')
    from owner_key import load_private
    from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
    private=load_private(private_path)
    if private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)!=owner:
        raise UpdateError('private key does not match provisioned owner')
    target=bytes.fromhex(plan['target_sha256']);base=bytes.fromhex(plan['base_runtime_sha256'])
    release=pack(payload.read_bytes(),private=private,target=target,base_runtime=base,world=world,counter=1)
    verify(release,target=target,owner=owner,base_runtime=base,world=world,counter=0)
    release_path=path.with_suffix('.rrt');session_path=path.with_suffix('.session.json')
    if release_path.exists() or session_path.exists():raise UpdateError('outputs exist; preserve SAME saved session')
    with release_path.open('xb') as out:out.write(release)
    with session_path.open('x') as out:json.dump(bundle(release,2,1),out,indent=2)
    print('SIGNED-NOT-SENT: '+str(release_path)+'; SHA256='+digest(release).hex())
    print('SAVED SESSION (NOT SENT): '+str(session_path))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sign-plan',type=Path);p.add_argument('--private',type=Path)
    p.add_argument('--reviewed-plan-sha256')
    p.add_argument('--installed-report',type=Path);p.add_argument('--world-package',type=Path)
    p.add_argument('--world-sha256');p.add_argument('--owner-public',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.sign_plan:
        if not a.private or not a.reviewed_plan_sha256:p.error('signing needs private path and reviewed plan SHA256')
        if any((a.installed_report,a.world_package,a.world_sha256,a.owner_public,a.output)):p.error('do not mix prepare and sign modes')
        sign_plan(a.sign_plan,a.private,a.reviewed_plan_sha256)
    else:
        if a.private or a.reviewed_plan_sha256:p.error('private key allowed only in explicit --sign-plan mode')
        if not all((a.installed_report,a.world_package,a.world_sha256,a.owner_public,a.output)):p.error('all preparation inputs required')
        plan=prepare_plan(a.installed_report,a.world_package,a.world_sha256,a.owner_public,a.output)
        print('PREPARED-NOT-SIGNED-NOT-SENT: '+str(a.output))
        print('PLAN SHA256: '+digest(a.output.read_bytes()).hex())
        print(json.dumps(plan,indent=2,sort_keys=True))
    print('STOP: no Bluetooth send, media/firmware write, or private-key output.')
if __name__=='__main__':main()
