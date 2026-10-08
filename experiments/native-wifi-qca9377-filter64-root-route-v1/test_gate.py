"""Exact64 source gate corruption checks; no key/radio/state mutation."""
import copy,unittest
from pathlib import Path
from unittest.mock import patch
import gate as g
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.payload=(g.CHECKED/'payload.efi').read_bytes();cls.world=(g.CHECKED/'world19.rup').read_bytes()
 def run_gate(self):return g.gates(g.CHECKED,self.payload,self.world)
 def test_positive(self):self.assertEqual(self.run_gate()['native_counter'],64)
 def test_outer_bytes(self):
  for directory,payload,world in ((g.CHECKED.parent,self.payload,self.world),(g.CHECKED,self.payload+b'x',self.world),(g.CHECKED,self.payload,self.world+b'x')):
   with self.subTest(directory=directory),self.assertRaises(ValueError):g.gates(directory,payload,world)
 def test_changed_hashes(self):
  original=g.sha
  for target in (g.CHECKED/'report.json',g.CHECKED/'reproduction.json',g.PROFILE/'native-abi.json',g.PROFILE/'components/filter_barrier.c',g.PROFILE/'evidence/2026-10-09/timing-production-join.json'):
   with self.subTest(path=target),patch.object(g,'sha',lambda p:'0'*64 if Path(p)==target else original(p)),self.assertRaises(ValueError):self.run_gate()
 def test_model_flags_and_owner_counts(self):
  read=g.flow.read_json;native=g.PROFILE/'runs/native-host/report.json'
  for key,value in (('slowpoll_actual_producer',False),('missing_third_DMA_rejected',False),('scenarios',16),('handover_checks',91),('wifi_connected',True),('actual_driver_poll',False)):
   def changed(path,*args,**kwargs):
    result=read(path,*args,**kwargs)
    if Path(path)==native:result=copy.deepcopy(result);result[key]=value
    return result
   with self.subTest(key=key),patch.object(g.flow,'read_json',changed),self.assertRaises(ValueError):self.run_gate()
if __name__=='__main__':unittest.main()
