#include "loader.h"
static int equal(const uint8_t*a,const uint8_t*b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return !x;}
int mod_efi_bind(ModEfi*out,SystemTable*s,void*parent){
 if(!out||!s||!parent||mod_overlap(out,sizeof(*out),s,sizeof(*s))||!s->boot)return -1;
 TableHeader*h=s->boot;if(h->signature!=UINT64_C(0x56524553544f4f42)||h->size<232||h->size>4096||mod_overlap(out,sizeof(*out),s->boot,h->size))return -1;
 ModEfi q={s,parent,(ModLoad)service(s,200),(ModStart)service(s,208),(ModUnload)service(s,224),(HandleProtocol)service(s,152),(ModFree)service(s,72)};
 if(!q.load||!q.start||!q.unload||!q.protocol||!q.free_pool)return -1;*out=q;return 0;
}
static int retire(ModLoader*l){
 if(l->unload_attempted)return -1;l->unload_attempted=1;l->active=0;l->registration.dispatch=0;
 l->status=l->efi.unload(l->handle);if(l->status){l->quarantine=1;return -1;}
 l->handle=0;l->image=0;if(l->budget->mapped<l->reserved_mapped){l->quarantine=1;return -1;}l->budget->mapped-=l->reserved_mapped;l->reserved_mapped=0;l->artifact->pinned=0;return mod_cancel(l->artifact);
}
int mod_load(ModLoader*l,ModArtifact*a,ModBudget*b,const ModEfi*e){
 if(!l||!a||!b||!e||!e->system||!e->parent||!e->load||!e->start||!e->unload||!e->protocol||!e->free_pool||l->attempted||l->active||l->quarantine||mod_overlap(l,sizeof(*l),a,sizeof(*a))||mod_overlap(l,sizeof(*l),b,sizeof(*b))||mod_overlap(l,sizeof(*l),e,sizeof(*e))||mod_overlap(a,sizeof(*a),b,sizeof(*b))||mod_overlap(e,sizeof(*e),a,sizeof(*a))||mod_overlap(e,sizeof(*e),b,sizeof(*b))||!a->memory||mod_overlap(l,sizeof(*l),a->memory,a->capacity)||mod_overlap(b,sizeof(*b),a->memory,a->capacity)||mod_overlap(e,sizeof(*e),a->memory,a->capacity)||b->epoch!=a->policy.epoch||!equal(b->parent_hash,a->policy.parent_hash,32)||a->policy.counter<=b->last_counter||b->mapped>MOD_AGGREGATE_MAX||a->policy.mapped>MOD_AGGREGATE_MAX-b->mapped)return -1;
 uint32_t mapped,entry;if(!a->ready||mod_pe(a->memory,a->policy.total,&mapped,&entry)||mapped!=a->policy.mapped||mod_pin(a))return -1;
 l->attempted=1;l->artifact=a;l->budget=b;l->efi=*e;l->reserved_mapped=mapped;b->mapped+=mapped;b->last_counter=a->policy.counter; /* consume before any firmware entry */
 l->status=e->load(0,e->parent,0,a->memory,a->policy.total,&l->handle);
 if(l->status||!l->handle){if(l->handle||!l->status){l->quarantine=1;return -1;}b->mapped-=mapped;l->reserved_mapped=0;a->pinned=0;mod_cancel(a);return -1;}
 void*iface=0;l->status=e->protocol(l->handle,&loaded_image_guid,&iface);
 if(l->status||!iface){if(iface){l->quarantine=1;return -1;}retire(l);return -1;}
 l->image=iface;
 if(mod_overlap(l->image,sizeof(*l->image),a->memory,a->capacity)||mod_overlap(l->image,sizeof(*l->image),l,sizeof(*l))||mod_overlap(l->image,sizeof(*l->image),b,sizeof(*b))){l->quarantine=1;return -1;}
 if(l->image->system!=e->system||l->image->parent!=e->parent||!l->image->base||l->image->size!=mapped||mapped>UINTPTR_MAX-(uintptr_t)l->image->base||l->image->options||l->image->options_size){retire(l);return -1;}
 if(mod_overlap(l->image->base,mapped,a->memory,a->capacity)||mod_overlap(l->image->base,mapped,l,sizeof(*l))||mod_overlap(l->image->base,mapped,b,sizeof(*b))){l->quarantine=1;return -1;}
 ModRegistration r={MOD_REG_MAGIC,MOD_ABI,sizeof(ModRegistration),a->policy.role,0,a->policy.epoch,a->policy.counter,{0},{0},0};
 for(unsigned i=0;i<32;i++){r.digest[i]=a->policy.digest[i];r.parent_hash[i]=a->policy.parent_hash[i];}l->registration=r;
 l->image->options_size=sizeof(l->registration);l->image->options=&l->registration;
 l->status=e->start(l->handle,&l->exit_size,&l->exit_data);
 l->image->options=0;l->image->options_size=0;
 if(l->exit_data){if(!l->exit_size||l->exit_size>65536||e->free_pool(l->exit_data)){l->quarantine=1;return -1;}l->exit_data=0;l->exit_size=0;}else if(l->exit_size){l->quarantine=1;return -1;}
 if(l->image->unload&&!mod_exec_address(a->memory,a->policy.total,(uintptr_t)l->image->base,l->image->size,(uintptr_t)l->image->unload)){l->registration.dispatch=0;l->quarantine=1;return -1;}
 if(l->status||l->registration.magic!=r.magic||l->registration.abi!=r.abi||l->registration.size!=r.size||l->registration.role!=r.role||l->registration.reserved||l->registration.epoch!=r.epoch||l->registration.counter!=r.counter||!equal(l->registration.digest,r.digest,32)||!equal(l->registration.parent_hash,r.parent_hash,32)||!l->registration.dispatch||!mod_exec_address(a->memory,a->policy.total,(uintptr_t)l->image->base,l->image->size,(uintptr_t)l->registration.dispatch)){retire(l);return -1;}
 l->active=1;return 0;
}
int mod_unload(ModLoader*l){if(!l||!l->active||l->quarantine||!l->handle||!l->registration.dispatch)return -1;l->status=l->registration.dispatch(0,0);if(l->status){l->active=0;l->registration.dispatch=0;l->quarantine=1;return -1;}return retire(l);}
