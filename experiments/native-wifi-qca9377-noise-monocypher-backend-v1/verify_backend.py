"""No install. Protocol library feasibility with public fixtures, not enrollment."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REF=Path('/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c');COMMIT='cfe25410979a87391bb9ac8d4d4bef64e9f268c6'
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
FILES=[*[f'src/protocol/{n}.c' for n in ['cipherstate','dhstate','handshakestate','hashstate','internal','names','patterns','symmetricstate','util']],*[f'src/backend/ref/{n}.c' for n in ['cipher-chachapoly','dh-curve25519','hash-sha256']],*[f'src/crypto/{n}.c' for n in ['chacha/chacha','donna/poly1305-donna','sha2/sha256','ed25519/ed25519']]]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def vector_header():
 v=next(v for v in json.loads((REF/'tests/vector/cacophony.txt').read_text())['vectors'] if v['name']=='Noise_NK_25519_ChaChaPoly_SHA256')
 s='/* Exact public Cacophony NK vector, pinned Noise-C tests/vector/cacophony.txt. */\n'
 for n in ['init_prologue','init_ephemeral','init_remote_static','resp_static','resp_ephemeral']:
  s+='static const uint8_t vec_'+n+'[]={'+','.join(str(x) for x in bytes.fromhex(v[n]))+'};\n'
 for i,m in enumerate(v['messages']):
  for n in ['payload','ciphertext']:
   s+='static const uint8_t vec_'+n+str(i)+'[]={'+','.join(str(x) for x in bytes.fromhex(m[n]))+'};\n'
 for n in ['payload','ciphertext']:
  s+='static const uint8_t *vec_'+n+'[]={'+','.join('vec_'+n+str(i) for i in range(6))+'};\n'
 for n in ['payload','ciphertext']:
  s+='static const size_t vec_'+n+'_len[]={'+','.join('sizeof(vec_'+n+str(i)+')' for i in range(6))+'};\n'
 return s
def main():
 MONO=Path('/home/yuka/rabbit-world/parallel-secure-provision-v1/reference')
 MP={'monocypher.c':'f1f838cdd483bdebe0df0ff5c5ed60535e496f769c6a2f933ac4c0b114207123','monocypher.h':'fcaf6ed771358bb4f40fba016f6518ae86ec02b1b877d2cc35ad92d3a26fd7b3'}
 for n,h in MP.items():assert sha(MONO/n)==h
 assert subprocess.check_output(['git','-C',str(REF),'rev-parse','HEAD'],text=True).strip()==COMMIT
 assert not subprocess.check_output(['git','-C',str(REF),'status','--porcelain'],text=True)
 assert (ROOT/'noise_vector.h').read_text()==vector_header()
 out=ROOT/'runs/backend';out.mkdir(parents=True,exist_ok=True)
 flags=['-I'+str(REF/'include'),'-I'+str(REF/'src'),'-I'+str(REF/'src/protocol'),'-I'+str(MONO),'-I'+str(ROOT),'-ffunction-sections','-fdata-sections']
 inputs={str(p.relative_to(REF)):sha(p) for p in [*REF.glob('include/**/*.h'),*REF.glob('src/**/*.h'),*REF.glob('src/**/*.c'),REF/'tests/vector/cacophony.txt']}
 local={n:sha(ROOT/n) for n in ['noise_dummy.c','noise_vector.h','verify_backend.py','differential.h','backend_entropy.h','dh_monocypher.c','cipher_monocypher.c']}
 protocol=[str(REF/f'src/protocol/{n}.c') for n in ['cipherstate','dhstate','handshakestate','hashstate','internal','names','patterns','symmetricstate','util']]
 sources=[*protocol,str(REF/'src/backend/ref/hash-sha256.c'),str(REF/'src/crypto/sha2/sha256.c'),str(MONO/'monocypher.c'),str(ROOT/'dh_monocypher.c'),str(ROOT/'cipher_monocypher.c'),str(ROOT/'noise_dummy.c')]
 logs=[]
 def run(cmd):
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=120);logs.extend([json.dumps(cmd),r.stdout,r.stderr]);assert not r.returncode,r.stderr;return r.stdout
 sanitizer=['-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all']
 refs=[]
 for f,defs in [('src/backend/ref/cipher-chachapoly.c',['-Dnoise_chachapoly_new=qca_reference_chachapoly_new']),('src/backend/ref/dh-curve25519.c',['-Dnoise_curve25519_new=qca_reference_curve25519_new']),('src/crypto/chacha/chacha.c',[]),('src/crypto/donna/poly1305-donna.c',[]),('src/crypto/ed25519/ed25519.c',['-DED25519_CUSTOMHASH','-DED25519_CUSTOMRANDOM'])]:
  obj=out/(Path(f).stem+'.o');run([str(CC),*sanitizer,*flags,*defs,'-c',str(REF/f),'-o',str(obj)]);refs.append(str(obj))
 link=['-Wl,--gc-sections','-Wl,--wrap=calloc','-Wl,--wrap=malloc','-Wl,--wrap=free']
 adapter_bytes={}
 for n in ['dh_monocypher','cipher_monocypher']:
  obj=out/(n+'-size.o');run([str(CC),'-Os','-Wall','-Wextra','-Werror',*flags,'-c',str(ROOT/(n+'.c')),'-o',str(obj)])
  adapter_bytes[n]=int(run(['size',str(obj)]).splitlines()[1].split()[0])
 exe=out/'differential-test';run([str(CC),*sanitizer,*flags,*sources,*refs,*link,'-o',str(exe)])
 result=run([str(exe)])
 compact=out/'compact-host';run([str(CC),'-Os','-DQCA_COMPACT_ONLY',*flags,*sources,*link,'-o',str(compact)])
 compact_result=run([str(compact)])
 size=run(['size',str(compact)]);text_bytes,data_bytes,bss_bytes=map(int,size.splitlines()[1].split()[:3])
 # Code-only baseline fixture and mature protocol provider size observations.
 # No native full-link / incremental EFI-size claim from these host binaries.
 (out/'host.log').write_text('\n'.join(logs))
 assert all(sha(REF/n)==h for n,h in inputs.items());assert all(sha(MONO/n)==h for n,h in MP.items());assert all(sha(ROOT/n)==h for n,h in local.items())
 report={'status':'NOISE-MONOCYPHER-PINNED-NK-DIFFERENTIAL-ASAN-UBSAN-PASS','noise_commit':COMMIT,'monocypher_commit':'ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f','reference_sha256':inputs,'monocypher_sha256':MP,'source_sha256':local,'checks':int(re.search(r'checks=(\d+)',result)[1]),'observed_nonnull_error_outputs':int(re.search(r'dangling_error_outputs=(\d+)',result)[1]),'compact_checks':int(re.search(r'checks=(\d+)',compact_result)[1]),'compact_host_text_including_fixture':text_bytes,'adapter_only_host_object_text':adapter_bytes,'compact_host_data':data_bytes,'compact_host_bss_including_fixture':bss_bytes,'host_log_sha256':sha(out/'host.log'),'fixed_suite':'Noise_NK_25519_ChaChaPoly_SHA256','noise_state_machine_modified':False,'public_dummy_only':True,'real_keys_credentials_signatures':False,'native_rng_proved':False,'native_allocator_ported':False,'coff_or_full_efi_proved':False,'owner_authorization_implemented':False,'native54_bytes':187392,'native_limit':262144}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.strip());print(compact_result.strip());print(size.strip())
if __name__=='__main__':main()
