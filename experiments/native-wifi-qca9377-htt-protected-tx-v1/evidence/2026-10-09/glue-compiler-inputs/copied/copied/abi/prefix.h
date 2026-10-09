#ifndef RABBIT_BOOT_PREFIX57_H
#define RABBIT_BOOT_PREFIX57_H
#include <stdint.h>
#define QCA_PREFIX_DEADLINE_US 5400000000ull
#define QCA_PREFIX_HCI_SLOTS 16u
#define QCA_PREFIX_HCI_BYTES 257u
/* 0 idle,1 active,2 stop requested,3 actual host owners released. */
typedef struct {
 uint64_t started,last;uint32_t phase,reason,polls,stop_calls;
 uint32_t stop_offset,stop_submitted,stop_completed,stop_plan,stop_io;
 uint32_t raw_count,raw_overflow,raw_frozen,usb_fault,frames;
 uint32_t critical_count,routine_count,routine_head,routine_overwritten;
 uint32_t ble_state,pending,connected,credits,inflight,stream_used,stream_goal;
 uint32_t usb_polls,usb_reads,usb_timeouts,usb_observation;
 uint64_t last_usb_status,poll_before,poll_after,max_poll_us,max_qca_us;
 uint32_t last_usb_result,last_usb_bytes;
 struct {uint64_t at;uint32_t length,state,pending;uint8_t bytes[QCA_PREFIX_HCI_BYTES];} raw[QCA_PREFIX_HCI_SLOTS];
} QcaPrefix;
void qca_prefix_arm(QcaPrefix*,uint64_t);
/* Native caller supplies actual boot plan/transport and genuine owner proof.
 * Return1 requests stop; never makes up chip readiness or owner release. */
int qca_prefix_tick(QcaPrefix*,uint64_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
void qca_prefix_request(QcaPrefix*,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
void qca_prefix_event(QcaPrefix*,const uint8_t*,unsigned,uint64_t,uint32_t,uint32_t);
unsigned qca_prefix_raw(const QcaPrefix*,uint8_t*,unsigned,unsigned);
#endif
