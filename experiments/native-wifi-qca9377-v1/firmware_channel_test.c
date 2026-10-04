#include "firmware_channel.h"
#include "sha256.h"
#ifndef QCA_FC_BASE
#define QCA_FC_BASE 11
#endif
#define H(n) (QCA_FC_BASE+((n)-11))
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
static uint32_t u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(i*8));}
static uint8_t*readfile(const char*dir,const char*name,size_t*n){char path[4096];snprintf(path,sizeof(path),"%s/%s",dir,name);FILE*f=fopen(path,"rb");assert(f);assert(!fseek(f,0,SEEK_END));long z=ftell(f);assert(z>0&&z<=QCA_FW_MAX);rewind(f);uint8_t*p=malloc((size_t)z);assert(p&&fread(p,1,(size_t)z,f)==(size_t)z);fclose(f);*n=(size_t)z;return p;}
static void control(uint8_t p[44],unsigned op,const uint8_t*packet,size_t n){memcpy(p,"RFC1",4);p[4]=(uint8_t)op;p[5]=p[6]=p[7]=0;put(p+8,(uint32_t)n);rabbit_sha256(p+12,packet,n);}
static void att_write(QcaFirmwareChannel*s,unsigned handle,const uint8_t*p,size_t n){uint8_t req[247],reply[247];assert(n<=244);req[0]=0x12;req[1]=(uint8_t)handle;req[2]=0;memcpy(req+3,p,n);assert(qca_fc_att(s,247,req,n+3,reply,sizeof(reply))==1&&reply[0]==0x13);}
static void snapshot(QcaFirmwareChannel*s,uint8_t out[64]){
 uint8_t p[5]={0x0a,H(17),0,0,0},r[247];size_t used=0;
 while(used<64){p[0]=used?0x0c:0x0a;p[3]=(uint8_t)used;p[4]=0;size_t n=qca_fc_att(s,23,p,used?5:3,r,sizeof(r));assert(n>1&&n<=23);memcpy(out+used,r+1,n-1);used+=n-1;}
 assert(used==64);p[3]=65;assert(qca_fc_att(s,23,p,5,r,sizeof(r))==5&&r[4]==7);
}
int main(int argc,char**argv){
 assert(argc==2);size_t n;uint8_t*raw=readfile(argv[1],"policy.bin",&n);assert(n==120);
 QcaFirmwarePolicy policy={0};memcpy(policy.owner,raw,32);memcpy(policy.target,raw+32,32);memcpy(policy.digest,raw+64,32);policy.total=u32(raw+96);policy.type=u32(raw+100);policy.version=u32(raw+104);policy.kind=u32(raw+108);policy.generation=u32(raw+112)|((uint64_t)u32(raw+116)<<32);free(raw);
 uint8_t*memory=malloc(policy.total),*workspace=malloc(QCA_FW_HEADER+QCA_FW_CHUNK);assert(memory&&workspace);
 QcaFirmwareChunks asset={0};assert(!qca_fw_begin(&asset,&policy,memory,policy.total));QcaFirmwareChannel s={0};assert(!qca_fc_init(&s,&asset,workspace,QCA_FW_HEADER+QCA_FW_CHUNK));
 uint8_t request[247]={2,247,0},reply[247],status[64];assert(qca_fc_att(&s,23,request,3,reply,247)==SIZE_MAX);
 request[0]=0x0a;request[1]=7;assert(qca_fc_att(&s,247,request,3,reply,247)==SIZE_MAX);request[1]=10;assert(qca_fc_att(&s,247,request,3,reply,247)==SIZE_MAX);
 request[0]=0x10;request[1]=H(11);request[3]=255;request[4]=255;request[5]=0;request[6]=0x28;assert(qca_fc_att(&s,247,request,7,reply,247)==22&&reply[2]==H(11)&&reply[4]==H(17));
 request[0]=6;request[1]=1;request[5]=0;request[6]=0x28;memcpy(request+7,reply+6,16);assert(qca_fc_att(&s,247,request,23,reply,247)==5&&reply[1]==H(11)&&reply[3]==H(17));
 for(unsigned h=H(12);h<=H(16);h+=2){request[0]=8;request[1]=(uint8_t)h;request[5]=3;request[6]=0x28;assert(qca_fc_att(&s,247,request,7,reply,247)==23&&reply[2]==h&&reply[5]==h+1&&reply[7]==(h-QCA_FC_BASE+11)/2+2);}
 /* Relocated receiver must delegate every legacy file/diagnostic handle. */
 for(unsigned h=1;h<QCA_FC_BASE;h++){request[0]=0x0a;request[1]=(uint8_t)h;assert(qca_fc_att(&s,247,request,3,reply,247)==SIZE_MAX);}
 snapshot(&s,status);assert(!u32(status+8));
 unsigned count=(policy.total+QCA_FW_CHUNK-1)/QCA_FW_CHUNK;
 for(unsigned i=0;i<count;i++){
  char name[64];snprintf(name,sizeof(name),"chunk-%u.bin",i);uint8_t*p=readfile(argv[1],name,&n),cmd[44],data[244];control(cmd,1,p,n);att_write(&s,H(13),cmd,44);
  if(i==0){
   cmd[5]=1;assert(qca_fc_control(&s,cmd,44)<0);cmd[5]=0;
   put(data,1);data[4]=42;assert(qca_fc_data(&s,data,5)<0&&!s.received);
   put(data,UINT32_MAX);assert(qca_fc_data(&s,data,5)<0&&!s.received);
   uint8_t foreign[44];memcpy(foreign,cmd,44);foreign[12]^=1;assert(qca_fc_control(&s,foreign,44)<0);assert(!s.received);
   control(cmd,2,p,n);assert(qca_fc_control(&s,cmd,44)<0);
   control(cmd,3,p,n);att_write(&s,H(13),cmd,44);assert(s.state==QCA_FC_ABORTED);control(cmd,1,p,n);att_write(&s,H(13),cmd,44);
  }
  for(size_t off=0;off<n;){size_t amount=1+(off*17)%240;if(amount>n-off)amount=n-off;put(data,(uint32_t)off);memcpy(data+4,p+off,amount);att_write(&s,H(15),data,amount+4);
   /* A lost ACK followed by exact DATA retry must not append twice. */
   assert(!qca_fc_data(&s,data,amount+4));assert(s.received==off+amount);
   data[4]^=1;assert(qca_fc_data(&s,data,amount+4)<0);data[4]^=1;
   off+=amount;
   if(off<n/2){control(cmd,1,p,n);assert(!qca_fc_control(&s,cmd,44));assert(s.received==off);}
  }
  snapshot(&s,status);assert(u32(status+20)==n);assert(!memcmp(status+24,s.digest,32));
  control(cmd,2,p,n);att_write(&s,H(13),cmd,44);assert(s.state==QCA_FC_ACCEPTED&&!s.error);assert(!qca_fc_control(&s,cmd,44));snapshot(&s,status);assert(u32(status+8)==QCA_FC_ACCEPTED&&u32(status+56)==asset.received);
  free(p);
 }
 assert(asset.ready);const uint8_t*view;size_t length;assert(!qca_fw_pin(&asset,&view,&length));assert(qca_fc_close(&s)<0);assert(!qca_fw_unpin(&asset));assert(!qca_fc_close(&s));assert(!qca_fw_cancel(&asset));
 /* Bad transport SHA and valid transport SHA with invalid owner signature. */
 assert(!qca_fw_begin(&asset,&policy,memory,policy.total));assert(!qca_fc_init(&s,&asset,workspace,QCA_FW_HEADER+QCA_FW_CHUNK));uint8_t*p=readfile(argv[1],"chunk-0.bin",&n),cmd[44],data[244];
 for(unsigned trial=0;trial<2;trial++){
  p[160]^=1;control(cmd,1,p,n);if(!trial)cmd[12]^=1;assert(!qca_fc_control(&s,cmd,44));
  for(size_t off=0;off<n;){size_t z=n-off;if(z>240)z=240;put(data,(uint32_t)off);memcpy(data+4,p+off,z);assert(!qca_fc_data(&s,data,z+4));off+=z;}
  cmd[4]=2;assert(!qca_fc_control(&s,cmd,44));assert(s.state==QCA_FC_REJECTED&&s.error==(trial?4:20)&&!asset.received);
  assert(!qca_fc_control(&s,cmd,44));p[160]^=1;
 }
 assert(!qca_fc_close(&s));snapshot(&s,status);assert(!u32(status+8)&&!u32(status+16));for(unsigned i=24;i<56;i++)assert(!status[i]);assert(!qca_fw_cancel(&asset));free(p);free(memory);free(workspace);
 printf("GATT CHUNK RESUME/RECEIPTS/ISOLATION PASS bytes=%u chunks=%u\n",policy.total,count);return 0;
}
