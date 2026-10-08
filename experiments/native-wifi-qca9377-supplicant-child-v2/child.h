#ifndef RABBIT_PRIVATE_RSN_CHILD
#define RABBIT_PRIVATE_RSN_CHILD
#include "module_abi.h"
#define RSN_CHILD_OPEN 1u
#define RSN_CHILD_EAPOL 2u
#define RSN_CHILD_POLL 3u
#define RSN_CHILD_STATUS 4u
typedef struct {
 void*context;size_t context_bytes;uint8_t source_sha256[32];
 int(EFIAPI*monotonic_us)(void*,uint64_t*);
 int(EFIAPI*wall_us)(void*,uint64_t*);
 int(EFIAPI*random)(void*,uint8_t*,size_t);
 int(EFIAPI*send_owned)(void*,uint64_t,const uint8_t[6],uint16_t,const uint8_t*,size_t);
 int(EFIAPI*install_confirmed)(void*,uint64_t,int,const uint8_t*,int,int,const uint8_t*,size_t,const uint8_t*,size_t,unsigned);
 int(EFIAPI*protect_confirmed)(void*,uint64_t,const uint8_t[6],int,int);
 void(EFIAPI*state)(void*,uint64_t,unsigned);
 void(EFIAPI*revoked)(void*,uint64_t,unsigned);
} RsnChildProviders;
typedef struct {uint64_t epoch,rx_floor;uint8_t*arena;size_t arena_bytes;RsnChildProviders providers;uint8_t peer[6],own[6];const uint8_t*ssid;size_t ssid_bytes;const uint8_t*rsn;size_t rsn_bytes;const uint8_t*pmk;size_t pmk_bytes;uint32_t auth_timeout_us,reserved;} RsnChildOpen;
typedef struct {uint64_t epoch,completion;const uint8_t*bytes;size_t count;uint8_t peer[6];uint16_t reserved;int32_t encryption;int result;} RsnChildEapol;
typedef struct {uint64_t epoch,now;uint32_t budget,reserved;int result;} RsnChildPoll;
typedef struct {uint64_t epoch;uint32_t opened,state,fault,borrowed,busy,allocations,timers,quarantined;} RsnChildStatus;
Status EFIAPI rsn_child_entry(void*,SystemTable*);
#endif
