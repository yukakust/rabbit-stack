#include "boot_image.h"
#include "sha256.h"
static const uint8_t board_hash[32]={0xb2,0x71,0x3b,0x77,0xc7,0x25,0xb0,0xff,0x81,0xaf,0x75,0xc8,0x5c,0x3a,0xeb,0xa9,0x78,0x85,0xd0,0xf4,0x01,0x74,0xf7,0x15,0xb1,0xe3,0x9d,0x5a,0x9d,0x50,0xf4,0xe7};
static const uint8_t helper_hash[32]={0xfa,0xc7,0xed,0xbb,0xdd,0xb4,0xe1,0xb1,0xa3,0xd8,0x46,0xcd,0x55,0xf8,0x3c,0x60,0x7c,0x31,0xb7,0xa0,0x7b,0x0c,0xee,0xe7,0x3d,0xc7,0xec,0x15,0x4e,0x8e,0x69,0x88};
static const uint8_t main_hash[32]={0x57,0xcb,0xd4,0x74,0xbd,0xa6,0xa5,0xe3,0x4e,0x5e,0x9e,0x75,0xec,0x5a,0xba,0x79,0xf4,0x26,0xf4,0xa0,0xb3,0x57,0x19,0x42,0x1c,0x75,0xf9,0x41,0xec,0x69,0x39,0x15};
static uint32_t word(const uint8_t*p){uint32_t v=0;for(unsigned i=0;i<4;i++)v|=(uint32_t)p[i]<<(8*i);return v;}
static void put(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
static int fail(QcaBootImage*s,unsigned e){s->error=e;s->phase=21;return -1;}
static int hash(const uint8_t*p,unsigned n,const uint8_t expected[32]){
 if(!p||(uintptr_t)p>UINTPTR_MAX-n)return -1;
 uint8_t got[32];rabbit_sha256(got,p,n);uint8_t difference=0;
 for(unsigned i=0;i<32;i++)difference|=got[i]^expected[i];
 return difference?-1:0;
}
int qca_boot_image_begin(QcaBootImage*s,const QcaBootAssets*a){
 if(!s||s->phase||!a||a->board_bytes!=8124||a->helper_bytes!=24193||a->main_bytes!=727125
  ||hash(a->board,a->board_bytes,board_hash)||hash(a->helper,a->helper_bytes,helper_hash)||hash(a->main,a->main_bytes,main_hash))return -1;
 s->assets=*a;s->phase=10;return 0;
}
int qca_boot_image_request(QcaBootImage*s,const uint8_t**request,unsigned*n,unsigned*reply){
 if(!s||!request||!n||!reply||!s->phase||s->error||s->pending||(s->phase>20&&s->phase!=22))return -1;
 if(s->phase==20)return 1;
 uint8_t*p=s->request;for(unsigned i=0;i<256;i++)p[i]=0;
 unsigned bytes=0;s->response_bytes=0;s->request_bytes=12;
 switch(s->phase){
 case 1:put(p,2);put(p+4,0x4008ac);put(p+8,4);s->response_bytes=4;break;
 case 2:put(p,2);put(p+4,0x400854);put(p+8,4);s->response_bytes=4;break;
 case 3:
  bytes=s->assets.board_bytes-s->offset;if(bytes>244)bytes=244;
  put(p,3);put(p+4,s->board_address+s->offset);put(p+8,bytes);
  for(unsigned i=0;i<bytes;i++)p[12+i]=s->assets.board[s->offset+i];
  s->request_bytes=12+bytes;break;
 case 4:
  bytes=s->assets.board_bytes-s->offset;if(bytes>244)bytes=244;
  put(p,2);put(p+4,s->board_address+s->offset);put(p+8,bytes);s->response_bytes=bytes;break;
 case 5:put(p,3);put(p+4,0x400858);put(p+8,4);put(p+12,1);s->request_bytes=16;break;
 case 6:case 8:case 16:case 18:
  put(p,13);put(p+4,s->phase==6||s->phase==16?0x1234:0);s->request_bytes=8;break;
 case 7:case 17:{
  const uint8_t*data=s->phase==7?s->assets.helper:s->assets.main;
  unsigned total=s->phase==7?s->assets.helper_bytes:s->assets.main_bytes;
  bytes=total-s->offset;if(bytes>248)bytes=248;
  unsigned padded=(bytes+3)&~3u;put(p,14);put(p+4,padded);
  for(unsigned i=0;i<bytes;i++)p[8+i]=data[s->offset+i];
  s->request_bytes=8+padded;break;
 }
 case 9:put(p,4);put(p+4,0x1234);put(p+8,0);s->response_bytes=4;break;
 case 10:put(p,2);put(p+4,0x400810);put(p+8,4);s->response_bytes=4;break;
 case 11:case 12:case 13:case 14:case 15:{
  uint32_t addr=s->phase==11?0x400810:s->phase==12?0x400800:s->phase==13?0x400844:s->phase==14?0x400904:0x4008bc;
  uint32_t value=s->phase==11?s->option_flags|0x2208:s->phase==12?2:s->phase==15?0x42:0;
  put(p,3);put(p+4,addr);put(p+8,4);put(p+12,value);s->request_bytes=16;break;
 }
 case 22:put(p,3);put(p+4,0x400814);put(p+8,4);put(p+12,0);s->request_bytes=16;break;
 case 19:put(p,1);s->request_bytes=4;break;
 default:return fail(s,1);
 }
 s->issued_phase=s->phase;s->issued_bytes=bytes;s->pending=1;s->submitted++;
 *request=p;*n=s->request_bytes;*reply=s->response_bytes;return 0;
}
int qca_boot_image_validate(const QcaBootImage*s){
 if(!s||!s->pending||s->error||s->phase<1||(s->phase>19&&s->phase!=22)||s->phase!=s->issued_phase)return -1;
 if((s->phase==3||s->phase==4)&&(!s->assets.board||s->assets.board_bytes!=8124||s->offset>=8124||s->board_address<0x400a00||s->board_address>0x410000-8124||(s->board_address&3)))return -1;
 if(s->phase==7&&(!s->assets.helper||s->assets.helper_bytes!=24193||s->offset>=24193))return -1;
 if(s->phase==17&&(!s->assets.main||s->assets.main_bytes!=727125||s->offset>=727125))return -1;
 QcaBootImage expected=*s;expected.pending=0;const uint8_t*p;unsigned n,reply;
 if(qca_boot_image_request(&expected,&p,&n,&reply)||n!=s->request_bytes||reply!=s->response_bytes||expected.issued_bytes!=s->issued_bytes)return -1;
 for(unsigned i=0;i<n;i++)if(p[i]!=s->request[i])return -1;
 return 0;
}
int qca_boot_image_complete(QcaBootImage*s,const uint8_t*p,unsigned n){
 if(!s||s->error||!s->pending||s->phase!=s->issued_phase)return -1;
 if(n!=s->response_bytes||(n&&!p))return fail(s,2);
 s->pending=0;s->completed++;
 if(s->phase==1&&word(p))return fail(s,3); /* no extended board data in exact catalog */
 if(s->phase==2){
  uint32_t addr=word(p);
  /* Deliberately narrow admitted RAM window, not a claim about chip RAM size.
   * Excludes host-interest state and all MMIO/ROM. Unexpected pointers require
   * a separately reviewed policy; never write first and diagnose afterwards. */
  if(addr<0x400a00||addr>0x410000-8124||(addr&3))return fail(s,4);
  s->board_address=addr;
 }
 if(s->phase==3||s->phase==4){
  if(s->phase==4)for(unsigned i=0;i<n;i++)if(p[i]!=s->assets.board[s->offset+i])return fail(s,5);
  s->offset+=s->issued_bytes;if(s->offset<s->assets.board_bytes)return 0;s->offset=0;
 }
 if(s->phase==7||s->phase==17){
  unsigned total=s->phase==7?s->assets.helper_bytes:s->assets.main_bytes;
  s->offset+=s->issued_bytes;if(s->offset<total)return 0;s->offset=0;
 }
 if(s->phase==9){s->calibration_result=word(p);if(s->calibration_result)return fail(s,6);}
 if(s->phase==10){s->option_flags=word(p);if(s->option_flags==UINT32_MAX)return fail(s,7);}
 if(s->phase==15)s->phase=1;
 else if(s->phase==9)s->phase=16;
 else if(s->phase==18)s->phase=22;
 else if(s->phase==22)s->phase=19;
 else s->phase++;
 return s->phase==20?1:0;
}
