"""Independent pinned Linux structs/assignments and ASAN/COFF, Yukabox only."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REF=Path('/home/yuka/rabbit-world/wmi-init-next/reference');EXTRA=Path('/home/yuka/rabbit-world/parallel-scan-native-plan-v1/reference')
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
PINS={'wmi-tlv.c':'02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb','wmi-tlv.h':'16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9','wmi.h':'fff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c'}
EPINS={'ath10k-mac.c':'e99b6749933719a39037645385ea88be181b380f1135d62aea07c0b474a8236c','ath10k-wmi.c':'68a4fedc3d0cd815c209dda9c0eb3aa3869bd3d35847c633e0c458ba53c320f4'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert all(sha(REF/n)==h for n,h in PINS.items());assert all(sha(EXTRA/n)==h for n,h in EPINS.items())
 out=ROOT/'runs/host';out.mkdir(parents=True,exist_ok=True)
 oracle='''#include "channel_wire.h"
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#define u8 uint8_t
#define u32 uint32_t
#define __le32 uint32_t
#define __packed __attribute__((packed))
#define __cpu_to_le32(n) (n)
#define WMI_TLV_CMD(g) (((g)<<12)|1)
'''
 for fn,kind,names in [('wmi-tlv.h','enum',['wmi_tlv_grp_id','wmi_tlv_cmd_id','wmi_tlv_tag']),('wmi.h','enum',['wmi_phy_mode']),('wmi.h','struct',['wmi_channel','wmi_channel_arg']),('wmi-tlv.h','struct',['wmi_tlv_scan_chan_list_cmd','wmi_tlv_pdev_set_rd_cmd'])]:
  for name in names:oracle+=re.search(kind+' '+name+r'\s*\{.*?^\}[^;]*;',(REF/fn).read_text(),re.S|re.M)[0]+'\n'
 text=(REF/'wmi.h').read_text()
 for macro in ['WMI_CHAN_FLAG_PASSIVE','WMI_CHAN_FLAG_ADHOC_ALLOWED','WMI_CHAN_FLAG_ALLOW_HT','WMI_CHAN_FLAG_ALLOW_VHT','WMI_CHAN_FLAG_HT40_PLUS','WMI_CHAN_FLAG_DFS']:
  oracle+=re.search(r'^#define '+macro+r'\b[^\n]*',text,re.M)[0]+'\n'
 wmi=(EXTRA/'ath10k-wmi.c').read_text();a=wmi.index('void ath10k_wmi_put_wmi_channel(');b=wmi.index('int ath10k_wmi_wait_for_service_ready',a);body=wmi[a:b]
 prefix=body[body.index('if (arg->passive)'):body.index('if (arg->mode == MODE_11AC_VHT80_80)')]
 suffix=body[body.index('ch->min_power ='):body.rindex('}')]
 mac=(EXTRA/'ath10k-mac.c').read_text();a=mac.index('static int ath10k_update_channel_list(');b=mac.index('static enum wmi_dfs_region',a);part=mac[a:b]
 powers=part[part.index('ch->min_power = 0;'):part.index('/* FIXME: why use only legacy modes')]
 tlv=(REF/'wmi-tlv.c').read_text();a=tlv.index('ath10k_wmi_tlv_op_gen_pdev_set_rd(');b=tlv.index('static enum wmi_txbf_conf',a);part=tlv[a:b];regd=part[part.index('cmd->regd ='):part.index('ath10k_dbg')]
 oracle+='''
static void put(uint8_t*p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(8*j));}
static void reference_channel(struct wmi_channel*out,const QcaPolicyChannel*row){
 struct {u32 max_power,max_reg_power,max_antenna_gain;} v={row->max_power_dbm,row->max_reg_power_dbm,row->antenna_gain_db},*channel=&v;
 struct wmi_channel_arg value={0},*ch=&value;
'''+powers+'''
 value.freq=row->frequency;value.band_center_freq1=row->centre1;value.band_center_freq2=0;value.passive=row->passive;
 value.chan_radar=!!(row->flags&QCA_POLICY_RADAR);value.mode=(enum wmi_phy_mode)row->mode;
 struct wmi_channel_arg*arg=&value;ch=0;(void)ch;
 struct wmi_channel*dest=out;
'''
 # Preserve actual assignments with original ch variable inside a separate scope.
 oracle+=' {struct wmi_channel*ch=dest;u32 flags=0;memset(ch,0,sizeof(*ch));\n'+prefix+suffix+'}\n}\n'
 oracle+='''
unsigned reference_channels(uint8_t*out,const QcaReviewedChannelPolicy*p){
 _Static_assert(sizeof(struct wmi_channel)==24,"channel layout");
 put(out,WMI_TLV_SCAN_CHAN_LIST_CMDID);put(out+4,sizeof(struct wmi_tlv_scan_chan_list_cmd)|(WMI_TLV_TAG_STRUCT_SCAN_CHAN_LIST_CMD<<16));struct wmi_tlv_scan_chan_list_cmd cmd={.num_scan_chans=p->count};memcpy(out+8,&cmd,sizeof(cmd));put(out+12,p->count*(4+sizeof(struct wmi_channel))|(WMI_TLV_TAG_ARRAY_STRUCT<<16));
 for(unsigned j=0;j<p->count;j++){uint8_t*d=out+16+j*28;put(d,sizeof(struct wmi_channel)|(WMI_TLV_TAG_STRUCT_CHANNEL<<16));struct wmi_channel c;reference_channel(&c,&p->channels[j]);memcpy(d+4,&c,sizeof(c));}return 16+28*p->count;
}
unsigned reference_regdomain(uint8_t*out,const QcaReviewedChannelPolicy*p){
 struct wmi_tlv_pdev_set_rd_cmd value={0},*cmd=&value;u32 rd=p->regdomain,rd2g=p->regdomain2,rd5g=p->regdomain5,ctl2g=p->ctl2,ctl5g=p->ctl5;
'''+regd+'''
 _Static_assert(sizeof(value)==24,"regdomain layout");put(out,WMI_TLV_PDEV_SET_REGDOMAIN_CMDID);put(out+4,sizeof(value)|(WMI_TLV_TAG_STRUCT_PDEV_SET_REGDOMAIN_CMD<<16));memcpy(out+8,&value,sizeof(value));return 32;
}
'''
 (out/'oracle.c').write_text(oracle)
 names=['channel_wire.c','channel_wire.h','channel_test.c','verify_channel.py','README.md'];hashes={n:sha(ROOT/n) for n in names}
 flags=['-Wall','-Wextra','-Werror','-I'+str(ROOT)]
 subprocess.run([str(CC),'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,str(ROOT/'channel_wire.c'),str(ROOT/'channel_test.c'),str(out/'oracle.c'),'-o',str(out/'test')],check=True)
 r=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os',*flags,'-c',str(ROOT/'channel_wire.c'),'-o',str(out/'channel_wire.obj')],check=True)
 assert all(sha(ROOT/n)==h for n,h in hashes.items())
 report={'status':'CHANNEL-REGDOMAIN-PINNED-WIRE-ASAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',r.stdout)[1]),'build_host':'yukabox','source_sha256':hashes,'reference_sha256':{**PINS,**EPINS},'linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','oracle_sha256':sha(out/'oracle.c'),'host_log_sha256':sha(out/'host.log'),'reviewed_authority_input_required':True,'authority_authenticated_by_serializer':False,'default_channels':[],'native_integrated':False,'physical_verified':False,'rf_admission_granted':False,'rf_command_sent':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip())
if __name__=='__main__':main()
