#include "pci_identity.h"
int qca_pci_identity(const uint32_t c[16],QcaPciIdentity *out){
 if(!c||!out||c[0]!=0x0042168cu||(c[2]>>16)!=0x0280u||((c[3]>>16)&0x7f))return 1;
 uint32_t bar=c[4],type=(bar>>1)&3u;
 if((bar&1)||type==1||type==3)return 2;
 uint64_t address=bar&0xfffffff0u;
 if(type==2)address|=(uint64_t)c[5]<<32;
 if(!address||address==0xfffffff0ull||address==0xfffffffffffffff0ull)return 3;
 QcaPciIdentity value={0};
 value.subsystem_vendor=(uint16_t)c[11];value.subsystem_device=(uint16_t)(c[11]>>16);
 value.command=(uint16_t)c[1];value.revision=(uint8_t)c[2];value.bar64=(type==2);value.bar0=address;
 *out=value;return 0;
}
