#include "board_smbios.h"
static int fail(QcaBoardSmbios*s,unsigned e){s->state=4;s->error=e;return -1;}
static int same(const uint8_t*a,const uint8_t*b,unsigned n){unsigned mismatch=0;for(unsigned i=0;i<n;i++)mismatch|=a[i]^b[i];return !mismatch;}
int qca_board_smbios_parse(QcaBoardSmbios*s,const uint8_t*p,size_t n){
 if(!s||!p||!n||n>1048576)return -1;
 *s=(QcaBoardSmbios){0};size_t off=0;unsigned found=0;
 while(off<n){
  if(++s->structures>4096||n-off<4||p[off+1]<4||p[off+1]>n-off)return fail(s,1);
  size_t strings=off+p[off+1],end=strings;
  while(end+1<n&&(p[end]||p[end+1]))end++;
  if(end+1>=n)return fail(s,2);
  if(p[off]==0xf8&&p[off+1]==9&&p[off+8]){
   size_t len=0;while(strings+len<=end&&p[strings+len])len++;
   const uint8_t magic[4]={'B','D','F','_'};
   if(len<5||len>=36||!same(p+strings,magic,4))return fail(s,3);
   for(size_t i=0;i<len;i++)if(p[strings+i]<32||p[strings+i]>126)return fail(s,4);
   if(found++)return fail(s,5);
   for(size_t i=4;i<len;i++)s->variant[i-4]=(char)p[strings+i];
  }
  s->bytes=(uint32_t)(end+2);
  if(p[off]==127){s->state=found?3:2;return 0;}
  off=end+2;
 }
 return fail(s,6);
}
static uint64_t little(const uint8_t*p,unsigned n){uint64_t v=0;for(unsigned i=0;i<n;i++)v|=(uint64_t)p[i]<<(8*i);return v;}
static int checksum(const uint8_t*p,unsigned n){unsigned sum=0;for(unsigned i=0;i<n;i++)sum+=p[i];return !(sum&255);}
static int span(const uint8_t*map,size_t size,size_t step,uint64_t address,uint64_t bytes){
 if(!address||!bytes||address>UINTPTR_MAX-bytes)return 0;
 for(size_t off=0;off<size;off+=step){
  unsigned type=(unsigned)little(map+off,4);uint64_t base=little(map+off+8,8),pages=little(map+off+24,8);
  if(type>10||type==1||type==2||type==5||type==8||pages>UINT64_MAX/4096)continue;
  uint64_t extent=pages*4096;
  if(address>=base&&address-base<=extent&&bytes<=extent-(address-base))return 1;
 }
 return 0;
}
typedef struct {Guid guid;void*address;} Configuration;
typedef Status(EFIAPI *MemoryMap)(uint64_t*,void*,uint64_t*,uint64_t*,uint32_t*);
int qca_board_smbios_collect(QcaBoardSmbios*s,SystemTable*st){
 static uint8_t map[65536];
 if(!s||!st)return -1;
 *s=(QcaBoardSmbios){0};
 if(st->header.signature!=0x5453595320494249ull||st->header.size<sizeof(*st)||!st->boot||st->tables>128)return fail(s,10);
 const TableHeader*b=st->boot;
 if(b->signature!=0x56524553544f4f42ull||b->size<64||!service(st,56))return fail(s,11);
 uint64_t bytes=sizeof(map),key=0,step=0;uint32_t version=0;
 if(((MemoryMap)service(st,56))(&bytes,map,&key,&step,&version)||bytes>sizeof(map)||!bytes||step<40||step>256||bytes%step||version!=1)return fail(s,12);
 if(st->tables&&!span(map,(size_t)bytes,(size_t)step,(uintptr_t)st->configuration,st->tables*sizeof(Configuration)))return fail(s,13);
 const Guid g2={0xeb9d2d31,0x2d88,0x11d3,{0x9a,0x16,0,0x90,0x27,0x3f,0xc1,0x4d}};
 const Guid g3={0xf2fd1544,0x9794,0x4a2c,{0x99,0x2e,0xe5,0xbb,0xcf,0x20,0xe3,0x94}};
 const Configuration*c=st->configuration;const uint8_t*entry=0;unsigned mode=0,counts[2]={0};
 for(uint64_t i=0;i<st->tables;i++){
  unsigned selected=same((const uint8_t*)&c[i].guid,(const uint8_t*)&g3,16)?3:same((const uint8_t*)&c[i].guid,(const uint8_t*)&g2,16)?2:0;
  if(!selected)continue;
  if(++counts[selected-2]>1)return fail(s,14);
  if(selected>mode){entry=c[i].address;mode=selected;}
 }
 if(!mode){s->state=1;return 0;}
 if(!span(map,(size_t)bytes,(size_t)step,(uintptr_t)entry,8))return fail(s,15);
 unsigned length=entry[mode==3?6:5];
 if(length<(mode==3?24u:31u)||length>64||!span(map,(size_t)bytes,(size_t)step,(uintptr_t)entry,length)||!checksum(entry,length))return fail(s,16);
 const uint8_t m3[5]={'_','S','M','3','_'},m2[4]={'_','S','M','_'},dmi[5]={'_','D','M','I','_'};
 uint64_t address=0,table_bytes=0;
 if(mode==3){
  if(!same(entry,m3,5)||entry[7]<3)return fail(s,17);
  table_bytes=little(entry+12,4);address=little(entry+16,8);
 }else{
  if(!same(entry,m2,4)||!same(entry+16,dmi,5)||!checksum(entry+16,15))return fail(s,18);
  table_bytes=little(entry+22,2);address=little(entry+24,4);
 }
 if(table_bytes>1048576||!span(map,(size_t)bytes,(size_t)step,address,table_bytes))return fail(s,19);
 return qca_board_smbios_parse(s,(const uint8_t*)(uintptr_t)address,(size_t)table_bytes);
}
