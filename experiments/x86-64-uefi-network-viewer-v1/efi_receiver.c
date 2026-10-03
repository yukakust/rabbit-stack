/* Test-only standalone EFI app. Production native profile is a separate gate. */
#define RF_RECEIVER
#include "efi_probe.c"
#include <ipxe/efi/efi_download.h>
#include <ipxe/efi/Protocol/GraphicsOutput.h>
#include "frame_core.h"
#include "fixture_public.h"
typedef struct {
 EFI_STATUS (EFIAPI *Begin)(void);
 EFI_STATUS (EFIAPI *Status)(void);
 EFI_STATUS (EFIAPI *Close)(void);
} RabbitConfig;
static uint8_t *wire;
static size_t used;
static int finished;
static EFI_STATUS transfer_status;
static IPXE_DOWNLOAD_PROTOCOL *download;
static unsigned poll_limit=15000;
static EFI_STATUS EFIAPI data(void *ctx,void *bytes,UINTN length,UINTN offset){
 (void)ctx;
 if(!length)return offset<=RF_MAX_WIRE?EFI_SUCCESS:EFI_BAD_BUFFER_SIZE;
 if(offset!=used||length>RF_MAX_WIRE-used)return EFI_BAD_BUFFER_SIZE;
 for(UINTN i=0;i<length;i++)wire[used+i]=((uint8_t*)bytes)[i];
 used+=length;return EFI_SUCCESS;
}
static void EFIAPI done(void *ctx,EFI_STATUS status){
 (void)ctx;transfer_status=status;finished=1;
}
static EFI_STATUS fetch(char *url){
 IPXE_DOWNLOAD_FILE token=0;used=0;finished=0;
 EFI_STATUS rc=download->Start(download,url,data,done,0,&token);
 if(EFI_ERROR(rc))return rc;
 /* Standalone test loop. Native root must call one Poll per existing tick. */
 for(unsigned i=0;i<poll_limit&&!finished;i++){
  download->Poll(download);system->BootServices->Stall(1000);
 }
 if(!finished)download->Abort(download,token,EFI_TIMEOUT);
 download->Poll(download); /* retire allocations after callbacks return */
 return finished?transfer_status:EFI_TIMEOUT;
}
static void network_trial(void){
 EFI_GUID config_guid={0x384c4d11,0x7b19,0x44a2,{0xb1,0x16,0x71,0x4a,0x66,0x21,0x08,0x03}};
 EFI_GUID download_guid=IPXE_DOWNLOAD_PROTOCOL_GUID,gop_guid=EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID;
 RabbitConfig *config=0;EFI_GRAPHICS_OUTPUT_PROTOCOL *gop=0;
 UINT32 *pixels=0;RfFrame state={0};uint8_t stream[16]={0};
 EFI_BOOT_SERVICES *bs=system->BootServices;
 EFI_STATUS rc=bs->LocateProtocol(&config_guid,0,(void**)&config);
 say("RABBIT CONFIG SERVICE ");hex(rc);if(EFI_ERROR(rc))return;
 rc=bs->LocateProtocol(&download_guid,0,(void**)&download);
 say("RABBIT DOWNLOAD SERVICE ");hex(rc);if(EFI_ERROR(rc))return;
 if(EFI_ERROR(bs->AllocatePool(EfiBootServicesData,RF_MAX_WIRE,(void**)&wire)))return;
 if(EFI_ERROR(bs->AllocatePool(EfiBootServicesData,RF_MAX_PIXELS*4,(void**)&pixels)))goto release;
 rc=config->Begin();say("RABBIT DHCP BEGIN ");hex(rc);
 if(EFI_ERROR(rc))goto close;
 for(unsigned i=0;i<12000&&config->Status()==EFI_NOT_READY;i++){
  download->Poll(download);bs->Stall(1000);
 }
 rc=config->Status();say("RABBIT DHCP STATUS ");hex(rc);if(EFI_ERROR(rc))goto close;
 rc=fetch("http://10.0.2.2:9783/first.rpf");say("RABBIT HTTP FIRST ");hex(rc);
 if(EFI_ERROR(rc))goto close;
 int decoded=rf_accept(wire,used,stream,fixture_public,&state,pixels,RF_MAX_PIXELS);
 say("RABBIT DECODE FIRST ");hex(decoded);if(decoded)goto close;
 say("RABBIT SEQUENCE FIRST ");hex(state.sequence);
 if(!EFI_ERROR(bs->LocateProtocol(&gop_guid,0,(void**)&gop))){
  /* Separate viewer rectangle. Never overwrite the left-hand fixture region. */
  UINTN x=gop->Mode->Info->HorizontalResolution>640?gop->Mode->Info->HorizontalResolution-640:0;
  UINTN h=gop->Mode->Info->VerticalResolution;
  if(x&&h>=360){
   EFI_GRAPHICS_OUTPUT_BLT_PIXEL old={0x20,0xa0,0x20,0};
   gop->Blt(gop,&old,EfiBltVideoFill,0,0,0,0,x,h,0);
   rc=gop->Blt(gop,(EFI_GRAPHICS_OUTPUT_BLT_PIXEL*)pixels,EfiBltBufferToVideo,0,0,x,0,640,360,640*4);
   say("RABBIT GOP PRESENT ");hex(rc);
   say("RABBIT FRAME VISIBLE\n");bs->Stall(3000000);
  }
 }
 uint32_t sentinel=pixels[0];
 rc=fetch("http://10.0.2.2:9783/invalid.rpf");
 decoded=EFI_ERROR(rc)?-1:rf_accept(wire,used,stream,fixture_public,&state,pixels,RF_MAX_PIXELS);
 if(decoded&&state.sequence==1&&pixels[0]==sentinel)say("RABBIT BAD SIGNATURE PRESERVED\n");
 rc=fetch("http://10.0.2.2:9783/second.rpf");
 if(!EFI_ERROR(rc)&&!rf_accept(wire,used,stream,fixture_public,&state,pixels,RF_MAX_PIXELS)){
  say("RABBIT SEQUENCE SECOND ");hex(state.sequence);
 }
 rc=fetch("http://10.0.2.2:9783/oversize.rpf");
 if(EFI_ERROR(rc)&&state.sequence==2&&pixels[0]==sentinel)say("RABBIT OVERSIZE PRESERVED\n");
 poll_limit=100;
 rc=fetch("http://10.0.2.2:9783/slow.rpf");
 if(rc==EFI_TIMEOUT&&state.sequence==2&&pixels[0]==sentinel)say("RABBIT ABORT PRESERVED\n");
 poll_limit=15000;
 rc=fetch("http://10.0.2.2:9783/second.rpf");
 if(!EFI_ERROR(rc)&&rf_accept(wire,used,stream,fixture_public,&state,pixels,RF_MAX_PIXELS)&&
    state.sequence==2&&pixels[0]==sentinel)say("RABBIT REPLAY AFTER ABORT PRESERVED\n");
close:
 rc=config->Close();say("RABBIT CONFIG CLOSE ");hex(rc);
 if(pixels)bs->FreePool(pixels);
release:
 bs->FreePool(wire);wire=0;
}
/* Compiler intrinsics for freestanding COFF crypto. */
void *memcpy(void *d,const void *s,size_t n){for(size_t i=0;i<n;i++)((unsigned char*)d)[i]=((const unsigned char*)s)[i];return d;}
void *memset(void *d,int c,size_t n){for(size_t i=0;i<n;i++)((unsigned char*)d)[i]=(unsigned char)c;return d;}
int memcmp(const void *a,const void *b,size_t n){for(size_t i=0;i<n;i++)if(((const unsigned char*)a)[i]!=((const unsigned char*)b)[i])return ((const unsigned char*)a)[i]-((const unsigned char*)b)[i];return 0;}
