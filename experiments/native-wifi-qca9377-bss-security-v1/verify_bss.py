"""Yukabox: exact mature extraction + independent original upstream oracle."""
import hashlib,json,re,subprocess
from pathlib import Path
import make_rsn_core as make
ROOT=Path(__file__).resolve().parent;TREE=make.references();SESSION=ROOT.parent/'native-wifi-qca9377-session-v1';BEACON=ROOT.parent/'native-wifi-qca9377-beacon-rx-v1'
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert (ROOT/'rsn_core.c').read_text()==make.core();assert (ROOT/'HOSTAP-LICENSE.txt').read_text()==make.license()
 out=ROOT/'runs/host';out.mkdir(parents=True,exist_ok=True)
 (out/'oracle.c').write_text('''#include "utils/includes.h"
#include "utils/common.h"
#include "common/wpa_common.h"
#include "utils/wpa_debug.h"
#include "rsn_core.h"
void wpa_printf(int level,const char*fmt,...){(void)level;(void)fmt;}
void wpa_hexdump(int level,const char*title,const void*buf,size_t n){(void)level;(void)title;(void)buf;(void)n;}
int oracle_rsn(const uint8_t*p,unsigned n,QcaRsnFields*out){struct wpa_ie_data d;if(wpa_parse_wpa_ie_rsn(p,n,&d))return 0;QcaRsnFields v={.proto=d.proto,.group=d.group_cipher,.pairwise=d.pairwise_cipher,.akm=d.key_mgmt,.capabilities=d.capabilities,.pmkids=(uint32_t)d.num_pmkid,.management_group=d.mgmt_group_cipher,.has_group=d.has_group,.has_pairwise=d.has_pairwise};*out=v;return 1;}
''')
 defs=['-DCONFIG_SAE','-DCONFIG_IEEE80211R','-DCONFIG_SHA384','-DCONFIG_OWE','-DCONFIG_DPP','-DCONFIG_PASN']
 sources=[ROOT/'bss_security.c',ROOT/'rsn_core.c',BEACON/'beacon_rx.c',SESSION/'beacon_info.c']
 inputs=sources+[ROOT/n for n in ['bss_security.h','rsn_core.h','bss_test.c','make_rsn_core.py','verify_bss.py','README.md','HOSTAP-LICENSE.txt']]+[BEACON/'beacon_rx.h',SESSION/'beacon_info.h']
 hashes={str(p.relative_to(ROOT.parent)):sha(p) for p in inputs}
 flags=['-Wall','-Wextra','-Werror',*['-I'+str(p) for p in [ROOT,BEACON,SESSION]],'-isystem',str(TREE/'src'),'-isystem',str(TREE/'src/utils')]
 subprocess.run([str(CC),'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-ffunction-sections','-fdata-sections',*defs,*flags,'-Wno-unused-parameter','-c',str(TREE/'src/common/wpa_common.c'),'-o',str(out/'upstream.o')],check=True)
 subprocess.run([str(CC),'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-ffunction-sections','-fdata-sections',*defs,*flags,*map(str,sources),str(ROOT/'bss_test.c'),str(out/'oracle.c'),str(out/'upstream.o'),'-Wl,--gc-sections','-o',str(out/'test')],check=True)
 r=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 for name in ['bss_security','rsn_core']:
  subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os',*flags,'-c',str(ROOT/(name+'.c')),'-o',str(out/(name+'.obj'))],check=True)
 assert all(sha(ROOT.parent/n)==h for n,h in hashes.items())
 report={'status':'COPIED-BSS-LEGACY-PSK-CCMP-UPSTREAM-ORACLE-ASAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',r.stdout)[1]),'build_host':'yukabox','source_sha256':hashes,'hostap_release':'2.11','archive_sha256':make.ARCHIVE_SHA,'upstream_oracle_sha256':sha(TREE/'src/common/wpa_common.c'),'oracle_adapter_sha256':sha(out/'oracle.c'),'host_log_sha256':sha(out/'host.log'),'candidate_is_authentication':False,'credential_reads':0,'native_integrated':False,'physical_verified':False,'rf_admission_granted':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip());print(report['status'])
if __name__=='__main__':main()
