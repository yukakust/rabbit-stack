#include "firmware_sender_core.h"
#include "firmware_channel.h"
#include "sha256.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
static uint32_t u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(i*8));}
static uint8_t*readfile(const char*dir,const char*name,size_t*n){char path[4096];snprintf(path,sizeof(path),"%s/%s",dir,name);FILE*f=fopen(path,"rb");assert(f);assert(!fseek(f,0,SEEK_END));long z=ftell(f);assert(z>0&&z<=QCA_FW_MAX);rewind(f);uint8_t*p=malloc((size_t)z);assert(p&&fread(p,1,(size_t)z,f)==(size_t)z);fclose(f);*n=(size_t)z;return p;}
int main(int argc,char**argv){
 assert(argc==2);size_t n;uint8_t*p=readfile(argv[1],"policy.bin",&n);assert(n==120);QcaFirmwarePolicy policy={0};
 memcpy(policy.owner,p,32);memcpy(policy.target,p+32,32);memcpy(policy.digest,p+64,32);policy.total=u32(p+96);policy.type=u32(p+100);policy.version=u32(p+104);policy.kind=u32(p+108);policy.generation=u32(p+112)|((uint64_t)u32(p+116)<<32);free(p);
 uint8_t*memory=malloc(policy.total),*workspace=malloc(65760);assert(memory&&workspace);QcaFirmwareChunks asset={0};QcaFirmwareChannel channel={0};assert(!qca_fw_begin(&asset,&policy,memory,policy.total));assert(!qca_fc_init(&channel,&asset,workspace,65760));
 unsigned count=(policy.total+65535)/65536;uint32_t all=count==32?UINT32_MAX:(1u<<count)-1;
 for(unsigned i=0;i<count;i++){
  char name[64];snprintf(name,sizeof(name),"chunk-%u.bin",i);p=readfile(argv[1],name,&n);QfsExpected e={.length=(uint32_t)n,.bit=1u<<i,.all=all};rabbit_sha256(e.digest,p,n);QfsProgress progress={0};
  uint8_t raw[64],command[44]={0},data[244];QfsStatus status;unsigned writes=0;
  while(1){
   qca_fc_status(&channel,raw);assert(!qfs_parse(&status,raw,64));
   for(size_t truncated=0;truncated<64;truncated++)assert(qfs_parse(&status,raw,truncated)<0);
   assert(!qfs_parse(&status,raw,64));raw[63]=1;assert(qfs_parse(&status,raw,64)<0);raw[63]=0;assert(!qfs_parse(&status,raw,64));
   int action=qfs_next(&status,&e,&progress);assert(action>0);
   if(action==QFS_DONE){
    assert(progress.floor==n);QfsStatus corrupt=status;corrupt.bitmap=0;assert(qfs_next(&corrupt,&e,&progress)==QFS_INVALID);corrupt=status;corrupt.poisoned=1;assert(qfs_next(&corrupt,&e,&progress)==QFS_BUSY);
    corrupt=status;corrupt.state=3;corrupt.error=4;assert(qfs_next(&corrupt,&e,&progress)==QFS_REJECTED);
    uint8_t saved=raw[60];raw[60]=2;assert(qfs_parse(&corrupt,raw,64)<0);raw[60]=saved;
    saved=raw[8];raw[8]=5;assert(qfs_parse(&corrupt,raw,64)<0);raw[8]=saved;
    saved=raw[12];raw[12]=20;assert(qfs_parse(&corrupt,raw,64)<0);raw[12]=saved;
    if(i==count-1){corrupt=status;corrupt.pinned=1;assert(qfs_next(&corrupt,&e,&progress)==QFS_DONE);}
    break;
   }
   if(status.state==1&&status.received>0&&status.received<n){
    QfsProgress saved=progress;saved.floor++;assert(qfs_next(&status,&e,&saved)==QFS_LOSS);
    QfsStatus foreign=status;foreign.digest[0]^=1;assert(qfs_next(&foreign,&e,&saved)==QFS_BUSY);
    QfsStatus idle={0};assert(qfs_next(&idle,&e,&progress)==QFS_LOSS);
   }
   progress.attempted=1;writes++;
   if(action==QFS_BEGIN||action==QFS_COMMIT){memcpy(command,"RFC1",4);command[4]=action==QFS_BEGIN?1:2;put(command+8,(uint32_t)n);memcpy(command+12,e.digest,32);assert(!qca_fc_control(&channel,command,44));}
   else{assert(action==QFS_DATA);size_t z=n-progress.floor;if(z>240)z=240;put(data,progress.floor);memcpy(data+4,p+progress.floor,z);assert(!qca_fc_data(&channel,data,z+4));
    /* Client restarts from saved confirmed prefix; ACK is deliberately ignored. */
    uint32_t old=progress.floor;assert(!qca_fc_data(&channel,data,z+4));assert(progress.floor==old);
   }
   assert(writes<10000);
  }
  free(p);
 }
 assert(asset.ready);assert(!qca_fc_close(&channel));assert(!qca_fw_cancel(&asset));free(memory);free(workspace);
 printf("SENDER-RECEIVER EXACT RESUME/LOSS/BITMAP PASS bytes=%u chunks=%u\n",policy.total,count);return 0;
}
