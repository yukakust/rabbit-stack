/* Read-only active-profile probe. No PCI write, MMIO, DMA, UART or shutdown. */
#include "scene_abi.h"
#include "pci_collect.h"
#include "pci_identity.h"
uint8_t qca_diagnostic[QCA_DIAGNOSTIC_SIZE];
static void put(unsigned offset,uint64_t value,unsigned bytes){
 for(unsigned i=0;i<bytes;i++)qca_diagnostic[offset+i]=(uint8_t)(value>>(8*i));
}
typedef Status(EFIAPI *LocateHandles)(uint32_t,const Guid*,void*,uint64_t*,void***);
typedef Status(EFIAPI *FreePool)(void*);
typedef Status(EFIAPI *ReadPci)(void*,uint32_t,uint32_t,uint64_t,void*);
typedef Status(EFIAPI *Location)(void*,uint64_t*,uint64_t*,uint64_t*,uint64_t*);
static void *pci_function(void*p,unsigned offset){return *(void**)((uint8_t*)p+offset);}
void qca_collect(SystemTable*st){
 static const Guid guid={0x4cf5b200,0x68b8,0x4ca5,{0x9e,0xec,0xb2,0x3e,0x3f,0x50,0x02,0x9a}};
 for(unsigned i=0;i<QCA_DIAGNOSTIC_SIZE;i++)qca_diagnostic[i]=0;
 qca_diagnostic[0]='Q';qca_diagnostic[1]='P';qca_diagnostic[2]='D';qca_diagnostic[3]=1;
 if(!st||!st->boot){put(8,EFI_ERROR(2),8);return;}
 void**handles=0;uint64_t count=0;uint32_t flags=0,targets=0;
 Status rc=((LocateHandles)service(st,312))(2,&guid,0,&count,&handles);
 put(8,rc,8);put(16,count>0xffffffffu?0xffffffffu:count,4);
 if(!rc){
  flags=1;
  if(count>64||(!handles&&count))flags|=16;
  else for(uint64_t i=0;i<count;i++){
   void*pci=0;uint32_t config[16]={0};QcaPciIdentity identity;
   rc=((HandleProtocol)service(st,152))(handles[i],&guid,&pci);
   if(rc||!pci){put(24,rc?rc:EFI_ERROR(2),8);continue;}
   rc=((ReadPci)pci_function(pci,48))(pci,2,0,16,config);
   if(rc){put(24,rc,8);continue;}
   if(config[0]!=0x0042168cu)continue;
   if(++targets>1){flags|=32;continue;}
   flags|=2;
   for(unsigned j=0;j<16;j++)put(64+4*j,config[j],4);
   int decoded=qca_pci_identity(config,&identity);put(56,(uint32_t)decoded,4);
   if(!decoded)flags|=4;
   uint64_t segment=0,bus=0,device=0,function=0;
   rc=((Location)pci_function(pci,112))(pci,&segment,&bus,&device,&function);put(32,rc,8);
   if(!rc&&segment<=65535&&bus<=255&&device<=31&&function<=7){
    flags|=8;put(40,segment,4);put(44,bus,4);put(48,device,4);put(52,function,4);
   }
  }
 }
 if(handles)((FreePool)service(st,72))(handles);
 put(4,flags,4);put(20,targets,4);
}
