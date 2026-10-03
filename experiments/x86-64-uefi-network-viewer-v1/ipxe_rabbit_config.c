/* Rabbit's small adapter to iPXE, GPL-2.0-or-later. */
FILE_LICENCE ( GPL2_OR_LATER );
FILE_SECBOOT ( FORBIDDEN );
#define ERRFILE_ipxe_rabbit_config ERRFILE_efi_init
#include <errno.h>
#include <ipxe/interface.h>
#include <ipxe/netdevice.h>
#include <ipxe/dhcp.h>
#include <ipxe/efi/efi.h>
#include <ipxe/efi/efi_snp.h>

/* Pending DHCP progresses only when the caller polls the download service. */
typedef struct {
 EFI_STATUS (EFIAPI *Begin)(void);
 EFI_STATUS (EFIAPI *Status)(void);
 EFI_STATUS (EFIAPI *Close)(void);
} RabbitConfig;
static EFI_GUID guid={0x384c4d11,0x7b19,0x44a2,{0xb1,0x16,0x71,0x4a,0x66,0x21,0x08,0x03}};
static struct net_device *device;
static int result;
static void complete(struct interface *job,int rc){result=rc;intf_restart(job,rc);}
static struct interface_operation operations[]={INTF_OP(intf_close,struct interface *,complete)};
static struct interface_descriptor descriptor=INTF_DESC_PURE(operations);
static struct interface job=INTF_INIT(descriptor);
static EFI_STATUS EFIAPI begin(void){
 if(device)return EFI_ALREADY_STARTED;
 struct net_device *candidate;
 for_each_netdev(candidate){device=netdev_get(candidate);break;}
 if(!device)return EFI_NOT_FOUND;
 efi_snp_claim();
 result=netdev_open(device);
 if(result)return EFIRC(result);
 result=-EINPROGRESS;
 int rc=start_dhcp(&job,device);
 if(rc)result=rc;
 return rc?EFIRC(rc):EFI_SUCCESS;
}
static EFI_STATUS EFIAPI status(void){return result==-EINPROGRESS?EFI_NOT_READY:EFIRC(result);}
static EFI_STATUS EFIAPI close(void){
 if(!device)return EFI_SUCCESS;
 intf_restart(&job,-ECANCELED);
 netdev_close(device);netdev_put(device);device=0;
 efi_snp_release();result=-ENODEV;
 return EFI_SUCCESS;
}
static RabbitConfig protocol={begin,status,close};
int rabbit_config_install(EFI_HANDLE handle){
 EFI_STATUS rc=efi_systab->BootServices->InstallMultipleProtocolInterfaces(&handle,&guid,&protocol,NULL);
 return rc?-EEFI(rc):0;
}
void rabbit_config_uninstall(EFI_HANDLE handle){
 close();
 efi_systab->BootServices->UninstallMultipleProtocolInterfaces(handle,&guid,&protocol,NULL);
}
