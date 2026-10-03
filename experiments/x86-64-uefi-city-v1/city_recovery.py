"""Restore saved city after OWNER-CONFIRMED Dell reboot; never infer reboot from RF loss."""
import argparse
import base64
import copy
import tempfile
from pathlib import Path
import city_native
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
flow=city_native.flow
engine=city_native.engine

def recover(state_path,private_path,dell_rebooted=False,resume=False):
    with flow.state_lock(state_path):
        state=flow.read_json(state_path); saved=state.get('recovery_pending')
        if not saved:
            if resume or not dell_rebooted:raise ValueError('owner must explicitly confirm Dell reboot; RF loss is insufficient')
            world=flow.current(state)
            if world['schema_version']!=4 or state['pending'] or state.get('native_pending'):
                raise ValueError('idle saved city required; preserve any existing pending session')
            journal=flow.read_json(Path(state_path).parent/'control/journal.json',2*1024*1024)
            if journal['active']:raise ValueError('finish existing request first')
            directory=Path(tempfile.mkdtemp(prefix='city-recovery-',dir=Path(state_path).parent))
            flow.save(directory/'before-state.json',copy.deepcopy(state));flow.save(directory/'world.json',world)
            record={'schema_version':1,'status':'CHECKING-BOOT','owner_confirmed_reboot':True,
                    'world_sha256':state['world_sha256'],'old_world_counter':state['counter'],
                    'old_native_counter':state['engine']['native_counter'],'engine_done':False,'world_done':False,'sender_steps':[]}
            # Read-only probe BEFORE signing or sending anything with owner authority.
            probe=flow.bundle(flow.compile_world(directory/'world.json',state['counter']+1,flow.CREATOR),1,state['counter']+1)
            flow.save(directory/'session.json',probe)
            code,text=flow.sender_step(directory,record,'query',['--query-only'])
            observed=flow.parse_status(text,probe) if not code else None
            if not observed or observed['outcome']!='idle' or observed['raw_hex']!=('52465301'+'00'*56):
                raise ValueError('fresh empty receiver not observed; no recovery writes')
            installed=engine.gate_check(Path(state['engine']['installed_gate']))
            if state['engine'].get('installed_gate_sha256') and flow.sha(Path(state['engine']['installed_gate']).read_bytes())!=state['engine']['installed_gate_sha256']:
                raise ValueError('installed gate changed')
            previous=flow.read_json(state['engine']['last_release_report'])
            checked=Path(previous['checked_directory']);payload=(checked/'payload.efi').read_bytes()
            city_native.gates(checked,payload)
            boot=flow.read_json(checked/'empty-boot-qemu/report.json')
            if not boot.get('empty_boot') or boot['payload_sha256']!=flow.sha(payload) or boot['status']!='EXACT-CITY-QEMU-LOAD-FULLSCREEN-DATA-RESTORE-REJECTION-PASS' or flow.sha((checked/'empty-boot-qemu/observed.log').read_bytes())!=boot['observed_log_sha256']:
                raise ValueError('exact empty-boot recovery gate required')
            public=Path(private_path).with_suffix('.pub').read_bytes()
            if flow.sha(public)!=installed['owner_public_sha256']:raise ValueError('owner public identity differs')
            _,_,crypto=engine.prepare(directory,public)
            if city_native.build_city.compile_city_driver(directory,crypto)!=payload or city_native.build_city.compile_city_driver(directory,crypto)!=payload:
                raise ValueError('current city sources differ from gated payload')
            checks=flow.check_world(Path(state['package']),directory/'host')
            private=engine.load_private(private_path)
            if private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)!=public:raise ValueError('owner key differs')
            packet=engine.pack(payload,private=private,target=bytes.fromhex(installed['target_sha256']),
                               base_runtime=bytes.fromhex(installed['module_hashes']['1']),world=b'',counter=state['engine']['native_counter']+1)
            (directory/'native.rrt').write_bytes(packet);flow.save(directory/'session.json',flow.bundle(packet,2,state['engine']['native_counter']+1))
            record.update(status='CHECKED-NOT-SENT',profile_sources=city_native.source_hashes(),payload_sha256=flow.sha(payload),
                          packet_sha256=flow.sha(packet),session_sha256=flow.sha((directory/'session.json').read_bytes()),
                          checked_directory=str(checked),boot_gate=boot,host_checks=checks,sender_steps=[])
            flow.save(directory/'report.json',record);state['recovery_pending']=str(directory);flow.save(state_path,state)
        else:
            directory=Path(saved);record=flow.read_json(directory/'report.json')
        if record.get('status')=='REJECTED':raise ValueError('recovery rejected; inspect Dell, do not replay consumed counter')
        if record['profile_sources']!=city_native.source_hashes():raise ValueError('recovery profile source changed')
        if record['world_sha256']!=state['world_sha256']:raise ValueError('saved city changed during recovery')
        if not record['engine_done']:
            installed=engine.gate_check(Path(state['engine']['installed_gate']))
            if state['engine'].get('installed_gate_sha256') and flow.sha(Path(state['engine']['installed_gate']).read_bytes())!=state['engine']['installed_gate_sha256']:
                raise ValueError('installed gate changed')
            packet=(directory/'native.rrt').read_bytes();session=flow.validate_session(flow.read_json(directory/'session.json'))
            if flow.sha(packet)!=record['packet_sha256'] or flow.sha((directory/'session.json').read_bytes())!=record['session_sha256'] or base64.b64decode(session['stream_base64'])[32:]!=packet:
                raise ValueError('saved recovery session changed')
            checked=engine.verify(packet,target=bytes.fromhex(installed['target_sha256']),owner=Path(private_path).with_suffix('.pub').read_bytes(),
                                  base_runtime=bytes.fromhex(installed['module_hashes']['1']),world=b'',counter=record['old_native_counter'])
            if flow.sha(checked.payload)!=record['payload_sha256']:raise ValueError('recovery payload differs')
            def applied():
                record.update(status='EXACT-APPLIED-RECEIPT',receiver_reported_applied=True)
                flow.save(directory/'report.json',record)
                state['engine'].update(native_counter=session['counter'],payload_sha256=record['payload_sha256'],
                                       basis='owner-confirmed reboot and exact recovery native receipt; no attestation')
                flow.save(state_path,state)
                record.update(engine_done=True,status='ENGINE-APPLIED');flow.save(directory/'report.json',record)
                return 0
            result=flow.deliver_session(directory,record,session,applied)
            if result:
                if result==2:record['status']='REJECTED';flow.save(directory/'report.json',record)
                return record
        if not record['world_done']:
            if state['counter']==record['old_world_counter']+1 and not state['pending']:
                proof=flow.read_json(Path(state['package']).parent/'report.json')
                if not proof.get('receiver_reported_applied') or proof['package_sha256']!=state['package_sha256']:raise ValueError('recovery promotion lacks exact receipt')
            else:
                if not state['pending']:
                    flow.prepare_world(state_path,state,'Восстановить город после подтверждённой перезагрузки Dell',flow.read_json(directory/'world.json'),{'kind':'owner-confirmed-reboot-recovery'})
                result=flow.deliver(state_path,state)
                if result:return record
            record.update(world_done=True,status='APPLIED',world_counter=state['counter']);flow.save(directory/'report.json',record)
        state['recovery_pending']=None;flow.save(state_path,state)
        return record

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dell-rebooted',action='store_true');p.add_argument('--resume',action='store_true')
    p.add_argument('--state',type=Path,default=flow.ROOT/'runs/text-world/state.json');p.add_argument('--private',type=Path,default=Path.home()/'.rabbit-owner/runtime.key')
    a=p.parse_args();result=recover(a.state,a.private,a.dell_rebooted,a.resume);print(result['status'])
