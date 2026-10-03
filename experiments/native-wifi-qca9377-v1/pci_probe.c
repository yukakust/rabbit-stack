/* Read-only standalone UEFI diagnostic: VM fixture ONLY, not installed on Dell. */
#define FILE_LICENCE(x)
#define FILE_SECBOOT(x)
#include <ipxe/efi/Uefi.h>
#include <ipxe/efi/Protocol/PciIo.h>
#include "pci_identity.h"
static void say(const char *s){
 while(*s){__asm__ volatile("outb %0,%1" : : "a"(*s++),"Nd"((unsigned short)0x3f8));}
}
static void hex(UINT64 n){
 const char *digits="0123456789abcdef";
 for(int i=60;i>=0;i-=4){char c=digits[(n>>i)&15];__asm__ volatile("outb %0,%1" : : "a"(c),"Nd"((unsigned short)0x3f8));}
 say("\n");
}
EFI_STATUS EFIAPI efi_main(EFI_HANDLE image,EFI_SYSTEM_TABLE *st){
 (void)image;EFI_GUID guid=EFI_PCI_IO_PROTOCOL_GUID;
 EFI_HANDLE *handles=0;UINTN count=0,targets=0;
 EFI_STATUS rc=st->BootServices->LocateHandleBuffer(ByProtocol,&guid,0,&count,&handles);
 say("QCA PCI ENUM STATUS ");hex(rc);
 if(!EFI_ERROR(rc)&&count<=64){
  say("QCA PCI HANDLE COUNT ");hex(count);
  for(UINTN i=0;i<count;i++){
   EFI_PCI_IO_PROTOCOL *pci=0;UINT32 config[16]={0};QcaPciIdentity identity;
   if(EFI_ERROR(st->BootServices->HandleProtocol(handles[i],&guid,(void**)&pci))||!pci)continue;
   if(EFI_ERROR(pci->Pci.Read(pci,EfiPciIoWidthUint32,0,16,config)))continue;
   if(config[0]!=0x0042168cu)continue;
   targets++;say("QCA PCI SNAPSHOT RESULT ");hex(qca_pci_identity(config,&identity));
   /* Report every raw header word, even when BAR is disabled or not assigned. */
   for(UINTN j=0;j<16;j++){say("QCA PCI CONFIG WORD ");hex(config[j]);}
   UINTN segment=0,bus=0,device=0,function=0;
   rc=pci->GetLocation(pci,&segment,&bus,&device,&function);
   say("QCA PCI LOCATION STATUS ");hex(rc);
   if(!EFI_ERROR(rc)){hex(segment);hex(bus);hex(device);hex(function);}
  }
 }
 if(handles)st->BootServices->FreePool(handles);
 say("QCA PCI TARGET COUNT ");hex(targets);
 say("QCA PCI WRITES=0 MMIO=0 DMA=0 RADIO=0\n");
 /* VM harness poweroff; remove before any integration into active city. */
 __asm__ volatile("outw %0,%1" : : "a"((unsigned short)0x2000),"Nd"((unsigned short)0x604));
 return EFI_SUCCESS;
}
