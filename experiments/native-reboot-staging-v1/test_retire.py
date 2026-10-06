"""Read-only real signed fixture verification; mutations confined to temp copies."""
import copy,json,shutil,tempfile,time
from pathlib import Path
from unittest.mock import patch
import retire as r
REPO=r.REPO
state_source=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
observation_source=state_source.parent/'native47-reboot-observation/observation.json'
public=Path('/Users/yukakust/.rabbit-owner/runtime.pub')
def main():
 original=json.loads(state_source.read_text())
 if not original.get('hardware_trial_pending'):
  historical=Path(original['retired_hardware_trials'][-1]['session'])
  original=json.loads((historical/'before-reboot-retirement-state.json').read_text())
 assert original.get('hardware_trial_pending')
 checks=0
 with tempfile.TemporaryDirectory(prefix='rabbit-reset-check-') as t:
  root=Path(t);session=root/'saved-session';shutil.copytree(original['hardware_trial_pending'],session)
  if (session/'before-reboot-retirement-report.json').exists():shutil.copyfile(session/'before-reboot-retirement-report.json',session/'report.json')
  state=copy.deepcopy(original);state['hardware_trial_pending']=str(session);state_path=root/'state.json'
  obs=root/'observation.json';shutil.copyfile(observation_source,obs);shutil.copyfile(observation_source.with_name('query.log'),root/'query.log')
  raw=json.loads(obs.read_text());raw['observed_at']=time.time();obs.write_text(json.dumps(raw));state_path.write_text(json.dumps(state));before=state_path.read_bytes();report_before=(session/'report.json').read_bytes()
  with patch.object(r.recovery.engine,'load_private',side_effect=AssertionError('no secret loading')) as secret,patch.object(r.flow,'sender_step',side_effect=AssertionError('no radio operation')) as radio:
   for mode in range(8):
    mutated=copy.deepcopy(raw);bad_state=copy.deepcopy(state);confirmed=True
    if mode==0:confirmed=False
    if mode==1:mutated['observed_at']=0
    if mode==2:mutated['receiver']['raw_hex']='nonempty'
    if mode==3:mutated['log_sha256']='00'*32
    if mode==4:mutated['writes']=1
    if mode==5:mutated['peripheral']='wrong-peer'
    if mode==6:bad_state['native_pending']='another-operation'
    if mode==7:bad_state['engine']['payload_sha256']='00'*32
    obs.write_text(json.dumps(mutated));state_path.write_text(json.dumps(bad_state));expected=state_path.read_bytes()
    try:r.retire(state_path,obs,public,confirmed,True)
    except (ValueError,AssertionError):pass
    else:raise AssertionError('invalid reboot evidence accepted')
    assert state_path.read_bytes()==expected and (session/'report.json').read_bytes()==report_before;checks+=1
   obs.write_text(json.dumps(raw));state_path.write_bytes(before)
   result=r.retire(state_path,obs,public,True,True);assert result['private_key_loads']==0 and state_path.read_bytes()==before;checks+=1
   packets={p.name:p.read_bytes() for p in session.glob('chunk-*.bin')}
   p=session/'chunk-0.bin';saved=p.read_bytes();p.chmod(0o600);p.write_bytes(saved[:-1]+bytes([saved[-1]^1]))
   try:r.retire(state_path,obs,public,True,True)
   except ValueError:pass
   else:raise AssertionError('corrupt signed packet accepted')
   assert state_path.read_bytes()==before;p.write_bytes(saved);checks+=1
   result=r.retire(state_path,obs,public,True,False);after=json.loads(state_path.read_text());assert after['hardware_trial_pending'] is None
   assert after['engine']==state['engine'] and after['world_sha256']==state['world_sha256']
   assert all((session/name).read_bytes()==body for name,body in packets.items());checks+=1
   secret.assert_not_called();radio.assert_not_called()
 print(f'REBOOT RETIREMENT checks={checks} PASS; zero private-key loads/radio writes; production state unchanged')
if __name__=='__main__':main()
