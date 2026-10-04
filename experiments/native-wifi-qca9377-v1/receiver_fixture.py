"""Actual native setup/receiver entrypoints with explicit synthetic signer."""
import setup_fixture

def fixture(source):
 s=setup_fixture.fixture(source).replace('0x05020001,7}', '0x05020001,8}').replace('get(328)==7','get(328)==8')
 s=s.replace('#include "bringup.h"','#include "bringup.h"\n#include "firmware_port.h"\n#include <stdlib.h>\nconst QcaFirmwarePort*qca_ram_view(void);\nsize_t qca_ram_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);')
 # The fixture includes port_test.c; stdlib is not present before the pool helpers.
 if '#include <stdlib.h>' not in s:s='#include <stdlib.h>\n#include "firmware_port.h"\nconst QcaFirmwarePort*qca_ram_view(void);\nsize_t qca_ram_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);\n'+s
 insertion='''
static void*ram_blocks[2];static unsigned ram_allocs,ram_frees;
static Status EFIAPI ram_allocate(uint32_t kind,uint64_t n,void**out){
 assert(kind==4&&n>0&&ram_allocs<2&&!(config[1]&4)&&allocations==14&&dma_frees==14&&unmaps==14&&opens==closes);
 *out=ram_blocks[ram_allocs++]=malloc((size_t)n);assert(*out);return 0;
}
static Status EFIAPI ram_release(void*p){
 if(p==resource)return free_pool(p);
 unsigned slot=p==ram_blocks[0]?0:1;assert(p&&p==ram_blocks[slot]);free(p);ram_blocks[slot]=0;ram_frees++;return 0;
}
static uint8_t*packet_file(const char*dir,unsigned i,size_t*n){
 char path[4096];snprintf(path,sizeof(path),"%s/chunk-%u.bin",dir,i);FILE*f=fopen(path,"rb");assert(f&&!fseek(f,0,SEEK_END));long length=ftell(f);assert(length>224&&length<=65760);rewind(f);uint8_t*p=malloc((size_t)length);assert(p&&fread(p,1,(size_t)length,f)==(size_t)length);fclose(f);*n=(size_t)length;return p;
}
static void upload_fixture(const char*dir){
 const QcaFirmwarePort*r=qca_ram_view();fprintf(stderr,"RAM phase=%u error=%u allocs=%u frees=%u setup=%u/%u bmi=%u/%u type=%u stage=%u\\n",r->phase,r->error,ram_allocs,ram_frees,get(280),get(284),get(316),get(320),get(328),get(128));assert(r->phase==4&&ram_allocs==2&&!ram_frees);
 uint8_t request[247],reply[247];request[0]=0x0a;request[1]=19;request[2]=0;
 assert(qca_ram_att(247,request,3,reply,247)==65&&!memcmp(reply+1,"RFCS0001",8));
 /* Legacy file/diagnostic handles remain delegated. */
 for(unsigned h=1;h<=12;h++){request[1]=(uint8_t)h;assert(qca_ram_att(247,request,3,reply,247)==SIZE_MAX);}
 for(unsigned i=0;i<12;i++){
  size_t n;uint8_t*p=packet_file(dir,i,&n),cmd[44]={0};memcpy(cmd,"RFC1",4);cmd[4]=1;
  for(unsigned k=0;k<4;k++){cmd[8+k]=(uint8_t)(n>>(8*k));}rabbit_sha256(cmd+12,p,n);
  request[0]=0x12;request[1]=15;request[2]=0;memcpy(request+3,cmd,44);assert(qca_ram_att(247,request,47,reply,247)==1);
  for(size_t off=0;off<n;){size_t z=n-off;if(z>240)z=240;request[1]=17;for(unsigned k=0;k<4;k++)request[3+k]=(uint8_t)(off>>(8*k));memcpy(request+7,p+off,z);assert(qca_ram_att(247,request,z+7,reply,247)==1);off+=z;}
  cmd[4]=2;request[1]=15;memcpy(request+3,cmd,44);assert(qca_ram_att(247,request,47,reply,247)==1);assert(r->channel.state==QCA_FC_ACCEPTED&&!r->channel.error);free(p);
 }
 assert(r->asset.received==4095&&r->asset.ready&&!r->asset.poisoned);
 const uint8_t*data;size_t bytes;assert(!qca_fw_pin((QcaFirmwareChunks*)&r->asset,&data,&bytes)&&bytes==751436);
 assert(qca_stop()&&!ram_frees);assert(!qca_fw_unpin((QcaFirmwareChunks*)&r->asset));
 printf("ACTUAL RECEIVER RAM FULL SIGNED CONTAINER AND PINNED UNLOAD RETENTION PASS\\n");
}
'''
 s=s.replace('int main(int argc,char**argv){',insertion+'\nint main(int argc,char**argv){').replace('assert(argc==2);','assert(argc==3);')
 s=s.replace(' qca_start(&port_system,0);', ''' port_system.header.signature=0x5453595320494249ull;port_system.header.size=sizeof(port_system);
 ((TableHeader*)boot)->signature=0x56524553544f4f42ull;((TableHeader*)boot)->size=sizeof(boot);
 boot[64/8]=ram_allocate;boot[72/8]=ram_release;
 qca_start(&port_system,0);''')
 s=s.replace(' if(initial==4||initial==7){',' if(initial==0){upload_fixture(argv[2]);}\n if(initial==4||initial==7){')
 s=s.replace('assert(!qca_stop()&&get(140)==1', 'while(qca_stop()){tick(61000+ram_frees);assert(ram_frees<=2);}\n  assert(!qca_fwp_owned(qca_ram_view())&&ram_allocs==ram_frees);\n  assert(!qca_stop()&&get(140)==1')
 s='#include "sha256.h"\n'+s
 return s
