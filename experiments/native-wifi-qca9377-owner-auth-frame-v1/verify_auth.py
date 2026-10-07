#!/usr/bin/env python3
"""Yukabox-only host component verification, no signer/credentials/IO."""
import hashlib,json,pathlib,re,subprocess
ROOT=pathlib.Path(__file__).resolve().parent
REF=pathlib.Path('/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c')
MONO=pathlib.Path('/home/yuka/rabbit-world/parallel-secure-provision-v1/reference')
BACK=pathlib.Path('/home/yuka/rabbit-world/parallel-noise-monocypher-backend-v2/experiments/native-wifi-qca9377-noise-monocypher-backend-v2')
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
PINS={'monocypher.c':'f1f838cdd483bdebe0df0ff5c5ed60535e496f769c6a2f933ac4c0b114207123','monocypher.h':'fcaf6ed771358bb4f40fba016f6518ae86ec02b1b877d2cc35ad92d3a26fd7b3','monocypher-ed25519.c':'ce0d2f8e32ca8f66398ba5b3456cc74327c3eff14e7b950ce7d57be9025cc453','monocypher-ed25519.h':'3a3035181f991a158d0e1c7567258f0bae8ba0f1f23c5512b4a1db1b3c9730ce'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert subprocess.check_output(['git','-C',str(REF),'rev-parse','HEAD'],text=True).strip()=='cfe25410979a87391bb9ac8d4d4bef64e9f268c6'
 assert not subprocess.check_output(['git','-C',str(REF),'status','--porcelain'],text=True)
 for n,h in PINS.items():assert sha(MONO/n)==h
 upstream=[REF/'src/protocol'/f'{n}.c' for n in ['cipherstate','util','names']]
 upstream+=[MONO/'monocypher.c',MONO/'monocypher-ed25519.c',BACK/'cipher_monocypher.c']
 # Source hash is compared to the verified backend-v2's frozen proof as well.
 assert sha(BACK/'cipher_monocypher.c')=='b1559266548c82b77df10f8167d5d86bc2cc9490cc1d4504f7de0d6d92b3c790'
 local={n:sha(ROOT/n) for n in ['auth_frame.c','auth_frame.h','auth_test.c','factory.c','verify_auth.py','compat/malloc.h','public-fixture-request.json']}
 references={str(p):sha(p) for p in [*upstream,REF/'src/protocol/internal.h',*REF.glob('include/**/*.h')]}
 out=ROOT/'runs/verified';out.mkdir(parents=True,exist_ok=True);logs=[]
 fixture=json.loads((ROOT/'public-fixture-request.json').read_text());message=bytes.fromhex(fixture['message_hex']);assert len(message)==200 and fixture['signature'] is None
 (out/'canonical_fixture.h').write_text('static const uint8_t canonical_fixture[200]={'+','.join(map(str,message))+'};\n')
 def run(cmd):
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=120);logs.extend([json.dumps(cmd),r.stdout,r.stderr]);assert not r.returncode,r.stderr;return r.stdout
 inc=['-I'+str(out),'-I'+str(ROOT),'-I'+str(REF/'include'),'-I'+str(REF/'src'),'-I'+str(REF/'src/protocol'),'-I'+str(MONO)]
 flags=['-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-ffunction-sections','-fdata-sections']
 objects=[]
 for i,p in enumerate([*upstream,ROOT/'factory.c',ROOT/'auth_frame.c']):
  obj=out/f'host-{i}.o';strict=['-Wall','-Wextra','-Werror'] if p.parent==ROOT else []
  run([CC,*flags,*strict,*inc,'-c',str(p),'-o',str(obj)]);objects.append(str(obj))
 run([CC,*flags,*inc,'-Wall','-Wextra','-Werror',str(ROOT/'auth_test.c'),*objects,'-Wl,--gc-sections','-o',str(out/'test')])
 result=run([str(out/'test')]);checks=int(re.search(r'PASS (\d+) OWNER AUTH',result)[1])
 # Only component+actual verifier primitives COFF; full native link not claimed.
 coff=[]
 for p in [ROOT/'auth_frame.c',MONO/'monocypher.c',MONO/'monocypher-ed25519.c']:
  obj=out/(p.stem+'.obj');run([CC,'-target','x86_64-pc-win32-coff','-DWIN32=1','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT/'compat'),*inc,'-c',str(p),'-o',str(obj)]);coff.append({'file':p.name,'sha256':sha(obj)})
 assert local=={n:sha(ROOT/n) for n in local};assert references=={n:sha(pathlib.Path(n)) for n in references}
 (out/'host.log').write_text('\n'.join(logs))
 report={'status':'OWNER-AUTH-FRAME-ACTUAL-CRYPTO-NEGATIVE-KAT-ASAN-COFF-PASS','checks':checks,'source_sha256':local,'reference_sha256':references,'monocypher_sha256':PINS,'coff':coff,'log_sha256':sha(out/'host.log'),'signed_auth_positive_fixture':False,'ack_positive_end_to_end_verified':False,'synthetic_pre_authenticated_ack_gating_verified':True,'signatures_created':0,'real_keys_read':0,'credentials_read':0,'device_rng_calls':0,'radio_operations':0,'physical_pin_verified':False,'device_authenticated':False,'native_candidate':False,'provisioning_approved':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.strip())
if __name__=='__main__':main()
