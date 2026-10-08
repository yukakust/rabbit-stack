"""Pure public-inventory interpreter; NEVER executes CPUID/MSR/RDSEED.
Capability is not entropy provenance/approval. Root owns physical probe later.
"""
def inspect(d):
 if not isinstance(d,dict):raise ValueError('inventory')
 for k in ('basic_max','leaf1_eax','leaf1_ecx','leaf7_0_ebx','leaf7_0_edx'):
  if type(d.get(k)) is not int or not 0<=d[k]<=0xffffffff:raise ValueError(k)
 if d.get('vendor')!='GenuineIntel':raise ValueError('vendor')
 sig=d['leaf1_eax'];family=(sig>>8)&15
 if family==15:family+=(sig>>20)&255
 model=(sig>>4)&15
 if family in (6,15):model|=((sig>>16)&15)<<4
 step=sig&15;known_affected=family==6 and ((model==0x9e and step<=0xd) or (model==0x8e and step<=0xc))
 return {'family':family,'model':model,'stepping':step,'rdseed_enumerated':d['basic_max']>=7 and bool(d['leaf7_0_ebx']&(1<<18)),'hypervisor_enumerated':bool(d['leaf1_ecx']&(1<<31)),'srbds_control_enumerated':d['basic_max']>=7 and bool(d['leaf7_0_edx']&(1<<9)),'known_coffee_kaby_srbds_affected':known_affected,'srbds_affected_other_models_not_excluded':not known_affected,'entropy_approved':False,'physical_inventory_authenticity_verified':False,'rng_calls':0}
if __name__=='__main__':
 import unittest
 class Test(unittest.TestCase):
  def test_capability_not_authority(self):
   d={'vendor':'GenuineIntel','basic_max':7,'leaf1_eax':0x906ea,'leaf1_ecx':0,'leaf7_0_ebx':1<<18,'leaf7_0_edx':1<<9};r=inspect(d);self.assertTrue(r['rdseed_enumerated']);self.assertTrue(r['known_coffee_kaby_srbds_affected']);self.assertFalse(r['entropy_approved']);self.assertEqual(r['rng_calls'],0)
   d['leaf7_0_ebx']=0;self.assertFalse(inspect(d)['rdseed_enumerated']);d['leaf1_ecx']=1<<31;self.assertTrue(inspect(d)['hypervisor_enumerated']);d['basic_max']=6;self.assertFalse(inspect(d)['srbds_control_enumerated'])
  def test_malformed(self):
   d={'vendor':'GenuineIntel','basic_max':7,'leaf1_eax':0x906ea,'leaf1_ecx':0,'leaf7_0_ebx':1<<18,'leaf7_0_edx':0}
   for k in ('basic_max','leaf1_eax','leaf1_ecx','leaf7_0_ebx','leaf7_0_edx'):
    for bad in (True,-1,1<<32,'7',None):
     x=dict(d);x[k]=bad
     with self.assertRaises(ValueError):inspect(x)
 unittest.main()
