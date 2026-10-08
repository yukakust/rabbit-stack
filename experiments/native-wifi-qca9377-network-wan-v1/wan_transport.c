#include "wan_transport.h"
#include "network.h"
#include "lwip/tcp.h"
#include "lwip/dns.h"
#include "lwip/pbuf.h"
#include <string.h>
static struct {struct tcp_pcb *pcb;uint32_t epoch;uint16_t port;unsigned dns_pending,active,connected,failed,eof;uint8_t *rx;size_t capacity,head,used;} stream;
static int current(void){return stream.active&&rabbit_network_epoch()==stream.epoch&&rabbit_network_ip()!=0;}
static void clear_rx(void){if(stream.rx){volatile uint8_t *p=stream.rx;for(size_t i=0;i<stream.capacity;i++)p[i]=0;}stream.used=stream.head=0;}
void rabbit_wan_close(void){
 stream.active=stream.connected=0;
 if(stream.pcb){struct tcp_pcb *p=stream.pcb;stream.pcb=0;tcp_arg(p,0);tcp_recv(p,0);tcp_sent(p,0);tcp_err(p,0);tcp_abort(p);}
 clear_rx();stream.rx=0;stream.capacity=0;stream.epoch=0;
 /* An outstanding DNS callback owns this singleton until it fires or times out.
  * Never reuse its context as a new epoch while the mature resolver owns it. */
}
static void error_cb(void *arg,err_t error){(void)arg;(void)error;stream.pcb=0;stream.failed=1;stream.connected=0;clear_rx();}
static err_t receive_cb(void *arg,struct tcp_pcb *pcb,struct pbuf *p,err_t error){
 (void)arg;if(!current()||pcb!=stream.pcb){if(p)pbuf_free(p);rabbit_wan_close();return ERR_ABRT;}
 if(error!=ERR_OK){if(p)pbuf_free(p);stream.failed=1;return error;}
 if(!p){stream.eof=1;return ERR_OK;}
 if(p->tot_len>stream.capacity-stream.used)return ERR_MEM;
 size_t length=p->tot_len;
 for(size_t i=0;i<length;i++)stream.rx[(stream.head+stream.used+i)%stream.capacity]=pbuf_get_at(p,(u16_t)i);
 stream.used+=length;pbuf_free(p);tcp_recved(pcb,(u16_t)length);return ERR_OK;
}
static err_t connected_cb(void *arg,struct tcp_pcb *pcb,err_t error){
 (void)arg;if(!current()||pcb!=stream.pcb){rabbit_wan_close();return ERR_ABRT;}
 if(error!=ERR_OK){stream.failed=1;return error;}stream.connected=1;return ERR_OK;
}
static int connect_ip(const ip_addr_t *ip){
 if(!current()||!ip||!IP_IS_V4(ip)||ip_addr_isany(ip))return -1;
 stream.pcb=tcp_new();if(!stream.pcb)return -1;
 tcp_arg(stream.pcb,&stream);tcp_recv(stream.pcb,receive_cb);tcp_err(stream.pcb,error_cb);
 if(tcp_connect(stream.pcb,ip,stream.port,connected_cb)!=ERR_OK){rabbit_wan_close();return -1;}return 0;
}
static void found_cb(const char *name,const ip_addr_t *ip,void *arg){(void)name;(void)arg;stream.dns_pending=0;if(!current()||connect_ip(ip))stream.failed=1;}
int rabbit_wan_open(uint32_t epoch,const char *host,uint16_t port,uint8_t *rx,size_t capacity){
 if(stream.active||stream.dns_pending||!epoch||epoch!=rabbit_network_epoch()||!rabbit_network_ip()||!host||!port||!rx||capacity!=RABBIT_WAN_RX_CAP)return -1;
 size_t n=0;while(n<128&&host[n])n++;if(!n||n==128)return -1;
 memset(&stream,0,sizeof(stream));stream.active=1;stream.epoch=epoch;stream.port=port;stream.rx=rx;stream.capacity=capacity;clear_rx();
 ip_addr_t ip;stream.dns_pending=1;err_t result=dns_gethostbyname(host,&ip,found_cb,&stream);
 if(result==ERR_INPROGRESS)return 0;stream.dns_pending=0;if(result!=ERR_OK||connect_ip(&ip)){rabbit_wan_close();return -1;}return 0;
}
int rabbit_wan_poll(uint32_t epoch){if(!current()||epoch!=stream.epoch||stream.failed){rabbit_wan_close();return -1;}if(stream.connected){err_t e=tcp_output(stream.pcb);if(e!=ERR_OK&&e!=ERR_MEM&&e!=ERR_RTE){rabbit_wan_close();return -1;}}return stream.connected?1:0;}
int rabbit_wan_send(void *context,const unsigned char *bytes,size_t length){
 if(!context||((const struct rabbit_wan_context*)context)->epoch!=stream.epoch)return -1;
 if(!current()||!stream.connected||stream.failed||stream.eof||!bytes||!length||length>65535)return -1;
 u16_t room=tcp_sndbuf(stream.pcb);size_t n=length<room?length:room;if(!n)return RABBIT_WAN_WANT_WRITE;
 err_t e=tcp_write(stream.pcb,bytes,(u16_t)n,TCP_WRITE_FLAG_COPY);if(e==ERR_MEM)return RABBIT_WAN_WANT_WRITE;if(e!=ERR_OK)return -1;
 /* tcp_write owns a copy; ERR_MEM from output preserves queued data for poll/retry. */
 e=tcp_output(stream.pcb);if(e!=ERR_OK&&e!=ERR_MEM&&e!=ERR_RTE){stream.failed=1;return -1;}return (int)n;
}
int rabbit_wan_recv(void *context,unsigned char *bytes,size_t length){
 if(!context||((const struct rabbit_wan_context*)context)->epoch!=stream.epoch)return -1;
 if(!current()||!stream.connected||stream.failed||!bytes||!length)return -1;
 if(!stream.used)return stream.eof?0:RABBIT_WAN_WANT_READ;
 size_t n=length<stream.used?length:stream.used;for(size_t i=0;i<n;i++){bytes[i]=stream.rx[stream.head];stream.rx[stream.head]=0;stream.head=(stream.head+1)%stream.capacity;}stream.used-=n;return (int)n;
}
