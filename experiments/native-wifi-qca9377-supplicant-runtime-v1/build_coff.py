#!/usr/bin/env python3
"""Remote-only actual object compilation; missing implementations remain unresolved."""
import pathlib,subprocess,json,hashlib,shutil,os,argparse
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--clang',required=True);p.add_argument('--reference',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
r=pathlib.Path(__file__).resolve().parent;o=a.output.resolve();assert str(o).startswith('/home/yuka/rabbit-world/parallel-supplicant-runtime-v1/');o.mkdir(parents=True,exist_ok=True)
s=o/'tree';shutil.copytree(a.reference/'wpa_supplicant-2.11/src',s,dirs_exist_ok=True)
inc=s/'utils/includes.h';old=inc.read_text();idx=old.index('#include <stdlib.h>');inc.write_text(old[:idx]+'#ifdef RABBIT_FREESTANDING\n#include "native_abi.h"\n#else\n'+old[idx:].rsplit('#endif /* INCLUDES_H */',1)[0]+'#endif /* RABBIT_FREESTANDING */\n#endif /* INCLUDES_H */\n');shutil.copyfile(r/'native_abi.h',s/'utils/native_abi.h')
units=['rsn_supp/wpa.c','rsn_supp/wpa_ie.c','rsn_supp/pmksa_cache.c','common/wpa_common.c','utils/common.c','utils/wpabuf.c','common/ieee802_11_common.c','crypto/aes-internal.c','crypto/aes-internal-enc.c','crypto/aes-internal-dec.c','crypto/aes-wrap.c','crypto/aes-unwrap.c','crypto/aes-omac1.c','crypto/sha1.c','crypto/sha1-internal.c','crypto/sha1-pbkdf2.c','crypto/sha256.c','crypto/sha256-internal.c','crypto/md5.c','crypto/md5-internal.c','crypto/rc4.c','crypto/sha1-prf.c','crypto/sha256-prf.c','crypto/sha1-tprf.c']
tmp=o/'tmp';tmp.mkdir(exist_ok=True);env=os.environ.copy();env['TMPDIR']=str(tmp)
flags=['-I'+str(r),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-builtin','-fno-stack-protector','-Os','-DRABBIT_FREESTANDING','-DOS_NO_C_LIB_DEFINES','-DCONFIG_NO_STDOUT_DEBUG','-DCONFIG_NO_WPA_MSG','-DCONFIG_NO_TKIP','-DCONFIG_NO_RANDOM_POOL','-DCONFIG_SHA256','-DCONFIG_CRYPTO_INTERNAL','-isystem',str(s),'-isystem',str(s/'utils')]
logs=[];results=[]
for i,n in enumerate(units):
 out=o/f'{i}.obj';cmd=[a.clang,*flags,*(['-DIEEE8021X_EAPOL'] if n=='rsn_supp/pmksa_cache.c' else []),'-c',str(s/n),'-o',str(out)];q=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=60);logs.extend([json.dumps(cmd),q.stdout,q.stderr]);results.append({'source':n,'source_sha256':h(s/n),'returncode':q.returncode,'object_sha256':h(out) if q.returncode==0 else None})
for n in ['runtime.c','primitives.c','adapter.c']:
 out=o/(n+'.obj');q=subprocess.run([a.clang,*flags,'-Wall','-Wextra','-Werror','-c',str(r/n),'-o',str(out)],capture_output=True,text=True,env=env,timeout=60);logs.extend([n,q.stdout,q.stderr]);assert not q.returncode,q.stderr
(o/'compile.log').write_text('\n'.join(logs))
objs=[o/f'{i}.obj' for i,x in enumerate(results) if x['returncode']==0]+[o/(n+'.obj') for n in ['runtime.c','primitives.c','adapter.c']];nm=subprocess.run(['nm','-u',*[str(x) for x in objs]],capture_output=True,text=True);(o/'undefined.log').write_text(nm.stdout+nm.stderr)
allnm=subprocess.run(['nm',*[str(x) for x in objs]],capture_output=True,text=True);defined=set();undefined=set()
for line in allnm.stdout.splitlines():
 fields=line.split()
 if len(fields)==2 and fields[0]=='U':undefined.add(fields[1])
 elif len(fields)>=3 and fields[-2] in {'T','D','B','R'}:defined.add(fields[-1])
size=subprocess.run(['size',*[str(x) for x in objs]],capture_output=True,text=True);(o/'size.log').write_text(size.stdout+size.stderr)
section_totals={'text':0,'data':0,'bss':0}
for line in size.stdout.splitlines()[1:]:
 fields=line.split()
 if len(fields)>=6:
  for key,value in zip(section_totals,fields[:3]):section_totals[key]+=int(value)
lld=pathlib.Path(a.clang).with_name('lld');cmd=[str(lld),'-flavor','link','/dll','/noentry','/nodefaultlib','/include:wpa_sm_init','/include:wpa_sm_rx_eapol','/export:wpa_sm_init','/export:wpa_sm_rx_eapol','/export:rsn_runtime_bind','/export:rsn_runtime_poll','/export:rsn_runtime_revoke','/export:rsn_native_ctx','/export:rsn_runtime_sizes','/out:'+str(o/'runtime.dll'),*[str(x) for x in objs]];q=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=60);(o/'link-attempt.log').write_text(json.dumps(cmd)+'\n'+q.stdout+q.stderr);assert q.returncode==0,q.stdout+q.stderr
image=o/'runtime.dll';data=image.read_bytes();import struct
pe=struct.unpack_from('<I',data,0x3c)[0];opt=pe+24;assert data[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<H',data,opt)[0]==0x20b
size_image=struct.unpack_from('<I',data,opt+56)[0];directories=opt+112;
section_count=struct.unpack_from('<H',data,pe+6)[0];section_at=opt+struct.unpack_from('<H',data,pe+20)[0]
def offset(rva):
 for j in range(section_count):
  at=section_at+40*j;virtual,base,raw,ptr=struct.unpack_from('<IIII',data,at+8)
  if base<=rva<base+raw:return ptr+rva-base
 raise AssertionError('RVA outside owned file sections')
export_rva=struct.unpack_from('<I',data,directories)[0];export=offset(export_rva);count=struct.unpack_from('<I',data,export+24)[0];names,ordinals=struct.unpack_from('<II',data,export+32);functions=struct.unpack_from('<I',data,export+28)[0];runtime_sizes=None
for j in range(count):
 name=offset(struct.unpack_from('<I',data,offset(names)+4*j)[0]);end=data.index(0,name)
 if data[name:end]==b'rsn_runtime_sizes':
  ordinal=struct.unpack_from('<H',data,offset(ordinals)+2*j)[0];rva=struct.unpack_from('<I',data,offset(functions)+4*ordinal)[0];runtime_sizes=struct.unpack_from('<II',data,offset(rva));break
assert runtime_sizes and runtime_sizes[0]<16384 and runtime_sizes[1]<1024
assert struct.unpack_from('<II',data,directories+8)==(0,0),'OS import table must be empty'
report={'platform_object_sha256':{n:h(o/(n+'.obj')) for n in ['runtime.c','primitives.c','adapter.c']},'external_runtime_bytes':runtime_sizes[0],'external_native_io_bytes':runtime_sizes[1],'image_sha256':h(image),'file_bytes':len(data),'size_of_image':size_image,'OS_import_directory':False,'external_arena_bytes_max':1048576,'integrated_radio_image':False,'status':'FREESTANDING-SUPPLICANT-RUNTIME-COFF-LINKED','units':results,'successful_units':len(objs),'required_units':len(units)+3,'mature_units':len(units),'platform_units':3,'source_tree_sha256':{str(f.relative_to(s)):h(f) for f in sorted(s.rglob('*')) if f.is_file()},'boundary_headers_sha256':h(r/'native_abi.h'),'compile_log_sha256':h(o/'compile.log'),'undefined_log_sha256':h(o/'undefined.log'),'local_sources':{n:h(r/n) for n in ['build_coff.py','native_abi.h','runtime.c','runtime.h','primitives.c','adapter.c','adapter.h']},'unresolved_after_combining_units':sorted(undefined-defined),'object_section_totals':section_totals,'final_image_size_proven':False,'size_log_sha256':h(o/'size.log'),'actual_link_attempt_returncode':q.returncode,'link_attempt_log_sha256':h(o/'link-attempt.log'),'linked':True,'physical_verified':False,'fake_implementations':False,'native_admitted':False}
(o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('COFF',len(objs),'/',len(units));print('REPORT',h(o/'report.json'));print('\n'.join(logs)[-3000:])
