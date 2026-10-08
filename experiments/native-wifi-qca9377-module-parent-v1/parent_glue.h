#ifndef RABBIT_MODULE_PARENT_GLUE_H
#define RABBIT_MODULE_PARENT_GLUE_H
#include <stdint.h>
#include <stddef.h>
/* Opaque boundary avoids typedef collisions with the unchanged Connected ABI. */
#define PARENT_MODULE_PROTOCOL_MAGIC UINT64_C(0x31544f5250444f4d)
#define PARENT_PROTO_API __attribute__((ms_abi))
typedef struct {uint64_t magic;uint32_t abi,size;uint64_t epoch;uint32_t entropy_approved,reserved;int(PARENT_PROTO_API*lease)(uint64_t);int(PARENT_PROTO_API*release)(uint64_t);int(PARENT_PROTO_API*accept)(const uint8_t*,size_t);int(PARENT_PROTO_API*cpu)(void*,size_t);int(PARENT_PROTO_API*rng_info)(void*,size_t);} ParentModuleProtocol;
_Static_assert(sizeof(ParentModuleProtocol)==72,"parent-module public native protocol");
int parent_module_bind(void*,void*,uint64_t,const uint8_t[32],const uint8_t[32],const uint8_t[32]);
int parent_module_accept(const uint8_t*,size_t);
int parent_module_close(void);
int parent_module_released(void);
int parent_cpu_export(void*,size_t);
/* No key/TLS-open API is exposed until actual approved entropy/physical pin. */
#endif
