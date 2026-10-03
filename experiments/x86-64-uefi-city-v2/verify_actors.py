#!/usr/bin/env python3
"""No owner key or radio: actor codec, planner guards and real C timer checks."""
import copy,json,struct,sys,tempfile,unittest,subprocess
from pathlib import Path
import scene5 as scene
import actors_check
flow=scene.flow
sys.path.insert(0,str(flow.ROOT))
import world_planner as planner

class Checks(unittest.TestCase):
 def setUp(self):
  self.world=scene.city_world.initial_city();self.world.update(schema_version=5,actors=[scene.models()['rabbit.actor.roof-cat-v1']])
 def test_signed_geometry_roundtrip_and_bad_signature(self):
  packet=scene.compile_scene(self.world,12);decoded,counter=scene.decode_scene(packet)
  self.assertEqual(counter,12);self.assertEqual(decoded['actors'][0]['parts'],self.world['actors'][0]['parts'])
  with self.assertRaises(Exception):scene.decode_scene(packet[:-1]+bytes([packet[-1]^1]))
 def test_bounds_and_duplicate_ids(self):
  for mutate in (lambda w:w['actors'].append(copy.deepcopy(w['actors'][0])),lambda w:w['actors'][0]['parts'][0]['size'].update(width=1001),lambda w:w['actors'][0]['parts'][0]['motion'].update(phase_ms=60000),lambda w:w['actors'][0]['parts'][0]['visibility'].update(duration_ms=60000)):
   world=copy.deepcopy(self.world);mutate(world)
   with self.assertRaises(Exception):scene.compile_scene(world,12)
 def test_reserved_and_trailing_even_with_valid_fixture_signature(self):
  packet=scene.compile_scene(self.world,12)
  for offset in (32+len(self.world['buildings'])*32+10,32+len(self.world['buildings'])*32+16+36):
   body=bytearray(packet[:-64]);body[offset]=1
   with self.assertRaises(Exception):scene.decode_scene(bytes(body)+flow.CREATOR.sign(bytes(body)))
  body=bytearray(packet[:-64]+b'x');struct.pack_into('<H',body,6,len(body)+64)
  with self.assertRaises(Exception):scene.decode_scene(bytes(body)+flow.CREATOR.sign(bytes(body)))
 def test_actor_requires_reviewed_profile(self):
  with self.assertRaises(Exception):flow.actors_ready({'engine':{'family':'reviewed-city-v1'}})
 def test_assets_cannot_mix_unsupported_restore_or_native_effects(self):
  ref={'component_id':'rabbit.actor.roof-cat-v1','actor_id':1,'name':'Кот','position':{'x':620,'y':510,'z':600},'yaw':0}
  plan={'status':'ready','explanation':'Кот','base_world_sha256':'1'*64,'objects':None,'programs':None,'inventory_assets':[],'created_sprites':[],'created_drawings':[],'city_world':None,'actor_assets':[ref],'background':None,'restore_version':None,'missing_capabilities':[]}
  for fields in ({'status':'unsupported'},{'restore_version':'initial'},{'background':'ffffff'}):
   bad=copy.deepcopy(plan);bad.update(fields)
   with self.assertRaises(Exception):planner.parse_plan(json.dumps(bad))
 def test_actual_c_timers_tail_and_sanitized_bounds(self):
  with tempfile.TemporaryDirectory(prefix='rabbit-actors-check-') as tmp:
   root=Path(tmp);path=root/'world.rup';path.write_bytes(scene.compile_scene(self.world,12))
   result=actors_check.check_city(path,root/'check',True,True)
   self.assertTrue(result['roof_cat_timing']);self.assertTrue(result['sanitizers'])
   executable=root/'check/city-check'
   original=path.read_bytes();body=bytearray(original[:-64]);body[32+len(self.world['buildings'])*32+16+36]=1
   path.write_bytes(bytes(body)+flow.CREATOR.sign(bytes(body)))
   self.assertEqual(subprocess.run([str(executable),str(path),str(root/'bad.ppm')]).returncode,2)

if __name__=='__main__':unittest.main(verbosity=2)
