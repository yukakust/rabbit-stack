"""HOST MODELS ONLY: timestamps/EMPTY below are synthetic rejection fixtures.
No model result is accepted as a fresh physical observation or clears state.
"""
import copy,json,unittest
from pathlib import Path
import gate
encode=lambda v:json.dumps(v,sort_keys=True).encode()
class GateTest(unittest.TestCase):
 def setUp(self):
  self.n='/archived/native55';self.a='/archived/assets55';self.bundle={'source_count':642,'native_counter':55,'world_package_sha256':gate.PACKAGE,'world_semantic_sha256':gate.WORLD,'native':{'report.json':gate.NATIVE_REPORT},'assets':{'report.json':gate.ASSET_REPORT}}
  self.state={'pending':None,'native_pending':None,'recovery_pending':None,'hardware_trial_pending':self.a,'counter':17,'world_sha256':gate.WORLD,'package_sha256':gate.PACKAGE,'engine':{'native_counter':55,'payload_sha256':gate.PAYLOAD,'last_release_report':self.n+'/report.json'}}
  self.auth={'explicit_owner_authorization':True,'action':'controlled-dell-reboot-for-native55-recovery','native_counter':55,'state_before_sha256':gate.sha(encode(self.state)),'owner_message_reference':'HOST-MODEL-NOT-ACTUAL-USER','authorized_at':1000}
  self.log=b'HOST MODEL not an actual Dell read'
  self.obs={'owner_confirmed_reboot':True,'authorization_sha256':gate.sha(encode(self.auth)),'observed_at':1100,'reboot_confirmed_at':1050,'peripheral':gate.PEER,'writes':0,'receiver':{'raw_hex':gate.EMPTY,'outcome':'idle','counter':0},'log_sha256':gate.sha(self.log)}
 def call(self):return gate.conditional_retirement(encode(self.state),self.bundle,self.n,self.a,encode(self.auth),encode(self.obs),self.log,now=1200)
 def reject(self,obj,key,value):
  before=copy.deepcopy(obj);obj[key]=value
  try:
   with self.assertRaises((ValueError,KeyError,TypeError)):self.call()
  finally:obj.clear();obj.update(before)
 def test_host_only_acceptance_is_nonmutating(self):
  before=encode(self.state);result=self.call();self.assertEqual(before,encode(self.state))
  for k in ('pending_cleared','reboot_performed_by_gate','actual_all_owner_release_claimed','physical_admission'):self.assertFalse(result[k])
  self.assertEqual(result['next_native_counter_candidate'],56)
 def test_state_rejections(self):
  for key,value in [('pending','world'),('native_pending','native'),('recovery_pending','restore'),('hardware_trial_pending','different'),('counter',18),('package_sha256','0'*64),('world_sha256','0'*64)]:self.reject(self.state,key,value)
  for key,value in [('native_counter',56),('payload_sha256','0'*64),('last_release_report','other')]:self.reject(self.state['engine'],key,value)
 def test_authorization_rejections(self):
  for key,value in [('explicit_owner_authorization',False),('action','reboot'),('native_counter',54),('state_before_sha256','0'*64),('owner_message_reference',''),('authorized_at',1101)]:self.reject(self.auth,key,value)
 def test_observation_rejections(self):
  for key,value in [('owner_confirmed_reboot',False),('authorization_sha256','0'*64),('observed_at',899),('observed_at',1201),('observed_at',float('nan')),('observed_at','1100'),('reboot_confirmed_at',1101),('reboot_confirmed_at',999),('peripheral','OTHER'),('writes',1),('writes',False),('log_sha256','0'*64)]:self.reject(self.obs,key,value)
  for key,value in [('raw_hex','52465301'+'00'*55),('raw_hex','52465301'+'01'*56),('counter',1),('counter',False),('outcome','applied')]:self.reject(self.obs['receiver'],key,value)
 def test_wrong_bundle_rejected(self):
  self.reject(self.bundle,'source_count',641)
  self.reject(self.bundle,'native_counter',56)
  self.reject(self.bundle['native'],'report.json','0'*64)
  self.reject(self.bundle['assets'],'report.json','0'*64)
 def test_empty_log_rejected(self):
  self.log=b'';self.obs['log_sha256']=gate.sha(self.log)
  with self.assertRaises(ValueError):self.call()
if __name__=='__main__':unittest.main()
