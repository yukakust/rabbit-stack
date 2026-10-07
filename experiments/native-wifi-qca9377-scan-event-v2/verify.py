"""Pinned Linux prefix oracle and actual physical54 bytes; Yukabox only."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PIN={'wmi-tlv.c':'02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb','wmi.h':'fff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--clang',required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--session',type=Path,required=True);p.add_argument('--regression',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();o=a.output;o.mkdir(parents=True,exist_ok=True)
 assert all(sha(a.reference/n)==v for n,v in PIN.items())
 c=(a.reference/'wmi-tlv.c').read_text();h=(a.reference/'wmi.h').read_text()
 assert re.search(r'\[WMI_TLV_TAG_STRUCT_SCAN_EVENT\]\s*= \{ \.min_len = sizeof\(struct wmi_scan_event\)',c)
 fields=re.search(r'struct wmi_scan_event\s*\{.*?\} __packed;',h,re.S)[0]
 oracle=o/'oracle.c';oracle.write_text('#include "scan_event_v2.h"\n#include <string.h>\n#define __le32 uint32_t\n#define __packed __attribute__((packed))\n'+fields+'''
_Static_assert(sizeof(struct wmi_scan_event)==24,"upstream prefix");
unsigned reference(const uint8_t*p,unsigned n,QcaWmiScanEvent*out){
 if(n<32)return 0;unsigned length=p[4]|((unsigned)p[5]<<8);if(length<sizeof(struct wmi_scan_event)||length>n-8)return 0;
 struct wmi_scan_event ev;memcpy(&ev,p+8,sizeof ev);
 out->type=ev.event_type;out->reason=ev.reason;out->frequency=ev.channel_freq;out->request_id=ev.scan_req_id;out->scan_id=ev.scan_id;out->vdev=ev.vdev_id;return 1;
}
''')
 data=json.loads(a.regression.read_text());cases=[v for v in data['slots'] if v['event']==0x3001];assert len(cases)==2
 regression=o/'regression.c';body='#include "scan_event_v2.h"\n#include <assert.h>\n#include <string.h>\nunsigned reference(const uint8_t*,unsigned,QcaWmiScanEvent*);\nunsigned physical_regression(void){unsigned count=0;\n'
 for i,item in enumerate(cases):
  packet=bytes.fromhex(item['payload_hex']);assert hashlib.sha256(packet).hexdigest()==item['payload_sha256'];assert len(packet)==36
  body+='const uint8_t p'+str(i)+'[]={'+','.join(str(n) for n in packet)+'};QcaWmiScanEvent a'+str(i)+',b'+str(i)+';assert(qca_scan_event_v2(p'+str(i)+',sizeof p'+str(i)+',&a'+str(i)+')==1);assert(reference(p'+str(i)+',sizeof p'+str(i)+',&b'+str(i)+'));assert(!memcmp(&a'+str(i)+',&b'+str(i)+',sizeof a'+str(i)+'));assert(qca_scan_event_v2_match(p'+str(i)+',sizeof p'+str(i)+',7,8,&a'+str(i)+'));assert(a'+str(i)+'.reason==6);count+=5;\n'
 regression.write_text(body+'return count;}\n')
 sources={p.name:sha(p) for p in ROOT.iterdir() if p.is_file()};deps={n:sha(a.session/n) for n in ['wmi_scan.c','wmi_scan.h']}
 files=[ROOT/'scan_event_v2.c',ROOT/'event_test.c',a.session/'wmi_scan.c',oracle,regression]
 subprocess.run([a.clang,'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(ROOT),'-I'+str(a.session),*map(str,files),'-o',str(o/'test')],check=True)
 r=subprocess.run([str(o/'test')],capture_output=True,text=True,timeout=60);(o/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 subprocess.run([a.clang,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT),'-I'+str(a.session),'-c',str(ROOT/'scan_event_v2.c'),'-o',str(o/'scan_event_v2.obj')],check=True)
 assert sources=={p.name:sha(p) for p in ROOT.iterdir() if p.is_file()};assert all(sha(a.session/n)==v for n,v in deps.items())
 report={'status':'SCAN-EVENT-V2-PINNED-MIN-PREFIX-OPAQUE-REASON-ASAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',r.stdout)[1]),'build_host':'yukabox','source_sha256':sources,'dependency_sha256':deps,'reference_sha256':PIN,'physical54_regression_sha256':sha(a.regression),'oracle_sha256':sha(oracle),'host_log_sha256':sha(o/'host.log'),'physical_verified':False}
 (o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['checks'])
if __name__=='__main__':main()
