#ifndef RABBIT_BT_EVENT_STREAM_H
#define RABBIT_BT_EVENT_STREAM_H
#include <stdint.h>
typedef struct {uint8_t bytes[257];unsigned used,goal;} RabbitBtEventStream;
typedef void (*RabbitBtEventReceive)(void*,const uint8_t*,unsigned);
/* One exclusive owner, zero-initialized stream, successful USB reads only.
 * Callback gets a complete length-framed HCI event, not an authenticated event.
 * Callback must neither reenter nor retain this buffer. No allocation or I/O.
 * Error changes neither stream nor callback; n bounded to one260-byte USB read. */
int rabbit_bt_events(RabbitBtEventStream*,const uint8_t*,unsigned,RabbitBtEventReceive,void*);
#endif
