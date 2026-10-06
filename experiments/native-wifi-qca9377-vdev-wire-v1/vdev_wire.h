#ifndef RABBIT_QCA_VDEV_WIRE_H
#define RABBIT_QCA_VDEV_WIRE_H
#include <stdint.h>
/* Pure WMI body serializers, no HTC envelope/MMIO/send/state transition.
 * Native caller must use actual validated READY MAC, current credits and
 * retained owners. The checked resource profile has four vdev slots.
 * Returning bytes does NOT prove firmware created/stopped/deleted a vdev. */
unsigned qca_station_create_wire(uint8_t*,unsigned,unsigned,const uint8_t[6]);
unsigned qca_station_stop_wire(uint8_t*,unsigned,unsigned);
unsigned qca_station_delete_wire(uint8_t*,unsigned,unsigned);
#endif
