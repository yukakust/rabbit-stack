#include "pump.h"
static int span(const void*p,size_t n){return p&&n&&n<=UINTPTR_MAX-(uintptr_t)p;}
static int apart(const void*a,size_t n,const void*b,size_t m){return span(a,n)&&span(b,m)&&((uintptr_t)a+n<=(uintptr_t)b||(uintptr_t)b+m<=(uintptr_t)a);}
static void zero(void*p,size_t n){volatile uint8_t*q=p;while(n--)*q++=0;}
static void copy(void*d,const void*s,size_t n){uint8_t*p=d;const uint8_t*q=s;while(n--)*p++=*q++;}
static int same(const void*a,const void*b,size_t n){const uint8_t*p=a,*q=b;unsigned x=0;while(n--)x|=*p++^*q++;return !x;}
static int fail(TlsCipherPump*s,unsigned error){s->fault=1;if(!s->error)s->error=error;zero(s->incoming,sizeof s->incoming);zero(s->previous,sizeof s->previous);zero(s->outgoing,sizeof s->outgoing);s->incoming_bytes=s->previous_bytes=s->outgoing_bytes=0;return -1;}
static int current(TlsCipherPump*s,uint64_t e,uint64_t us){if(!s||!s->bound||s->closed||s->busy)return -1;if(e!=s->epoch)return fail(s,1);if(s->fault)return -1;if(!us||us<s->last||us>=s->deadline)return fail(s,2);s->last=us;return 0;}
int tp_bind(TlsCipherPump*s,const TpOps*ops,uint64_t e,uint64_t us,uint64_t duration){
 if(!apart(s,sizeof *s,ops,sizeof *ops)||!e||!us||!duration||duration>60000000||us>UINT64_MAX-duration)return -1;
 for(size_t i=0;i<sizeof *s;i++)if(((uint8_t*)s)[i])return -1;
 if(!ops->clock||!ops->feed||!ops->poll||!ops->drain||!ops->revoke||!ops->context_bytes||ops->context_bytes>1048576||!apart(s,sizeof *s,ops->context,ops->context_bytes)||!apart(ops,sizeof *ops,ops->context,ops->context_bytes))return -1;
 s->ops=*ops;s->epoch=e;s->last=us;s->deadline=us+duration;s->bound=1;return 0;
}
int tp_offer(TlsCipherPump*s,uint64_t e,uint32_t sequence,const uint8_t*p,size_t n,uint64_t us){
 if(!s||!n||n>TP_FRAGMENT||!apart(s,sizeof *s,p,n)||!apart(s->ops.context,s->ops.context_bytes,p,n)||current(s,e,us))return -1;
 if(s->previous_bytes&&sequence==s->rx_previous){if(n!=s->previous_bytes||!same(p,s->previous,n))return fail(s,3);return 0;}
 if(sequence!=s->rx_next)return fail(s,4);
 if(s->incoming_bytes){if(n!=s->incoming_bytes||!same(p,s->incoming,n))return fail(s,3);return 0;}
 if(s->rx_next==UINT32_MAX)return fail(s,5);
 copy(s->incoming,p,n);s->incoming_bytes=(uint32_t)n;return 0;
}
int tp_view(TlsCipherPump*s,uint64_t e,uint8_t*p,size_t capacity,uint32_t*sequence,uint64_t us){
 if(!s||!apart(s,sizeof *s,p,capacity)||!apart(s,sizeof *s,sequence,sizeof *sequence)||!apart(p,capacity,sequence,sizeof *sequence)||!apart(s->ops.context,s->ops.context_bytes,p,capacity)||!apart(s->ops.context,s->ops.context_bytes,sequence,sizeof *sequence)||current(s,e,us))return -1;
 if(capacity<s->outgoing_bytes)return -2;
 *sequence=s->tx_current;if(!s->outgoing_bytes)return 0;
 copy(p,s->outgoing,s->outgoing_bytes);return (int)s->outgoing_bytes;
}
int tp_ack(TlsCipherPump*s,uint64_t e,uint32_t sequence,uint64_t us){
 if(current(s,e,us))return -1;
 if(s->acked_valid&&sequence==s->tx_acked)return 0;
 if(!s->outgoing_bytes)return fail(s,6);
 if(sequence!=s->tx_current)return fail(s,6);
 zero(s->outgoing,sizeof s->outgoing);s->outgoing_bytes=0;s->tx_acked=sequence;s->acked_valid=1;return 0;
}
void tp_disconnected(TlsCipherPump*s){if(s&&s->bound&&!s->closed){if(s->busy){s->fault=1;if(!s->error)s->error=7;}else (void)fail(s,7);}}
static int post_time(TlsCipherPump*s){uint64_t fresh=0;if(s->ops.clock(s->ops.context,&fresh)||!fresh||fresh<s->last||fresh>=s->deadline||s->fault)return fail(s,12);s->last=fresh;return 0;}
int tp_poll(TlsCipherPump*s,uint64_t e,uint64_t us){
 if(!s||!s->bound||s->closed||s->busy)return -1;
 (void)current(s,e,us);
 if(s->fault){(void)fail(s,s->error);if(!s->revoke_notified){s->busy=1;int r=s->ops.revoke(s->ops.context,s->epoch);s->busy=0;if(r)return -1;s->revoke_notified=1;}return -1;}
 s->busy=1;
 if(s->incoming_bytes){int r=s->ops.feed(s->ops.context,s->epoch,s->rx_next,s->incoming,s->incoming_bytes);if(r!=1||post_time(s)){s->busy=0;return fail(s,8);}copy(s->previous,s->incoming,s->incoming_bytes);s->previous_bytes=s->incoming_bytes;s->rx_previous=s->rx_next++;zero(s->incoming,sizeof s->incoming);s->incoming_bytes=0;}
 if(s->fault){s->busy=0;return fail(s,s->error);}
 int r=s->ops.poll(s->ops.context,s->epoch,s->last);if(r<0||post_time(s)){s->busy=0;return fail(s,9);}
 if(!s->outgoing_bytes){if(s->tx_next==UINT32_MAX){s->busy=0;return fail(s,5);}int n=s->ops.drain(s->ops.context,s->epoch,s->outgoing,sizeof s->outgoing);if(n<0||n>TP_FRAGMENT||post_time(s)){s->busy=0;return fail(s,10);}if(n){s->outgoing_bytes=(uint32_t)n;s->tx_current=s->tx_next++;}}
 s->busy=0;return r;
}
int tp_close(TlsCipherPump*s,uint64_t e){
 if(!s||!s->bound||s->busy||s->epoch!=e)return -1;if(s->closed)return 0;
 (void)fail(s,11);if(!s->revoke_notified){s->busy=1;int r=s->ops.revoke(s->ops.context,e);s->busy=0;if(r)return -1;s->revoke_notified=1;}
 zero(&s->ops,sizeof s->ops);s->closed=1;return 0;
}
