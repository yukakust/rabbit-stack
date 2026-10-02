#ifndef RABBIT_FILE_CORE_H
#define RABBIT_FILE_CORE_H
#include <stdint.h>
#include <stddef.h>
#define RF_MAX_FILE 65535u
#define RF_MAX_NATIVE 262144u
#define RF_STATUS_SIZE 60u
enum { RF_IDLE, RF_STAGING, RF_APPLIED, RF_REJECTED, RF_PENDING };
/* Returning success requires signature, counter, bounds and health checks AND
 * atomic commit in the caller. Transport integrity alone never applies a world. */
typedef int (*RfApply)(const uint8_t *,uint32_t,uint32_t *);
/* Extended owner supervisor only. 0=committed, 1=rejected, 2=deferred until
 * the driver callback has returned. Transport never grants native authority. */
typedef int (*RfDispatch)(uint8_t,const uint8_t *,uint32_t,uint32_t *);
typedef struct {
 uint8_t stream[RF_MAX_NATIVE+32],digest[32],session[8];
 uint32_t length,received,counter;
 uint8_t state,error,kind;
 RfApply apply;
 RfDispatch dispatch;
} RfFile;
void rf_init(RfFile *,RfApply);
void rf_init_owner(RfFile *,RfDispatch);
int rf_finish(RfFile *,int,uint32_t); /* Only a pending, complete transaction. */
int rf_control(RfFile *,const uint8_t *,size_t);
int rf_data(RfFile *,const uint8_t *,size_t);
void rf_status(const RfFile *,uint8_t [RF_STATUS_SIZE]);
#endif
