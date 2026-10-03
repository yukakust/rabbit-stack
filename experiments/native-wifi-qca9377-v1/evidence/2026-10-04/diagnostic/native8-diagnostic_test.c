#include <assert.h>
#include <string.h>
#include <stdio.h>
#include "scene_abi.h"
#include "pci_collect.h"
#include "gatt_core.h"
void qca_collect(SystemTable*);
static void*boot[44],*pci[16];
static SystemTable system;
static uint32_t config[16];
static unsigned mode,freed,read_count;
static uint64_t get(unsigned offset,unsigned bytes){
 uint64_t result=0;for(unsigned i=0;i<bytes;i++)result|=(uint64_t)qca_diagnostic[offset+i]<<(8*i);return result;
}
static Status EFIAPI handles(uint32_t kind,const Guid*g,void*key,uint64_t*n,void***out){
 static void*items[2];assert(kind==2&&!key&&g->a==0x4cf5b200);
 items[0]=items[1]=pci;*out=items;*n=mode==1?65:mode==2?0:mode==3?2:1;
 return mode==4?EFI_ERROR(14):0;
}
static Status EFIAPI protocol(void*h,const Guid*g,void**out){(void)g;assert(h==pci);*out=pci;return 0;}
static Status EFIAPI release(void*p){assert(p);freed++;return 0;}
static Status EFIAPI read_pci(void*p,uint32_t width,uint32_t off,uint64_t count,void*out){
 assert(p==pci&&width==2&&!off&&count==16);read_count++;
 if(mode==5)return EFI_ERROR(7);
 memcpy(out,config,sizeof(config));return 0;
}
static Status EFIAPI location(void*p,uint64_t*s,uint64_t*b,uint64_t*d,uint64_t*f){
 assert(p==pci);*s=0;*b=2;*d=0;*f=0;return mode==6?EFI_ERROR(7):0;
}
static size_t att(RgServer*s,const uint8_t*p,size_t n,uint8_t*r){return rg_att(s,p,n,r,247);}
int main(void){
 system.boot=boot;boot[312/8]=handles;boot[152/8]=protocol;boot[72/8]=release;
 pci[48/8]=read_pci;pci[112/8]=location;
 config[0]=0x0042168c;config[2]=0x02800031;config[4]=0xc1000000;config[11]=0x18101028;
 qca_collect(&system);assert(get(4,4)==15&&get(20,4)==1&&get(44,4)==2);
 assert(get(64,4)==config[0]&&get(108,4)==config[11]&&freed==1);
 for(mode=1;mode<=6;mode++){
  read_count=0;qca_collect(&system);assert(freed==mode+1);
  if(mode==1)assert(get(4,4)==17&&!read_count);
  if(mode==2)assert(get(4,4)==1&&!get(20,4)&&!read_count);
  if(mode==3)assert(get(4,4)==47&&get(20,4)==2);
  if(mode==4)assert(!get(4,4)&&get(8,8)==EFI_ERROR(14)&&!read_count);
  if(mode==5)assert(get(4,4)==1&&get(24,8)==EFI_ERROR(7));
  if(mode==6)assert(get(4,4)==7&&get(32,8)==EFI_ERROR(7));
 }
 mode=0;config[4]=4;config[5]=1;qca_collect(&system);assert(get(4,4)==15);
 config[0]=0xffffffff;qca_collect(&system);assert(get(4,4)==1);
 config[0]=0x0042168c;qca_collect(&system);
 RgServer server;rg_init(&server,0);uint8_t response[247],reconstructed[128];
 uint8_t mtu[]={2,247,0};assert(att(&server,mtu,3,response)==3);
 uint8_t discovery[]={8,8,0,9,0,3,0x28};
 assert(att(&server,discovery,7,response)==23&&response[4]==2&&response[5]==9&&response[7]==5);
 uint8_t request[]={0x0a,9,0};assert(att(&server,request,3,response)==129);
 assert(!memcmp(response+1,qca_diagnostic,128));
 for(unsigned offset=0;offset<=128;offset++){
  uint8_t blob[]={0x0c,9,0,(uint8_t)offset,0};
  size_t n=att(&server,blob,5,response);assert(n==129-offset&&!memcmp(response+1,qca_diagnostic+offset,n-1));
 }
 uint8_t badblob[]={0x0c,9,0,129,0};assert(att(&server,badblob,5,response)==5&&response[4]==7);
 uint8_t write[]={0x12,9,0,0};assert(att(&server,write,4,response)==5&&response[4]==3);
 rg_disconnected(&server);unsigned offset=0;
 while(offset<128){uint8_t blob[]={0x0c,9,0,(uint8_t)offset,0};size_t n=att(&server,blob,5,response);assert(n>1&&n<=23);memcpy(reconstructed+offset,response+1,n-1);offset+=n-1;}
 assert(!memcmp(reconstructed,qca_diagnostic,128));
 uint8_t status[]={0x0a,7,0};assert(att(&server,status,3,response)==23&&!memcmp(response+1,"RFS\1",4));
 qca_collect(0);assert(get(8,8)==EFI_ERROR(2));
 puts("PCI collection + read-only ATT: bounds, absent/error/duplicate, location, 32/64-bit BAR, blob, legacy status PASS");
 return 0;
}
