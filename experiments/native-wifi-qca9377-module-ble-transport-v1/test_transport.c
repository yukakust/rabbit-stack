#include "transport.h"
#include "artifact.h"
#include "reference/sha256.h"
#include "reference/monocypher-ed25519.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define C(x) do {checks++;if(!(x)){fprintf(stderr,"line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static unsigned checks,calls;
static ModuleTransport s;
static ModArtifact artifact;
static ModPolicy policy;
static uint8_t payload[65536],memory[MOD_FILE_MAX],packet[MT_MAX],key[64],pub[32],begin[45],frame[244];
static uint64_t now;
static void w32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=v>>(8*i);}
static void w64(uint8_t*p,uint64_t v){w32(p,v);w32(p+4,v>>32);}
static int accept(void*c,const uint8_t*p,size_t n){
 C(c==&artifact);C(s.borrowed&&s.state==MT_PENDING);C(mt_close(&s,65)<0);C(mt_poll(&s,65,now)<0);uint8_t status[80];C(mt_status(&s,65,status)<0);calls++;
 return mod_accept(&artifact,p,n); /* Genuine signed artifact verifier, not success stub. */
}
static size_t fixture(unsigned len){
 memset(&s,0,sizeof s);memset(&artifact,0,sizeof artifact);memset(memory,0,sizeof memory);memset(&policy,0,sizeof policy);calls=0;now=1;
 for(unsigned i=0;i<len;i++)payload[i]=(uint8_t)i;
 memcpy(policy.owner,pub,32);memset(policy.target,2,32);memset(policy.parent_hash,3,32);rabbit_sha256(policy.digest,payload,len);policy.epoch=65;policy.counter=1;policy.total=len;policy.mapped=8192;policy.role=2;policy.abi=1;
 memset(packet,0,sizeof packet);memcpy(packet,"RABRSN01",8);memcpy(packet+8,policy.owner,32);memcpy(packet+40,policy.target,32);memcpy(packet+72,policy.parent_hash,32);memcpy(packet+104,policy.digest,32);rabbit_sha256(packet+136,payload,len);w64(packet+168,65);w64(packet+176,1);w32(packet+184,len);w32(packet+192,len);w32(packet+196,2);w32(packet+200,1);w32(packet+204,8192);w32(packet+208,65536);crypto_ed25519_sign(packet+224,key,packet,224);memcpy(packet+288,payload,len);
 C(!mod_begin(&artifact,&policy,memory,sizeof memory));C(!mt_bind(&s,65,accept,&artifact));return 288+len;
}
static void start(size_t n){memset(begin,0,sizeof begin);begin[0]=1;begin[1]=1;w32(begin+9,n);rabbit_sha256(begin+13,packet,n);C(!mt_control(&s,begin,sizeof begin,65,now++));}
static void data(size_t n){
 for(unsigned off=0;off<n;){unsigned b=n-off;if(b>231)b=231;memset(frame,0,13);frame[0]=2;frame[1]=1;w32(frame+9,off);memcpy(frame+13,packet+off,b);C(!mt_data(&s,frame,b+13,65,now++));if(!off){C(!mt_data(&s,frame,b+13,65,now++));C(s.received==b);C(!mt_control(&s,begin,sizeof begin,65,now++));C(s.received==b);}off+=b;}
}
static void commit(void){uint8_t end[9]={3,1};C(!mt_control(&s,end,sizeof end,65,now++));C(s.state==MT_PENDING&&calls==0);C(!mt_control(&s,end,sizeof end,65,now++));}
static void wiped(void){for(unsigned i=0;i<MT_MAX;i++)C(!s.bytes[i]);}
int main(void){
 /* Public model key only, never a real owner key or Dell private identity. */
 uint8_t seed[32]={1,2,3};crypto_ed25519_key_pair(key,pub,seed);
 size_t n=fixture(65536);start(n);data(n);commit();C(mt_poll(&s,65,now++)==1);C(s.state==MT_ACCEPTED&&calls==1&&artifact.ready&&!memcmp(memory,payload,65536));wiped();C(!mt_control(&s,begin,sizeof begin,65,now++));C(!mt_poll(&s,65,now++)&&calls==1);C(!mt_close(&s,65));C(mt_poll(&s,65,now++)<0);
 for(unsigned j=0;j<288;j++){
  n=fixture(512);packet[j]^=1;start(n);data(n);uint8_t end[9]={3,1};int rc=mt_control(&s,end,9,65,now++);if(j<8){C(rc<0&&calls==0);}else{C(!rc);C(mt_poll(&s,65,now++)<0&&calls==1);}C(!artifact.ready);wiped();
 }
 n=fixture(512);start(n);data(n);s.bytes[500]^=1;uint8_t end[9]={3,1};C(mt_control(&s,end,9,65,now++)<0&&calls==0);wiped();
 n=fixture(512);packet[500]^=1;start(n);data(n);commit();C(mt_poll(&s,65,now++)<0&&calls==1);C(!artifact.ready);wiped();
 n=fixture(512);start(n);C(mt_control(&s,(uint8_t*)&s,45,65,now)<0);C(mt_data(&s,frame,14,64,now)<0);C(mt_poll(&s,64,now)<0);uint8_t status[80];C(mt_status(&s,64,status)<0);C(mt_status(&s,65,(uint8_t*)&s)<0);
 C(!mt_poll(&s,65,45000000));C(mt_poll(&s,65,45000001)<0);C(s.error==2);wiped();
 n=fixture(512);start(n);C(!mt_poll(&s,65,2));C(mt_poll(&s,65,1)<0&&s.error==1);wiped();
 n=fixture(512);start(n);memset(frame,0,13);frame[0]=2;frame[1]=1;frame[13]=packet[0];C(!mt_data(&s,frame,14,65,now++));frame[13]^=1;C(mt_data(&s,frame,14,65,now++)<0&&s.error==6);wiped();
 /* Discovery, bounds, paging, wrong offset/op/MTU and metadata alias. */
 n=fixture(512);uint8_t p[247]={6,1,0,255,255,0,0x28,33,0,0,0,0,0,0,0x80,0x49,0x46,0x54,0x49,0x42,0x42,0x41,0x52},out[247];
 C(mt_att(&s,247,p,23,out,sizeof out,65,now)==5&&out[0]==7&&out[1]==20&&out[3]==26);p[7]=7;C(mt_att(&s,247,p,23,out,sizeof out,65,now)==SIZE_MAX);
 p[0]=0x0a;p[1]=26;p[2]=0;C(mt_att(&s,23,p,3,out,sizeof out,65,now)==23&&out[0]==0x0b);C(mt_att(&s,247,p,3,out,sizeof out,65,now)==81);p[0]=0x0c;p[3]=80;p[4]=0;C(mt_att(&s,247,p,5,out,sizeof out,65,now)==1);p[3]=81;C(mt_att(&s,247,p,5,out,sizeof out,65,now)==5&&out[4]==7);
 C(!mt_att(&s,248,p,5,out,sizeof out,65,now));C(!mt_att(&s,247,p,5,p,sizeof p,65,now));C(!mt_att(&s,247,p,5,(uint8_t*)&s,247,65,now));C(!mt_att(&s,247,(uint8_t*)&s,5,out,sizeof out,65,now));
 C(!mt_status(&s,65,status)&&!memcmp(status,"QMT00001",8));C(mt_bind(&s,65,accept,&artifact)<0);C(mt_close(&s,64)<0);C(!mt_close(&s,65));
 mod_wipe(key,sizeof key);printf("MODULE TRANSPORT genuine signed artifact tests: %u checks; no physical LoadImage/BLE or credential claim\n",checks);return 0;
}
