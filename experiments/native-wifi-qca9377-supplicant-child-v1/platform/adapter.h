#ifndef RABBIT_RSN_CALLBACK_ADAPTER_H
#define RABBIT_RSN_CALLBACK_ADAPTER_H
#include "runtime.h"
#include "utils/includes.h"
#include "utils/common.h"
#include "rsn_supp/wpa.h"
typedef struct {
 RsnRuntime*runtime;uint64_t epoch;void*owner;void*network;
 struct wpa_sm*sm;enum wpa_states state;uint8_t peer[6],own[6];
 uint8_t rsn[257];size_t rsn_bytes;uint8_t closed;uint32_t auth_timeout_us;
 int(*send_owned)(void*,uint64_t,const uint8_t[6],uint16_t,const uint8_t*,size_t);
 int(*install_confirmed)(void*,uint64_t,int,const uint8_t*,int,int,const uint8_t*,size_t,const uint8_t*,size_t,unsigned);
 int(*protect_confirmed)(void*,uint64_t,const uint8_t[6],int,int);
 void(*core_state)(void*,uint64_t,unsigned);
 void(*close)(void*,uint64_t,unsigned);
} RsnNativeIo;
/* Actual mature ctx object must be os_zalloc-owned; wpa_sm_deinit frees it.
 * Provider success means synchronous owned copy/real key confirmation under
 * caller contract, not mere enqueue/DMA completion. Never a default success. */
int rsn_native_ctx(RsnNativeIo*,struct wpa_sm_ctx*);
#endif
