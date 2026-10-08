#include "probe65.h"
#include "inventory.h"
#include "platform.h"
#include "pci_collect.h"
#include "inventory65_hashes.h"
static RngSession rng_session;
static unsigned attempted,closed;
static void put32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
static void put64(uint8_t*p,uint64_t v){put32(p,(uint32_t)v);put32(p+4,(uint32_t)(v>>32));}
static void copy(uint8_t*d,const void*s,size_t n){const uint8_t*p=s;for(size_t i=0;i<n;i++)d[i]=p[i];}
int inventory65_begin(const void*system){
 if(attempted)return 0;attempted=1;
 for(unsigned i=0;i<QCA_DIAGNOSTIC_SIZE;i++)qca_diagnostic[i]=0;
 copy(qca_diagnostic,"QINV0065",8);put32(qca_diagnostic+8,1);put32(qca_diagnostic+12,QCA_DIAGNOSTIC_SIZE);put64(qca_diagnostic+16,65);
 put32(qca_diagnostic+24,sizeof(InvRecord));put32(qca_diagnostic+28,sizeof(RngPublicDiagnostic));copy(qca_diagnostic+40,probe65_code_sha256,32);
 InvRecord cpu={0};int cpu_result=inv_capture(&cpu,inv_cpuid_native,0,65,cpuid65_source_sha256);put32(qca_diagnostic+32,cpu_result?1:0);copy(qca_diagnostic+80,&cpu,sizeof(cpu));
 RngBootApi boot;RngPublicDiagnostic public={0};int discovered=-1;
 if(protected_boot_api(system,&boot))discovered=rng_discover(&rng_session,&boot,65);
 rng_diagnostic(&rng_session,probe65_code_sha256,&public);copy(qca_diagnostic+336,&public,sizeof(public));put32(qca_diagnostic+688,(uint32_t)discovered);
 /* Discover already attempted its pool cleanup. Never retry a failed free. */
 int cleanup=(rng_session.pool_uncertain||(rng_session.pool&&rng_session.error==9))?0:rng_cleanup(&rng_session);put32(qca_diagnostic+692,cleanup?1:0);
 RngPublicDiagnostic after={0};rng_diagnostic(&rng_session,probe65_code_sha256,&after);put32(qca_diagnostic+696,after.owned_pool_count);put32(qca_diagnostic+700,after.uncertain_pool_count);
 /* No entropy approval, no GetRNG call count, no RF/DMA acquisition. */
 closed=cleanup&&!after.owned_pool_count&&!after.uncertain_pool_count;
 put32(qca_diagnostic+704,closed);return 1;
}
int inventory65_close(void){return !attempted||closed;}
