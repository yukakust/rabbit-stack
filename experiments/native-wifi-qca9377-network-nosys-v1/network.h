#ifndef RABBIT_NETWORK_H
#define RABBIT_NETWORK_H
#include <stdint.h>
#include <stddef.h>
struct rabbit_network_authorization {
 uint32_t generation, association_epoch, key_install_verified, rsn_controlled_port_authorized;
};
/* Root/driver must establish these values from actual RSN/key installation proof;
 * this adapter never authenticates Wi-Fi and these are not user input flags. */
struct rabbit_network_ops {
 int (*send_ethernet)(void*,const uint8_t*,size_t);
 uint32_t (*random32)(void*);
 void *context;
};
int rabbit_network_start(const struct rabbit_network_authorization*,const struct rabbit_network_ops*,const uint8_t mac[6]);
int rabbit_network_input(const uint8_t*,size_t,uint32_t epoch);
int rabbit_network_tick(uint32_t elapsed_ms);
void rabbit_network_revoke(void);
uint32_t rabbit_network_ip(void);
#endif
