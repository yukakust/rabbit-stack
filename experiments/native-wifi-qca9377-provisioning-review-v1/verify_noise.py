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
 assert subprocess.check_output(['git','-C',str(REF),'rev-parse','HEAD'],text=True).strip()==COMMIT
 assert not subprocess.check_output(['git','-C',str(REF),'status','--porcelain'],text=True)
 assert (ROOT/'noise_vector.h').read_text()==vector_header()
 out=ROOT/'runs/noise';out.mkdir(parents=True,exist_ok=True)
 flags=['-I'+str(REF/'include'),'-I'+str(REF/'src'),'-I'+str(REF/'src/protocol'),'-DED25519_CUSTOMHASH','-DED25519_CUSTOMRANDOM','-ffunction-sections','-fdata-sections']
 inputs={str(p.relative_to(REF)):sha(p) for p in [*[REF/n for n in FILES],*REF.glob('include/**/*.h'),*REF.glob('src/**/*.h'),*REF.glob('src/**/*.c'),REF/'tests/vector/cacophony.txt']}
 local={n:sha(ROOT/n) for n in ['noise_dummy.c','noise_vector.h','verify_noise.py']}
 exe=out/'dummy-test';subprocess.run([str(CC),'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,*[str(REF/n) for n in FILES],str(ROOT/'noise_dummy.c'),'-Wl,--gc-sections','-Wl,--wrap=calloc','-Wl,--wrap=malloc','-Wl,--wrap=free','-o',str(exe)],check=True)
 r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 # Size of optimized linked HOST library+fixture is a code-size proxy,
 # not full EFI size or evidence a native allocator/RNG port exists.
 lean=out/'dummy-size';subprocess.run([str(CC),'-Os',*flags,*[str(REF/n) for n in FILES],str(ROOT/'noise_dummy.c'),'-Wl,--gc-sections','-Wl,--wrap=calloc','-Wl,--wrap=malloc','-Wl,--wrap=free','-o',str(lean)],check=True)
 size=subprocess.check_output(['size',str(lean)],text=True);(out/'size.log').write_text(size)
 values=size.splitlines()[1].split();text_bytes,data_bytes,bss_bytes=map(int,values[:3])
 assert all(sha(REF/n)==h for n,h in inputs.items());assert all(sha(ROOT/n)==h for n,h in local.items())
 report={'status':'NOISE-NK-PINNED-LIBRARY-DUMMY-ASAN-UBSAN-PASS','library_commit':COMMIT,'library_source_sha256':inputs,'source_sha256':local,'checks':int(re.search(r'checks=(\d+)',r.stdout)[1]),'peak_heap_two_party_fixture':int(re.search(r'peak_heap=(\d+)',r.stdout)[1]),'host_linked_text_bytes_including_fixture':text_bytes,'host_linked_data_bytes':data_bytes,'host_linked_bss_bytes_including_fixture':bss_bytes,'host_log_sha256':sha(out/'host.log'),'size_log_sha256':sha(out/'size.log'),'build_host':'yukabox','native_rng_proved':False,'native_allocator_ported':False,'coff_or_full_efi_proved':False,'native54_bytes':187392,'native_efi_limit':262144,'owner_signature_or_authorization_implemented':False,'physical_fingerprint_verified':False,'provisioning_performed':False,'real_keys_or_credentials_used':False,'exact_pinned_cacophony_nk_vector_messages':6}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip());print(size.strip())
if __name__=='__main__':main()
