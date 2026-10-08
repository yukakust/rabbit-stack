#!/usr/bin/env python3
"""Yukabox-only real pinned Linux oracle, ASAN/UBSAN and actual COFF objects."""
import pathlib,hashlib,json,re,subprocess,os,argparse
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
PINS={'wmi.h':'fff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c','wmi-tlv.h':'16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9','wmi-tlv.c':'02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb','wmi.c':'68a4fedc3d0cd815c209dda9c0eb3aa3869bd3d35847c633e0c458ba53c320f4'}
def extract(text,kind,name):
 m=re.search(r'\b'+kind+r'\s+'+name+r'\s*\{',text);assert m;at=m.end();depth=1
 while depth:
  if text[at]=='{':depth+=1
  if text[at]=='}':depth-=1
  at+=1
 return text[m.start():text.index(';',at)+1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--reference',type=pathlib.Path,required=True);p.add_argument('--clang',required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();r=pathlib.Path(__file__).resolve().parent;o=a.output.resolve();assert str(o).startswith('/home/yuka/rabbit-world/parallel-filter-barrier-v1/');o.mkdir(parents=True,exist_ok=True);tmp=o/'tmp';tmp.mkdir(exist_ok=True);env=os.environ.copy();env['TMPDIR']=str(tmp)
 for n,s in PINS.items():assert h(a.reference/n)==s,n
 tlv=(a.reference/'wmi-tlv.h').read_text();wmi=(a.reference/'wmi.h').read_text();ops=(a.reference/'wmi-tlv.c').read_text().split('static const struct wmi_ops wmi_tlv_ops',1)[1].split('};',1)[0];assert '.gen_pdev_set_base_macaddr' not in ops
 wrapper=pathlib.Path('/home/yuka/rabbit-world/parallel-filter-barrier-v1/reference/wmi-ops.h');assert 'if (!ar->wmi.ops->gen_pdev_set_base_macaddr)\n\t\treturn -EOPNOTSUPP;' in wrapper.read_text()
 oracle='/* Extracted ISC-licensed Linux ath10k pinned definitions; upstream notices retained in README. */\n#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\ntypedef uint8_t u8;typedef uint32_t u32;typedef uint32_t __le32;typedef uint16_t __le16;\n#define __packed __attribute__((packed))\n#define WMI_TLV_CMD(g) (((g)<<12)|1)\n#define WMI_TLV_EV(g) (((g)<<12)|1)\n'
 for n in ['wmi_tlv_grp_id','wmi_tlv_cmd_id','wmi_tlv_event_id','wmi_tlv_tag']:oracle+=extract(tlv,'enum',n)+'\n'
 for n in ['wmi_cmd_hdr','wmi_mac_addr','wmi_vdev_create_cmd','wmi_vdev_delete_cmd','wmi_echo_cmd','wmi_echo_event']:oracle+=extract(wmi,'struct',n)+'\n'
 oracle+=extract(tlv,'struct','wmi_tlv')+'\n'+extract(wmi,'enum','wmi_vdev_type')+'\n'
 oracle+='''
static unsigned ref_wire(unsigned step,uint8_t*out,const uint8_t mac[6],uint32_t arg){
 struct wmi_cmd_hdr h={0};struct wmi_tlv t={0};
 if(step==0){struct wmi_vdev_create_cmd c={0};_Static_assert(sizeof(c)==20,"CREATE body size");h.cmd_id=WMI_TLV_VDEV_CREATE_CMDID;t.tag=WMI_TLV_TAG_STRUCT_VDEV_CREATE_CMD;t.len=sizeof(c);c.vdev_type=WMI_VDEV_TYPE_STA;memcpy(c.vdev_macaddr.addr,mac,6);memcpy(out,&h,sizeof(h));memcpy(out+sizeof(h),&t,sizeof(t));memcpy(out+sizeof(h)+sizeof(t),&c,sizeof(c));return sizeof(h)+sizeof(t)+sizeof(c);}
 if(step==1){struct wmi_vdev_delete_cmd c={0};_Static_assert(sizeof(c)==4,"DELETE body size");h.cmd_id=WMI_TLV_VDEV_DELETE_CMDID;t.tag=WMI_TLV_TAG_STRUCT_VDEV_DELETE_CMD;t.len=sizeof(c);memcpy(out,&h,sizeof(h));memcpy(out+sizeof(h),&t,sizeof(t));memcpy(out+sizeof(h)+sizeof(t),&c,sizeof(c));return sizeof(h)+sizeof(t)+sizeof(c);}
 struct wmi_echo_cmd c={0};_Static_assert(sizeof(c)==4,"ECHO body size");h.cmd_id=WMI_TLV_ECHO_CMDID;t.tag=WMI_TLV_TAG_STRUCT_ECHO_CMD;t.len=sizeof(c);c.value=arg;memcpy(out,&h,sizeof(h));memcpy(out+sizeof(h),&t,sizeof(t));memcpy(out+sizeof(h)+sizeof(t),&c,sizeof(c));return sizeof(h)+sizeof(t)+sizeof(c);
}

'''
 (o/'oracle.h').write_text(oracle);sources=[r/'filter_barrier.c',*[r/'dependencies'/n for n in ['htc_wire.c','htc_credit.c','wmi_boot_info.c','wmi_scan.c']]];logs=[]
 def run(c):
  q=subprocess.run(c,capture_output=True,text=True,env=env,timeout=60);logs.extend([json.dumps(c),q.stdout,q.stderr]);assert q.returncode==0,q.stdout+q.stderr;return q
 inputs={str(f.relative_to(r)):h(f) for f in [r/'filter_barrier.c',r/'filter_barrier.h',r/'filter_test.c',r/'verify.py',r/'dependency-inputs.json',*sorted((r/'dependencies').glob('*'))]};flags=['-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-I',str(r),'-I',str(r/'dependencies'),'-I',str(o)]
 run([a.clang,*flags,'-fsanitize=address,undefined',*[str(f) for f in sources],str(r/'filter_test.c'),'-o',str(o/'test')]);result=run([str(o/'test')]).stdout.strip();assert 'synthetic only' in result
 objs=[]
 for i,f in enumerate(sources):
  obj=o/f'{i}.obj';run([a.clang,*flags,'-Os','-target','x86_64-pc-win32-coff','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-c',str(f),'-o',str(obj)]);objs.append(obj)
 (o/'host.log').write_text('\n'.join(logs));assert inputs=={n:h(r/n) for n in inputs};report={'status':'FILTER-BARRIER-PINNED-WIRE-BODY-ONLY-SHARED-LEDGER-ASAN-COFF-PASS','result':result,'source_sha256':inputs,'reference_sha256':{**PINS,'wmi-ops.h':h(wrapper)},'oracle_sha256':h(o/'oracle.h'),'host_log_sha256':h(o/'host.log'),'COFF_objects_sha256':{f.name:h(f) for f in objs},'credit_writers_in_coordinator':False,'persistentTX_owner_required':True,'RX_credits_already_applied':True,'ECHO_raw_required':True,'ECHO_dma_required':True,'baseMAC_TLV_supported':False,'all3_commands_actual_oracle_joined':True,'device_operations':0,'key_accesses':0,'state_operations':0,'physical_verified':False,'native_candidate':False,'signing_admitted':False,'complete_startup':False,'SSID_observed':False,'data_plane_ready':False};(o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result);print('REPORT',h(o/'report.json'))
if __name__=='__main__':main()
