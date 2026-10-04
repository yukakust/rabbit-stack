"""Offline city recovery plan; writes require owner reboot + fresh empty receiver.

The old pending native packet is retained verbatim, never retried against bootstrap.
All native compilation and world C checks happen in the Yukabox preflight.
"""
import argparse
import base64
import copy
from pathlib import Path
import native_route

flow, engine = native_route.flow, native_route.engine
REPO = native_route.REPO
profile = flow.actors_module('actors_native')
EMPTY = '52465301' + '00' * 56


def hashes(directory, names):
    return {name: flow.sha((directory / name).read_bytes()) for name in names}


def gate(checked, world, owner):
    report = flow.read_json(checked / 'recovery-gate.json', 8 * 1024 * 1024)
    payload = (checked / 'payload.efi').read_bytes()
    if (report['status'] != 'CITY-REBOOT-RECOVERY-PREFLIGHT-PASS' or
        report['payload_sha256'] != flow.sha(payload) or
        report['world_sha256'] != flow.sha(flow.canonical(world)) or
        report['owner_public_sha256'] != flow.sha(owner)):
        raise ValueError('recovery gate identity differs')
    for name, expected in report['inputs'].items():
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or flow.sha((REPO / path).read_bytes()) != expected:
            raise ValueError('recovery source changed: ' + name)
    profile.gates(checked, payload)
    boot = flow.read_json(checked / 'actors-empty-boot-qemu/report.json')
    if (not boot['empty_boot'] or boot['status'] != 'EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS' or
        boot['payload_sha256'] != flow.sha(payload) or
        flow.sha((checked / 'actors-empty-boot-qemu/observed.log').read_bytes()) != boot['observed_log_sha256']):
        raise ValueError('exact empty boot gate required')
    for name, expected in report['evidence'].items():
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or flow.sha((checked / path).read_bytes()) != expected:
            raise ValueError('recovery evidence changed: ' + name)
    return payload, report


def pending(state, owner, installed):
    directory = Path(state['native_pending'])
    report = flow.read_json(directory / 'report.json')
    session = flow.validate_session(flow.read_json(directory / 'session.json'))
    packet = (directory / 'native.rrt').read_bytes()
    if (report['kind'] != 'native-read-only-pci' or session['kind'] != 2 or
        session['counter'] != report['counter'] or session['counter'] != state['engine']['native_counter'] + 1 or
        base64.b64decode(session['stream_base64'])[32:] != packet or
        flow.sha(packet) != report['package_sha256'] or
        flow.sha((directory / 'session.json').read_bytes()) != report['session_sha256'] or
        report['base_runtime_sha256'] != state['engine']['payload_sha256'] or
        report['base_world_sha256'] != state['world_sha256'] or
        report['world_package_sha256'] != state['package_sha256']):
        raise ValueError('old pending session differs')
    verified = engine.verify(packet, target=bytes.fromhex(installed['target_sha256']), owner=owner,
        base_runtime=bytes.fromhex(state['engine']['payload_sha256']),
        world=Path(state['package']).read_bytes(), counter=state['engine']['native_counter'])
    if verified.payload != (directory / 'payload.efi').read_bytes():
        raise ValueError('old pending payload differs')
    return directory, session['counter']


def recovery_reservation(state, owner, installed):
    """Reserve above an existing failed boot-recovery packet, preserving it."""
    directory = Path(state['recovery_pending'])
    plan = flow.read_json(directory / 'plan.json')
    report = flow.read_json(directory / 'report.json')
    if (plan['kind'] != 'owner-reboot-city-recovery' or report['engine_done'] or report['world_done'] or
        report.get('receiver_reported_applied') or hashes(directory, plan['files']) != plan['files']):
        raise ValueError('only intact unconfirmed boot recovery may be superseded')
    before = flow.read_json(directory / 'before-state.json')
    if before['world_sha256'] != state['world_sha256'] or before['engine']['native_counter'] != state['engine']['native_counter']:
        raise ValueError('old recovery world/counter differs')
    packet = (directory / 'native.rrt').read_bytes()
    session = flow.validate_session(flow.read_json(directory / 'session.json'))
    verified = engine.verify(packet, target=bytes.fromhex(installed['target_sha256']), owner=owner,
        base_runtime=bytes.fromhex(installed['module_hashes']['1']), world=b'', counter=state['engine']['native_counter'])
    if (session['kind'] != 2 or session['counter'] != verified.counter or verified.counter != plan['counter'] or
        base64.b64decode(session['stream_base64'])[32:] != packet or verified.payload != (directory / 'payload.efi').read_bytes()):
        raise ValueError('old recovery signature/session differs')
    return directory, verified.counter


def completed_reservation(state, owner, installed):
    """Bind an idle completed diagnostic release; never fabricate pending state."""
    if state.get('pending') or state.get('native_pending') or state.get('recovery_pending'):
        raise ValueError('completed recovery requires idle controller')
    directory = Path(state['engine']['last_release_report']).parent
    report = flow.read_json(directory / 'report.json')
    session = flow.validate_session(flow.read_json(directory / 'session.json'))
    packet = (directory / 'native.rrt').read_bytes()
    payload = (directory / 'payload.efi').read_bytes()
    counter = state['engine']['native_counter']
    if (report.get('kind') != 'native-read-only-pci' or report.get('status') != 'EXACT-APPLIED-RECEIPT'
        or report.get('receiver_reported_applied') is not True or counter < 1
        or report.get('counter') != counter or session['kind'] != 2 or session['counter'] != counter
        or report.get('payload_sha256') != state['engine']['payload_sha256']
        or flow.sha(payload) != state['engine']['payload_sha256']
        or report.get('base_world_sha256') != state['world_sha256']
        or report.get('world_package_sha256') != state['package_sha256']
        or base64.b64decode(session['stream_base64'])[32:] != packet
        or flow.sha(packet) != report.get('package_sha256')
        or flow.sha((directory / 'session.json').read_bytes()) != report.get('session_sha256')):
        raise ValueError('completed release/session/world binding differs')
    verified = engine.verify(packet, target=bytes.fromhex(installed['target_sha256']), owner=owner,
        base_runtime=bytes.fromhex(report['base_runtime_sha256']),
        world=Path(state['package']).read_bytes(), counter=counter - 1)
    if verified.counter != counter or verified.payload != payload:
        raise ValueError('completed release signature differs')
    return directory, counter


def reservation(state, owner, installed, kind):
    if kind == 'recovery':return recovery_reservation(state, owner, installed)
    if kind == 'native':return pending(state, owner, installed)
    if kind == 'completed':return completed_reservation(state, owner, installed)
    raise ValueError('unknown predecessor kind')


def prepare(state_path, checked, directory, private):
    with flow.state_lock(state_path):
        state = flow.read_json(state_path)
        if state['pending'] or (state.get('recovery_pending') and state.get('native_pending')):
            raise ValueError('world request or conflicting recovery blocks preparation')
        world = flow.current(state)
        if world['schema_version'] != 5 or state['engine']['family'] != 'reviewed-city-v2':
            raise ValueError('reviewed actor city required')
        journal = state_path.parent / 'control/journal.json'
        if flow.read_json(journal, 2 * 1024 * 1024)['active']:
            raise ValueError('active world request blocks recovery')
        installed = engine.gate_check(Path(state['engine']['installed_gate']))
        if flow.sha(Path(state['engine']['installed_gate']).read_bytes()) != state['engine']['installed_gate_sha256']:
            raise ValueError('installed gate changed')
        owner = private.with_suffix('.pub').read_bytes()
        if flow.sha(owner) != installed['owner_public_sha256']:
            raise ValueError('owner identity differs')
        old_kind = 'recovery' if state.get('recovery_pending') else 'native' if state.get('native_pending') else 'completed'
        old, old_counter = reservation(state, owner, installed, old_kind)
        payload, checked_report = gate(checked, world, owner)
        counter = old_counter + 1  # Never reuse the still-saved native15 identity.
        if counter > 0xffffffff or state['counter'] >= 0xffffffff:
            raise ValueError('counter exhausted')
        directory.mkdir(parents=True, exist_ok=False)
        flow.save(directory / 'before-state.json', state)
        flow.save(directory / 'world.json', world)
        restored = flow.compile_world(directory / 'world.json', state['counter'] + 1, flow.CREATOR)
        if flow.sha(restored) != checked_report['restored_package_sha256']:
            raise ValueError('exact restored world was not C checked')
        (directory / 'world.rup').write_bytes(restored)
        # Native owner secret is touched only after exact source/VM/world gates.
        key = engine.load_private(private)
        packet = engine.pack(payload, private=key, target=bytes.fromhex(installed['target_sha256']),
            base_runtime=bytes.fromhex(installed['module_hashes']['1']), world=b'', counter=counter)
        engine.verify(packet, target=bytes.fromhex(installed['target_sha256']), owner=owner,
            base_runtime=bytes.fromhex(installed['module_hashes']['1']), world=b'', counter=state['engine']['native_counter'])
        (directory / 'native.rrt').write_bytes(packet)
        (directory / 'payload.efi').write_bytes(payload)
        flow.save(directory / 'session.json', flow.bundle(packet, 2, counter))
        flow.save(directory / 'world-session.json', flow.bundle(restored, 1, state['counter'] + 1))
        names = ('before-state.json', 'world.json', 'world.rup', 'native.rrt', 'payload.efi', 'session.json', 'world-session.json')
        plan = {'schema_version': 1, 'status': 'PREPARED-NOT-ACTIVATED', 'kind': 'owner-reboot-city-recovery',
            'checked_directory': str(checked.resolve()), 'gate_sha256': flow.sha((checked / 'recovery-gate.json').read_bytes()),
            'files': hashes(directory, names), 'old_pending_directory': str(old),
            'old_pending_files': hashes(old, ('native.rrt', 'session.json', 'payload.efi', 'report.json')),
            'reserved_counter': old_counter, 'old_pending_kind': old_kind,
            'journal_sha256': flow.sha(journal.read_bytes()), 'counter': counter,
            'world_counter': state['counter'] + 1, 'owner_confirmed_reboot': False,
            'engine_done': False, 'world_done': False, 'receiver_reported_applied': False, 'sender_steps': []}
        flow.save(directory / 'plan.json', plan)
        flow.save(directory / 'report.json', copy.deepcopy(plan))
        return plan


def restore(state_path, directory, private, dell_rebooted=False):
    with flow.state_lock(state_path):
        state = flow.read_json(state_path)
        plan = flow.read_json(directory / 'plan.json')
        boot_query_text = None
        report = flow.read_json(directory / 'report.json')
        before = flow.read_json(directory / 'before-state.json')
        if hashes(directory, plan['files']) != plan['files']:
            raise ValueError('saved recovery bytes changed')
        checked = Path(plan['checked_directory'])
        owner = private.with_suffix('.pub').read_bytes()
        payload, _ = gate(checked, flow.read_json(directory / 'world.json'), owner)
        if flow.sha((checked / 'recovery-gate.json').read_bytes()) != plan['gate_sha256'] or payload != (directory / 'payload.efi').read_bytes():
            raise ValueError('recovery gate changed')
        installed = engine.gate_check(Path(before['engine']['installed_gate']))
        if flow.sha(Path(before['engine']['installed_gate']).read_bytes()) != before['engine']['installed_gate_sha256']:
            raise ValueError('installed gate changed')
        native_session = flow.validate_session(flow.read_json(directory / 'session.json'))
        native = (directory / 'native.rrt').read_bytes()
        verified = engine.verify(native, target=bytes.fromhex(installed['target_sha256']), owner=owner,
            base_runtime=bytes.fromhex(installed['module_hashes']['1']), world=b'', counter=before['engine']['native_counter'])
        world_session = flow.validate_session(flow.read_json(directory / 'world-session.json'))
        restored = (directory / 'world.rup').read_bytes()
        if (native_session['kind'] != 2 or native_session['counter'] != plan['counter'] or
            verified.counter != plan['counter'] or verified.payload != payload or
            plan['counter'] != plan.get('reserved_counter', before['engine']['native_counter'] + 1) + 1 or
            base64.b64decode(native_session['stream_base64'])[32:] != native or
            world_session['kind'] != 1 or world_session['counter'] != plan['world_counter'] or
            plan['world_counter'] != before['counter'] + 1 or
            base64.b64decode(world_session['stream_base64'])[32:] != restored or
            flow.compile_world(directory / 'world.json', plan['world_counter'], flow.CREATOR) != restored):
            raise ValueError('recovery packet/session/counter binding differs')
        active = state.get('recovery_pending') == str(directory.resolve())
        if not active:
            if not dell_rebooted:
                raise ValueError('owner must explicitly confirm actual Dell reboot')
            if state != before or flow.sha((state_path.parent / 'control/journal.json').read_bytes()) != plan['journal_sha256']:
                raise ValueError('controller state changed since preparation')
            old = Path(plan['old_pending_directory'])
            if hashes(old, plan['old_pending_files']) != plan['old_pending_files']:
                raise ValueError('old pending evidence changed')
            old_kind = plan.get('old_pending_kind', 'native')
            reserved_dir, reserved_counter = reservation(state, owner, installed, old_kind)
            if reserved_dir != old or reserved_counter + 1 != plan['counter']:
                raise ValueError('reserved signed predecessor differs')
            # No BEGIN/DATA/COMMIT until owner observation AND exact zero receipt.
            code, text = flow.sender_step(directory, report, 'query', ['--query-only'])
            observed = flow.parse_status(text, native_session) if not code else None
            if not observed or observed['outcome'] != 'idle' or observed['raw_hex'] != EMPTY:
                raise ValueError('fresh empty receiver not observed; old pending preserved')
            boot_query_text = text
            report.update(owner_confirmed_reboot=True, boot_receiver_status=observed)
            flow.save(directory / 'report.json', report)
            state.update(native_pending=None, recovery_pending=str(directory.resolve()))
            state.setdefault('retired_native_sessions', []).append({'directory': str(old),
                'files': plan['old_pending_files'], 'reason': 'owner-confirmed-reboot-and-fresh-zero-receiver',
                'replacement_counter': plan['counter']})
            flow.save(state_path, state)  # One atomic state write; old files untouched.
        elif not report.get('owner_confirmed_reboot') or report.get('boot_receiver_status', {}).get('raw_hex') != EMPTY:
            raise ValueError('recovery activation proof absent')
        if report.get('status') == 'EXACT-REJECTED-RECEIPT':
            raise ValueError('recovery rejected; retained for inspection')
        if state['world_sha256'] != before['world_sha256'] or state.get('native_pending'):
            raise ValueError('world changed or another native operation pending')
        if not report['engine_done']:
            if state['counter'] != before['counter'] or state['engine']['native_counter'] not in (before['engine']['native_counter'], plan['counter']):
                raise ValueError('unexpected pre-engine counters')
            def applied():
                report.update(status='EXACT-APPLIED-RECEIPT', receiver_reported_applied=True)
                flow.save(directory / 'report.json', report)
                state['engine'].update(native_counter=plan['counter'], payload_sha256=flow.sha(payload),
                    last_release_report=str(directory / 'report.json'), diagnostic_profile=None,
                    actor_core_sha256=profile.source_hashes()['city_core.c'],
                    basis='owner-confirmed reboot + exact city recovery receipt; physical observation separate')
                flow.save(state_path, state)
                report.update(engine_done=True, status='ENGINE-APPLIED')
                flow.save(directory / 'report.json', report)
                return 0
            result = flow.deliver_session(directory, report, native_session, applied, initial_query_text=boot_query_text) if boot_query_text is not None else flow.deliver_session(directory, report, native_session, applied)
            if result:
                return report
        elif state['engine']['native_counter'] != plan['counter'] or state['engine']['payload_sha256'] != flow.sha(payload):
            raise ValueError('applied recovery engine differs')
        world_dir = directory / 'restored-world'
        if state['counter'] == before['counter']:
            if state['pending'] and Path(state['pending']) != world_dir:
                raise ValueError('another world session pending')
            if not state['pending']:
                world_dir.mkdir(exist_ok=True)
                for source, dest in [('world.json','world.json'), ('world.rup','world.rup'), ('world-session.json','session.json')]:
                    (world_dir / dest).write_bytes((directory / source).read_bytes())
                wr = {'schema_version':1, 'status':'CHECKED-NOT-SENT', 'counter':plan['world_counter'],
                    'base_world_sha256':before['world_sha256'], 'world_sha256':before['world_sha256'],
                    'package_sha256':flow.sha((world_dir / 'world.rup').read_bytes()),
                    'session_sha256':flow.sha((world_dir / 'session.json').read_bytes()),
                    'authority':state['authority'], 'host_checks':{'basis':'exact Yukabox recovery preflight'},
                    'physical_execution_verified':False, 'receiver_reported_applied':False, 'sender_steps':[]}
                flow.save(world_dir / 'report.json', wr)
                state['pending'] = str(world_dir); flow.save(state_path, state)
            # Shared validator/signature/receipt logic; C checks already gated remotely.
            wd, wr, ws, _ = flow.pending_world(state)
            if flow.deliver_session(wd, wr, ws, lambda: flow.advance(state_path, state, wd, wr, ws)):
                return report
        if state['counter'] != plan['world_counter'] or state['pending'] or Path(state['package']) != world_dir / 'world.rup':
            raise ValueError('restored world promotion missing')
        proof = flow.read_json(world_dir / 'report.json')
        if not proof.get('receiver_reported_applied') or proof['status'] != 'EXACT-APPLIED-RECEIPT':
            raise ValueError('restored world receipt missing')
        report.update(world_done=True, status='APPLIED'); flow.save(directory / 'report.json', report)
        state['recovery_pending'] = None; flow.save(state_path, state)
        return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('prepare','restore'))
    p.add_argument('--state', type=Path, required=True)
    p.add_argument('--directory', type=Path, required=True)
    p.add_argument('--checked', type=Path)
    p.add_argument('--private', type=Path, required=True)
    p.add_argument('--dell-rebooted', action='store_true')
    a = p.parse_args(); directory = a.directory.resolve()
    result = prepare(a.state, a.checked, directory, a.private) if a.action == 'prepare' else restore(a.state, directory, a.private, a.dell_rebooted)
    print(result['status'])


if __name__ == '__main__':
    main()
