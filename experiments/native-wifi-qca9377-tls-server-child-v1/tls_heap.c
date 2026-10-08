#include "tls_heap.h"
static TlsHeap*owned;
static int range(const void*p,size_t n){return p&&n&&n<=UINTPTR_MAX-(uintptr_t)p;
 }
static int apart(const void*a,size_t n,const void*b,size_t m){return range(a,n)&&range(b,m)&&((uintptr_t)a+n<=(uintptr_t)b||(uintptr_t)b+m<=(uintptr_t)a);
 }
static void wipe(void*p,size_t n){volatile uint8_t*q=p;
 while(n--)*q++=0;
 }
int tls_heap_bind(TlsHeap*h,uint8_t*p,size_t n){
 if(owned||!apart(h,sizeof *h,p,n)||(uintptr_t)p%16||n<4096||n>2097152||h->live||h->quarantine)return 0;
 wipe(h,sizeof *h);
 wipe(p,n);
 h->base=p;
 h->capacity=n;
 owned=h;
 return 1;
}
void*tls_heap_calloc(size_t n,size_t size){
 TlsHeap*h=owned;
 if(!h||h->quarantine||!n||!size||n>SIZE_MAX/size)return 0;
 size_t bytes=n*size;
 if(bytes>h->capacity||bytes>SIZE_MAX-15)return 0;
 bytes=(bytes+15)&~(size_t)15;
 unsigned slot=512;
 for(unsigned i=0;i<512;i++)if(!h->block[i].live){slot=i;
 break;
 }if(slot==512)return 0;
 size_t offset=0;
 unsigned changed=1;
 while(changed&&offset<=h->capacity-bytes){changed=0;
 for(unsigned i=0;i<512;i++)if(h->block[i].live&&offset<h->block[i].offset+h->block[i].bytes&&h->block[i].offset<offset+bytes){offset=h->block[i].offset+h->block[i].bytes;
 changed=1;
 break;
 }}
 if(offset>h->capacity-bytes)return 0;
 h->block[slot]=(TlsHeapBlock){offset,bytes,1};
 h->live++;
 h->used+=bytes;
 if(h->used>h->high_water)h->high_water=h->used;
 wipe(h->base+offset,bytes);
 return h->base+offset;
}
void tls_heap_free(void*p){
 if(!p)return;
 TlsHeap*h=owned;
 if(!h||h->quarantine)return;
 for(unsigned i=0;i<512;i++)if(h->block[i].live&&p==h->base+h->block[i].offset){wipe(p,h->block[i].bytes);
 h->used-=h->block[i].bytes;
 h->block[i].live=0;
 h->live--;
 return;
 }
 h->quarantine=1;
 /* Invalid/double free never pretends owner release. */
}
int tls_heap_release(TlsHeap*h){if(!h||owned!=h||h->live||h->quarantine)return 0;
 wipe(h->base,h->capacity);
 owned=0;
 wipe(h,sizeof *h);
 return 1;
 }
