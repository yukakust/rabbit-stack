"""Exact upstream packed-field oracle, only compiled on Yukabox."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parent
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'runs/host';out.mkdir(parents=True,exist_ok=True)
 pins={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and 'runs' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts}
 h=(ROOT/'references/htt.h').read_text();ie=(ROOT/'references/ieee80211.h').read_text()
 assert '#define ATH10K_MAX_NUM_PEER_IDS (1 << 11)' in (ROOT/'references/core.h').read_text()
 structs='\n'.join(re.search(r'struct '+n+r'\s*\{.*?\n\} __packed;',h,re.S)[0] for n in ['htt_resp_hdr','htt_rx_peer_map','htt_rx_peer_unmap','htt_security_indication'])
 # Direct field lists from exact primary anonymous management bodies.
 bodies=[]
 for n in ['auth','assoc_resp']:
  m=re.search(r'struct \{([^{}]*?)\} __packed '+n+r'(?:;|,)',ie,re.S);assert m
  bodies.append('struct oracle_'+n+' {'+m[1]+'} __packed;')
 oracle=out/'oracle.c';oracle.write_text('''#include <stdint.h>
#include <stddef.h>
#include <string.h>
#define u8 uint8_t
#define __le16 uint16_t
#define __packed __attribute__((packed))
'''+structs+'\n'+'\n'.join(bodies)+'''
_Static_assert(sizeof(struct htt_resp_hdr)==1&&sizeof(struct htt_rx_peer_map)==11&&sizeof(struct htt_rx_peer_unmap)==3&&sizeof(struct htt_security_indication)==27,"actual HTT body sizes");
_Static_assert(offsetof(struct htt_rx_peer_map,peer_id)==1&&offsetof(struct htt_rx_peer_map,addr)==3&&offsetof(struct htt_security_indication,peer_id)==1,"actual HTT body offsets");
_Static_assert(sizeof(struct oracle_auth)==6&&offsetof(struct oracle_auth,status_code)==4&&offsetof(struct oracle_assoc_resp,aid)==4,"actual management body offsets");
void oracle_peer(uint8_t*out,unsigned vdev,unsigned id,const uint8_t*addr){struct htt_resp_hdr h={3};struct htt_rx_peer_map m={.vdev_id=(uint8_t)vdev,.peer_id=(uint16_t)id};memcpy(m.addr,addr,6);memcpy(out,&h,1);memcpy(out+1,&m,sizeof(m));}
void oracle_sec(uint8_t*out,unsigned flags,unsigned id){struct htt_resp_hdr h={11};struct htt_security_indication m={0};m.flags=(uint8_t)flags;m.peer_id=(uint16_t)id;memcpy(out,&h,1);memcpy(out+1,&m,sizeof(m));}
''')
 flags=['-Wall','-Wextra','-Werror','-I'+str(ROOT/'abi'),'-I'+str(ROOT/'copied')]
 sources=[ROOT/'station.c',ROOT/'copied/htc_wire.c']
 subprocess.run([str(CC),'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,*map(str,sources),str(ROOT/'test_station.c'),str(oracle),'-o',str(out/'test')],check=True)
 p=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=90);(out/'host.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stdout+p.stderr
 for s in sources:subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os',*flags,'-c',str(s),'-o',str(out/(s.stem+'.obj'))],check=True)
 assert all(sha(ROOT/n)==h for n,h in pins.items())
 report={'status':'STATION-OWNED-PRIMARY-ORACLE-ASAN-UBSAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',p.stdout)[1]),'build_host':'yukabox','source_sha256':pins,'oracle_sha256':sha(oracle),'compiler_sha256':sha(CC),'host_log_sha256':sha(out/'host.log'),'executable_sha256':sha(out/'test'),'coff_sha256':{p.name:sha(p) for p in out.glob('*.obj')},'native_integrated':False,'native_capabilities_proven':False,'physical_verified':False,'credential_reads':0,'rf_admission_granted':False,'controlled_port_is_actual_open':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(p.stdout.strip());print(report['status'])
if __name__=='__main__':main()
