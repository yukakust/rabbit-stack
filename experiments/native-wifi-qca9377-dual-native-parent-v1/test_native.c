#include "native_parent.h"
#include "reference/sha256.h"
#include "reference/monocypher-ed25519.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define C(x) do{checks++;if(!(x)){fprintf(stderr,"line%d %s\n",__LINE__,#x);exit(1);}}while(0)
static unsigned checks,mode,loads,starts,unloads,closes,revokes;
static DualNativeParent np;
static LoadedImage own_image;
static uint8_t own_code[MOD_AGGREGATE_MAX],boot[232] __attribute__((aligned(8)));
static unsigned allocs,frees,alloc_mode;
static uint8_t image_bytes[2][1536],packet[1824],arena[2][MOD_FILE_MAX],key[64],pub[32],target[32],hashes[2][32];
static LoadedImage loaded[2];static SystemTable table;static int parent,handles[2];
static void w32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=v>>(i*8);}
static void w64(uint8_t*p,uint64_t v){w32(p,v);w32(p+4,v>>32);}
static Status EFIAPI __attribute__((noinline,aligned(16384))) dispatch1(uint32_t op,void*a){C(op==0&&!a&&np.modules.busy);closes++;C(dual_close(&np.modules,65)<0);return mode==3?EFI_ERROR(3):0;}
static Status EFIAPI __attribute__((noinline,aligned(16384))) dispatch2(uint32_t op,void*a){C(op==0&&!a&&np.modules.busy);closes++;C(dual_close(&np.modules,65)<0);return mode==4?EFI_ERROR(3):0;}
static Status EFIAPI load(uint8_t boot,void*p,void*path,void*bytes,uint64_t n,void**out){
 C(!boot&&p==&parent&&!path&&n==1536&&np.modules.busy);unsigned i=bytes==arena[0]?0:1;C(bytes==arena[i]);loads++;C(np.modules.budget.mapped==np.modules.base_mapped+(i+1)*8192);C(np.modules.budget.last_counter==i+1);*out=&handles[i];return mode==1?EFI_ERROR(26):0;
}
static Status EFIAPI protocol(void*h,const Guid*g,void**out){C(g->a==loaded_image_guid.a);unsigned i=h==&handles[0]?0:1;if(h==&parent){*out=&own_image;return 0;}C(h==&handles[i]);*out=&loaded[i];return 0;}
static Status EFIAPI start(void*h,uint64_t*n,uint16_t**out){
 unsigned i=h==&handles[0]?0:1;C(h==&handles[i]);starts++;ModRegistration*r=loaded[i].options;C(r&&r->role==i+1&&np.modules.busy);r->dispatch=i?dispatch2:dispatch1;C(dual_close(&np.modules,65)<0);uint8_t digest[32];C(dual_seal(&np.modules,65,digest)<0);*n=0;*out=0;return mode==2?EFI_ERROR(3):0;
}
static Status EFIAPI unload(void*h){C(h==&handles[0]||h==&handles[1]);unloads++;return mode==5?EFI_ERROR(3):0;}
static Status EFIAPI release(void*p){C(p==arena[0]||p==arena[1]);frees++;for(unsigned i=0;i<MOD_FILE_MAX;i++)C(!((uint8_t*)p)[i]);return alloc_mode==5?EFI_ERROR(3):0;}
static Status EFIAPI allocate(uint32_t type,uint64_t n,void**out){C(type==2&&n==MOD_FILE_MAX&&np.busy);unsigned i=allocs++;if(alloc_mode==1){*out=0;return EFI_ERROR(9);}if(alloc_mode==2){*out=arena[i];return EFI_ERROR(9);}if(alloc_mode==3){*out=0;return 0;}if(alloc_mode==4){*out=&np;return 0;}*out=arena[i];return 0;}
static int revoke(void*c,uint64_t epoch,const uint8_t hash[32]){C(c==&parent&&epoch==65&&hash==np.modules.code_set&&np.modules.busy);revokes++;C(dual_close(&np.modules,65)<0);return mode==6?-1:0;}

static void make_pe(unsigned i){uint8_t*p=image_bytes[i];memset(p,0,1536);memcpy(p,"MZ",2);w32(p+60,64);memcpy(p+64,"PE\0\0",4);p[68]=0x64;p[69]=0x86;p[70]=1;p[84]=240;p[88]=0x0b;p[89]=2;w32(p+104,4096);w32(p+120,4096);w32(p+144,8192);w32(p+148,512);p[156]=11;w32(p+196,16);w32(p+336,1024);w32(p+340,4096);w32(p+344,1024);w32(p+348,512);w32(p+364,0x60000020);p[600]=i+1;rabbit_sha256(hashes[i],p,1536);}
static void fixture(unsigned m,uint32_t mapped){
 mode=m;loads=starts=unloads=closes=revokes=0;memset(&np,0,sizeof np);allocs=frees=0;memset(arena,0,sizeof arena);memset(target,2,32);make_pe(0);make_pe(1);
 for(unsigned i=0;i<2;i++){loaded[i]=(LoadedImage){0};loaded[i].system=&table;loaded[i].parent=&parent;loaded[i].base=(void*)((uintptr_t)(i?dispatch2:dispatch1)-4096);loaded[i].size=8192;}
 memset(boot,0,sizeof boot);((TableHeader*)boot)->signature=UINT64_C(0x56524553544f4f42);((TableHeader*)boot)->size=232;table.boot=boot;
 *(void**)(boot+64)=(void*)allocate;*(void**)(boot+72)=(void*)release;*(void**)(boot+152)=(void*)protocol;*(void**)(boot+200)=(void*)load;*(void**)(boot+208)=(void*)start;*(void**)(boot+224)=(void*)unload;
 own_image=(LoadedImage){0};own_image.system=&table;own_image.parent=&handles[0];own_image.base=own_code;own_image.size=mapped;
 C(!dn_bind(&np,&table,&parent,65,pub,target,hashes,revoke,&parent));C(dn_inventory(&np)&&allocs==2);C(dual_inventory(&np.modules));
}
static void frame(unsigned role){
 unsigned i=role-1;memset(packet,0,288);memcpy(packet,role==1?"RABMOD01":"RABRSN01",8);memcpy(packet+8,pub,32);memcpy(packet+40,target,32);memset(packet+72,3,32);memcpy(packet+104,hashes[i],32);memcpy(packet+136,hashes[i],32);w64(packet+168,65);w64(packet+176,role);w32(packet+184,1536);w32(packet+192,1536);w32(packet+196,role);w32(packet+200,1);w32(packet+204,8192);w32(packet+208,65536);crypto_ed25519_sign(packet+224,key,packet,224);memcpy(packet+288,image_bytes[i],1536);
}
static int old_dual_cases(void){
 uint8_t seed[32]={2,3,4};crypto_ed25519_key_pair(key,pub,seed);
 fixture(0,2236416);frame(1);C(!dual_accept(&np.modules,packet,sizeof packet,arena[0],sizeof arena[0]));C(np.modules.loader[0].active&&np.modules.budget.mapped==2244608);uint8_t sealed[32];C(dual_seal(&np.modules,65,sealed)<0);frame(2);C(!dual_accept(&np.modules,packet,sizeof packet,arena[1],sizeof arena[1]));C(np.modules.loader[1].active&&np.modules.budget.mapped==2252800&&np.modules.budget.last_counter==2);C(!dual_seal(&np.modules,65,sealed)&&!memcmp(sealed,np.modules.code_set,32));C(dual_accept(&np.modules,packet,sizeof packet,arena[1],sizeof arena[1])<0);C(dual_close(&np.modules,64)<0);C(!dual_close(&np.modules,65)&&np.modules.budget.mapped==np.modules.base_mapped&&closes==2&&unloads==2&&revokes==1);C(!dual_close(&np.modules,65)&&revokes==1&&unloads==2);for(unsigned i=0;i<sizeof arena;i++)C(!((uint8_t*)arena)[i]);
 fixture(0,MOD_AGGREGATE_MAX-8192);frame(1);C(!dual_accept(&np.modules,packet,sizeof packet,arena[0],sizeof arena[0]));frame(2);C(dual_accept(&np.modules,packet,sizeof packet,arena[1],sizeof arena[1])<0&&loads==1&&np.modules.budget.mapped==MOD_AGGREGATE_MAX&&!np.modules.artifact[1].memory);C(!dual_close(&np.modules,65)&&unloads==1);
 for(unsigned j=0;j<288;j++){fixture(0,2236416);frame(1);packet[j]^=1;C(dual_accept(&np.modules,packet,sizeof packet,arena[0],sizeof arena[0])<0);C(loads==0&&np.modules.budget.mapped==np.modules.base_mapped);}
 fixture(0,2236416);frame(1);packet[104]^=1;crypto_ed25519_sign(packet+224,key,packet,224);C(dual_accept(&np.modules,packet,sizeof packet,arena[0],sizeof arena[0])<0&&loads==0);C(dual_accept(&np.modules,(uint8_t*)&np.modules,288,arena[0],sizeof arena[0])<0);
 for(unsigned m=1;m<=6;m++){fixture(m,2236416);frame(1);int r=dual_accept(&np.modules,packet,sizeof packet,arena[0],sizeof arena[0]);if(m<3){C(r<0&&np.modules.quarantine&&loads==1);C(dual_close(&np.modules,65)<0);}else{C(!r);frame(2);C(!dual_accept(&np.modules,packet,sizeof packet,arena[1],sizeof arena[1]));C(!dual_seal(&np.modules,65,sealed));C(dual_close(&np.modules,65)<0);if(m==6){C(!np.modules.quarantine&&unloads==0&&np.modules.loader[0].active&&np.modules.loader[1].active);}else C(np.modules.quarantine);}}
 fixture(0,2236416);np.modules.quarantine=1;C(dual_accept(&np.modules,packet,sizeof packet,arena[0],sizeof arena[0])<0);C(dual_seal(&np.modules,65,sealed)<0);C(dual_close(&np.modules,65)<0);
 mod_wipe(key,sizeof key);printf("DUAL signed loader/shared mapped ledger: %u checks; firmware injected, physical=0\n",checks);return 0;
}

int main(void){
 old_dual_cases();unsigned cases=0;uint8_t seed[32]={2,3,4};crypto_ed25519_key_pair(key,pub,seed);
 alloc_mode=0;fixture(0,2236416);frame(1);C(!dn_accept(&np,packet,sizeof packet));frame(2);C(!dn_accept(&np,packet,sizeof packet));uint8_t digest[32];C(!dual_seal(&np.modules,65,digest));C(!dn_close(&np,65)&&frees==2&&np.closed&&!np.owned[0]&&!np.owned[1]);C(!dn_close(&np,65)&&frees==2);cases++;
 for(unsigned m=1;m<=5;m++){
  alloc_mode=0;fixture(0,2236416);C(!dn_close(&np,65));memset(&np,0,sizeof np);allocs=frees=0;alloc_mode=m;
  int r=dn_bind(&np,&table,&parent,65,pub,target,hashes,revoke,&parent);
  if(m<=4){C(r<0&&np.fault);if(m==1)C(!dn_close(&np,65)&&!frees);else C(dn_close(&np,65)<0&&!frees);}
  else{C(!r);C(dn_close(&np,65)<0&&frees==1&&np.uncertain[0]);C(dn_close(&np,65)<0&&frees==1);}
  cases++;
 }
 mod_wipe(key,sizeof key);printf("DIRECT-NATIVE-DUAL %u boundary cases / %u checks; firmware injected, physical=0\n",cases,checks);return 0;
}
