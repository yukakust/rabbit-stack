#include "native_port.h"
#include "backend_entropy.h"
#include "monocypher.h"
#include <string.h>
static QcaNoisePort *owned;
static int range(const void*p,size_t n){uintptr_t a=(uintptr_t)p;return p&&n&&a<=UINTPTR_MAX-n;}
static int overlap(const void*a,size_t an,const void*b,size_t bn){return (uintptr_t)a<(uintptr_t)b+bn&&(uintptr_t)b<(uintptr_t)a+an;}

static int slot(void*p){
 if(!owned||!p)return -1;
 if(owned->used>QCA_NOISE_SLOTS){owned->quarantined=1;return -1;}
 for(unsigned i=0;i<owned->used;i++)if(p==owned->bytes[i])return (int)i;
 return -1;
}
int qca_native_reset(QcaNoisePort*p,uint64_t epoch){
 if((owned&&owned!=p)||!range(p,sizeof(*p))||((uintptr_t)p%_Alignof(QcaNoisePort))||!epoch||p->live||p->quarantined||(p->rng&&(p->rng->pool||p->rng->pool_uncertain)))return 0;
 /* Caller must prove no outstanding raw handles, teardown epoch, valid storage. */
 crypto_wipe(p,sizeof(*p));p->epoch=epoch;p->fail_after=-1;return 1;
}
int qca_native_bind(QcaNoisePort*p){
 if(!range(p,sizeof(*p))||((uintptr_t)p%_Alignof(QcaNoisePort))||!p->epoch||p->quarantined||p->used>QCA_NOISE_SLOTS||p->live>p->used||(owned&&owned!=p&&(owned->live||owned->quarantined||(owned->rng&&(owned->rng->pool||owned->rng->pool_uncertain)))))return 0;
 owned=p;return 1;
}
int qca_native_rng_bind(RngSession*s,const RngReview*r){
 if(!owned||owned->live||owned->quarantined||(owned->rng&&(owned->rng->pool||owned->rng->pool_uncertain))||!range(s,sizeof(*s))||!range(r,sizeof(*r))||overlap(s,sizeof(*s),r,sizeof(*r))||overlap(s,sizeof(*s),owned,sizeof(*owned))||overlap(r,sizeof(*r),owned,sizeof(*owned)))return 0;
 if((uintptr_t)s%_Alignof(RngSession)||(uintptr_t)r%_Alignof(RngReview)||s->epoch!=owned->epoch||r->epoch!=owned->epoch)return 0;
 owned->rng=s;owned->review=r;return 1;
}
size_t qca_native_live(void){return owned?owned->live:0;}
size_t qca_native_peak(void){return owned?owned->peak_live:0;}
unsigned qca_native_allocations(void){return owned?owned->allocation_calls:0;}
void*qca_port_malloc(size_t n){
 if(!owned||!owned->epoch||owned->quarantined||!n||n>QCA_NOISE_SLOT_BYTES||owned->used>=QCA_NOISE_SLOTS||owned->fail_after==0)return 0;
 if(owned->fail_after>0)owned->fail_after--;
 unsigned i=owned->used++;owned->lengths[i]=n;owned->states[i]=1;owned->live++;owned->allocation_calls++;
 if(owned->live>owned->peak_live)owned->peak_live=owned->live;
 memset(owned->bytes[i],0,QCA_NOISE_SLOT_BYTES);return owned->bytes[i];
}
void*qca_port_calloc(size_t count,size_t n){if(!count||!n||count>SIZE_MAX/n)return 0;return qca_port_malloc(count*n);}
void*qca_noise_new_object(size_t n){void*p=qca_port_calloc(1,n);if(p&&n>=sizeof(size_t))*(size_t*)p=n;return p;}
void qca_noise_free(void*p,size_t n){
 if(!p)return;int i=slot(p);
 if(i<0||!owned->live||owned->states[i]!=1||owned->lengths[i]!=n){if(owned)owned->quarantined=1;return;}
 /* Validate ownership and exact size BEFORE any dereference/wipe. */
 crypto_wipe(owned->bytes[i],QCA_NOISE_SLOT_BYTES);owned->states[i]=2;owned->live--;
}
void qca_port_free(void*p){if(!p)return;int i=slot(p);if(i<0){if(owned)owned->quarantined=1;return;}qca_noise_free(p,owned->lengths[i]);}
int qca_nk_new(NoiseHandshakeState**out,int role){
 if(!range(out,sizeof(*out))||((uintptr_t)out%_Alignof(NoiseHandshakeState*))||(owned&&overlap(out,sizeof(*out),owned,sizeof(*owned)))||(owned&&owned->rng&&overlap(out,sizeof(*out),owned->rng,sizeof(*owned->rng)))||(owned&&owned->review&&overlap(out,sizeof(*out),owned->review,sizeof(*owned->review))))return NOISE_ERROR_INVALID_PARAM;*out=0;
 if(!owned||!owned->epoch||owned->quarantined||!(role==NOISE_ROLE_INITIATOR||role==NOISE_ROLE_RESPONDER))return NOISE_ERROR_INVALID_STATE;
 NoiseHandshakeState*tmp=0;int rc=noise_handshakestate_new_by_name(&tmp,"Noise_NK_25519_ChaChaPoly_SHA256",role);
 if(rc){/* Upstream may have destroyed tmp already. NEVER free/dereference. */return rc;}
 if(owned->quarantined){noise_handshakestate_free(tmp);return NOISE_ERROR_INVALID_STATE;}
 *out=tmp;return NOISE_ERROR_NONE;
}
int qca_noise_entropy(uint8_t*p,size_t n){
 if(!owned||owned->quarantined||owned->used>QCA_NOISE_SLOTS||!owned->epoch||!owned->rng||!owned->review||n!=32||owned->rng->epoch!=owned->epoch||owned->review->epoch!=owned->epoch)return -1;
 if(!range(p,n))return -1;
 int contained=0;for(unsigned i=0;i<owned->used;i++)if(owned->states[i]==1&&(uintptr_t)p>=(uintptr_t)owned->bytes[i]&&(uintptr_t)p+n<=(uintptr_t)owned->bytes[i]+owned->lengths[i])contained=1;
 if(!contained)return -1;
 return rng_fill(owned->rng,owned->review,p,n)?0:-1;
}
