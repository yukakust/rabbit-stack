#include "pci_identity.h"
#include <assert.h>
#include <stdio.h>
static void rejected(uint32_t *c){QcaPciIdentity v={.bar0=123};assert(qca_pci_identity(c,&v));assert(v.bar0==123);}
int main(void){
 uint32_t c[16]={0};QcaPciIdentity v;
 c[0]=0x0042168c;c[1]=6;c[2]=0x02800031;c[4]=0xd0000000;c[11]=0x18101028;
 assert(!qca_pci_identity(c,&v)&&v.bar0==0xd0000000&&v.subsystem_vendor==0x1028&&v.subsystem_device==0x1810&&v.revision==0x31&&!v.bar64);
 c[4]=0x10000004;c[5]=1;
 assert(!qca_pci_identity(c,&v)&&v.bar0==0x110000000ull&&v.bar64);
 for(unsigned i=0;i<32;i++){uint32_t original=c[0];c[0]^=1u<<i;rejected(c);c[0]=original;}
 c[2]=0x02000031;rejected(c);c[2]=0x02800031;
 c[3]=0x00010000;rejected(c);c[3]=0;
 for(unsigned i=0;i<8;i++)if((i&1)||i==2||i==6){c[4]=0x10000000|i;rejected(c);}
 c[4]=0;rejected(c);c[4]=0xfffffff0;rejected(c);
 c[4]=0xfffffff4;c[5]=0xffffffff;rejected(c);
 puts("PASS PCI snapshot: identity/subsystem/revision,32/64bit BAR,invalid target/BAR,unchanged-on-rejection");
 return 0;
}
