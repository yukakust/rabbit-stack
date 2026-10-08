from pathlib import Path
import subprocess,hashlib,json,platform
assert platform.system()=='Linux','native C only Yukabox'
R=Path(__file__).resolve().parent;O=R/'runs/renderer';O.mkdir(parents=True,exist_ok=True)
S=Path('/home/yuka/rabbit-world/parallel-filter64-native-v1/source/experiments/native-wifi-qca9377-filter64-native-v1/runs/checked-candidate')
B={
'city_core.c':'87118d150ae88002e5851410bbf1cb56c130f9f8b6933d70111cb80fe5504005',
'city_core.h':'32a5c95574bd3a022df954b4af57a56ee27e20d372085efc31a77a5297aabbf8',
'monocypher-ed25519.c':'ce0d2f8e32ca8f66398ba5b3456cc74327c3eff14e7b950ce7d57be9025cc453',
'monocypher-ed25519.h':'3a3035181f991a158d0e1c7567258f0bae8ba0f1f23c5512b4a1db1b3c9730ce',
'monocypher.c':'f1f838cdd483bdebe0df0ff5c5ed60535e496f769c6a2f933ac4c0b114207123',
'monocypher.h':'fcaf6ed771358bb4f40fba016f6518ae86ec02b1b877d2cc35ad92d3a26fd7b3',
'world19.rup':'89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in B.items():
 assert sha(S/name)==digest,name
 (O/name).write_bytes((S/name).read_bytes())
source=(O/'city_core.c').read_text();needle='static uint32_t depth[CITY_W*CITY_H];';assert source.count(needle)==1
derived=source.replace(needle,'static uint32_t *depth;\nuint32_t **arena_depth_holder(void){return &depth;}')
(O/'arena_renderer.c').write_text(derived)
C='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
F=[C,'-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(O),'-I'+str(R)]
objects=[]
for name,args in [('city_core.c',['-Dcity_decode=original_decode','-Dcity_render=original_render']),('arena_renderer.c',[]),('monocypher.c',[]),('monocypher-ed25519.c',[])]:
 obj=O/(name+'.o');subprocess.run([*F,*args,'-c',str(O/name),'-o',str(obj)],check=True);objects.append(str(obj))
subprocess.run([*F,str(R/'test_renderer.c'),str(R/'city_arena.c'),*objects,'-o',str(O/'test')],check=True)
a=subprocess.run([str(O/'test'),str(O/'world19.rup')],capture_output=True,text=True,check=True)
report={'status':'SYNTHETIC-WORLD19-ORIGINAL-ARENA-DIFFERENTIAL-PASS','build_host':'yukabox','frozen_input_sha256':B,'derived_source_sha256':sha(O/'arena_renderer.c'),'source_sha256':{p.name:sha(p) for p in [R/'city_arena.c',R/'city_arena.h',R/'test_renderer.c',R/'verify_renderer.py']},'result':a.stdout.strip(),'physical_proved':False,'integrated':False}
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(a.stdout)
