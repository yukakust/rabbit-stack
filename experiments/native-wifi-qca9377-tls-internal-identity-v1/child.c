#include "child.h"
#include "identity.h"
#include "tls_heap.h"
#include "mbedtls/platform.h"
#include "mbedtls/ctr_drbg.h"
#include "psa/crypto.h"
#include <string.h>
static PairingPanel qr_panel;static TlsBleEndpoint endpoint;static TlsHeap heap;static DellIdentity identity;
static struct {uint64_t epoch,counter,key_created,key_deadline,key_last;uint8_t digest[32],parent_hash[32];uintptr_t image_base;size_t image_size;IdentitySeed source;RngApproval approval;mbedtls_ctr_drbg_context drbg;uint8_t seed_scratch[64];unsigned bound,attempted,generated,active,busy,borrowed,drbg_ready,fault,quarantine,sessions,keystore_live;} context;
static void wipe(void*p,size_t n){volatile uint8_t*q=p;while(n--)*q++=0;}
static int overlap(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if((n&&!a)||(m&&!b)||n>UINTPTR_MAX-x||m>UINTPTR_MAX-y)return 1;return n&&m&&x<y+m&&y<x+n;}
static int external(const void*p,size_t n){return p&&n&&!overlap(p,n,&context,sizeof context)&&!overlap(p,n,&endpoint,sizeof endpoint)&&!overlap(p,n,&heap,sizeof heap)&&!overlap(p,n,&qr_panel,sizeof qr_panel)&&!overlap(p,n,&identity,sizeof identity)&&!overlap(p,n,(void*)context.image_base,context.image_size);}
static int same(const uint8_t*a,const uint8_t*b,size_t n){unsigned x=0;while(n--)x|=*a++^*b++;return x==0;}
static int nz(const uint8_t*p,size_t n){unsigned x=0;while(n--)x|=*p++;return x!=0;}
static int seed_callback(void*unused,uint8_t*out,size_t n){
 (void)unused;int r=-1;
 if(!context.busy||context.borrowed||context.fault||!context.source.fill||!out||!n||n>sizeof context.seed_scratch)return -1;
 size_t rounded=(n+7u)&~(size_t)7;context.borrowed++;
 int rc=context.source.fill(context.source.context,context.epoch,context.approval.admitted_code_set_sha256,context.seed_scratch,rounded);context.borrowed--;
 if(!rc&&!context.fault){memcpy(out,context.seed_scratch,n);r=0;}else {wipe(out,n);context.fault=1;}
 wipe(context.seed_scratch,sizeof context.seed_scratch);return r;
}
static int entropy_adapter(void*unused,uint8_t*out,size_t n){(void)unused;if(!context.drbg_ready||context.fault||!out||!n||n>1024)return -1;if(!context.busy||context.borrowed){wipe(out,n);context.fault=1;return -1;}int r=mbedtls_ctr_drbg_random(&context.drbg,out,n);if(r){wipe(out,n);context.fault=1;}return r;}
psa_status_t mbedtls_psa_external_get_random(mbedtls_psa_external_random_context_t*c,uint8_t*out,size_t n,size_t*written){(void)c;*written=0;if(entropy_adapter(0,out,n))return PSA_ERROR_INSUFFICIENT_ENTROPY;*written=n;return PSA_SUCCESS;}
static Status close_context(void){
 if(context.borrowed)return EFI_ERROR(3);
 qr_panel_clear(&qr_panel);tls_ble_close(&endpoint);dell_identity_free(&identity);mbedtls_psa_crypto_free();
 if(context.drbg_ready)mbedtls_ctr_drbg_free(&context.drbg);context.drbg_ready=0;
 if(heap.live||heap.quarantine||(heap.base&&!tls_heap_release(&heap))){context.quarantine=1;return EFI_ERROR(3);}
 context.generated=context.active=0;wipe(&context.source,sizeof context.source);wipe(&context.approval,sizeof context.approval);return 0;
}
static int approval(const RngApproval*a){return a->epoch==context.epoch&&a->reviewed==1&&a->trusted_owner_code_only==1&&a->cpu_signature==0x906ea&&a->cpu_flags==3&&nz(a->actual_inventory_sha256,32)&&nz(a->admitted_code_set_sha256,32)&&same(a->parent_file_sha256,context.parent_hash,32);}
static Status generate(ChildGenerate*r){
 if(!external(r,sizeof(*r))||context.attempted||r->epoch!=context.epoch||!r->now||r->now>UINT64_MAX-600000000||!approval(&r->approval)||!external(r->pool,r->pool_bytes)||((uintptr_t)r->pool&15)||r->pool_bytes<65536||r->pool_bytes>131072||!r->source.fill||!external(r->source.context,r->source.context_bytes)||r->source.context_bytes>1048576||!nz(r->source.source_sha256,32)||overlap(r,sizeof(*r),r->pool,r->pool_bytes)||overlap(r->source.context,r->source.context_bytes,r,sizeof(*r))||overlap(r->source.context,r->source.context_bytes,r->pool,r->pool_bytes))return EFI_ERROR(2);
 context.attempted=1;if(!tls_heap_bind(&heap,r->pool,r->pool_bytes))return EFI_ERROR(9);context.source=r->source;context.approval=r->approval;
 if(mbedtls_platform_set_calloc_free(tls_heap_calloc,tls_heap_free)){close_context();return EFI_ERROR(3);}mbedtls_ctr_drbg_init(&context.drbg);mbedtls_ctr_drbg_set_entropy_len(&context.drbg,48);mbedtls_ctr_drbg_set_prediction_resistance(&context.drbg,MBEDTLS_CTR_DRBG_PR_ON);mbedtls_ctr_drbg_set_reseed_interval(&context.drbg,1);
 uint8_t domain[96]={0};memcpy(domain,"RABBIT-IDENTITY-1",17);for(unsigned j=0;j<8;j++)domain[24+j]=(uint8_t)(context.epoch>>(j*8));memcpy(domain+32,context.parent_hash,32);memcpy(domain+64,context.approval.admitted_code_set_sha256,32);
 int rc=mbedtls_ctr_drbg_seed(&context.drbg,seed_callback,0,domain,sizeof domain);wipe(domain,sizeof domain);if(rc){mbedtls_ctr_drbg_free(&context.drbg);context.fault=1;close_context();return EFI_ERROR(3);}context.drbg_ready=1;
 if(psa_crypto_init()!=PSA_SUCCESS||dell_identity_create(&identity,entropy_adapter,0)){context.fault=1;close_context();return EFI_ERROR(3);}context.key_created=context.key_last=r->now;context.key_deadline=r->now+600000000;context.keystore_live=heap.live;context.generated=1;return 0;
}
static Status public_identity(ChildPublic*r){
 if(!external(r,sizeof(*r))||r->epoch!=context.epoch||!context.generated||context.fault||overlap(r,sizeof(*r),heap.base,heap.capacity))return EFI_ERROR(2);
 uint64_t epoch=r->epoch;wipe(r,sizeof(*r));r->epoch=epoch;r->certificate_bytes=(uint32_t)identity.certificate_bytes;r->spki_bytes=(uint32_t)identity.spki_bytes;memcpy(r->certificate,identity.certificate,identity.certificate_bytes);memcpy(r->spki,identity.spki,identity.spki_bytes);memcpy(r->sha256,identity.sha256,32);const char*h="0123456789abcdef";for(unsigned j=0;j<32;j++){r->fingerprint[2*j]=h[r->sha256[j]>>4];r->fingerprint[2*j+1]=h[r->sha256[j]&15];}return 0;
}
static Status public_qr(ChildPublicQr*r){if(!external(r,sizeof(*r))||r->epoch!=context.epoch||!context.generated||context.fault||overlap(r,sizeof(*r),heap.base,heap.capacity)||!r->now||r->now<context.key_last||r->now>=context.key_deadline)return EFI_ERROR(2);context.key_last=r->now;if(!qr_panel.ready&&qr_panel_bind(&qr_panel,context.epoch,identity.sha256,r->now))return EFI_ERROR(3);if(qr_panel.expires>context.key_deadline)qr_panel.expires=context.key_deadline;if(!qr_panel_live(&qr_panel,context.epoch,r->now))return EFI_ERROR(3);r->panel=qr_panel;return 0;}
static Status activate(ChildActivate*r){if(!external(r,sizeof(*r))||r->epoch!=context.epoch||!context.generated||context.active||context.sessions>=64||!external(r->peer_spki,32)||overlap(r,sizeof(*r),heap.base,heap.capacity)||overlap(r->peer_spki,32,heap.base,heap.capacity)||!r->now||r->now<context.key_last||r->now>=context.key_deadline||!r->duration||r->duration>60000000)return EFI_ERROR(2);if(tls_ble_open_owned(&endpoint,identity.certificate,identity.certificate_bytes,&identity.key,r->peer_spki,entropy_adapter,0,r->epoch,r->now,r->duration)!=1){context.fault=1;return EFI_ERROR(3);}context.key_last=r->now;context.sessions++;context.active=1;return 0;}
static Status EFIAPI dispatch(uint32_t op,void*argument){
 if(!context.bound)return EFI_ERROR(3);
 if(op==CHILD_STATUS){ChildStatus*r=argument;if(!external(r,sizeof(*r))||r->epoch!=context.epoch||overlap(r,sizeof(*r),heap.base,heap.capacity))return EFI_ERROR(2);r->initialized=context.generated;r->ready=endpoint.ready;r->fault=context.fault||endpoint.fault;r->heap_live=heap.live;r->quarantine=heap.quarantine||context.quarantine;r->tls_error=endpoint.tls_error;return 0;}
 if(context.busy||context.borrowed||context.quarantine)return EFI_ERROR(3);context.busy=1;Status result=EFI_ERROR(3);
 if(!op){result=argument?EFI_ERROR(2):close_context();goto done;}
 if(context.fault)goto done;
 if(op==CHILD_GENERATE){result=generate(argument);goto done;}
 if(op==CHILD_PUBLIC){result=public_identity(argument);goto done;}
 if(op==CHILD_PUBLIC_QR){result=public_qr(argument);goto done;}
 if(op==CHILD_ACTIVATE){result=activate(argument);goto done;}
 if(op==CHILD_DEACTIVATE){if(!argument){tls_ble_close(&endpoint);context.active=0;if(heap.live!=context.keystore_live||heap.quarantine){context.quarantine=1;result=EFI_ERROR(3);}else result=0;}else result=EFI_ERROR(2);goto done;}
 ChildIo*r=argument;
 if(op==CHILD_POLL&&external(r,sizeof(*r))&&r->epoch==context.epoch&&!r->reserved&&context.generated&&!overlap(r,sizeof(*r),heap.base,heap.capacity)){
  if(r->now<context.key_last||r->now>=context.key_deadline){context.fault=1;r->result=-1;result=close_context();goto done;}context.key_last=r->now;if(!context.active){r->result=0;result=0;goto done;}
 }
 if(op==CHILD_OPEN||!external(r,sizeof(*r))||r->epoch!=context.epoch||r->reserved||!context.active||overlap(r,sizeof(*r),heap.base,heap.capacity)){result=EFI_ERROR(2);goto done;}
 if(op!=CHILD_POLL&&(!external(r->bytes,r->count)||overlap(r,sizeof(*r),r->bytes,r->count)||overlap(r->bytes,r->count,heap.base,heap.capacity))){result=EFI_ERROR(2);goto done;}
 switch(op){case CHILD_FEED:r->result=tls_ble_feed(&endpoint,r->epoch,r->sequence,r->bytes,r->count);result=0;break;case CHILD_DRAIN:r->result=(int)tls_ble_drain(&endpoint,r->epoch,r->bytes,r->count);result=0;break;case CHILD_POLL:r->result=tls_ble_poll(&endpoint,r->epoch,r->now);result=0;break;case CHILD_WRITE:r->result=tls_ble_write(&endpoint,r->epoch,r->bytes,r->count);result=0;break;case CHILD_READ:r->result=tls_ble_read(&endpoint,r->epoch,r->bytes,r->count);result=0;break;default:break;}
 done:context.busy=0;return result;
}
static Status EFIAPI child_unload(void*image){(void)image;if(context.generated||context.active||context.busy||context.borrowed||context.quarantine||heap.live||heap.quarantine||context.drbg_ready)return EFI_ERROR(3);wipe(&context,sizeof context);return 0;}
Status EFIAPI tls_child_entry(void*handle,SystemTable*system){
 if(!handle||!system||!system->boot||context.bound)return EFI_ERROR(2);TableHeader*h=system->boot;if(h->signature!=UINT64_C(0x56524553544f4f42)||h->size<160)return EFI_ERROR(3);HandleProtocol get=(HandleProtocol)service(system,152);void*p=0;if(!get||get(handle,&loaded_image_guid,&p)||!p)return EFI_ERROR(3);LoadedImage*image=p;
 if(image->system!=system||!image->parent||!image->base||!image->size||image->size>4194304||image->size>UINTPTR_MAX-(uintptr_t)image->base||!image->options||image->options_size!=sizeof(ModRegistration))return EFI_ERROR(2);ModRegistration*r=image->options;
 if(overlap(r,sizeof(*r),image,sizeof(*image))||overlap(r,sizeof(*r),image->base,image->size)||!external(r,sizeof(*r))||r->magic!=MOD_REG_MAGIC||r->abi!=1||r->size!=sizeof(*r)||r->role!=1||r->reserved||!r->epoch||!r->counter||r->dispatch||!nz(r->digest,32)||!nz(r->parent_hash,32))return EFI_ERROR(2);
 context.epoch=r->epoch;context.counter=r->counter;memcpy(context.digest,r->digest,32);memcpy(context.parent_hash,r->parent_hash,32);context.image_base=(uintptr_t)image->base;context.image_size=image->size;context.bound=1;image->unload=child_unload;r->dispatch=dispatch;return 0;
}

#ifdef RABBIT_IDENTITY_MODEL
/* Host-only two-endpoint tests share PSA globals; privileged model borrow,
 * never exported or compiled into the native child. */
void identity_model_external_crypto(unsigned enter){context.busy=enter;}
int identity_model_seed_round(uint8_t*out,size_t n){context.busy=1;int r=seed_callback(0,out,n);context.busy=0;return r;}
unsigned identity_model_private_wiped(void){const uint8_t*p=(const uint8_t*)&identity;unsigned x=0;for(size_t i=0;i<sizeof identity;i++)x|=p[i];for(size_t i=0;i<sizeof context.seed_scratch;i++)x|=context.seed_scratch[i];return x==0;}
#endif
