#include "network.h"
#include "wan_transport.h"
#include "dhcp_policy.h"
#include "lwip/dhcp.h"
#include "lwip/prot/dhcp.h"
#include "lwip/netif.h"
#include "lwip/dns.h"
#include "lwip/tcp.h"
#include "lwip/pbuf.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
static uint8_t last[1518],server[1518];static size_t lastn;static unsigned sends,arp,checks;static uint8_t mac[6]={2,0,0,0,0,1};
void rabbit_network_panic(const char*s){fprintf(stderr,"panic %s\n",s);abort();}
static int output(void*c,const uint8_t*b,size_t n){(void)c;assert(n<=1518);memcpy(last,b,n);lastn=n;sends++;if(b[12]==8&&b[13]==6)arp++;return 0;}
static uint32_t rng(void*c){(void)c;return 0x12345678;}
static void w16(uint8_t*b,unsigned x){b[0]=x>>8;b[1]=x;}
static unsigned checksum(const uint8_t*b,unsigned n){unsigned x=0;for(unsigned i=0;i<n;i+=2)x+=(b[i]<<8)|b[i+1];while(x>>16)x=(x&65535)+(x>>16);return (~x)&65535;}
static size_t reply(unsigned type,unsigned wrong,unsigned missing_server){
 assert(netif_default);memset(server,0,sizeof(server));memset(server,255,6);memcpy(server+6,mac,6);server[12]=8;
 uint8_t*ip=server+14,*udp=ip+20,*d=udp+8;ip[0]=0x45;ip[8]=64;ip[9]=17;ip[12]=10;ip[15]=1;memset(ip+16,255,4);w16(udp,67);w16(udp+2,68);
 d[0]=2;d[1]=1;d[2]=6;uint32_t xid=lwip_htonl(netif_dhcp_data(netif_default)->xid);memcpy(d+4,&xid,4);if(wrong)d[4]^=1;d[16]=10;d[19]=42;memcpy(d+28,mac,6);d[236]=99;d[237]=130;d[238]=83;d[239]=99;
 unsigned k=240;d[k++]=53;d[k++]=1;d[k++]=type;if(!missing_server){d[k++]=54;d[k++]=4;d[k++]=10;d[k++]=0;d[k++]=0;d[k++]=1;}
 d[k++]=51;d[k++]=4;d[k++]=0;d[k++]=0;d[k++]=2;d[k++]=88;
 d[k++]=1;d[k++]=4;d[k++]=255;d[k++]=255;d[k++]=255;d[k++]=0;
 d[k++]=3;d[k++]=4;d[k++]=10;d[k++]=0;d[k++]=0;d[k++]=1;d[k++]=255;
 w16(udp+4,k+8);w16(ip+2,k+28);w16(ip+10,checksum(ip,20));return k+42;
}
static unsigned resolved,connected;static ip_addr_t resolved_ip;
static void found(const char*name,const ip_addr_t*ip,void*context){(void)name;(void)context;assert(ip);resolved_ip=*ip;resolved++;}
static err_t established(void*arg,struct tcp_pcb*pcb,err_t result){(void)arg;(void)pcb;assert(result==ERR_OK);connected++;return ERR_OK;}
static uint32_t r32(const uint8_t*p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void w32(uint8_t*p,uint32_t value){p[0]=value>>24;p[1]=value>>16;p[2]=value>>8;p[3]=value;}
static void router_arp(void){
 uint8_t b[42]={0};memcpy(b,mac,6);const uint8_t router[6]={2,1,2,3,4,5};memcpy(b+6,router,6);w16(b+12,0x806);w16(b+14,1);w16(b+16,0x800);b[18]=6;b[19]=4;w16(b+20,2);memcpy(b+22,router,6);b[28]=10;b[31]=1;memcpy(b+32,mac,6);b[38]=10;b[41]=42;assert(!rabbit_network_input(b,sizeof(b),1));
}
static size_t dns_reply(uint8_t*b){
 assert(lastn>=54&&last[23]==17&&last[36]==0&&last[37]==53);unsigned qlen=lastn-42;assert(qlen<1200);memset(b,0,1518);memcpy(b,mac,6);memcpy(b+6,last,6);w16(b+12,0x800);uint8_t*ip=b+14,*udp=ip+20,*d=udp+8;ip[0]=0x45;ip[8]=64;ip[9]=17;ip[12]=10;ip[15]=1;ip[16]=10;ip[19]=42;w16(udp,53);memcpy(udp+2,last+34,2);memcpy(d,last+42,qlen);d[2]=0x81;d[3]=0x80;w16(d+6,1);w16(d+8,0);w16(d+10,0);uint8_t*a=d+qlen;a[0]=0xc0;a[1]=12;w16(a+2,1);w16(a+4,1);w32(a+6,60);w16(a+10,4);a[12]=198;a[13]=51;a[14]=100;a[15]=9;unsigned length=qlen+16;w16(udp+4,length+8);w16(ip+2,length+28);w16(ip+10,checksum(ip,20));return length+42;
}
static void tcp_synack(uint8_t*b){
 assert(lastn>=54&&last[23]==6&&(last[47]&2));memset(b,0,1518);memcpy(b,mac,6);memcpy(b+6,last,6);w16(b+12,0x800);uint8_t*ip=b+14,*t=ip+20;ip[0]=0x45;ip[8]=64;ip[9]=6;memcpy(ip+12,last+30,4);memcpy(ip+16,last+26,4);w16(ip+2,40);w16(ip+10,checksum(ip,20));memcpy(t,last+36,2);memcpy(t+2,last+34,2);w32(t+4,7);w32(t+8,r32(last+38)+1);t[12]=0x50;t[13]=0x12;w16(t+14,4096);unsigned sum=0;for(unsigned i=12;i<20;i+=2)sum+=(ip[i]<<8)|ip[i+1];sum+=6+20;for(unsigned i=0;i<20;i+=2)sum+=(t[i]<<8)|t[i+1];while(sum>>16)sum=(sum&65535)+(sum>>16);w16(t+16,(~sum)&65535);
}
static void tcp_payload(uint8_t *b,size_t n){
 uint8_t *ip=b+14,*t=ip+20;assert(n<=1200);w16(ip+2,(unsigned)n+40);ip[10]=ip[11]=0;w16(ip+10,checksum(ip,20));w32(t+4,8);t[13]=0x18;t[16]=t[17]=0;for(size_t i=0;i<n;i++)t[20+i]=(uint8_t)i;
 unsigned sum=0;for(unsigned i=12;i<20;i+=2)sum+=(ip[i]<<8)|ip[i+1];sum+=6+20+(unsigned)n;for(unsigned i=0;i<20+n;i+=2)sum+=(t[i]<<8)|t[i+1];while(sum>>16)sum=(sum&65535)+(sum>>16);w16(t+16,(~sum)&65535);
}
static void wan_checks(void){
 ip_addr_t dns;IP_ADDR4(&dns,10,0,0,1);dns_setserver(0,&dns);router_arp();
 ip_addr_t answer;assert(dns_gethostbyname("yukabox.tail1e1ad1.ts.net",&answer,found,0)==ERR_INPROGRESS);assert(!resolved);checks++;
 uint8_t packet[1518];size_t n=dns_reply(packet);packet[42]^=1;assert(!rabbit_network_input(packet,n,1)&&!resolved);checks++;packet[42]^=1;assert(rabbit_network_input(packet,n,2)==-1&&!resolved);checks++;assert(!rabbit_network_input(packet,n,1)&&resolved==1);checks++;
 assert(!rabbit_network_input(packet,n,1)&&resolved==1);checks++;
 struct tcp_pcb*pcb=tcp_new();assert(pcb);assert(tcp_connect(pcb,&resolved_ip,10000,established)==ERR_OK&&!connected);checks++;
 tcp_synack(packet);packet[50]^=1;assert(!rabbit_network_input(packet,54,1)&&!connected);checks++;packet[50]^=1;assert(!rabbit_network_input(packet,54,1)&&connected==1);checks++;
 assert(!rabbit_network_input(packet,54,1)&&connected==1);checks++;tcp_abort(pcb);
 static uint8_t rx[RABBIT_WAN_RX_CAP];struct rabbit_wan_context ctx={1},stale={2};unsigned char bytes[3000]={0};
 assert(rabbit_wan_open(2,"yukabox.tail1e1ad1.ts.net",10000,rx,sizeof(rx))==-1);checks++;
 assert(!rabbit_wan_open(1,"yukabox.tail1e1ad1.ts.net",10000,rx,sizeof(rx)));checks++;
 assert(rabbit_wan_poll(1)==0);checks++;tcp_synack(packet);assert(!rabbit_network_input(packet,54,1)&&rabbit_wan_poll(1)==1);checks++;
 assert(rabbit_wan_recv(&stale,bytes,1)==-1&&rabbit_wan_recv(&ctx,bytes,1)==RABBIT_WAN_WANT_READ);checks++;
 tcp_payload(packet,1200);assert(!rabbit_network_input(packet,1254,1));checks++;
 assert(rabbit_wan_recv(&ctx,bytes,3000)==1200);for(size_t i=0;i<1200;i++)assert(bytes[i]==(uint8_t)i);checks++;
 assert(!rabbit_network_input(packet,1254,1)&&rabbit_wan_recv(&ctx,bytes,1)==RABBIT_WAN_WANT_READ);checks++;
 assert(rabbit_wan_send(&stale,bytes,1)==-1);checks++;
 int accepted=rabbit_wan_send(&ctx,bytes,sizeof(bytes));assert(accepted>0&&accepted<=TCP_SND_BUF);checks++;
 assert(rabbit_wan_send(&ctx,bytes,1)==RABBIT_WAN_WANT_WRITE);checks++;
 rabbit_wan_close();for(size_t i=0;i<sizeof(rx);i++)assert(rx[i]==0);checks++;
 assert(rabbit_wan_poll(1)==-1&&rabbit_wan_recv(&ctx,bytes,1)==-1);checks++;
 assert(!rabbit_wan_open(1,"pending.example.invalid",10000,rx,sizeof(rx)));checks++;
 rabbit_wan_close();assert(rabbit_wan_open(1,"another.example.invalid",10000,rx,sizeof(rx))==-1);checks++;
 for(unsigned i=0;i<200;i++)assert(!rabbit_network_tick(100));
 assert(!rabbit_wan_open(1,"198.51.100.9",10000,rx,sizeof(rx)));checks++;rabbit_wan_close();


}
static void ticks(unsigned ms){for(unsigned i=0;i<ms;i+=100)assert(!rabbit_network_tick(100));}
int main(void){
 struct rabbit_network_ops o={output,rng,0};struct rabbit_network_authorization a={61,1,1,0};
 assert(rabbit_network_start(&a,&o,mac)==-1&&sends==0);checks++;
 a.rsn_controlled_port_authorized=1;assert(!rabbit_network_start(&a,&o,mac)&&sends==1);checks++;assert(last[42]==1);assert(!rabbit_network_ip());
 uint8_t eapol[14]={0};eapol[12]=0x88;eapol[13]=0x8e;assert(rabbit_network_input(eapol,14,1)==-1);checks++;
 size_t n=reply(2,1,0);unsigned before=sends;assert(!rabbit_network_input(server,n,1));assert(sends==before&&!rabbit_network_ip());checks++;
 n=reply(2,0,1);assert(!rabbit_network_input(server,n,1));assert(sends==before);checks++;
 n=reply(2,0,0);assert(rabbit_network_input(server,n,2)==-1);checks++;
 assert(rabbit_network_input(server,30,1)==-1);assert(sends==before);checks++;
 server[42+241]=255;assert(rabbit_network_input(server,n,1)==-1);assert(sends==before&&!rabbit_network_ip());checks++;server[42+241]=1;
 server[24]^=1;assert(!rabbit_network_input(server,n,1));assert(sends==before);checks++;server[24]^=1;
 assert(!rabbit_network_input(server,n,1));assert(sends>before&&!rabbit_network_ip());checks++;
 n=reply(5,1,0);assert(!rabbit_network_input(server,n,1)&&!rabbit_network_ip());checks++;
 n=reply(5,0,0);
unsigned unchanged=sends;
 for(size_t clipped=0;clipped<n;clipped++){assert(rabbit_network_input(server,clipped,1)==-1&&!rabbit_network_ip());checks++;}
 uint8_t selected[4]={10,0,0,1},accepted[4];assert(!rabbit_dhcp_ingress_policy(server,n,DHCP_STATE_RENEWING,selected,accepted));checks++;
 uint8_t overloaded[1518];memcpy(overloaded,server,n);memset(overloaded+42+243,0,6);overloaded[42+108]=54;overloaded[42+109]=4;memcpy(overloaded+42+110,selected,4);overloaded[42+114]=255;
 overloaded[n-1]=52;overloaded[n]=1;overloaded[n+1]=1;overloaded[n+2]=255;w16(overloaded+16,n+3-14);w16(overloaded+38,n+3-34);assert(!rabbit_dhcp_ingress_policy(overloaded,n+3,DHCP_STATE_REQUESTING,selected,accepted)&&!memcmp(accepted,selected,4));checks++;

 assert(rabbit_network_input(server,n-1,1)==-1&&!rabbit_network_ip());checks++;
 server[20]=0x20;assert(rabbit_network_input(server,n,1)==-1&&!rabbit_network_ip());checks++;server[20]=0;
 server[42+243]=0;assert(rabbit_network_input(server,n,1)==-1&&!rabbit_network_ip());checks++;server[42+243]=54;
 uint8_t saved[1518];memcpy(saved,server,n);server[n-1]=54;server[n]=4;server[n+1]=10;server[n+2]=0;server[n+3]=0;server[n+4]=1;server[n+5]=255;
 w16(server+14+2,n+6-14);w16(server+14+20+4,n+6-34);server[24]=server[25]=0;w16(server+24,checksum(server+14,20));assert(rabbit_network_input(server,n+6,1)==-1&&!rabbit_network_ip());checks++;memcpy(server,saved,n);
 assert(sends==unchanged);checks++;
 server[42+248]=99;assert(rabbit_network_input(server,n,1)==-1&&!rabbit_network_ip());checks++;server[42+248]=1;

 assert(!rabbit_network_input(server,n,1));ticks(10000);assert(rabbit_network_ip()!=0&&arp>=2);checks++;
 wan_checks();
 unsigned assigned=rabbit_network_ip();assert(!rabbit_network_input(server,n,1)&&rabbit_network_ip()==assigned);checks++;
 ticks(310000);assert(rabbit_network_ip()==assigned&&sends>before&&netif_dhcp_data(netif_default)->state==DHCP_STATE_RENEWING);checks++;
 n=reply(5,0,0);server[42+248]=99;assert(rabbit_network_input(server,n,1)==-1&&netif_dhcp_data(netif_default)->state==DHCP_STATE_RENEWING);checks++;server[42+248]=1;assert(!rabbit_network_input(server,n,1)&&netif_dhcp_data(netif_default)->state==DHCP_STATE_BOUND);checks++;
 ticks(550000);assert(netif_dhcp_data(netif_default)->state==DHCP_STATE_REBINDING);checks++;
 n=reply(5,0,0);server[42+248]=99;assert(!rabbit_network_input(server,n,1)&&rabbit_network_ip()==assigned);checks++;assert(netif_dhcp_data(netif_default)->state==DHCP_STATE_BOUND);assert(((uint8_t*)&netif_dhcp_data(netif_default)->server_ip_addr)[3]==99);checks++;
 ticks(605000);assert(!rabbit_network_ip()&&netif_dhcp_data(netif_default)->state==DHCP_STATE_SELECTING);checks++;
 rabbit_network_revoke();assert(!rabbit_network_ip()&&rabbit_network_input(server,n,1)==-1);checks++;
 a.association_epoch=2;assert(!rabbit_network_start(&a,&o,mac));checks++;
 n=reply(2,0,0);assert(!rabbit_network_input(server,n,2));n=reply(5,0,0);assert(!rabbit_network_input(server,n,2));checks++;
 uint8_t conflict[42]={0};memset(conflict,255,6);const uint8_t other[6]={2,9,8,7,6,5};memcpy(conflict+6,other,6);w16(conflict+12,0x806);w16(conflict+14,1);w16(conflict+16,0x800);conflict[18]=6;conflict[19]=4;w16(conflict+20,2);memcpy(conflict+22,other,6);conflict[28]=10;conflict[31]=42;memcpy(conflict+32,mac,6);conflict[38]=10;conflict[41]=42;
 assert(!rabbit_network_input(conflict,sizeof(conflict),2)&&!rabbit_network_ip());checks++;
 assert(netif_dhcp_data(netif_default)->state==DHCP_STATE_BACKING_OFF);checks++;
 rabbit_network_revoke();
 printf("PASS %u SYNTHETIC DHCP/ARP/PORT/DNS/TCP checks sends=%u arp=%u\n",checks,sends,arp);return 0;
}
