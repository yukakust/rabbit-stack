#include "boot_image.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
static uint32_t word(const uint8_t*p){uint32_t v=0;for(unsigned i=0;i<4;i++)v|=(uint32_t)p[i]<<(8*i);return v;}
static void put(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
static uint8_t*load(const char*name,unsigned n){
 FILE*f=fopen(name,"rb");assert(f);uint8_t*p=malloc(n);assert(p);
 assert(fread(p,1,n,f)==n&&fgetc(f)==EOF);assert(!fclose(f));return p;
}
int main(int argc,char**argv){
 assert(argc==5);unsigned scenario=(unsigned)atoi(argv[4]);assert(scenario<=13);
 QcaBootAssets a={.board=load(argv[1],8124),.helper=load(argv[2],24193),.main=load(argv[3],727125),.board_bytes=8124,.helper_bytes=24193,.main_bytes=727125};
 QcaBootImage s={0};
 if(scenario>=1&&scenario<=3){
  uint8_t*p=(uint8_t*)(scenario==1?a.board:scenario==2?a.helper:a.main);p[0]^=1;
  assert(qca_boot_image_begin(&s,&a)==-1&&!s.phase);p[0]^=1;
 }
 for(unsigned k=0;k<3;k++){
  QcaBootAssets bad=a;uint32_t*n=k==0?&bad.board_bytes:k==1?&bad.helper_bytes:&bad.main_bytes;(*n)--;
  assert(qca_boot_image_begin(&s,&bad)==-1&&!s.phase);
 }
 assert(!qca_boot_image_begin(&s,&a));assert(qca_boot_image_begin(&s,&a)==-1);
 unsigned board_written=0,board_read=0,helper_written=0,main_written=0,helper_starts=0,main_starts=0,calibrations=0,done=0;
 unsigned loops=0;const uint8_t*p;unsigned n,reply;uint8_t response[244];
 while(s.phase!=20&&s.phase!=21){
  assert(++loops<4000);assert(!qca_boot_image_request(&s,&p,&n,&reply));assert(!qca_boot_image_validate(&s));
  assert(qca_boot_image_request(&s,&p,&n,&reply)==-1);
  memset(response,0,sizeof(response));unsigned phase=s.phase;uint32_t op=word(p);
  if(phase==1||phase==2||phase==10){
   assert(op==2&&n==12&&reply==4&&word(p+8)==4);
   assert(word(p+4)==(phase==1?0x4008ac:phase==2?0x400854:0x400810));
   put(response,phase==2?0x402000:phase==10?0x80:0);
   if(phase==1&&scenario==4)put(response,0x402000);
   if(phase==2&&scenario>=5&&scenario<=8)put(response,scenario==5?0:scenario==6?0x400854:scenario==7?0x410000-8120:0x402001);
   if(phase==10&&scenario==11)put(response,UINT32_MAX);
  }else if(phase==3||phase==4){
   unsigned*off=phase==3?&board_written:&board_read,bytes=8124-*off;if(bytes>244)bytes=244;
   assert(op==(phase==3?3u:2u)&&word(p+4)==0x402000+*off&&word(p+8)==bytes);
   if(phase==3){assert(n==12+bytes&&!reply&&!memcmp(p+12,a.board+*off,bytes));}
   else{assert(n==12&&reply==bytes);memcpy(response,a.board+*off,bytes);if(scenario==9&&!*off)response[bytes-1]^=1;}
   *off+=bytes;
  }else if(phase==6||phase==8||phase==16||phase==18){
   assert(op==13&&n==8&&!reply&&word(p+4)==(phase==6||phase==16?0x1234:0));
   if(phase==6)helper_starts++;
   if(phase==16)main_starts++;
  }else if(phase==7||phase==17){
   unsigned*off=phase==7?&helper_written:&main_written,total=phase==7?24193:727125,bytes=total-*off;
   const uint8_t*data=phase==7?a.helper:a.main;if(bytes>248)bytes=248;
   unsigned padded=(bytes+3)&~3u;assert(op==14&&!reply&&n==8+padded&&word(p+4)==padded&&!memcmp(p+8,data+*off,bytes));
   for(unsigned i=bytes;i<padded;i++)assert(!p[8+i]);
   *off+=bytes;
  }else if(phase==9){
   assert(op==4&&n==12&&reply==4&&word(p+4)==0x1234&&!word(p+8));calibrations++;
   if(scenario==10)put(response,1);
  }else if(phase==5||(phase>=11&&phase<=15)){
   assert(op==3&&n==16&&!reply&&word(p+8)==4);
   uint32_t address=phase==5?0x400858:phase==11?0x400810:phase==12?0x400800:phase==13?0x400844:phase==14?0x400904:0x4008bc;
   uint32_t value=phase==5?1:phase==11?0x2288:phase==12?2:phase==15?0x42:0;
   assert(word(p+4)==address&&word(p+12)==value);
  }else{assert(phase==19&&op==1&&n==4&&!reply);assert(main_written==727125);done++;}
  unsigned reply_n=reply;
  if(scenario==12&&phase==2)reply_n=3;
  if(scenario==13&&phase==9)reply_n=5;
  int rc=qca_boot_image_complete(&s,response,reply_n);
  if(rc<0){assert(scenario>=4);break;}
  assert(rc==(s.phase==20));assert(qca_boot_image_complete(&s,response,reply_n)==-1);
 }
 if(scenario<=3){assert(s.phase==20&&!s.error&&done==1&&calibrations==1&&helper_starts==1&&main_starts==1&&board_written==8124&&board_read==8124&&helper_written==24193&&main_written==727125&&s.submitted==s.completed);assert(qca_boot_image_request(&s,&p,&n,&reply)==1);}
 else assert(s.phase==21&&s.error&&!done&&!main_written);
 free((void*)a.board);free((void*)a.helper);free((void*)a.main);
 printf("EXACT BOARD READBACK/CALIBRATION/MAIN/DONE scenario%u PASS; HOST MOCK, NO PHYSICAL READY CLAIM\n",scenario);
}
