#include "dual.h"
#include "reference/sha256.h"
#include "reference/monocypher-ed25519.h"
static uint32_t u32(const uint8_t*p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static uint64_t u64(const uint8_t*p){return u32(p)|(uint64_t)u32(p+4)<<32;}
static int eq(const void*a,const void*b,size_t n){const uint8_t*x=a,*y=b;unsigned d=0;while(n--)d|=*x++^*y++;return !d;}
static int nz(const void*a,size_t n){const uint8_t*p=a;unsigned x=0;while(n--)x|=*p++;return !!x;}
static void cp(void*a,const void*b,size_t n){uint8_t*x=a;const uint8_t*y=b;while(n--)*x++=*y++;}
static int outside(const DualModules*d,const void*p,size_t n){
 if(!p||!n||mod_overlap(d,sizeof *d,p,n))return 0;
 for(unsigned i=0;i<2;i++){const ModLoader*l=&d->loader[i];const ModArtifact*a=&d->artifact[i];if((a->memory&&mod_overlap(a->memory,a->capacity,p,n))||(l->image&&mod_overlap(l->image,sizeof *l->image,p,n))||(l->image&&l->image->base&&mod_overlap(l->image->base,l->image->size,p,n)))return 0;}
 return 1;
}
int dual_inventory(const DualModules*d){
 if(!d||!d->initialized||!d->budget.epoch||d->base_mapped>MOD_AGGREGATE_MAX||d->budget.mapped>MOD_AGGREGATE_MAX)return 0;
 uint64_t total=d->base_mapped;
 for(unsigned i=0;i<2;i++){
  const ModLoader*l=&d->loader[i];const ModArtifact*a=&d->artifact[i];total+=l->reserved_mapped;
  if(l->attempted&&(l->budget!=&d->budget||l->artifact!=a))return 0;
  if(a->memory&&(a->policy.role!=i+1||a->policy.abi!=1||a->policy.epoch!=d->budget.epoch||!eq(a->policy.digest,d->expected_digest[i],32)||!eq(a->policy.parent_hash,d->budget.parent_hash,32)))return 0;
  if(l->active&&(!l->handle||!l->image||!a->pinned||!l->registration.dispatch||l->quarantine||l->registration.epoch!=d->budget.epoch||l->registration.role!=i+1))return 0;
 }
 if(d->loader[0].active&&d->loader[1].active){const LoadedImage*a=d->loader[0].image,*b=d->loader[1].image;if(a==b||d->loader[0].handle==d->loader[1].handle||mod_overlap(a->base,a->size,b->base,b->size))return 0;}
 return total==d->budget.mapped;
}
int dual_bind(DualModules*d,const ModEfi*e,uint64_t epoch,uint32_t mapped,const uint8_t owner[32],const uint8_t target[32],const uint8_t hashes[2][32],DualRevoke revoke,void*ctx){
 if(!d||!e||!owner||!target||!hashes||!epoch||!mapped||mapped>MOD_AGGREGATE_MAX||!revoke||mod_overlap(d,sizeof *d,e,sizeof *e)||mod_overlap(d,sizeof *d,owner,32)||mod_overlap(d,sizeof *d,target,32)||mod_overlap(d,sizeof *d,hashes,64)||(ctx&&mod_overlap(d,sizeof *d,ctx,1)))return -1;
 for(size_t j=0;j<sizeof *d;j++)if(((const uint8_t*)d)[j])return -1;
 if(!e->system||!e->parent||!e->load||!e->start||!e->unload||!e->protocol||!e->free_pool)return -1;
 if(!nz(owner,32)||!nz(target,32)||!nz(hashes[0],32)||!nz(hashes[1],32)||eq(hashes[0],hashes[1],32))return -1;
 d->efi=*e;d->budget.epoch=epoch;d->budget.mapped=d->base_mapped=mapped;cp(d->owner,owner,32);cp(d->target,target,32);cp(d->expected_digest,hashes,64);d->revoke=revoke;d->revoke_context=ctx;d->initialized=1;return 0;
}
int dual_accept(DualModules*d,const uint8_t*p,size_t n,uint8_t*arena,size_t capacity){
 if(!d||!d->initialized||d->closed||d->busy||d->sealed||d->quarantine||!dual_inventory(d)||n<MOD_HEADER||n>MOD_HEADER+MOD_CHUNK||!outside(d,p,n))return -1;
 unsigned role=u32(p+196);if(role<1||role>2||u32(p+200)!=1||!eq(p,role==1?"RABMOD01":"RABRSN01",8)||!eq(p+8,d->owner,32)||!eq(p+40,d->target,32)||!eq(p+104,d->expected_digest[role-1],32)||u64(p+168)!=d->budget.epoch||!nz(p+72,32)||crypto_ed25519_check(p+224,d->owner,p,224))return -1;
 ModArtifact*a=&d->artifact[role-1];ModLoader*l=&d->loader[role-1];
 if(l->attempted)return -1;
 if(d->artifact[2-role].memory&&!d->loader[2-role].active)return -1;
 if(!a->memory){
  if(!arena||capacity!=MOD_FILE_MAX||!outside(d,arena,capacity)||mod_overlap(p,n,arena,capacity)||u64(p+176)<=d->budget.last_counter)return -1;
  if(nz(d->budget.parent_hash,32)&&!eq(p+72,d->budget.parent_hash,32))return -1;
  ModPolicy q={0};cp(q.owner,d->owner,32);cp(q.target,d->target,32);cp(q.parent_hash,p+72,32);cp(q.digest,p+104,32);q.epoch=d->budget.epoch;q.counter=u64(p+176);q.last_counter=d->budget.last_counter;q.total=u32(p+184);q.mapped=u32(p+204);q.role=role;q.abi=1;
  if(q.mapped>MOD_AGGREGATE_MAX-d->budget.mapped||mod_begin(a,&q,arena,capacity))return -1;
  cp(d->budget.parent_hash,q.parent_hash,32);
 }else if(arena!=a->memory||capacity!=a->capacity)return -1;
 d->busy=1;int r=mod_accept(a,p,n);
 if(r>=0&&a->ready){if(mod_load(l,a,&d->budget,&d->efi)){d->quarantine=1;r=-1;}}
 d->busy=0;if(!dual_inventory(d)){d->quarantine=1;return -1;}return r;
}
int dual_seal(DualModules*d,uint64_t e,uint8_t out[32]){
 if(!d||d->closed||d->busy||d->quarantine||e!=d->budget.epoch||!outside(d,out,32)||!dual_inventory(d)||!d->loader[0].active||!d->loader[1].active)return -1;
 if(!d->sealed){uint8_t record[112]={0};cp(record,"RABSET01",8);cp(record+8,d->budget.parent_hash,32);cp(record+40,d->expected_digest,64);for(unsigned i=0;i<8;i++)record[104+i]=e>>(i*8);rabbit_sha256(d->code_set,record,sizeof record);mod_wipe(record,sizeof record);d->sealed=1;}
 cp(out,d->code_set,32);return 0;
}
int dual_close(DualModules*d,uint64_t e){
 if(!d||!d->initialized||d->busy||d->quarantine||e!=d->budget.epoch||!dual_inventory(d))return -1;
 if(d->closed)return 0;
 d->busy=1;
 if(d->sealed&&d->revoke(d->revoke_context,e,d->code_set)){d->busy=0;return -1;}
 for(unsigned i=0;i<2;i++){
  ModLoader*l=&d->loader[i];ModArtifact*a=&d->artifact[i];
  if(l->quarantine||(l->active?mod_unload(l):a->pinned?-1:a->memory?mod_cancel(a):0)){d->quarantine=1;d->busy=0;return -1;}
 }
 d->busy=0;if(!dual_inventory(d)||d->budget.mapped!=d->base_mapped)return -1;d->closed=1;return 0;
}
