/* Only official layout assertions; NEVER calls any real firmware method. */
#include "reference/connected_platform_abi.h"
#include "reference/oracle-boot.h"
#include <stdio.h>
_Static_assert(offsetof(EFI_BOOT_SERVICES,LoadImage)==200,"official LoadImage offset");
_Static_assert(offsetof(EFI_BOOT_SERVICES,StartImage)==208,"official StartImage offset");
_Static_assert(offsetof(EFI_BOOT_SERVICES,UnloadImage)==224,"official UnloadImage offset");
_Static_assert(offsetof(EFI_BOOT_SERVICES,HandleProtocol)==152,"official HandleProtocol offset");
_Static_assert(offsetof(EFI_BOOT_SERVICES,InstallProtocolInterface)==128,"official protocol offset");
_Static_assert(offsetof(EFI_BOOT_SERVICES,FreePool)==72,"official exit-data cleanup");
_Static_assert(offsetof(SystemTable,boot)==96&&sizeof(SystemTable)==120,"actual parent ABI");
_Static_assert(offsetof(LoadedImage,options_size)==48&&offsetof(LoadedImage,options)==56,"actual options ABI");
_Static_assert(offsetof(LoadedImage,base)==64&&offsetof(LoadedImage,size)==72&&offsetof(LoadedImage,unload)==88,"actual image bounds/lifetime");
int main(void){puts("PASS 9 UEFI existing load/registration layout assertions; firmware_calls=0");return 0;}
