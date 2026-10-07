import argparse,hashlib,json,re,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--clang',required=True);a.add_argument('--reference',type=Path,required=True);a.add_argument('--session',type=Path,required=True);a.add_argument('--output',type=Path,required=True);x=a.parse_args();o=x.output;o.mkdir(parents=True,exist_ok=True)
 pins=json.loads((P/'references.json').read_text())['files'];assert all(sha(x.reference/n)==h for n,h in pins.items())
 h=(x.reference/'htt.h').read_text();hw=(x.reference/'hw.h').read_text()
 enums='\n'.join(re.search(r'enum '+n+r'\s*\{.*?\};',h,re.S)[0] for n in ['htt_h2t_msg_type','htt_tlv_t2h_msg_type'])
 structs='\n'.join(re.search(r'struct '+n+r'\s*\{.*?\} __packed;',h,re.S)[0] for n in ['htt_cmd_hdr','htt_ver_req','htt_resp_hdr','htt_ver_resp'])
 # No copied simulator protocol layout: headers and member offsets come from pinned upstream.
 oracle=o/'oracle.c';oracle.write_text("""#include <stdint.h>
#include <string.h>
#define u8 uint8_t
#define u32 uint32_t
#define __packed __attribute__((packed))
"""+enums+'\n'+structs+'\n'+re.search(r'enum ath10k_fw_htt_op_version\s*\{.*?\};',hw,re.S)[0]+"""
_Static_assert(ATH10K_FW_HTT_OP_VERSION_TLV==3,"op version");
unsigned ref_req(uint8_t*p){struct {struct htt_cmd_hdr hdr;struct htt_ver_req ver_req;} __packed v={0};v.hdr.msg_type=HTT_H2T_MSG_TYPE_VERSION_REQ;memcpy(p,&v,sizeof v);return sizeof v;}
void ref_conf(uint8_t*p,unsigned major,unsigned minor){struct {struct htt_resp_hdr hdr;struct htt_ver_resp ver_resp;} __packed v={0};v.hdr.msg_type=HTT_TLV_T2H_MSG_TYPE_VERSION_CONF;v.ver_resp.major=major;v.ver_resp.minor=minor;_Static_assert(sizeof v==4,"version layout");memcpy(p,&v,sizeof v);}
""")
 inputs={n:sha(P/n) for n in ['version.c','version.h','version_test.c','verify.py','references.json','integration-inputs.json','README.md']};deps={n:sha(x.session/n) for n in ['htc_session.h','htc_wire.h']}
 subprocess.run([x.clang,'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(P),'-I'+str(x.session),str(P/'version.c'),str(P/'version_test.c'),str(oracle),'-o',str(o/'test')],check=True)
 r=subprocess.run([str(o/'test')],capture_output=True,text=True,timeout=60);(o/'host.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 subprocess.run([x.clang,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(P),'-I'+str(x.session),'-c',str(P/'version.c'),'-o',str(o/'version.obj')],check=True)
 assert all(sha(P/n)==v for n,v in inputs.items());assert all(sha(x.session/n)==v for n,v in deps.items())
 report={'status':'HTT-VERSION-NEGOTIATED-BINDING-ASAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',r.stdout)[1]),'build_host':'yukabox','source_sha256':inputs,'dependency_sha256':deps,'reference_sha256':pins,'oracle_sha256':sha(oracle),'host_log_sha256':sha(o/'host.log'),'physical_verified':False,'native_integrated':False,'request_sent':False,'htt_dataplane_ready':False}
 (o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip())
if __name__=='__main__':main()
