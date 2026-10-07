#ifndef QCA_PEER_WIRE_H
#define QCA_PEER_WIRE_H
#include <stdint.h>
/* Pure bytes: no admission, ownership, transmission or acknowledgement. */
unsigned qca_sta_peer_create_wire(uint8_t *out, unsigned capacity,
                                  unsigned vdev_id, const uint8_t bssid[6]);
#endif
