#include "network.h"
#include "wan_transport.h"
#include "dhcp_policy.h"
#include "lwip/prot/dhcp.h"
#include "lwip/init.h"
#include "lwip/netif.h"
#include "lwip/timeouts.h"
#include "lwip/dhcp.h"
#include "lwip/etharp.h"
#include "lwip/udp.h"
#include "netif/ethernet.h"
#include <string.h>
static struct netif iface;
static struct dhcp client;
static struct rabbit_network_ops ops;
static uint32_t now,epoch;
static int initialized,authorized;
static uint8_t frame[1518];
uint32_t sys_now(void){return now;}
unsigned int rabbit_network_rand(void){if(!authorized||!ops.random32)rabbit_network_panic("rng boundary");return ops.random32(ops.context);}
static err_t transmit(struct netif*n,struct pbuf*p){(void)n;if(!authorized||p->tot_len>sizeof(frame))return ERR_IF;if(pbuf_copy_partial(p,frame,p->tot_len,0)!=p->tot_len)return ERR_BUF;return ops.send_ethernet(ops.context,frame,p->tot_len)?ERR_IF:ERR_OK;}
static err_t net_init(struct netif*n){n->name[0]='r';n->name[1]='b';n->mtu=1500;n->flags=NETIF_FLAG_BROADCAST|NETIF_FLAG_ETHARP;n->output=etharp_output;n->linkoutput=transmit;return ERR_OK;}
void rabbit_network_revoke(void){if(!initialized)return;authorized=0;rabbit_wan_close();dhcp_stop(&iface);netif_set_link_down(&iface);netif_set_down(&iface);netif_set_addr(&iface,IP4_ADDR_ANY4,IP4_ADDR_ANY4,IP4_ADDR_ANY4);epoch=0;}
int rabbit_network_start(const struct rabbit_network_authorization*a,const struct rabbit_network_ops*o,const uint8_t mac[6]){
 if(!a||!o||!mac||!a->generation||!a->association_epoch||a->key_install_verified!=1||a->rsn_controlled_port_authorized!=1||!o->send_ethernet||!o->random32)return -1;
 if(authorized)return -1;ops=*o;epoch=a->association_epoch;authorized=1;
 if(!initialized){lwip_init();memset(&iface,0,sizeof(iface));if(!netif_add(&iface,IP4_ADDR_ANY4,IP4_ADDR_ANY4,IP4_ADDR_ANY4,0,net_init,ethernet_input)){authorized=0;epoch=0;return -1;}dhcp_set_struct(&iface,&client);initialized=1;}
 memcpy(iface.hwaddr,mac,6);iface.hwaddr_len=6;authorized=1;netif_set_default(&iface);netif_set_up(&iface);netif_set_link_up(&iface);
 if(dhcp_start(&iface)!=ERR_OK){rabbit_network_revoke();return -1;}return 0;
}
int rabbit_network_input(const uint8_t*b,size_t length,uint32_t association_epoch){
 if(!authorized||association_epoch!=epoch||!b||length<14||length>1518)return -1;
 /* EAPOL belongs to the separate supplicant; it cannot enter the IP stack. */
 if(!((b[12]==8&&b[13]==0)||(b[12]==8&&b[13]==6)))return -1;
 uint8_t accepted_server[4];unsigned before_state=client.state;
 if(rabbit_dhcp_ingress_policy(b,length,client.state,(const uint8_t*)&client.server_ip_addr,accepted_server))return -1;
 struct pbuf*p=pbuf_alloc(PBUF_RAW,(uint16_t)length,PBUF_POOL);if(!p)return -1;
 if(pbuf_take(p,b,(uint16_t)length)!=ERR_OK){pbuf_free(p);return -1;}
 if(iface.input(p,&iface)!=ERR_OK){pbuf_free(p);return -1;}
 /* Only actual lwIP acceptance of a matching rebind ACK can adopt its server.
  * No change on checksum/xid/MAC/parser rejection, which leaves state REBINDING. */
 if(before_state==DHCP_STATE_REBINDING&&client.state==DHCP_STATE_BOUND)memcpy(&client.server_ip_addr,accepted_server,4);
 return 0;
}
int rabbit_network_tick(uint32_t ms){if(ms>100)return -1;now+=ms;sys_check_timeouts();return 0;}
uint32_t rabbit_network_ip(void){return authorized?ip4_addr_get_u32(netif_ip4_addr(&iface)):0;}

uint32_t rabbit_network_epoch(void){return authorized?epoch:0;}
