#include "boot_native.h"
#include "sha256.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned scenario,guard,calls,done,ready_posted,wire_ready;
static uint8_t response_buffer[4096],board_buffer[8124];
static QcaBootNative*current;
static uint32_t word(const uint8_t*p){uint32_t v=0;for(unsigned i=0;i<4;i++)v|=(uint32_t)p[i]<<(8*i);return v;}
static void put(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
int qca_mapped_irq_active_guard(QcaMappedIrq*m){assert(m);return guard;}
int qca_init_adapter_released(const QcaInitAdapter*a){return a->phase==QCA_INIT_CLOSED;}
int qca_boot_transport_begin(QcaBmiLoader*l,QcaCeBus*b,QcaCeRing*tx,QcaCeRing*rx,QcaDmaBuffer*req,QcaDmaBuffer*resp,const QcaBootImage*s,uint64_t now){
 assert(!qca_boot_image_validate(s)&&b&&tx&&rx&&req&&resp&&now);calls++;
 if(scenario==7&&s->phase==3)return -1;
 const uint8_t*p=s->request;uint32_t op=word(p),addr=word(p+4);
 memset(response_buffer,0,sizeof(response_buffer));
 if(op==2){
  if(addr==0x400854)put(response_buffer,0x402000);
  else if(addr>=0x402000&&addr<0x402000+8124){assert(word(p+8)<=244);memcpy(response_buffer,board_buffer+addr-0x402000,word(p+8));}
 }else if(op==3&&s->phase==3){assert(addr>=0x402000&&addr+s->issued_bytes<=0x402000+8124);memcpy(board_buffer+addr-0x402000,p+12,s->issued_bytes);}
 else if(op==4&&s->phase==9&&scenario==18)put(response_buffer,3);
 else if(op==1){assert(s->phase==19);done++;}
 l->wire.phase=QCA_BMI_WAIT;l->wire.response=resp;l->request_bytes=s->request_bytes;l->response_bytes=s->response_bytes;wire_ready=1;return 0;
}
int qca_boot_transport_poll(QcaBmiLoader*l,uint64_t now){
 assert(wire_ready&&now);
 if(scenario==8&&current->plan.phase==7){l->wire.error=5;return -1;}
 l->wire.phase=QCA_BMI_DONE;wire_ready=0;return 1;
}
int qca_ce_post(QcaCeRing*r,uint64_t addr,uint32_t bytes,uint32_t cookie,uint32_t meta,uint32_t flags){
 assert(done==1&&r&&addr==0x100000&&bytes==256&&cookie==3&&!meta&&!flags);ready_posted++;
 if(scenario==9)return -1;
 const uint8_t ready[20]={0,0,12,0,0,0,0,0,1,0,10,0,0,1,9,0,1,0,0,0};
 memcpy(response_buffer,ready,20);
 if(scenario==11)response_buffer[8]=2;
 if(scenario==12)response_buffer[14]=10;
 if(scenario==13)response_buffer[1]=2;
 return 0;
}
int qca_ce_hw_index(QcaCeHw*h,int receive,unsigned*index){assert(h&&receive==1);*index=1;return 0;}
int qca_ce_complete(QcaCeRing*r,uint32_t index,uint32_t*cookie,uint32_t*bytes){
 assert(r&&index==1&&ready_posted);if(scenario==10)return 1;
 *cookie=3;*bytes=scenario==14?257:20;return 0;
}
static uint8_t*load(const char*name,unsigned n){FILE*f=fopen(name,"rb");assert(f);uint8_t*p=malloc(n);assert(p&&fread(p,1,n,f)==n&&fgetc(f)==EOF);assert(!fclose(f));return p;}
int main(int argc,char**argv){
 assert(argc==4);scenario=(unsigned)atoi(argv[3]);assert(scenario<=18);
 uint8_t*container=load(argv[1],751436),*board_data=load(argv[2],8124);
 QcaUefiPort port={0};QcaBootIrq irq={.port=&port};QcaInitAdapter a={.phase=QCA_INIT_READY,.mapped={.irq=&irq}};
 a.access.port=&port;a.bus.access=&a.access;
 a.channels.buffers[3]=(QcaDmaBuffer){.port=&port,.host=response_buffer,.address=0x100000,.bytes=4096,.valid=1,.mapped=1,.allocated=1,.exposed=1};
 QcaConfigSetup setup={.phase=4,.op=10,.write_mask=31,.readback_mask=31,.write_attempts=5,.cpu_attempted=1,.bmi={.phase=QCA_BMI_DONE,.type=8,.version=0x05020001,.info_length=12,.bytes=12,.tx_done=1,.rx_done=1,.bus=&a.bus,.tx=&a.channels.rings[0],.rx=&a.channels.rings[1],.request=&a.channels.buffers[1],.response=&a.channels.buffers[3]}};
 setup.read.full.adapter=&a;
 setup.read.phase=4;setup.read.mask=7;setup.read.slot=3;setup.read.full.exchange.phase=QCA_DIAG_DONE;setup.read.full.exchange.value=0x401ee0;
 setup.read.words[0]=0x401a00;setup.read.words[1]=0x401b00;
 QcaBoardQuery query={.setup=&setup,.phase=5,.submitted=101,.offset=24196,.helper_bytes=24193};QcaBoardSmbios smbios={.state=2};
 QcaFirmwareChunks asset={.memory=container,.capacity=751436,.ready=1,.policy={.total=751436,.type=8,.version=0x05020001,.kind=1}};rabbit_sha256(asset.policy.digest,container,751436);
 QcaBootNative boot={0};current=&boot;
 if(scenario==1)query.result=0x400;
 if(scenario==2)smbios.state=3;
 if(scenario==3)setup.bmi.type=7;
 if(scenario==4)asset.ready=0;
 if(scenario==5)guard=1;
 if(scenario==6)container[0]^=1;
 if(scenario==16)setup.read.words[0]=0x402000;
 if(scenario==17)setup.read.mask=0;
 int rc=qca_boot_native_begin(&boot,&query,&smbios,&asset,board_data,8124,1);
 if((scenario>=1&&scenario<=6)||scenario==17){assert(rc==-1&&!calls&&!done);assert(!boot.owns_pin&&!asset.pinned);}
 else{
  assert(!rc&&boot.owns_pin&&asset.pinned);
  assert(qca_boot_native_close(&boot)==-1&&asset.pinned);
  uint64_t now=2;
  while(boot.phase!=5&&boot.phase!=6){assert(now<40000000);if(scenario==15&&boot.plan.phase==17)guard=1;int r=qca_boot_native_poll(&boot,now);assert(r==(boot.phase==5?1:boot.phase==6?-1:0));now+=1000;if(scenario==10&&boot.phase==3)now+=20000000;}
  if(!scenario||scenario==18){assert(boot.phase==5&&boot.ready_bytes==20&&boot.credit_count==10&&boot.credit_size==256&&boot.max_endpoints==9&&done==1&&calls==boot.plan.completed&&!memcmp(board_data,board_buffer,8124));assert(boot.plan.calibration_result==(scenario==18?3u:0u));}
  else assert(boot.phase==6&&boot.error);
  assert(qca_boot_native_close(&boot)==-1&&asset.pinned);
  a.phase=QCA_INIT_CLOSED;assert(!qca_boot_native_close(&boot)&&!asset.pinned&&!boot.owns_pin);
 }
 free(container);free(board_data);
 printf("NATIVE BOOT/PIN/HTC_READY scenario%u PASS; DMA/DEVICE MOCK ONLY\n",scenario);
}
