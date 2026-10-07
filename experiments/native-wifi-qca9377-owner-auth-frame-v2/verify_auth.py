#!/usr/bin/env python3
"""Yukabox only. Authorized RFC8032 PUBLIC testseed fixture signing, never real keys."""
import hashlib,json,pathlib,re,struct,subprocess
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
 assert sha(BACK/'cipher_monocypher.c')=='b1559266548c82b77df10f8167d5d86bc2cc9490cc1d4504f7de0d6d92b3c790'
 upstream=[REF/'src/protocol'/f'{n}.c' for n in ['cipherstate','dhstate','handshakestate','hashstate','internal','names','patterns','symmetricstate','util']]
 upstream+=[REF/'src/backend/ref/hash-sha256.c',REF/'src/crypto/sha2/sha256.c',MONO/'monocypher.c',MONO/'monocypher-ed25519.c',BACK/'cipher_monocypher.c',BACK/'dh_monocypher.c']
 local={n:sha(ROOT/n) for n in ['auth_frame.c','auth_frame.h','auth_test.c','factory.c','verify_auth.py','compat/malloc.h','public-fixture-request.json','fixture_noise.h','fixture_probe.c']}
 references={str(p):sha(p) for p in [*upstream,*REF.glob('include/**/*.h'),*REF.glob('src/**/*.h'),REF/'tests/vector/cacophony.txt',BACK/'backend_entropy.h']}
 out=ROOT/'runs/verified';out.mkdir(parents=True,exist_ok=True);logs=[]
 def run(cmd):
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=180);logs.extend([json.dumps(cmd),r.stdout,r.stderr]);assert not r.returncode,r.stderr;return r.stdout
 v=next(v for v in json.loads((REF/'tests/vector/cacophony.txt').read_text())['vectors'] if v['name']=='Noise_NK_25519_ChaChaPoly_SHA256')
 vh='/* PUBLIC Cacophony dummy fixture, pinned upstream. */\n'
 for n in ['init_prologue','init_ephemeral','init_remote_static','resp_static','resp_ephemeral']:
  vh+='static const uint8_t vec_'+n+'[]={'+','.join(map(str,bytes.fromhex(v[n])))+'};\n'
 for i,m in enumerate(v['messages']):
  for n in ['payload','ciphertext']:vh+='static const uint8_t vec_'+n+str(i)+'[]={'+','.join(map(str,bytes.fromhex(m[n])))+'};\n'
 for n in ['payload','ciphertext']:
  vh+='static const uint8_t *vec_'+n+'[]={'+','.join('vec_'+n+str(i) for i in range(6))+'};\n'
  vh+='static const size_t vec_'+n+'_len[]={'+','.join('sizeof(vec_'+n+str(i)+')' for i in range(6))+'};\n'
 (out/'noise_vector.h').write_text(vh)
 oldfixture=json.loads((ROOT/'public-fixture-request.json').read_text());oldmessage=bytes.fromhex(oldfixture['message_hex']);assert len(oldmessage)==200
 (out/'canonical_fixture.h').write_text('static const uint8_t canonical_fixture[200]={'+','.join(map(str,oldmessage))+'};\n')
 inc=['-I'+str(out),'-I'+str(ROOT),'-I'+str(REF/'include'),'-I'+str(REF/'src'),'-I'+str(REF/'src/protocol'),'-I'+str(MONO),'-I'+str(BACK)]
 flags=['-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-ffunction-sections','-fdata-sections']
 objects=[]
 for i,p in enumerate([*upstream,ROOT/'factory.c',ROOT/'auth_frame.c']):
  obj=out/f'host-{i}.o';strict=['-Wall','-Wextra','-Werror'] if p.parent==ROOT else []
  run([CC,*flags,*strict,*inc,'-c',str(p),'-o',str(obj)]);objects.append(str(obj))
 run([CC,*flags,*inc,'-Wall','-Wextra','-Werror',str(ROOT/'fixture_probe.c'),*objects,'-Wl,--gc-sections','-o',str(out/'probe')])
 message=bytes.fromhex(run([str(out/'probe')]).strip());assert len(message)==200
 owner=bytes.fromhex('d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a')
 assert message[:40]==b'ROWN0001'+struct.pack('<IIIIQQ',1,1,1,0,0,43)
 assert message[72:104]==hashlib.sha256(bytes.fromhex(v['init_prologue'])).digest()
 assert message[104:136]==bytes([3])*32 and message[136:168]==bytes([4])*32 and message[168:200]==owner
 # Explicitly authorized PUBLIC RFC8032 section7.1 TEST1 seed. NOT owner/device key.
 from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
 from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
 seed=bytes.fromhex('9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60')
 key=Ed25519PrivateKey.from_private_bytes(seed);assert key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)==owner
 signature=key.sign(message);key.public_key().verify(signature,message)
 # Persist only public canonical bytes/signature, never seed/secret serialization.
 fixture={'fixture_kind':'PUBLIC-RFC8032-TEST1-SIGNED-AUTH-NOT-REAL-DEVICE','message_hex':message.hex(),'owner_public':owner.hex(),'signature':signature.hex(),'signing_authorized':True,'published_testseed_only':True,'device_private_key_reads':0,'user_private_key_reads':0}
 (out/'public-signed-fixture.json').write_text(json.dumps(fixture,indent=2)+'\n')
 fh='/* Authorized PUBLIC dummy fixture signature only. No private seed. */\n'
 for n,b in [('fixture_message',message),('fixture_signature',signature)]:fh+='static const uint8_t '+n+'[]={'+','.join(map(str,b))+'};\n'
 (out/'auth_fixture.h').write_text(fh)
 run([CC,*flags,*inc,'-Wall','-Wextra','-Werror',str(ROOT/'auth_test.c'),*objects,'-Wl,--gc-sections','-o',str(out/'test')])
 result=run([str(out/'test')]);checks=int(re.search(r'PASS (\d+) OWNER AUTH',result)[1])
 coff=[]
 for p in [ROOT/'auth_frame.c',MONO/'monocypher.c',MONO/'monocypher-ed25519.c']:
  obj=out/(p.stem+'.obj');run([CC,'-target','x86_64-pc-win32-coff','-DWIN32=1','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT/'compat'),*inc,'-c',str(p),'-o',str(obj)]);coff.append({'file':p.name,'sha256':sha(obj)})
 assert local=={n:sha(ROOT/n) for n in local};assert references=={n:sha(pathlib.Path(n)) for n in references}
 (out/'host.log').write_text('\n'.join(logs))
 report={'status':'OWNER-AUTH-FRAME-V2-REAL-NK-SPLIT-ED25519-AUTH-ACK-ASAN-COFF-PASS','checks':checks,'source_sha256':local,'reference_sha256':references,'monocypher_sha256':PINS,'coff':coff,'log_sha256':sha(out/'host.log'),'public_signed_fixture_sha256':sha(out/'public-signed-fixture.json'),'actual_nk_split_verified':True,'signed_auth_positive_fixture':True,'ack_positive_end_to_end_verified':True,'authorized_public_rfc8032_testseed_signatures':1,'real_keys_read':0,'credentials_read':0,'device_rng_calls':0,'radio_operations':0,'physical_pin_verified':False,'device_authenticated':False,'native_candidate':False,'provisioning_approved':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.strip())
if __name__=='__main__':main()
