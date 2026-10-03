#!/usr/bin/env python3
"""Text -> bounded V3 edit -> checked signed world -> saved connected session."""
import argparse
import copy
import fcntl
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V3 = ROOT.parent / 'x86-64-uefi-god-runtime-v3'
V2 = ROOT.parent / 'x86-64-uefi-god-runtime-v2'
sys.path[:0] = [str(V3), str(V2)]
from compile_world import compile_world
from package import decode_package, PackageError
from codex_world import propose_json
from llm_world import WORLD_SCHEMA, obj, strict_json, validate_schema
from prepare_file import bundle
from send_file import validate as validate_session
from world_check import check_world
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

# Existing installed data-world authority, PUBLIC development key; not owner-native.
CREATOR = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
PUBLIC = CREATOR.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
SCHEMA = obj({
    'status': {'type': 'string', 'enum': ['ready', 'unsupported']},
    'explanation': {'type': 'string', 'maxLength': 1200},
    'base_world_sha256': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'},
    'objects': {'anyOf': [WORLD_SCHEMA['properties']['objects'], {'type': 'null'}]},
    'programs': {'anyOf': [WORLD_SCHEMA['properties']['programs'], {'type': 'null'}]},
})
INSTRUCTIONS = """Propose a small data-only edit of the supplied current Rabbit world.
Return all resulting objects and programs, preserving unrelated values. Existing
sprites, palette, geometry, frame bytes and world identity cannot change. You may
change velocity, placement, straight-line VM behavior, animation period, and add
objects referencing existing sprites. New artwork, a new mouse asset when absent,
background color (fixed121826), voice, native code and new VM instructions are
unsupported: return status unsupported and null objects/programs. Never pretend
an existing cat sprite is a new mouse. Copy base_world_sha256 exactly.
VM: 0 END; 1 MOVE; 2 BOUNCE; 3 target speed CHASE; 4 target speed FLEE;
5 period ANIMATE; 6 target impulse COLLIDE. Targets must exist; magnitudes1..8,
period1..255. CHASE/FLEE set velocity: follow with MOVE and BOUNCE. At most16
instructions and32 bytes, one END at the end. Keep ids stable and unique. Explain
the proposed visible change briefly in Russian. Do not use tools or emit code.
"""


def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def read_json(path, limit=400000):
    path = Path(path)
    if path.stat().st_size > limit: raise ValueError('saved JSON exceeds input budget')
    # Same duplicate/non-finite rejection as the compiler, with a larger sprite budget.
    from compile_world import unique_pairs
    return json.loads(path.read_text(), object_pairs_hook=unique_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('non-finite JSON')))


def save(path, value):
    path = Path(path)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as out:
        json.dump(value, out, ensure_ascii=False, indent=2); out.write('\n'); name = out.name
    Path(name).replace(path)


def parse_edit(text):
    value = strict_json(text); validate_schema(value, SCHEMA)
    ready = value['status'] == 'ready'
    if ready != (value['objects'] is not None) or ready != (value['programs'] is not None):
        raise ValueError('edit status and data disagree')
    return value


def apply_edit(base, proposal):
    validate_schema(proposal, SCHEMA)
    if proposal['base_world_sha256'] != sha(canonical(base)):
        raise ValueError('candidate refers to a different current world')
    if proposal['status'] != 'ready': raise ValueError('unsupported intent; nothing prepared or sent')
    result = copy.deepcopy(base)
    result['objects'] = copy.deepcopy(proposal['objects'])
    result['programs'] = copy.deepcopy(proposal['programs'])
    if result == base: raise ValueError('candidate makes no world change')
    return result


def current(state):
    if sha((V3 / 'runtime_core.c').read_bytes()) != state['runtime_core_sha256']:
        raise ValueError('runtime source differs from saved installed gate')
    world = read_json(state['world'], 2 * 1024 * 1024)
    packet = Path(state['package']).read_bytes()
    if sha(canonical(world)) != state['world_sha256'] or sha(packet) != state['package_sha256']:
        raise ValueError('saved current world/package changed')
    if compile_world(Path(state['world']), state['counter'], CREATOR) != packet:
        raise ValueError('current JSON does not reconstruct exact signed world')
    decode_package(packet, PUBLIC)
    return world


def initialize(state_path, world_path, package_path, installed_report):
    if state_path.exists(): raise ValueError('state exists; preserve current world and pending session')
    gate = read_json(installed_report)
    runtime_sha = sha((V3 / 'runtime_core.c').read_bytes())
    if gate.get('status') != 'OWNER-OBSERVED-EXACT-MAC-QEMU-NO-DEVICE' or gate['source_hashes'].get('experiments/x86-64-uefi-god-runtime-v3/runtime_core.c') != runtime_sha:
        raise ValueError('installed runtime gate/source mismatch')
    world = read_json(world_path, 2 * 1024 * 1024)
    packet = Path(package_path).read_bytes(); decoded = decode_package(packet, PUBLIC)
    if world.get('schema_version') != 3: raise ValueError('this path requires a V3 current world')
    if compile_world(Path(world_path), decoded['counter'], CREATOR) != packet:
        raise ValueError('bootstrap JSON/package do not match exactly')
    directory = Path(tempfile.mkdtemp(prefix='current-', dir=state_path.parent))
    save(directory / 'world.json', world); (directory / 'world.rup').write_bytes(packet)
    state = {'schema_version': 1, 'counter': decoded['counter'],
             'world': str(directory / 'world.json'), 'package': str(directory / 'world.rup'),
             'world_sha256': sha(canonical(world)), 'package_sha256': sha(packet),
             'authority': 'installed-public-development-world-creator-NOT-owner-native',
             'runtime_core_sha256': runtime_sha, 'installed_report_sha256': sha(Path(installed_report).read_bytes()),
             'pending': None, 'bootstrap_basis': 'operator-supplied current package; not device attestation'}
    save(state_path, state)
    return state


def prepare(state_path, state, intent, proposal):
    if state['pending']: raise ValueError('pending delivery exists; resume SAME saved session first')
    base = current(state); world = apply_edit(base, proposal)
    if state['counter'] >= 0xffffffff: raise ValueError('world counter exhausted')
    directory = Path(tempfile.mkdtemp(prefix='edit-', dir=state_path.parent))
    save(directory / 'proposal.json', proposal); (directory / 'intent.txt').write_text(intent)
    save(directory / 'world.json', world)
    packet = compile_world(directory / 'world.json', state['counter'] + 1, CREATOR)
    decoded = decode_package(packet, PUBLIC)
    if decoded.get('health_fault'): raise ValueError('health-fault fixtures forbidden')
    (directory / 'world.rup').write_bytes(packet)
    checks = check_world(directory / 'world.rup', state_path.parent / 'host-check')
    session = bundle(packet, 1, state['counter'] + 1); save(directory / 'session.json', session)
    report = {'schema_version': 1, 'status': 'CHECKED-NOT-SENT', 'counter': session['counter'],
              'base_world_sha256': state['world_sha256'], 'world_sha256': sha(canonical(world)),
              'package_sha256': sha(packet), 'session_sha256': sha((directory / 'session.json').read_bytes()),
              'authority': state['authority'], 'host_checks': checks,
              'physical_execution_verified': False, 'receiver_reported_applied': False,
              'sender_steps': []}
    save(directory / 'report.json', report)
    state['pending'] = str(directory); save(state_path, state)
    return directory, report


def deliver(state_path, state):
    if not state['pending']: raise ValueError('no saved pending session')
    directory = Path(state['pending']); report = read_json(directory / 'report.json')
    if report['status'] == 'DISCARDED-NEVER-SENT':
        raise ValueError('draft discarded; no radio')
    session_path = directory / 'session.json'
    if sha(session_path.read_bytes()) != report['session_sha256']:
        raise ValueError('saved session changed; no radio')
    session = validate_session(read_json(session_path))
    import base64
    packet = base64.b64decode(session['stream_base64'])[32:]
    world = read_json(directory / 'world.json', 2 * 1024 * 1024)
    if (session['kind'] != 1 or session['counter'] != report['counter'] or session['counter'] != state['counter'] + 1 or
        (directory / 'world.rup').read_bytes() != packet or
        report['base_world_sha256'] != state['world_sha256'] or
        sha(packet) != report['package_sha256'] or
        sha(canonical(world)) != report['world_sha256'] or
        compile_world(directory / 'world.json', session['counter'], CREATOR) != packet):
        raise ValueError('pending world/package/counter binding differs; no radio')
    current(state)
    report['host_checks'] = check_world(directory / 'world.rup', state_path.parent / 'host-check')
    # Stage the whole stream with pacing, stop BEFORE COMMIT, then query/commit SAME session.
    steps = [('paced-stage', ['--stage-only-bytes', str(len(packet) + 31), '--data-delay-ms', '50']),
             ('commit', [])]
    for name, flags in steps:
        report['status'] = 'SENDING-' + name.upper(); save(directory / 'report.json', report)
        result = subprocess.run([sys.executable, '-u', str(ROOT / 'send_file.py'), str(session_path),
                                 '--send', '--chunk-bytes', '100', *flags], text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=380)
        text = result.stdout; log = directory / f'{name}-{len(report["sender_steps"])}.log'
        log.write_text(text); print(text, end='', flush=True)
        report['sender_steps'].append({'name': name, 'exit_code': result.returncode,
                                      'log': str(log), 'log_sha256': sha(text.encode())})
        if result.returncode:
            report['status'] = 'DELIVERY-NOT-CONFIRMED'; save(directory / 'report.json', report)
            return result.returncode if result.returncode > 0 else 1
        if name == 'commit' and 'FILE APPLIED RECEIPT (NOT ATTESTATION): exact SHA256/session/counter matched' not in text:
            report['status'] = 'DELIVERY-NOT-CONFIRMED'; save(directory / 'report.json', report)
            return 1
    report['status'] = 'EXACT-APPLIED-RECEIPT'; report['receiver_reported_applied'] = True
    save(directory / 'report.json', report)
    state.update(counter=session['counter'], world=str(directory / 'world.json'),
                 package=str(directory / 'world.rup'), world_sha256=report['world_sha256'],
                 package_sha256=report['package_sha256'], pending=None)
    save(state_path, state)
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('intent', nargs='?'); p.add_argument('--state', type=Path, default=ROOT / 'runs/text-world/state.json')
    p.add_argument('--initialize', action='store_true'); p.add_argument('--world', type=Path); p.add_argument('--package', type=Path)
    p.add_argument('--installed-report', type=Path); p.add_argument('--candidate', type=Path); p.add_argument('--send', action='store_true'); p.add_argument('--resume', action='store_true'); p.add_argument('--discard', action='store_true', help='discard ONLY a prepared draft that has never started sending')
    a = p.parse_args(); a.state = a.state.resolve(); a.state.parent.mkdir(parents=True, exist_ok=True)
    with (a.state.parent / 'state.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if a.initialize:
            if not a.world or not a.package or not a.installed_report or a.intent or a.send or a.resume or a.discard or a.candidate:
                p.error('initialize requires only current --world, --package and --installed-report')
            initialize(a.state, a.world, a.package, a.installed_report); print('CURRENT WORLD SAVED; no Bluetooth or owner key access'); return 0
        if a.world or a.package or a.installed_report: p.error('--world/--package are initialization-only')
        state = read_json(a.state)
        if a.discard:
            if a.send or a.resume or a.intent or a.candidate or not state['pending']:
                p.error('--discard requires only an existing never-sent pending draft')
            directory = Path(state['pending']); report = read_json(directory / 'report.json')
            if report['status'] != 'CHECKED-NOT-SENT' or report['sender_steps']:
                raise ValueError('delivery may have started; cannot discard or change nonce/counter')
            report['status'] = 'DISCARDED-NEVER-SENT'; save(directory / 'report.json', report)
            state['pending'] = None; save(a.state, state)
            print('UNSENT DRAFT DISCARDED; current world unchanged; archive preserved'); return 0
        if a.resume:
            if not a.send or a.intent or a.candidate: p.error('--resume requires --send and no new intent/candidate')
            return deliver(a.state, state)
        if not a.intent or not a.intent.strip() or len(a.intent) > 4000: p.error('intent must contain 1..4000 characters')
        if state['pending']: raise ValueError('pending session exists; use --resume --send, no new counter/nonce')
        base = current(state)
        if a.candidate:
            if a.candidate.stat().st_size > 65536: raise ValueError('candidate exceeds input budget')
            proposal = parse_edit(a.candidate.read_text())
        else:
            context = {'base_world_sha256': state['world_sha256'], 'objects': base['objects'],
                       'programs': base['programs'], 'sprites': [{k: v for k, v in s.items() if k != 'frames'} for s in base['sprites']]}
            proposal, _ = propose_json(a.intent, context, schema=SCHEMA, instructions=INSTRUCTIONS, parser=parse_edit)
        print(''.join(c if c.isprintable() else ' ' for c in proposal['explanation']), flush=True)
        if proposal['status'] == 'unsupported': print('UNSUPPORTED: no world prepared or sent'); return 2
        directory, _ = prepare(a.state, state, a.intent, proposal)
        print('CHECKED SAVED WORLD/SESSION: ' + str(directory), flush=True)
        return deliver(a.state, state) if a.send else 0


if __name__ == '__main__':
    try: sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('FAIL: ' + str(error), file=sys.stderr); sys.exit(1)
