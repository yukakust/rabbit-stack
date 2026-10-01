#include "transport_core.h"
#include "verify_core.h"
static uint8_t staging[MAX_RUNTIME_BYTES],transfer,receiving,completed;
static uint32_t length,position,sequence;
static uint16_t le16(const uint8_t*p){return p[0]|((uint16_t)p[1]<<8);}
static uint32_t le32(const uint8_t*p){return le16(p)|((uint32_t)le16(p+2)<<16);}
static uint32_t be32(const uint8_t*p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static uint32_t fnv(const uint8_t*p,size_t n){uint32_t x=0x811c9dc5;for(size_t i=0;i<n;i++)x=(x^p[i])*0x01000193;return x;}
const uint8_t *rabbit_rx_data(void){return staging;}
size_t rabbit_rx_length(void){return position;}
void rabbit_rx_reset(void){length=position=sequence=0;receiving=completed=transfer=0;}
int rabbit_rx_frame(const uint8_t f[16]){
 if(f[0]!='R'||f[1]!='P'||!f[3]||be32(f+12)!=fnv(f,12))return 1;
 unsigned kind=f[2];uint32_t index=le16(f+4);
 if(kind==0x31){
  uint32_t total=le32(f+6);
  if(index||f[10]||f[11]||total<257||total>MAX_RUNTIME_BYTES)return 1;
  if(receiving&&!completed&&transfer==f[3]&&length==total)return 0;
  length=total;transfer=f[3];position=sequence=0;receiving=1;completed=0;return 0;
 }
 if(!receiving||transfer!=f[3])return 1;
 if(kind==0x32){
  if(index<sequence){
   uint32_t start=index*6,count=length-start;if(count>6)count=6;
   for(unsigned i=0;i<count;i++)if(staging[start+i]!=f[6+i])return 1;
   for(unsigned i=count;i<6;i++)if(f[6+i])return 1;
   return 0;
  }
  if(index!=sequence||position>=length)return 1;
  unsigned count=length-position;if(count>6)count=6;
  for(unsigned i=count;i<6;i++)if(f[6+i])return 1;
  for(unsigned i=0;i<count;i++)staging[position+i]=f[6+i];
  position+=count;sequence++;return 0;
 }
 if(kind!=0x33||f[10]||f[11]||index!=sequence||!position||be32(f+6)!=fnv(staging,position))return 1;
 if(position==length){completed=1;return 2;}
 return 3;
}
