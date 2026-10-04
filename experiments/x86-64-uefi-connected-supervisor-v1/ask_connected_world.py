#!/usr/bin/env python3
"""Text -> bounded V3 edit -> checked signed world -> saved connected session."""
import argparse
import copy
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOCK_FD = None
V3 = ROOT.parent / 'x86-64-uefi-god-runtime-v3'
V2 = ROOT.parent / 'x86-64-uefi-god-runtime-v2'
sys.path[:0] = [str(V3), str(V2)]
from compile_world import compile_world as compile_v3_world
from package import decode_package as decode_v3_package, PackageError
from codex_world import propose_json
from llm_world import WORLD_SCHEMA, obj, strict_json, validate_schema
from prepare_file import bundle
from send_file import validate as validate_session
from world_check import check_world as check_v3_world


def city_module(name):
    import importlib
    directory = Path(__file__).resolve().parent.parent / 'x86-64-uefi-city-v1'
    if str(directory) not in sys.path: sys.path.insert(0, str(directory))
    return importlib.import_module(name)


def actors_module(name):
    import importlib
    directory = ROOT.parent / 'x86-64-uefi-city-v2'
    if str(directory) not in sys.path: sys.path.insert(0, str(directory))
    return importlib.import_module(name)


def actors_ready(state):
    if state.get('engine', {}).get('family') != 'reviewed-city-v2':
        raise ValueError('reviewed actor driver must be applied before animated city data')
    core = actors_module('scene5').ROOT / 'city_core.c'
    if state['engine'].get('actor_core_sha256') != sha(core.read_bytes()):
        raise ValueError('actor core differs from the applied native profile')


def compile_world(path, counter, private):
    world = read_json(path, 2 * 1024 * 1024)
    if world.get('schema_version') == 5:
        return actors_module('scene5').compile_scene(world, counter, private)
    if world.get('schema_version') == 4:
        return city_module('city_world').compile_city(world, counter, private)
    return compile_v3_world(path, counter, private)


def decode_package(packet, public):
    if packet[:5] == b'RUP5\x05':
        world, counter = actors_module('scene5').decode_scene(packet, public)
        return {'counter': counter, 'health_fault': False, 'world': world}
    if packet[:5] == b'RUP4\x04':
        world, counter = city_module('city_world').decode_city(packet, public)
        return {'counter': counter, 'health_fault': False, 'world': world}
    return decode_v3_package(packet, public)


def check_world(path, cache):
    if Path(path).read_bytes()[:5] == b'RUP5\x05':
        return actors_module('actors_check').check_city(path, Path(cache) / 'actors')
    if Path(path).read_bytes()[:5] == b'RUP4\x04':
        return city_module('check_city').check_city(path, Path(cache) / 'city')
    return check_v3_world(path, cache)


def city_ready(state):
    engine = state.get('engine', {})
    if engine.get('family') not in ('reviewed-city-v1','reviewed-city-v2'):
        raise ValueError('reviewed city driver must be applied before city data')
    core = city_module('city_world').ROOT / 'city_core.c'
    if engine.get('city_core_sha256') != sha(core.read_bytes()):
        raise ValueError('city core differs from the applied native profile')
    if engine.get('family') == 'reviewed-city-v2': actors_ready(state)
from delivery_status import parse_status, confirmed_prefix
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


@contextmanager
def state_lock(path):
    global LOCK_FD
    with (path.parent / 'state.lock').open('a') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise ValueError('another controller/sender still holds this state; wait for its bounded completion')
        LOCK_FD = lock.fileno()
        try: yield
        finally: LOCK_FD = None


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
    if world.get('schema_version') == 4: city_ready(state)
    if world.get('schema_version') == 5: actors_ready(state)
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
    return prepare_world(state_path, state, intent, world, proposal)


def prepare_world(state_path, state, intent, world, proposal):
    if state['pending'] or state.get('native_pending'): raise ValueError('pending delivery exists; resume SAME saved session first')
    current(state)
    if world.get('schema_version') == 5: actors_ready(state)
    elif world.get('schema_version') == 4: city_ready(state)
    elif world.get('schema_version') != 3: raise ValueError('candidate requires reviewed V3, city4 or actors5 data')
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


def pending_world(state):
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
    return directory, report, session, packet


def sender_step(directory, report, name, flags, quiet=False):
    """Persist attempt before radio; stream output into an archive even on interruption."""
    log = directory / f'{name}-{len(report["sender_steps"])}.log'
    entry = {'name': name, 'exit_code': None, 'log': str(log), 'log_sha256': None}
    report['sender_steps'].append(entry)
    report['status'] = 'QUERYING' if name == 'query' else 'SENDING-' + name.upper()
    save(directory / 'report.json', report)
    command = [sys.executable, '-u', str(ROOT / 'send_file.py'), str(directory / 'session.json'), *flags]
    env = os.environ.copy(); env.pop('RABBIT_CONNECTED_LOCK_FD', None)
    held = () if LOCK_FD is None else (LOCK_FD,)
    if held: env['RABBIT_CONNECTED_LOCK_FD'] = str(LOCK_FD)
    try:
        with log.open('w') as out:
            result = subprocess.run(command, stdout=out, stderr=subprocess.STDOUT, timeout=380,
                                    env=env, pass_fds=held)
        code = result.returncode
    except subprocess.TimeoutExpired:
        with log.open('a') as out: out.write('\nORCHESTRATOR TIMEOUT: outcome unknown; saved session retained\n')
        code = 1
    except OSError as error:
        with log.open('a') as out: out.write('\nLAUNCH FAILED: ' + str(error) + '\n')
        code = 1
    text = log.read_text()
    if not quiet: print(text, end='', flush=True)
    entry.update(exit_code=code, log_sha256=sha(text.encode()))
    save(directory / 'report.json', report)
    return code, text


def advance(state_path, state, directory, report, session):
    report['status'] = 'EXACT-APPLIED-RECEIPT'; report['receiver_reported_applied'] = True
    save(directory / 'report.json', report)
    state.update(counter=session['counter'], world=str(directory / 'world.json'),
                 package=str(directory / 'world.rup'), world_sha256=report['world_sha256'],
                 package_sha256=report['package_sha256'], pending=None)
    save(state_path, state)
    return 0


def deliver(state_path, state):
    directory, report, session, packet = pending_world(state)
    report['host_checks'] = check_world(directory / 'world.rup', state_path.parent / 'host-check')
    return deliver_session(directory, report, session,
                           lambda: advance(state_path, state, directory, report, session))


def deliver_session(directory, report, session, on_applied, initial_query_text=None):
    """Shared world/native transport; caller verifies authority, package and health first."""
    import base64
    # Finish a local crash between durable receipt and durable current-state promotion.
    if report.get('receiver_reported_applied') and report['status'] == 'EXACT-APPLIED-RECEIPT':
        return on_applied()
    length = len(base64.b64decode(session['stream_base64']))
    floor = report.get('confirmed_received', 0)
    attempted = False
    for step in report['sender_steps']:
        if step['name'] != 'query': attempted = True
        log = Path(step['log'])
        if log.exists():
            text = log.read_text()
            floor = max(floor, confirmed_prefix(text, length))
            if 'RECEIVER STAGING REGRESSED:' in text: report['receiver_loss_detected'] = True
    report['confirmed_received'] = floor
    if report.get('receiver_loss_detected'):
        report['status'] = 'RECOVERY-REQUIRED-RECEIVER-LOSS'; save(directory / 'report.json', report)
        print('Receiver loss detected; no replay, new nonce or counter. Inspect receiver state.'); return 1
    # At most two resumable transfer attempts. Every attempt starts with a read-only query.
    for attempt in range(2):
        # Dedicated boot recovery already queried under the SAME controller lock
        # immediately before activation. Reuse that result once, through the same
        # parser and state checks, instead of another connect/disconnect cycle.
        if attempt == 0 and initial_query_text is not None:
            code, text = 0, initial_query_text
        else:
            code, text = sender_step(directory, report, 'query', ['--query-only'])
        if code:
            report['status'] = 'DELIVERY-NOT-CONFIRMED'; save(directory / 'report.json', report); return 1
        try: observed = parse_status(text, session)
        except ValueError:
            report['status'] = 'INVALID-RECEIVER-STATUS'; save(directory / 'report.json', report); return 1
        report['last_receiver_status'] = observed
        outcome = observed['outcome']
        if outcome == 'applied': return on_applied()
        if outcome == 'rejected':
            report['status'] = 'EXACT-REJECTED-RECEIPT'; save(directory / 'report.json', report); return 2
        if outcome == 'pending':
            report['status'] = 'RECEIVER-APPLICATION-PENDING'; save(directory / 'report.json', report); return 1
        if outcome == 'staging' and observed['received'] >= floor:
            floor = observed['received']
        elif not attempted and (outcome == 'idle' or (outcome == 'foreign-final' and not observed['session_matches'])):
            pass  # First delivery only; do not erase a foreign active session.
        else:
            report['status'] = 'RECOVERY-REQUIRED-RECEIVER-LOSS' if outcome in ('staging', 'idle', 'foreign-final') else 'RECEIVER-STATE-BLOCKED'
            report['receiver_loss_detected'] = report['status'] == 'RECOVERY-REQUIRED-RECEIVER-LOSS'
            save(directory / 'report.json', report); print(report['status'] + ': no DATA or COMMIT'); return 1
        report['confirmed_received'] = floor; save(directory / 'report.json', report)
        steps = [] if floor == length else [('paced-stage', ['--stage-only-bytes', str(length - 1), '--data-delay-ms', '50'])]
        steps.append(('commit', []))
        for name, flags in steps:
            code, text = sender_step(directory, report, name,
                                     ['--send', '--chunk-bytes', '100', '--minimum-received', str(floor), *flags])
            attempted = True
            floor = max(floor, confirmed_prefix(text, length)); report['confirmed_received'] = floor
            if 'RECEIVER STAGING REGRESSED:' in text:
                report['receiver_loss_detected'] = True
                report['status'] = 'RECOVERY-REQUIRED-RECEIVER-LOSS'; save(directory / 'report.json', report); return 1
            if code == 0 and 'FILE APPLIED RECEIPT (NOT ATTESTATION): exact SHA256/session/counter matched' in text:
                return on_applied()
            if code == 2 and 'FILE REJECTED RECEIPT (NOT ATTESTATION): exact SHA256/session/counter matched' in text:
                report['status'] = 'EXACT-REJECTED-RECEIPT'; save(directory / 'report.json', report); return 2
            if code or name == 'commit' or 'STAGED-NOT-APPLIED:' not in text or floor != length:
                report['status'] = 'DELIVERY-NOT-CONFIRMED'; save(directory / 'report.json', report); break
            save(directory / 'report.json', report)
        # Recover a lost COMMIT response by querying the same receipt, without inventing success.
    report['status'] = 'DELIVERY-NOT-CONFIRMED'; save(directory / 'report.json', report)
    return 1


def status_view(state_path, state, query=False):
    world = current(state)
    view = {'schema_version': 1, 'current_world': {'id': world['world_id'], 'counter': state['counter'],
            'sha256': state['world_sha256'], 'package_sha256': state['package_sha256']},
            'authority': state['authority'], 'pending': None,
            'capabilities': {'text_objects_programs': True, 'checked_asset_candidate': True,
                             'automatic_native_upgrade': False, 'voice': False},
            'receiver': None, 'device_attestation': False}
    if state['pending']:
        directory, report, session, packet = pending_world(state)
        view['pending'] = {'status': report['status'], 'counter': session['counter'],
                           'intent': (directory / 'intent.txt').read_text(),
                           'confirmed_received': report.get('confirmed_received', 0),
                           'stream_bytes': len(packet) + 32,
                           'same_session_resume_required': True}
    else:
        directory = Path(state['world']).parent
        session_file = directory / 'session.json'
        if session_file.exists():
            session = validate_session(read_json(session_file))
            import base64
            if base64.b64decode(session['stream_base64'])[32:] != Path(state['package']).read_bytes() or session['counter'] != state['counter']:
                raise ValueError('current session/package differs; no radio')
        else:
            session = bundle(Path(state['package']).read_bytes(), 1, state['counter'], b'\0' * 8)
    if query:
        # Diagnostics have their own archive; no state/report promotion and no write to Dell.
        archive = Path(tempfile.mkdtemp(prefix='status-', dir=state_path.parent))
        save(archive / 'session.json', session)
        report = {'sender_steps': []}
        code, text = sender_step(archive, report, 'query', ['--query-only'], quiet=True)
        view['query_archive'] = str(archive)
        view['receiver'] = parse_status(text, session) if code == 0 else {'outcome': 'unreachable', 'exit_code': code}
    return view


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('intent', nargs='?'); p.add_argument('--state', type=Path, default=ROOT / 'runs/text-world/state.json')
    p.add_argument('--initialize', action='store_true'); p.add_argument('--world', type=Path); p.add_argument('--package', type=Path)
    p.add_argument('--installed-report', type=Path)
    candidate = p.add_mutually_exclusive_group()
    candidate.add_argument('--candidate', type=Path)
    candidate.add_argument('--world-candidate', type=Path, help='complete V3 asset world; same deterministic/signature/health gates')
    p.add_argument('--send', action='store_true'); p.add_argument('--resume', action='store_true'); p.add_argument('--discard', action='store_true', help='discard ONLY a prepared draft that has never started sending')
    p.add_argument('--status', action='store_true', help='show current world, pending operation and supported routes')
    p.add_argument('--query', action='store_true', help='with --status, read Dell state without sending or promoting a world')
    a = p.parse_args(); a.state = a.state.resolve(); a.state.parent.mkdir(parents=True, exist_ok=True)
    with state_lock(a.state):
        if a.query and not a.status: p.error('--query requires --status')
        if a.status and (a.initialize or a.world or a.package or a.installed_report or a.intent or a.send or a.resume or a.discard or a.candidate or a.world_candidate):
            p.error('--status accepts only --state and optional --query')
        if a.initialize:
            if not a.world or not a.package or not a.installed_report or a.intent or a.send or a.resume or a.discard or a.candidate or a.world_candidate:
                p.error('initialize requires only current --world, --package and --installed-report')
            initialize(a.state, a.world, a.package, a.installed_report); print('CURRENT WORLD SAVED; no Bluetooth or owner key access'); return 0
        if a.world or a.package or a.installed_report: p.error('--world/--package are initialization-only')
        state = read_json(a.state)
        if a.status:
            print(json.dumps(status_view(a.state, state, a.query), ensure_ascii=False, indent=2)); return 0
        if a.discard:
            if a.send or a.resume or a.intent or a.candidate or a.world_candidate or not state['pending']:
                p.error('--discard requires only an existing never-sent pending draft')
            directory = Path(state['pending']); report = read_json(directory / 'report.json')
            if report['status'] != 'CHECKED-NOT-SENT' or report['sender_steps']:
                raise ValueError('delivery may have started; cannot discard or change nonce/counter')
            report['status'] = 'DISCARDED-NEVER-SENT'; save(directory / 'report.json', report)
            state['pending'] = None; save(a.state, state)
            print('UNSENT DRAFT DISCARDED; current world unchanged; archive preserved'); return 0
        if a.resume:
            if not a.send or a.intent or a.candidate or a.world_candidate: p.error('--resume requires --send and no new intent/candidate')
            return deliver(a.state, state)
        if not a.intent or not a.intent.strip() or len(a.intent) > 4000: p.error('intent must contain 1..4000 characters')
        if state['pending']: raise ValueError('pending session exists; use --resume --send, no new counter/nonce')
        base = current(state)
        if a.world_candidate:
            world = read_json(a.world_candidate, 2 * 1024 * 1024)
            source = {'schema_version': 1, 'kind': 'generated-asset-world',
                      'base_world_sha256': state['world_sha256'],
                      'candidate_world_sha256': sha(canonical(world))}
            directory, _ = prepare_world(a.state, state, a.intent, world, source)
            print('CHECKED SAVED ASSET WORLD/SESSION: ' + str(directory), flush=True)
            return deliver(a.state, state) if a.send else 0
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
