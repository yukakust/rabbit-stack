#include "network.h"
#include "dhcp_policy.h"
#include "lwip/dhcp.h"
#include "lwip/prot/dhcp.h"
#include "lwip/netif.h"
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
 unsigned assigned=rabbit_network_ip();assert(!rabbit_network_input(server,n,1)&&rabbit_network_ip()==assigned);checks++;
 ticks(310000);assert(rabbit_network_ip()==assigned&&sends>before&&netif_dhcp_data(netif_default)->state==DHCP_STATE_RENEWING);checks++;
 n=reply(5,0,0);server[42+248]=99;assert(rabbit_network_input(server,n,1)==-1&&netif_dhcp_data(netif_default)->state==DHCP_STATE_RENEWING);checks++;server[42+248]=1;assert(!rabbit_network_input(server,n,1)&&netif_dhcp_data(netif_default)->state==DHCP_STATE_BOUND);checks++;
 ticks(550000);assert(netif_dhcp_data(netif_default)->state==DHCP_STATE_REBINDING);checks++;
 n=reply(5,0,0);server[42+248]=99;assert(!rabbit_network_input(server,n,1)&&rabbit_network_ip()==assigned);checks++;assert(netif_dhcp_data(netif_default)->state==DHCP_STATE_BOUND);assert(((uint8_t*)&netif_dhcp_data(netif_default)->server_ip_addr)[3]==99);checks++;
 ticks(605000);assert(!rabbit_network_ip()&&netif_dhcp_data(netif_default)->state==DHCP_STATE_SELECTING);checks++;
 rabbit_network_revoke();assert(!rabbit_network_ip()&&rabbit_network_input(server,n,1)==-1);checks++;
 printf("PASS %u SYNTHETIC DHCP/ARP/PORT checks sends=%u arp=%u\n",checks,sends,arp);return 0;
}
