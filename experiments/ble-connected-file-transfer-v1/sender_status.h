#ifndef RABBIT_SENDER_STATUS_H
#define RABBIT_SENDER_STATUS_H
/* Shared by real Mac sender and host tests. Status is correlated, NOT authenticated. */
#include <stdint.h>
#include <stddef.h>
enum { RS_INVALID,RS_STAGING,RS_APPLIED,RS_PENDING };
static inline uint32_t rs_u32(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static inline int rs_equal(const uint8_t*a,const uint8_t*b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return !x;}
static inline int rs_status(const uint8_t*p,size_t n,const uint8_t*nonce,
 const uint8_t*digest,uint32_t counter,uint32_t length,uint32_t*received){
 if(!p||!nonce||!digest||!received||n!=60||!rs_equal(p,(const uint8_t*)"RFS\1",4)||
    !rs_equal(p+4,nonce,8)||rs_u32(p+16)!=length||p[21]||p[22]||p[23]||rs_u32(p+12)>length)return RS_INVALID;
 *received=rs_u32(p+12);
 if(p[20]==1)return RS_STAGING;
 if(*received!=length)return RS_INVALID;
 if(p[20]==4)return RS_PENDING;
 if(p[20]==2&&rs_u32(p+24)==counter&&rs_equal(p+28,digest,32))return RS_APPLIED;
 return RS_INVALID;
}
#endif
