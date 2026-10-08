#ifndef RABBIT_ROLE2_PARENT
#define RABBIT_ROLE2_PARENT
#include "loader.h"
#include "rsn_child.h"
/* Parent-owned lease. Loader, pools, callbacks and provider context must outlive
 * this lease. This API does not approve entropy/NIC/key/port providers. */
typedef struct {ModLoader*loader;uint64_t epoch;uint32_t bound,busy,closed,quarantined;} RsnParentLease;
int rsn_parent_bind(RsnParentLease*,ModLoader*);
Status rsn_parent_call(RsnParentLease*,uint32_t,void*);
int rsn_parent_close(RsnParentLease*);
int rsn_parent_can_unload(const RsnParentLease*);
#endif
