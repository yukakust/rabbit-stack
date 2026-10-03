/* Isolated QEMU probe. Never installed on Dell; no disks/variables written. */
#define FILE_LICENCE(x)
#define FILE_SECBOOT(x)
#include <ipxe/efi/Uefi.h>
#include <ipxe/efi/Protocol/SimpleNetwork.h>
#include <ipxe/efi/Protocol/Tcp4.h>
#include <ipxe/efi/Protocol/ServiceBinding.h>
#include <ipxe/efi/Protocol/LoadedImage.h>
#include <ipxe/efi/Protocol/DevicePath.h>
#include "driver_bytes.h"

static EFI_SYSTEM_TABLE *system;
#ifdef RF_RECEIVER
static void network_trial(void);
#endif
static void serial(char c) {
  __asm__ volatile("outb %0,%1" : : "a"(c), "Nd"((unsigned short)0x3f8));
}
static void say(const char *s) { while (*s) serial(*s++); }
static void hex(UINTN n) {
  const char *digits="0123456789abcdef";
  for (int i=60;i>=0;i-=4) serial(digits[(n>>i)&15]);
  say("\n");
}
static UINTN count(EFI_GUID *guid) {
  UINTN n=0; EFI_HANDLE *handles=0;
  EFI_STATUS s=system->BootServices->LocateHandleBuffer(ByProtocol,guid,0,&n,&handles);
  if (handles) system->BootServices->FreePool(handles);
  return EFI_ERROR(s)?0:n;
}
EFI_STATUS EFIAPI efi_main(EFI_HANDLE image, EFI_SYSTEM_TABLE *st) {
  (void)image; system=st;
  EFI_GUID snp=EFI_SIMPLE_NETWORK_PROTOCOL_GUID;
  EFI_GUID tcp=EFI_TCP4_SERVICE_BINDING_PROTOCOL_GUID;
  say("RABBIT SNP BEFORE ");hex(count(&snp));
  say("RABBIT TCP BEFORE ");hex(count(&tcp));
  EFI_HANDLE driver=0;
  EFI_GUID loaded_guid=EFI_LOADED_IMAGE_PROTOCOL_GUID,path_guid=EFI_DEVICE_PATH_PROTOCOL_GUID;
  EFI_LOADED_IMAGE_PROTOCOL *parent=0;
  EFI_DEVICE_PATH_PROTOCOL *path=0;
  st->BootServices->HandleProtocol(image,&loaded_guid,(void**)&parent);
  if(parent)st->BootServices->HandleProtocol(parent->DeviceHandle,&path_guid,(void**)&path);
  EFI_STATUS load=st->BootServices->LoadImage(FALSE,image,path,(void *)driver_bytes,sizeof(driver_bytes),&driver);
  say("RABBIT DRIVER LOAD ");hex(load);
  if(!EFI_ERROR(load)) {
    say("RABBIT DRIVER START ");hex(st->BootServices->StartImage(driver,0,0));
  }
  UINTN n=0; EFI_HANDLE *all=0;
  if (!EFI_ERROR(st->BootServices->LocateHandleBuffer(AllHandles,0,0,&n,&all))) {
    for(UINTN i=0;i<n;i++) st->BootServices->ConnectController(all[i],0,0,TRUE);
    st->BootServices->FreePool(all);
  }
  say("RABBIT SNP AFTER ");hex(count(&snp));
  say("RABBIT TCP AFTER ");hex(count(&tcp));
#ifdef RF_RECEIVER
  network_trial();
#endif
  if(driver){say("RABBIT DRIVER UNLOAD ");hex(st->BootServices->UnloadImage(driver));}
  say("RABBIT SNP FINAL ");hex(count(&snp));
  __asm__ volatile("outw %0,%1" : : "a"((unsigned short)0x2000), "Nd"((unsigned short)0x604));
  return EFI_SUCCESS;
}
