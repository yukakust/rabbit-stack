#ifndef RABBIT_FRAME_CORE_H
#define RABBIT_FRAME_CORE_H
#include <stddef.h>
#include <stdint.h>
#define RF_MAX_WIDTH 640u
#define RF_MAX_HEIGHT 360u
#define RF_MAX_PIXELS (RF_MAX_WIDTH*RF_MAX_HEIGHT)
#define RF_HEADER 64u
#define RF_SIGNATURE 64u
#define RF_MAX_WIRE (RF_HEADER+RF_MAX_PIXELS*5u+RF_SIGNATURE)
typedef struct {uint64_t sequence; uint16_t width,height;} RfFrame;
/* A session's public key and stream ID must be bound by the owner's checked
 * profile. Public fixture keys are ONLY for host/QEMU tests. No code execution.
 * Failure changes neither output pixels nor state. Success writes packed RGB.
 * Caller owns bounded staging/display buffers; no static framebuffer or malloc.
 */
int rf_accept(const uint8_t *wire,size_t length,const uint8_t stream[16],
              const uint8_t public_key[32],RfFrame *state,
              uint32_t *pixels,size_t capacity);
#endif
