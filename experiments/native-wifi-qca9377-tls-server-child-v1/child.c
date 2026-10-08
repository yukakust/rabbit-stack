#include "child.h"
#include "tls_heap.h"
#include "mbedtls/platform.h"
#include "psa/crypto.h"
static TlsBleEndpoint endpoint;
static TlsHeap heap;
static struct {uint64_t epoch,counter;uint8_t digest[32],parent_hash[32];uintptr_t image_base;size_t image_size;ChildEntropy entropy;void*entropy_context;unsigned bound,opened,quarantine;} context;
static void wipe(void*p,size_t n){volatile uint8_t*q=p;while(n--)*q++=0;}
static int overlap(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if((n&&!a)||(m&&!b)||n>UINTPTR_MAX-x||m>UINTPTR_MAX-y)return 1;return n&&m&&x<y+m&&y<x+n;}
static int external(const void*p,size_t n){return p&&n&&!overlap(p,n,&context,sizeof(context))&&!overlap(p,n,&endpoint,sizeof(endpoint))&&!overlap(p,n,&heap,sizeof(heap))&&!overlap(p,n,(void*)context.image_base,context.image_size);}
static int entropy_adapter(void*unused,uint8_t*out,size_t n){(void)unused;if(!context.opened||context.quarantine||!context.entropy||!out||!n)return -1;int result=context.entropy(context.entropy_context,out,n);if(result)wipe(out,n);return result;}
psa_status_t mbedtls_psa_external_get_random(mbedtls_psa_external_random_context_t*c,uint8_t*out,size_t n,size_t*written){(void)c;*written=0;if(entropy_adapter(0,out,n))return PSA_ERROR_INSUFFICIENT_ENTROPY;*written=n;return PSA_SUCCESS;}
static Status close_context(void){
 if(!context.opened)return context.quarantine?EFI_ERROR(3):0;
 tls_ble_close(&endpoint);mbedtls_psa_crypto_free();
 if(heap.live||heap.quarantine||!tls_heap_release(&heap)){context.quarantine=1;return EFI_ERROR(3);}
 context.opened=0;context.entropy=0;context.entropy_context=0;return 0;
}
static Status EFIAPI dispatch(uint32_t op,void*argument){
 if(!context.bound)return EFI_ERROR(3);
 if(op==CHILD_STATUS){ChildStatus*r=argument;if(!external(r,sizeof(*r))||r->epoch!=context.epoch||overlap(r,sizeof(*r),heap.base,heap.capacity))return EFI_ERROR(2);r->initialized=context.opened;r->ready=endpoint.ready;r->fault=endpoint.fault;r->heap_live=heap.live;r->quarantine=heap.quarantine||context.quarantine;r->tls_error=endpoint.tls_error;return 0;}
 if(context.quarantine)return EFI_ERROR(3);
 if(!op)return argument?EFI_ERROR(2):close_context();
 if(op==CHILD_OPEN){
  ChildOpen*r=argument;if(!external(r,sizeof(*r))||context.opened||r->epoch!=context.epoch||!r->entropy||!external(r->pool,r->pool_bytes)||r->pool_bytes<65536||r->pool_bytes>131072||(r->entropy_context&&overlap(r->entropy_context,1,r->pool,r->pool_bytes))||!external(r->certificate,r->certificate_bytes)||!external(r->private_key,r->private_key_bytes)||!external(r->peer_spki,32)||overlap(r,sizeof(*r),r->pool,r->pool_bytes)||overlap(r->pool,r->pool_bytes,r->certificate,r->certificate_bytes)||overlap(r->pool,r->pool_bytes,r->private_key,r->private_key_bytes)||overlap(r->pool,r->pool_bytes,r->peer_spki,32)||!r->now||!r->duration||r->duration>60000000)return EFI_ERROR(2);
  if(!tls_heap_bind(&heap,r->pool,r->pool_bytes))return EFI_ERROR(9);
  context.entropy=r->entropy;context.entropy_context=r->entropy_context;context.opened=1;
  if(mbedtls_platform_set_calloc_free(tls_heap_calloc,tls_heap_free)||psa_crypto_init()!=PSA_SUCCESS||tls_ble_open(&endpoint,1,r->certificate,r->certificate_bytes,r->private_key,r->private_key_bytes,r->peer_spki,0,entropy_adapter,0,r->epoch,r->now,r->duration)!=1){close_context();return EFI_ERROR(3);}return 0;
 }
 
 ChildIo*r=argument;if(!external(r,sizeof(*r))||r->epoch!=context.epoch||r->reserved||!context.opened||overlap(r,sizeof(*r),heap.base,heap.capacity))return EFI_ERROR(2);
 if(op!=CHILD_POLL&&(!external(r->bytes,r->count)||overlap(r,sizeof(*r),r->bytes,r->count)||overlap(r->bytes,r->count,heap.base,heap.capacity)))return EFI_ERROR(2);
 switch(op){case CHILD_FEED:r->result=tls_ble_feed(&endpoint,r->epoch,r->sequence,r->bytes,r->count);break;case CHILD_DRAIN:r->result=(int)tls_ble_drain(&endpoint,r->epoch,r->bytes,r->count);break;case CHILD_POLL:r->result=tls_ble_poll(&endpoint,r->epoch,r->now);break;case CHILD_WRITE:r->result=tls_ble_write(&endpoint,r->epoch,r->bytes,r->count);break;case CHILD_READ:r->result=tls_ble_read(&endpoint,r->epoch,r->bytes,r->count);break;default:return EFI_ERROR(3);}return 0;
}
static Status EFIAPI child_unload(void*image){(void)image;if(context.opened||context.quarantine||heap.live||heap.quarantine)return EFI_ERROR(3);wipe(&context,sizeof(context));return 0;}
Status EFIAPI tls_child_entry(void*handle,SystemTable*system){
 if(!handle||!system||!system->boot||context.bound)return EFI_ERROR(2);
 TableHeader*h=system->boot;if(h->signature!=UINT64_C(0x56524553544f4f42)||h->size<160)return EFI_ERROR(3);
 HandleProtocol get=(HandleProtocol)service(system,152);if(!get)return EFI_ERROR(3);void*p=0;Status status=get(handle,&loaded_image_guid,&p);if(status||!p)return EFI_ERROR(3);LoadedImage*image=p;
 if(image->system!=system||!image->parent||!image->base||!image->size||image->size>4194304||image->size>UINTPTR_MAX-(uintptr_t)image->base||!image->options||image->options_size!=sizeof(ModRegistration))return EFI_ERROR(2);
 ModRegistration*r=image->options;if(overlap(r,sizeof(*r),image,sizeof(*image))||overlap(r,sizeof(*r),image->base,image->size)||overlap(r,sizeof(*r),&context,sizeof(context))||overlap(r,sizeof(*r),&endpoint,sizeof(endpoint))||overlap(r,sizeof(*r),&heap,sizeof(heap))||r->magic!=MOD_REG_MAGIC||r->abi!=1||r->size!=sizeof(*r)||r->role!=1||r->reserved||!r->epoch||!r->counter||r->dispatch)return EFI_ERROR(2);
 uint8_t d=0,pub=0;for(unsigned i=0;i<32;i++){d|=r->digest[i];pub|=r->parent_hash[i];}if(!d||!pub)return EFI_ERROR(2);
 context.epoch=r->epoch;context.counter=r->counter;for(unsigned i=0;i<32;i++){context.digest[i]=r->digest[i];context.parent_hash[i]=r->parent_hash[i];}context.image_base=(uintptr_t)image->base;context.image_size=image->size;context.bound=1;image->unload=child_unload;r->dispatch=dispatch;return 0;
}
