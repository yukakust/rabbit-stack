"""No install. Protocol library feasibility with public fixtures, not enrollment."""
import hashlib,json,re,subprocess,struct
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
 RNG=ROOT/'dependencies/rng'
 RNG_PINS={'rng_port.c': '5ac751cc0d2e0feed19e7ed1e8bc4f2a92e9aaec729bbacc1b8c3368885f6752', 'rng_port.h': 'c68480b6b5677d907d6b535fe1ead1d03ef4d27096cb5b56417415305bb9fd31'}
 for n,h in RNG_PINS.items():assert sha(RNG/n)==h
 MP={'monocypher.c':'f1f838cdd483bdebe0df0ff5c5ed60535e496f769c6a2f933ac4c0b114207123','monocypher.h':'fcaf6ed771358bb4f40fba016f6518ae86ec02b1b877d2cc35ad92d3a26fd7b3'}
 for n,h in MP.items():assert sha(MONO/n)==h
 assert subprocess.check_output(['git','-C',str(REF),'rev-parse','HEAD'],text=True).strip()==COMMIT
 assert not subprocess.check_output(['git','-C',str(REF),'status','--porcelain'],text=True)
 assert (ROOT/'noise_vector.h').read_text()==vector_header()
 out=ROOT/'runs/port';out.mkdir(parents=True,exist_ok=True)
 inc=['-I'+str(REF/'include'),'-I'+str(REF/'src'),'-I'+str(REF/'src/protocol'),'-I'+str(MONO),'-I'+str(ROOT),'-I'+str(RNG)]
 alloc=['-Dnoise_new_object=qca_noise_new_object','-Dnoise_free=qca_noise_free','-Dmalloc=qca_port_malloc','-Dcalloc=qca_port_calloc','-Dfree=qca_port_free']
 util=['-Dnoise_new_object=qca_unused_new','-Dnoise_free=qca_unused_free','-Dmalloc=qca_port_malloc','-Dcalloc=qca_port_calloc','-Dfree=qca_port_free']
 inputs={str(p.relative_to(REF)):sha(p) for p in [*REF.glob('include/**/*.h'),*REF.glob('src/**/*.h'),*REF.glob('src/**/*.c'),REF/'tests/vector/cacophony.txt']}
 local={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and 'runs' not in p.parts and 'evidence' not in p.parts}
 sources=[(REF/f'src/protocol/{n}.c',util if n=='util' else alloc) for n in ['cipherstate','dhstate','handshakestate','hashstate','internal','names','patterns','symmetricstate','util']]
 sources += [(REF/'src/backend/ref/hash-sha256.c',alloc),(REF/'src/crypto/sha2/sha256.c',[]),(MONO/'monocypher.c',[]),(ROOT/'dh_monocypher.c',alloc),(ROOT/'cipher_monocypher.c',alloc),(ROOT/'native_port.c',[]),(ROOT/'native_factories.c',[]),(ROOT/'native_abi_probe.c',[]),(RNG/'rng_port.c',[])]
 logs=[]
 def run(cmd):
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=120);logs.extend([json.dumps(cmd),r.stdout,r.stderr]);assert not r.returncode,r.stderr;return r.stdout
 host=[];san=['-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all']
 for i,(p,defs) in enumerate(sources):
  obj=out/f'host-{i}.o';strict=['-Wall','-Wextra','-Werror'] if p.parent==ROOT or p.parent==RNG else []
  run([str(CC),*san,*strict,*inc,*defs,'-c',str(p),'-o',str(obj)]);host.append(str(obj))
 exe=out/'port-test';run([str(CC),*san,*inc,str(ROOT/'port_test.c'),*host,'-Wl,--gc-sections','-o',str(exe)])
 result=run([str(exe)]);quarantine={m:run([str(exe),m]) for m in ['foreign','interior','size','double']}
 coff={};undefined=set();defined=set()
 for i,(p,defs) in enumerate([*sources,(ROOT/'native_memory.c',[])]):
  obj=out/f'coff-{i}.obj';run([str(CC),'-target','x86_64-pc-win32-coff','-DWIN32=1','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-Os','-I'+str(ROOT/'compat'),*inc,*defs,'-c',str(p),'-o',str(obj)])
  z=run(['size',str(obj)]).splitlines()[1].split();coff[str(p)]={'text':int(z[0]),'data':int(z[1]),'bss':int(z[2]),'sha256':sha(obj)}
  if p.name=='native_abi_probe.c':
   abi=out/'abi.bin';run(['objcopy','-O','binary','-j','.rdata',str(obj),str(abi)]);abi_values=list(struct.unpack('<11Q',abi.read_bytes()))
  ds=run(['nm','-g','--defined-only',str(obj)]);defined.update(line.split()[-1] for line in ds.splitlines() if line.strip())
  syms=run(['nm','-u',str(obj)]);undefined.update(line.split()[-1] for line in syms.splitlines() if line.strip())
 assert abi_values==list(map(int,re.search(r'abi=([0-9,]+)',result)[1].split(',')))
 (out/'host.log').write_text('\n'.join(logs))
 assert all(sha(REF/n)==h for n,h in inputs.items());assert all(sha(MONO/n)==h for n,h in MP.items());assert all(sha(ROOT/n)==h for n,h in local.items())
 report={'status':'NOISE-NATIVE-PORT-BOUNDED-OWNED-MODEL-ASAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',result)[1]),'quarantine_modes':list(quarantine),'noise_commit':COMMIT,'reference_sha256':inputs,'monocypher_sha256':MP,'source_sha256':local,'coff_objects':coff,'coff_port_layout_abi_values':abi_values,'coff_text_sum_unlinked':sum(z['text'] for z in coff.values()),'coff_data_sum_unlinked':sum(z['data'] for z in coff.values()),'coff_bss_sum_unlinked':sum(z['bss'] for z in coff.values()),'coff_undefined_symbols_before_full_link':sorted(undefined),'coff_unresolved_after_object_definition_match':sorted(undefined-defined),'host_log_sha256':sha(out/'host.log'),'arena_slot_count':64,'arena_slot_bytes':512,'arena_bytes':32768,'no_slot_reuse_inside_epoch':True,'no_unix_rng_compiled':True,'noise_handshake_modified':False,'rng_port_version':2,'actual_provider_approved':False,'whole_efi_linked':False,'actual_target_abi_verified':False,'physical_owner_inventory_complete':False,'physical_pin_verified':False,'owner_auth_or_credentials':False,'device_operations':False,'native54_payload':187392,'efi_limit':262144}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.strip());print('quarantine modes PASS',list(quarantine));print('COFF',len(coff),'objects PASS; full EFI not linked')
if __name__=='__main__':main()
