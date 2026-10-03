"""Reviewed background engine family; no arbitrary LLM native code is executed."""
import base64
import json
import re
import shutil
import subprocess
import tempfile
import sys
from pathlib import Path
import ask_connected_world as flow
sys.path.insert(0, str(flow.ROOT))  # Connected builder, not the V3 experiment's same-named helper.
from build_image import ROOT, OLD, LINK, NATIVE, V3, old, prepare, compile_efi, digest
from release import pack, verify
from owner_key import load_private
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

DEFAULT_GATE = ROOT / 'runs/owner-gate-s0bxi9d8/report.json'


def gate_check(gate_path):
    gate = flow.read_json(gate_path)
    if gate.get('status') != 'OWNER-OBSERVED-EXACT-MAC-QEMU-NO-DEVICE' or not gate.get('qemu_verified') or gate.get('test_key_only') is not False:
        raise ValueError('installed owner gate required for native route')
    if digest((gate_path.parent / 'connected-supervisor.img').read_bytes()).hex() != gate['image_sha256']:
        raise ValueError('installed image binding changed')
    sources = [ROOT / 'driver.c', ROOT / 'loop.c', ROOT / 'connected_abi.h', ROOT / 'target.json', ROOT / 'build_image.py',
               OLD / 'supervisor.c', OLD / 'scene_module.c', OLD / 'scene_abi.h', OLD / 'build_image.py', V3 / 'runtime_core.c']
    sources += [LINK / name for name in ('usb_port.c', 'usb_port.h', 'hci_link.c', 'hci_link.h', 'gatt_core.c', 'gatt_core.h', 'file_core.c', 'file_core.h')]
    sources += [NATIVE / name for name in ('abi.h', 'verify_core.c', 'verify_core.h', 'sha256.c', 'sha256.h')]
    for source in sources:
        if gate['source_hashes'].get(str(source.relative_to(ROOT.parents[1]))) != digest(source.read_bytes()).hex():
            raise ValueError('installed production source changed: ' + source.name)
    return gate


def initialize_engine(state, gate_path=DEFAULT_GATE):
    gate = gate_check(gate_path)
    return {'schema_version': 1, 'family': 'reviewed-background-v1', 'background': '121826',
            'native_counter': 3, 'payload_sha256': gate['module_hashes']['1'],
            'installed_gate': str(gate_path), 'installed_gate_sha256': flow.sha(gate_path.read_bytes()),
            'basis': 'owner-observed driver1 retained after exact rejected native3; same physical boot required'}


def sources(directory, color):
    if not re.fullmatch('[0-9a-f]{6}', color): raise ValueError('invalid background RGB')
    runtime = (V3 / 'runtime_core.c').read_text()
    scene = (OLD / 'scene_module.c').read_text()
    if runtime.count('fill(0x121826)') != 2 or scene.count('fill(0x121826)') != 1:
        raise ValueError('reviewed background replacement anchors changed')
    (directory / 'runtime_core.c').write_text(runtime.replace('fill(0x121826)', f'fill(0x{color})'))
    (directory / 'scene_module.c').write_text(scene.replace('fill(0x121826)', f'fill(0x{color})'))
    shutil.copyfile(ROOT / 'driver.c', directory / 'driver.c')


def compile_background(directory, color, crypto):
    sources(directory, color)
    return compile_efi(directory, 'background', [directory / 'driver.c', LINK / 'usb_port.c', LINK / 'hci_link.c',
        LINK / 'gatt_core.c', LINK / 'file_core.c', NATIVE / 'sha256.c', *crypto],
        driver=True, definitions=('SCENE_REVISION=1',))


def qemu_gate(directory, payload, color):
    """Execute the exact candidate with actual UEFI LoadImage/StartImage, mock radio."""
    from run_qemu import firmware
    code, variables = firmware()
    fixture = directory / 'qemu'; fixture.mkdir()
    key = Ed25519PrivateKey.from_private_bytes(bytes(range(32, 64)))
    public = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    target, modules, crypto = prepare(fixture, public)
    world = flow.compile_world(V3 / 'worlds/ginger-cat-walk-v1.json', 2, flow.CREATOR)
    def release(p, base, counter):
        return pack(p, private=key, target=target, base_runtime=digest(base), world=world, counter=counter)
    releases = {'world': world, 'a': release(payload, modules[1], 1),
                'b': release(modules[1], payload, 2), 'bad': release(modules[3], modules[1], 3)}
    tampered = bytearray(release(payload, modules[1], 4)); tampered[-1] ^= 1
    releases['tampered'] = bytes(tampered)
    releases['hung'] = release(modules[3], modules[1], 4)  # Referenced but never exercised by this family gate.
    header = ''.join(old.c_bytes(name + '_stream', digest(data) + data) for name, data in releases.items())
    header += old.c_bytes('base_hash', digest(modules[1])) + old.c_bytes('a_hash', digest(payload))
    (fixture / 'test_data.h').write_text(header)
    from build_image import supervisor_source
    (fixture / 'supervisor.c').write_text(supervisor_source() + '\nuint32_t rabbit_test_background(void){return pixels[0];}\n')
    test = (ROOT / 'qemu_test.c').read_text()
    test = test.replace('static int test(SystemTable*st){', 'uint32_t rabbit_test_background(void);\nstatic int test(SystemTable*st){')
    marker = 'say("CONNECTED DRIVER A COMMITTED VIA MOCK USB ACL ATT; OLD CONNECTION CONFIRMED CLOSED; RECEIPT RETAINED");'
    if test.count(marker) != 1: raise ValueError('QEMU gate anchor changed')
    test = test.replace(marker, f'if(rabbit_scene_tick(st)||rabbit_test_background()!=0x{color})return 1;\n ' + marker)
    (fixture / 'test.c').write_text(test)
    efi = compile_efi(fixture, 'fixture', [fixture / 'test.c', fixture / 'supervisor.c', fixture / 'native_verify.c',
        NATIVE / 'transport_core.c', NATIVE / 'sha256.c', LINK / 'file_core.c', *crypto], definitions=('RABBIT_INTEGRATION_TEST',))
    image = old.load('background_media', ROOT.parent / 'x86-64-uefi-v0/build_image.py').build_image(efi)
    (fixture / 'fixture.img').write_bytes(image); shutil.copyfile(variables, fixture / 'vars.fd')
    observer = old.load('background_qmp', NATIVE / 'run_qemu.py')
    with tempfile.TemporaryDirectory(prefix='rabbit-engine-qmp-', dir='/tmp') as sockets:
        command = [shutil.which('qemu-system-x86_64'), '-machine', 'q35', '-m', '256M', '-nic', 'none', '-display', 'none',
                   '-qmp', f'unix:{sockets}/qmp.sock,server=on,wait=off', '-debugcon', f'file:{fixture}/debug.log',
                   '-drive', f'if=pflash,format=raw,unit=0,readonly=on,file={code}',
                   '-drive', f'if=pflash,format=raw,unit=1,file={fixture}/vars.fd',
                   '-drive', f'file={fixture}/fixture.img,format=raw,snapshot=on',
                   '-device', 'qemu-xhci,id=rabbit-xhci', '-device', 'usb-kbd,bus=rabbit-xhci.0']
        with (fixture / 'stderr.log').open('w') as err:
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=err)
            monitor = None
            try:
                monitor = observer.QMP(Path(sockets) / 'qmp.sock', process)
                observer.wait_for(fixture / 'debug.log', 'CONNECTED BOOTSTRAP FALLBACK ACTIVE', process)
                monitor.key('t')
                observer.wait_for(fixture / 'debug.log', 'CONNECTED NATIVE INTEGRATION PASS', process, timeout=45)
                snapshot = (fixture / 'debug.log').read_bytes()
            finally:
                if monitor: monitor.close()
                process.terminate()
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired: process.kill(); process.wait()
    (fixture / 'observed.log').write_bytes(snapshot)
    result = {'status': 'EXACT-CANDIDATE-QEMU-LOAD-SWAP-RESTORE-REJECTION-PASS', 'payload_sha256': digest(payload).hex(),
              'background': color, 'observed_log_sha256': digest(snapshot).hex(), 'physical_verified': False,
              'bluetooth_verified': False, 'controller': 'mock USB only', 'fixture_image_sha256': digest(image).hex()}
    flow.save(fixture / 'report.json', result)
    return result


def prepare_engine(state_path, state, color, private_path):
    if state.get('native_pending') or state['pending']: raise ValueError('existing operation must finish first')
    engine = state['engine']; gate_path = Path(engine['installed_gate']); gate = gate_check(gate_path)
    if flow.sha(gate_path.read_bytes()) != engine['installed_gate_sha256']: raise ValueError('engine gate changed')
    flow.current(state)
    directory = Path(tempfile.mkdtemp(prefix='engine-', dir=state_path.parent))
    owner = Path(private_path).with_suffix('.pub')
    public = owner.read_bytes()
    if flow.sha(public) != gate['owner_public_sha256']: raise ValueError('owner public identity differs from installation')
    _, _, crypto = prepare(directory, public)
    payload = compile_background(directory, color, crypto)
    if compile_background(directory, color, crypto) != payload: raise ValueError('engine build nondeterministic')
    (directory / 'payload.efi').write_bytes(payload)
    # Current data health and exact native LoadImage/swap/rollback gates precede owner signing.
    checks = flow.check_world(Path(state['package']), state_path.parent / 'host-check')
    qemu = qemu_gate(directory, payload, color)
    world = Path(state['package']).read_bytes()
    counter = engine['native_counter'] + 1
    private = load_private(private_path)
    if private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw) != public: raise ValueError('owner key identity mismatch')
    data = pack(payload, private=private, target=bytes.fromhex(gate['target_sha256']),
                base_runtime=bytes.fromhex(engine['payload_sha256']), world=world, counter=counter)
    verify(data, target=bytes.fromhex(gate['target_sha256']), owner=public, base_runtime=bytes.fromhex(engine['payload_sha256']),
           world=world, counter=engine['native_counter'])
    (directory / 'native.rrt').write_bytes(data)
    session = flow.bundle(data, 2, counter); flow.save(directory / 'session.json', session)
    report = {'schema_version': 1, 'status': 'CHECKED-NOT-SENT', 'kind': 'native-background', 'counter': counter,
              'background': color, 'base_runtime_sha256': engine['payload_sha256'],
              'base_world_sha256': state['world_sha256'], 'world_package_sha256': state['package_sha256'],
              'payload_sha256': flow.sha(payload), 'package_sha256': flow.sha(data),
              'session_sha256': flow.sha((directory / 'session.json').read_bytes()),
              'host_checks': checks, 'qemu_gate': qemu, 'receiver_reported_applied': False, 'sender_steps': []}
    flow.save(directory / 'report.json', report)
    state['native_pending'] = str(directory); flow.save(state_path, state)
    return directory


def deliver_engine(state_path, state, private_path):
    directory = Path(state['native_pending']); report = flow.read_json(directory / 'report.json')
    engine = state['engine']; gate = gate_check(Path(engine['installed_gate']))
    session_path = directory / 'session.json'
    if flow.sha(session_path.read_bytes()) != report['session_sha256']: raise ValueError('native session changed')
    session = flow.validate_session(flow.read_json(session_path))
    data = (directory / 'native.rrt').read_bytes(); payload = (directory / 'payload.efi').read_bytes()
    if (session['kind'] != 2 or session['counter'] != engine['native_counter'] + 1 or
        base64.b64decode(session['stream_base64'])[32:] != data or flow.sha(data) != report['package_sha256'] or
        flow.sha(payload) != report['payload_sha256'] or report['base_runtime_sha256'] != engine['payload_sha256'] or
        state['world_sha256'] != report['base_world_sha256'] or state['package_sha256'] != report['world_package_sha256'] or
        report['qemu_gate']['payload_sha256'] != flow.sha(payload) or
        report['qemu_gate']['status'] != 'EXACT-CANDIDATE-QEMU-LOAD-SWAP-RESTORE-REJECTION-PASS'):
        raise ValueError('native candidate/base/gate binding changed; no radio')
    candidate = verify(data, target=bytes.fromhex(gate['target_sha256']), owner=Path(private_path).with_suffix('.pub').read_bytes(),
                       base_runtime=bytes.fromhex(engine['payload_sha256']), world=Path(state['package']).read_bytes(), counter=engine['native_counter'])
    if candidate.payload != payload or candidate.counter != report['counter'] or report['background'] != report['qemu_gate']['background']:
        raise ValueError('native signed payload/effect differs from checked candidate')
    log = directory / 'qemu/observed.log'
    if flow.sha(log.read_bytes()) != report['qemu_gate']['observed_log_sha256']:
        raise ValueError('native QEMU evidence changed')
    flow.current(state)
    def applied():
        report.update(status='EXACT-APPLIED-RECEIPT', receiver_reported_applied=True)
        flow.save(directory / 'report.json', report)
        state['engine'].update(background=report['background'], native_counter=report['counter'], payload_sha256=report['payload_sha256'],
                               last_release_report=str(directory / 'report.json'),
                               basis='exact correlated native applied receipt; not authenticated device attestation')
        state['native_pending'] = None; flow.save(state_path, state); return 0
    result = flow.deliver_session(directory, report, session, applied)
    if result == 2:
        state['engine']['native_counter'] = report['counter']
        state['native_pending'] = None; flow.save(state_path, state)
    return result
