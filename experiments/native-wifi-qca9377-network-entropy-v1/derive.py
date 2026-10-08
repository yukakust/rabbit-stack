"""NEW fallible-RNG lwIP projection; frozen WAN implementation is unchanged."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parent;BASE=R.parent/'native-wifi-qca9377-network-wan-v1'
def one(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b)
def derive(out):
 freeze=json.loads((BASE/'evidence/freeze.json').read_text())
 for n,h in freeze['source_sha256'].items():assert hashlib.sha256((BASE/n).read_bytes()).hexdigest()==h,n
 shutil.copytree(BASE,out,ignore=shutil.ignore_patterns('runs','__pycache__','.git'),dirs_exist_ok=True)
 p=out/'network.h';s=p.read_text();s=one(s,'uint32_t (*random32)(void*);','int (*random32)(void*,uint32_t*);');p.write_text(s)
 p=out/'network_hardened.c';s=p.read_text();s=one(s,'static int initialized,authorized;','static int initialized,authorized,rng_fault;\nstatic uint32_t failed_epoch;')
 s=one(s,'unsigned int rabbit_network_rand(void){if(!authorized||!ops.random32)rabbit_network_panic("rng boundary");return ops.random32(ops.context);}', '''unsigned int rabbit_network_rand(void){uint32_t value=0;
 if(!authorized||rng_fault||!ops.random32||ops.random32(ops.context,&value)){
  rng_fault=1;if(epoch>failed_epoch)failed_epoch=epoch;return 0;
 }return value;
}''')
 s=one(s,'if(!authorized||p->tot_len>sizeof(frame))','if(!authorized||rng_fault||p->tot_len>sizeof(frame))')
 s=one(s,'void rabbit_network_revoke(void){if(!initialized)return;authorized=0;', 'void rabbit_network_revoke(void){authorized=0;if(!initialized){epoch=0;return;}')
 s=one(s,'if(authorized)return -1;ops=*o;epoch=a->association_epoch;authorized=1;', 'if(authorized||a->association_epoch<=failed_epoch)return -1;ops=*o;epoch=a->association_epoch;authorized=1;rng_fault=0;')
 s=one(s,'dhcp_set_struct(&iface,&client);initialized=1;}', 'dhcp_set_struct(&iface,&client);initialized=1;}if(rng_fault){rabbit_network_revoke();return -1;}')
 s=one(s,'if(dhcp_start(&iface)!=ERR_OK)', 'if(dhcp_start(&iface)!=ERR_OK||rng_fault)')
 s=one(s,' if(!authorized||association_epoch!=epoch', ' if(rng_fault){rabbit_network_revoke();return -1;}\n if(!authorized||association_epoch!=epoch')
 s=one(s,' if(before_state==DHCP_STATE_REBINDING', ' if(rng_fault){rabbit_network_revoke();return -1;}\n if(before_state==DHCP_STATE_REBINDING')
 s=one(s,'int rabbit_network_tick(uint32_t ms){if(ms>100)return -1;now+=ms;sys_check_timeouts();return 0;}', 'int rabbit_network_tick(uint32_t ms){if(ms>100)return -1;if(rng_fault){rabbit_network_revoke();return -1;}now+=ms;sys_check_timeouts();if(rng_fault){rabbit_network_revoke();return -1;}return 0;}')
 s=s.replace('return authorized?','return authorized&&!rng_fault?');p.write_text(s)
 p=out/'fixture_hardened.c';s=p.read_text();s=one(s,'static uint32_t rng(void*c){(void)c;return 0x12345678;}', 'static unsigned rng_mode;\nstatic int rng(void*c,uint32_t*out){(void)c;*out=rng_mode==2?0:0x12345678;return rng_mode==1?-1:0;}')
 s=one(s,'int main(void){', (R/'entropy_fixture.inc').read_text()+'\nint main(int argc,char**argv){\n if(argc>1)return entropy_first(argv[1]);')
 s=one(s,' printf("PASS %u SYNTHETIC DHCP/ARP/PORT/DNS/TCP', ' entropy_late();\n printf("PASS %u SYNTHETIC DHCP/ARP/PORT/DNS/TCP');p.write_text(s)
 return freeze
if __name__=='__main__':derive(R/'runs/derived')
