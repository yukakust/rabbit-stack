#include "parent.h"
static int loan(const RsnParentLease*p,const void*a,size_t n){ModLoader*l=p->loader;return a&&n&&!mod_overlap(a,n,p,sizeof(*p))&&!mod_overlap(a,n,l,sizeof(*l))&&!mod_overlap(a,n,l->artifact,sizeof(*l->artifact))&&!mod_overlap(a,n,l->budget,sizeof(*l->budget))&&!mod_overlap(a,n,l->image,sizeof(*l->image))&&!mod_overlap(a,n,l->image->base,l->image->size)&&!mod_overlap(a,n,l->artifact->memory,l->artifact->capacity);}
int rsn_parent_bind(RsnParentLease*p,ModLoader*l){
 if(!p||!l||p->bound||p->busy||p->quarantined||!l->active||l->quarantine||!l->artifact||!l->budget||!l->image||!l->registration.dispatch||l->registration.role!=MOD_ROLE_RSN_STATION||l->registration.abi!=MOD_ABI||l->registration.epoch!=l->budget->epoch||mod_overlap(p,sizeof(*p),l,sizeof(*l))||mod_overlap(p,sizeof(*p),l->artifact,sizeof(*l->artifact))||mod_overlap(p,sizeof(*p),l->budget,sizeof(*l->budget))||mod_overlap(p,sizeof(*p),l->artifact->memory,l->artifact->capacity)||mod_overlap(p,sizeof(*p),l->image,sizeof(*l->image))||mod_overlap(p,sizeof(*p),l->efi.system,sizeof(*l->efi.system))||mod_overlap(p,sizeof(*p),l->image->base,l->image->size))return -1;
 p->loader=l;p->epoch=l->registration.epoch;p->bound=1;p->closed=0;return 0;
}
Status rsn_parent_call(RsnParentLease*p,uint32_t op,void*a){
 if(!p||!p->bound||p->busy||p->closed||p->quarantined||!p->loader||!p->loader->active||p->loader->quarantine||p->loader->registration.epoch!=p->epoch||!p->loader->registration.dispatch)return EFI_ERROR(3);
 /* CLOSE is loader-mediated: op0 may not release/wipe artifact before unload. */
 if(!op||op>RSN_CHILD_STATUS)return EFI_ERROR(2);
 size_t n=op==RSN_CHILD_OPEN?sizeof(RsnChildOpen):op==RSN_CHILD_EAPOL?sizeof(RsnChildEapol):op==RSN_CHILD_POLL?sizeof(RsnChildPoll):sizeof(RsnChildStatus);
 if(!loan(p,a,n))return EFI_ERROR(2);
 if(op==RSN_CHILD_OPEN){const RsnChildOpen*o=a;if(!loan(p,o->arena,o->arena_bytes)||!loan(p,o->pmk,o->pmk_bytes)||!loan(p,o->rsn,o->rsn_bytes)||!loan(p,o->ssid,o->ssid_bytes)||(o->providers.context&&!loan(p,o->providers.context,o->providers.context_bytes))||(!o->providers.context&&o->providers.context_bytes))return EFI_ERROR(2);}
 if(op==RSN_CHILD_EAPOL){const RsnChildEapol*e=a;if(!loan(p,e->bytes,e->count))return EFI_ERROR(2);}
 uint64_t epoch=0;for(unsigned i=0;i<8;i++)epoch|=((uint64_t)((const uint8_t*)a)[i])<<(8*i);if(epoch!=p->epoch)return EFI_ERROR(2);
 p->busy=1;Status r=p->loader->registration.dispatch(op,a);p->busy=0;return r;
}
int rsn_parent_close(RsnParentLease*p){
 if(!p||!p->bound||p->busy||p->closed||p->quarantined||!p->loader)return -1;
 p->busy=1;int r=mod_unload(p->loader);p->busy=0;
 if(r){p->quarantined=1;return -1;}p->closed=1;return 0;
}
int rsn_parent_can_unload(const RsnParentLease*p){return p&&p->bound&&p->closed&&!p->busy&&!p->quarantined&&p->loader&&p->loader->artifact&&!p->loader->active&&!p->loader->handle&&!p->loader->quarantine&&!p->loader->artifact->memory;}
