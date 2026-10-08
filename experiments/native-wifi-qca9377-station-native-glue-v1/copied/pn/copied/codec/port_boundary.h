/* Unbound native service boundary. No physical approval or firmware implementation. */
#ifndef RABBIT_RSN_PORT_BOUNDARY_H
#define RABBIT_RSN_PORT_BOUNDARY_H
#include <stdint.h>
#include <stddef.h>
struct RsnKeyBinding { uint64_t epoch; uint8_t peer[6],vdev,cipher,index,pairwise; };
enum RsnKeyOutcome { RSN_KEY_CONFIRMED=1, RSN_KEY_FAILED=2, RSN_KEY_AMBIGUOUS=3 };
struct RsnPort {
 void *ctx; uint8_t *arena; size_t arena_bytes; uint64_t epoch,last_time; unsigned have_time,quarantined,key_attempted,key_confirmed;
 void *(*allocate)(void*,size_t); void (*release)(void*,void*,size_t);
 int (*clock_us)(void*,uint64_t*); int (*entropy)(void*,uint8_t*,size_t);
 enum RsnKeyOutcome (*install)(void*,const struct RsnKeyBinding*,const uint8_t*,size_t,struct RsnKeyBinding*);
};
int rsn_port_valid(const struct RsnPort*);
void *rsn_port_allocate(struct RsnPort*,size_t);
int rsn_port_release(struct RsnPort*,void*,size_t);
int rsn_port_time(struct RsnPort*,uint64_t*);
int rsn_port_entropy(struct RsnPort*,uint8_t*,size_t);
int rsn_port_key(struct RsnPort*,const struct RsnKeyBinding*,const uint8_t*,size_t);
#endif
