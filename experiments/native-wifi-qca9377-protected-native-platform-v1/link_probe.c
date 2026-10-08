#include "platform.h"
/* Link-only probe, never launched. No firmware method calls or RNG sample. */
void*memset(void*d,int value,size_t n){volatile unsigned char*p=d;while(n--)*p++=(unsigned char)value;return d;}
RngStatus RNG_EFIAPI link_entry(void*handle,void*system){
 (void)handle;RngBootApi api={0};return protected_boot_api(system,&api)?0:1;
}
