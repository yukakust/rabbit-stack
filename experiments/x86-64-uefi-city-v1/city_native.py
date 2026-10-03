"""Explicit city profile activation; exact gates precede local owner signing."""
import base64
import tempfile
from pathlib import Path
import build_city
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
engine=build_city.engine
flow=engine.flow
ROOT=Path(__file__).resolve().parent
PROFILE_FILES=('city_core.c','city_core.h','city_display.c','build_city.py','city_gate.py')

def source_hashes():
    return {name:flow.sha((ROOT/name).read_bytes()) for name in PROFILE_FILES}

def gates(directory,payload):
    gate=flow.read_json(directory/'city-qemu/report.json')
    if gate['status']!='EXACT-CITY-QEMU-LOAD-FULLSCREEN-DATA-RESTORE-REJECTION-PASS' or gate['payload_sha256']!=flow.sha(payload):
        raise ValueError('exact city UEFI gate required')
    if flow.sha((directory/'city-qemu/observed.log').read_bytes())!=gate['observed_log_sha256']:
        raise ValueError('city UEFI evidence changed')
    return gate

def prepare_city(state_path,state,checked_directory,private_path):
    if state['pending'] or state.get('native_pending'):raise ValueError('pending operation must finish first')
    flow.current(state)
    installed=engine.gate_check(Path(state['engine']['installed_gate']))
    if flow.sha(Path(state['engine']['installed_gate']).read_bytes())!=state['engine']['installed_gate_sha256']:
        raise ValueError('installed owner gate changed')
    checked_directory=Path(checked_directory);payload=(checked_directory/'payload.efi').read_bytes()
    gate=gates(checked_directory,payload)
    public=Path(private_path).with_suffix('.pub').read_bytes()
    if flow.sha(public)!=installed['owner_public_sha256']:raise ValueError('owner identity differs')
    # Rebuild now from current sources; no stale gate can approve changed code.
    directory=Path(tempfile.mkdtemp(prefix='city-native-',dir=Path(state_path).parent))
    _,_,crypto=engine.prepare(directory,public)
    if build_city.compile_city_driver(directory,crypto)!=payload or build_city.compile_city_driver(directory,crypto)!=payload:
        raise ValueError('current city sources differ from exact gated payload')
    (directory/'payload.efi').write_bytes(payload)
    checks=flow.check_world(Path(state['package']),Path(state_path).parent/'host-check')
    counter=state['engine']['native_counter']+1;world=Path(state['package']).read_bytes()
    private=engine.load_private(private_path)
    if private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)!=public:raise ValueError('owner key mismatch')
    packet=engine.pack(payload,private=private,target=bytes.fromhex(installed['target_sha256']),
                       base_runtime=bytes.fromhex(state['engine']['payload_sha256']),world=world,counter=counter)
    engine.verify(packet,target=bytes.fromhex(installed['target_sha256']),owner=public,
                  base_runtime=bytes.fromhex(state['engine']['payload_sha256']),world=world,counter=state['engine']['native_counter'])
    (directory/'native.rrt').write_bytes(packet)
    session=flow.bundle(packet,2,counter);flow.save(directory/'session.json',session)
    report={'schema_version':1,'kind':'native-city','status':'CHECKED-NOT-SENT','counter':counter,
            'base_runtime_sha256':state['engine']['payload_sha256'],'base_world_sha256':state['world_sha256'],
            'world_package_sha256':state['package_sha256'],'payload_sha256':flow.sha(payload),
            'package_sha256':flow.sha(packet),'session_sha256':flow.sha((directory/'session.json').read_bytes()),
            'qemu_gate':gate,'checked_directory':str(checked_directory),'profile_sources':source_hashes(),
            'host_checks':checks,'sender_steps':[],'receiver_reported_applied':False}
    flow.save(directory/'report.json',report);state['native_pending']=str(directory);flow.save(state_path,state)
    return directory

def deliver_city(state_path,state,private_path):
    directory=Path(state['native_pending']);report=flow.read_json(directory/'report.json')
    installed=engine.gate_check(Path(state['engine']['installed_gate']))
    packet=(directory/'native.rrt').read_bytes();payload=(directory/'payload.efi').read_bytes()
    session=flow.validate_session(flow.read_json(directory/'session.json'))
    if (report['kind']!='native-city' or report['profile_sources']!=source_hashes() or
        report['qemu_gate']!=gates(Path(report['checked_directory']),payload) or
        flow.sha((directory/'session.json').read_bytes())!=report['session_sha256'] or
        session['kind']!=2 or session['counter']!=report['counter'] or session['counter']!=state['engine']['native_counter']+1 or
        base64.b64decode(session['stream_base64'])[32:]!=packet or flow.sha(packet)!=report['package_sha256'] or
        flow.sha(payload)!=report['payload_sha256'] or state['engine']['payload_sha256']!=report['base_runtime_sha256'] or
        state['world_sha256']!=report['base_world_sha256'] or state['package_sha256']!=report['world_package_sha256']):
        raise ValueError('city source/package/session/base binding changed; no radio')
    checked=engine.verify(packet,target=bytes.fromhex(installed['target_sha256']),owner=Path(private_path).with_suffix('.pub').read_bytes(),
                          base_runtime=bytes.fromhex(state['engine']['payload_sha256']),world=Path(state['package']).read_bytes(),
                          counter=state['engine']['native_counter'])
    if checked.payload!=payload:raise ValueError('signed city payload differs')
    flow.current(state)
    def applied():
        report.update(status='EXACT-APPLIED-RECEIPT',receiver_reported_applied=True);flow.save(directory/'report.json',report)
        state['engine'].update(family='reviewed-city-v1',native_counter=report['counter'],payload_sha256=report['payload_sha256'],
                               city_core_sha256=report['profile_sources']['city_core.c'],last_release_report=str(directory/'report.json'),
                               basis='exact correlated applied receipt; physical appearance still needs owner observation')
        state['native_pending']=None;flow.save(state_path,state);return 0
    result=flow.deliver_session(directory,report,session,applied)
    if result==2:
        state['engine']['native_counter']=report['counter'];state['native_pending']=None;flow.save(state_path,state)
    return result
