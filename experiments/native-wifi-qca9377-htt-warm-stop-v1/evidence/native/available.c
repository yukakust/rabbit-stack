#include "available.h"
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
int qca_wmi_available(const uint8_t*p,unsigned n,QcaWmiAvailable*out){
 if(!p||!out||n!=28||word(p)!=3||word(p+4)!=(20u|(559u<<16))||word(p+8)!=128)return 0;
 QcaWmiAvailable value={0};value.advertised_length=word(p+8);
 for(unsigned i=0;i<4;i++)value.words[i]=word(p+12+4*i);
 *out=value;return 1;
}
