"""Pinned upstream layout/assignments oracle; native builds only Yukabox."""
import hashlib,json,re,subprocess,argparse
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--clang',required=True);a.add_argument('--reference',type=Path,required=True);a.add_argument('--output',type=Path,required=True);x=a.parse_args()
 pin=json.loads((P/'references.json').read_text());ref=x.reference;out=x.output;out.mkdir(parents=True,exist_ok=True)
 assert all(sha(ref/n)==v for n,v in pin['files'].items())
 h=(ref/'wmi-tlv.h').read_text();w=(ref/'wmi.h').read_text();c=(ref/'wmi-tlv.c').read_text()
 enums='\n'.join(re.search(r'enum '+n+r'\s*\{.*?\};',h,re.S)[0] for n in ['wmi_tlv_grp_id','wmi_tlv_cmd_id','wmi_tlv_tag'])
 enums+='\n'+re.search(r'enum wmi_peer_type\s*\{.*?\};',w,re.S)[0]
 structs=re.search(r'struct wmi_mac_addr\s*\{.*?\n\} __packed;',w,re.S)[0]+'\n'+re.search(r'struct wmi_tlv_peer_create_cmd\s*\{.*?\n\} __packed;',h,re.S)[0]
 fun=c[c.index('ath10k_wmi_tlv_op_gen_peer_create('):];assign=fun[fun.index('cmd->vdev_id ='):fun.index('ath10k_dbg')]
 oracle=out/'reference.c';oracle.write_text("""#include <stdint.h>
#include <string.h>
#define __le32 uint32_t
#define u8 uint8_t
#define u32 uint32_t
#define __packed __attribute__((packed))
#define __cpu_to_le32(x) (x)
#define ether_addr_copy(a,b) memcpy(a,b,6)
#define WMI_TLV_CMD(grp_id) (((grp_id)<<12)|1)
"""+enums+'\n'+structs+"""
static void put(uint8_t*p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(8*j));}
unsigned reference(uint8_t*out,unsigned vdev_id,const uint8_t peer_addr[6]){
 struct wmi_tlv_peer_create_cmd value={0},*cmd=&value;
 enum wmi_peer_type peer_type=WMI_PEER_TYPE_DEFAULT;
 _Static_assert(sizeof(value)==16,"peer size");
 """+assign+"""
 put(out,WMI_TLV_PEER_CREATE_CMDID);put(out+4,sizeof(value)|(WMI_TLV_TAG_STRUCT_PEER_CREATE_CMD<<16));memcpy(out+8,&value,sizeof(value));return 24;
}
""")
 sources={n:sha(P/n) for n in ['peer_wire.c','peer_wire.h','peer_test.c','verify.py','references.json','README.md']}
 subprocess.run([x.clang,'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(P),str(P/'peer_wire.c'),str(P/'peer_test.c'),str(oracle),'-o',str(out/'peer-test')],check=True)
 result=subprocess.run([str(out/'peer-test')],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 subprocess.run([x.clang,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(P),'-c',str(P/'peer_wire.c'),'-o',str(out/'peer_wire.obj')],check=True)
 assert sources=={n:sha(P/n) for n in sources}
 report={'status':'STA-PEER-CREATE-PINNED-ASAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',result.stdout)[1]),'build_host':'yukabox','source_sha256':sources,'reference_sha256':pin['files'],'oracle_sha256':sha(oracle),'host_log_sha256':sha(out/'host.log'),'physical_verified':False,'native_integrated':False,'command_sent':False,'association_complete':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.stdout.strip())
if __name__=='__main__':main()
