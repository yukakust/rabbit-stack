/* Public RFC8032 fixture only; injected firmware, never physical invocation. */
#include "loader.h"
#include "reference/sha256.h"
#include "reference/monocypher-ed25519.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks,mode,loads,starts,unloads,closes,frees;
#define C(x) do{checks++;assert(x);}while(0)
static uint8_t data[MOD_FILE_MAX],memory[MOD_FILE_MAX],packet[MOD_HEADER+MOD_CHUNK],secret[64],pub[32];
static LoadedImage image;static SystemTable table;static int handle,parent;
static void put32(uint8_t*p,uint32_t x){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(x>>(8*i));}
static void put64(uint8_t*p,uint64_t x){put32(p,(uint32_t)x);put32(p+4,(uint32_t)(x>>32));}
static Status EFIAPI dispatch(uint32_t op,void*a){(void)a;C(op==0);closes++;return mode==7?EFI_ERROR(3):0;}
static Status EFIAPI load(uint8_t boot,void*p,void*path,void*src,uint64_t bytes,void**out){C(!boot&&p==&parent&&!path&&src==memory&&bytes>=1536);loads++;*out=mode==1||mode==12?0:&handle;return mode==1||mode==2?EFI_ERROR(26):0;}
static Status EFIAPI protocol(void*h,const Guid*g,void**out){C(h==&handle&&g->a==loaded_image_guid.a);*out=mode==3?0:&image;return mode==3||mode==13?EFI_ERROR(3):0;}
static Status EFIAPI start(void*h,uint64_t*z,uint16_t**d){C(h==&handle);starts++;ModRegistration*r=image.options;C(r&&image.options_size==sizeof(*r));r->dispatch=mode==4?(ModDispatch)((uintptr_t)image.base+1):dispatch;if(mode==5)r->epoch++;*z=0;*d=0;static uint16_t exit_message[2];if(mode==9||mode==10||mode==11){*d=exit_message;*z=mode==10?0:sizeof(exit_message);}return mode==6?EFI_ERROR(3):0;}
static Status EFIAPI unload(void*h){C(h==&handle);unloads++;return mode==8?EFI_ERROR(3):0;}
static Status EFIAPI free_pool(void*p){(void)p;frees++;return mode==9?EFI_ERROR(3):0;}
static void make_pe(size_t n){memset(data,0,n);data[0]='M';data[1]='Z';put32(data+60,64);memcpy(data+64,"PE\0\0",4);data[68]=0x64;data[69]=0x86;data[70]=1;data[84]=240;data[88]=0xb;data[89]=2;put32(data+104,4096);put32(data+120,4096);put32(data+144,8192);put32(data+148,512);data[156]=11;put32(data+196,16);uint8_t*s=data+328;put32(s+8,1024);put32(s+12,4096);put32(s+16,1024);put32(s+20,512);put32(s+36,0x60000020);}
static ModPolicy policy(size_t n){ModPolicy p={0};memcpy(p.owner,pub,32);memset(p.target,2,32);memset(p.parent_hash,3,32);rabbit_sha256(p.digest,data,n);p.epoch=64;p.counter=2;p.last_counter=1;p.total=(uint32_t)n;p.mapped=8192;p.role=1;p.abi=1;return p;}
static size_t frame(const ModPolicy*p,uint32_t offset){size_t len=p->total-offset;if(len>MOD_CHUNK)len=MOD_CHUNK;memset(packet,0,MOD_HEADER);memcpy(packet,"RABMOD01",8);memcpy(packet+8,p->owner,32);memcpy(packet+40,p->target,32);memcpy(packet+72,p->parent_hash,32);memcpy(packet+104,p->digest,32);rabbit_sha256(packet+136,data+offset,len);put64(packet+168,p->epoch);put64(packet+176,p->counter);put32(packet+184,p->total);put32(packet+188,offset);put32(packet+192,(uint32_t)len);put32(packet+196,p->role);put32(packet+200,p->abi);put32(packet+204,p->mapped);put32(packet+208,MOD_CHUNK);crypto_ed25519_sign(packet+224,secret,packet,224);memcpy(packet+MOD_HEADER,data+offset,len);return MOD_HEADER+len;}
static void setup(ModArtifact*a,ModPolicy*p){C(!mod_begin(a,p,memory,sizeof(memory)));for(uint32_t off=0;off<p->total;off+=MOD_CHUNK)C(!mod_accept(a,packet,frame(p,off)));C(a->ready);}
int main(void){
 uint8_t seed[32]={0x9d,0x61,0xb1,0x9d,0xef,0xfd,0x5a,0x60,0xba,0x84,0x4a,0xf4,0x92,0xec,0x2c,0xc4,0x44,0x49,0xc5,0x69,0x7b,0x32,0x69,0x19,0x70,0x3b,0xac,0x03,0x1c,0xae,0x7f,0x60};crypto_ed25519_key_pair(secret,pub,seed);
 make_pe(sizeof(data));ModPolicy p=policy(sizeof(data));ModArtifact a={0};C(!mod_begin(&a,&p,memory,sizeof(memory)));C(mod_accept(&a,packet,frame(&p,3))<0);for(unsigned off=0;off<MOD_FILE_MAX;off+=MOD_CHUNK){size_t n=frame(&p,off);C(!mod_accept(&a,packet,n));C(mod_accept(&a,packet,n)==1);}C(a.ready);C(!mod_pin(&a));C(mod_cancel(&a)<0);a.pinned=0;C(!mod_cancel(&a));for(size_t i=0;i<sizeof(memory);i++)C(!memory[i]);
 make_pe(1536);p=policy(1536);size_t n=frame(&p,0);for(size_t i=0;i<MOD_HEADER;i++){a=(ModArtifact){0};C(!mod_begin(&a,&p,memory,sizeof(memory)));packet[i]^=1;C(mod_accept(&a,packet,n)<0);packet[i]^=1;C(!a.received);C(!mod_cancel(&a));}
 a=(ModArtifact){0};C(mod_begin(&a,&a.policy,memory,sizeof(memory))<0);C(mod_begin(&a,&p,(uint8_t*)&a,sizeof(a))<0);C(mod_overlap((void*)(UINTPTR_MAX-2),4,memory,1));
 
 /* Meaningful body/full-hash and contradictory owner-signed duplicate cases. */
 a=(ModArtifact){0};p=policy(1536);n=frame(&p,0);C(!mod_begin(&a,&p,memory,sizeof(memory)));packet[MOD_HEADER+5]^=1;C(mod_accept(&a,packet,n)==-5&&!a.received);C(!mod_cancel(&a));
 a=(ModArtifact){0};p=policy(1536);p.digest[0]^=1;n=frame(&p,0);C(!mod_begin(&a,&p,memory,sizeof(memory)));C(mod_accept(&a,packet,n)==-7&&a.poisoned&&!a.ready);C(!mod_cancel(&a));
 a=(ModArtifact){0};p=policy(1536);setup(&a,&p);data[520]^=1;n=frame(&p,0);C(mod_accept(&a,packet,n)==-6&&a.poisoned&&!a.ready);data[520]^=1;C(!mod_cancel(&a));
 for(unsigned size=65537;size<=196613;size+=65538){make_pe(size);p=policy(size);a=(ModArtifact){0};setup(&a,&p);C(!mod_cancel(&a));}
 make_pe(1536);p=policy(1536);
 uint32_t m,e;C(!mod_pe(data,1536,&m,&e)&&m==8192&&e==4096);data[328+36]|=0x80;/* low flags no WX here */data[328+39]|=0x80;C(mod_pe(data,1536,&m,&e)<0);make_pe(1536);
 for(mode=0;mode<9;mode++){loads=starts=unloads=closes=0;a=(ModArtifact){0};p=policy(1536);setup(&a,&p);ModLoader l={0};ModBudget b={2224128,1,64,{0}};memcpy(b.parent_hash,p.parent_hash,32);image=(LoadedImage){0};image.system=&table;image.parent=&parent;image.base=(void*)((uintptr_t)dispatch-4096);image.size=8192;ModEfi ef={&table,&parent,load,start,unload,protocol,free_pool};int result=mod_load(&l,&a,&b,&ef);C(loads==1&&b.last_counter==2);C(mod_load(&l,&a,&b,&ef)<0&&loads==1);if(mode==0){C(!result&&l.active&&b.mapped==2232320);C(!mod_unload(&l)&&!a.memory&&b.mapped==2224128&&unloads==1&&closes==1);}else if(mode==7||mode==8){C(!result);C(mod_unload(&l)<0&&l.quarantine&&a.pinned);C(mod_unload(&l)<0);C(unloads==(mode==8?1:0));}else {C(result<0&&!l.active);if(mode==2)C(l.quarantine&&a.pinned&&unloads==0);else C(!a.memory&&unloads==(mode==1?0:1));}C(!image.options&&!image.options_size);}

 for(mode=9;mode<=17;mode++){
  loads=starts=unloads=closes=frees=0;a=(ModArtifact){0};p=policy(1536);setup(&a,&p);ModLoader f={0};ModBudget z={2224128,1,64,{0}};memcpy(z.parent_hash,p.parent_hash,32);image=(LoadedImage){.system=&table,.parent=&parent,.base=(void*)((uintptr_t)dispatch-4096),.size=8192};
  if(mode==14)image.parent=&handle;if(mode==15)image.size=4096;if(mode==16)image.options=&p;if(mode==17)image.unload=(Status(EFIAPI*)(void*))((uintptr_t)image.base+1);
  ModEfi v={&table,&parent,load,start,unload,protocol,free_pool};int rc=mod_load(&f,&a,&z,&v);
  if(mode==11){C(!rc&&f.active&&frees==1);C(!mod_unload(&f)&&!a.memory);}else if(mode==14||mode==15||mode==16){C(rc<0&&unloads==1&&!a.memory);}else {C(rc<0&&f.quarantine&&a.pinned&&!unloads);C(mod_unload(&f)<0);}
 }
 a=(ModArtifact){0};p=policy(1536);setup(&a,&p);ModLoader l={0};ModBudget b={MOD_AGGREGATE_MAX-4096,1,64,{0}};memcpy(b.parent_hash,p.parent_hash,32);ModEfi ef={&table,&parent,load,start,unload,protocol,free_pool};loads=0;C(mod_load(&l,&a,&b,&ef)<0&&loads==0&&!a.pinned);b.mapped=2224128;b.epoch=65;C(mod_load(&l,&a,&b,&ef)<0&&loads==0);b.epoch=64;b.last_counter=2;C(mod_load(&l,&a,&b,&ef)<0&&loads==0);C(!mod_cancel(&a));mod_wipe(secret,sizeof(secret));puts("PASS genuine owner-signature chunks + injected UEFI ownership/failure models; physical_calls=0");printf("checks=%u\n",checks);return 0;
}
