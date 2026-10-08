#include "trusted_utc.h"
#include "mbedtls/platform.h"
#include "mbedtls/platform_util.h"
#include <string.h>
static struct {uint64_t epoch,base_ms,last_ms;int64_t utc;unsigned bound;} clock_state;
static mbedtls_time_t approved_time(mbedtls_time_t*out){
 mbedtls_time_t t=(mbedtls_time_t)-1;
 if(clock_state.bound)t=(mbedtls_time_t)(clock_state.utc+(int64_t)((clock_state.last_ms-clock_state.base_ms)/1000));
 if(out)*out=t;return t;
}
mbedtls_ms_time_t mbedtls_ms_time(void){return clock_state.bound&&clock_state.last_ms<=INT64_MAX?(mbedtls_ms_time_t)clock_state.last_ms:-1;}
void wan_utc_revoke(void){volatile unsigned char*p=(void*)&clock_state;for(unsigned i=0;i<sizeof clock_state;i++)p[i]=0;}
int wan_utc_bind(uint64_t epoch,int64_t utc,uint64_t ms){
 if(clock_state.bound||!epoch||utc<1577836800LL||utc>=4102444800LL)return -1;
 if(mbedtls_platform_set_time(approved_time))return -1;
 clock_state.epoch=epoch;clock_state.utc=utc;clock_state.base_ms=clock_state.last_ms=ms;clock_state.bound=1;return 0;
}
int wan_utc_advance(uint64_t epoch,uint64_t ms){
 if(!clock_state.bound||clock_state.epoch!=epoch||ms<clock_state.last_ms||ms-clock_state.base_ms>600000){wan_utc_revoke();return -1;}
 clock_state.last_ms=ms;return 0;
}
int wan_utc_current(uint64_t epoch){return clock_state.bound&&clock_state.epoch==epoch;}
static int leap(int y){return !(y%4)&&((y%100)||!(y%400));}
struct tm*mbedtls_platform_gmtime_r(const mbedtls_time_t*input,struct tm*out){
 if(!input||!out||*input<0||*input>=4102444800LL)return 0;
 int64_t seconds=*input,days=seconds/86400;int y=1970;memset(out,0,sizeof *out);
 out->tm_sec=(int)(seconds%60);out->tm_min=(int)((seconds/60)%60);out->tm_hour=(int)((seconds/3600)%24);out->tm_wday=(int)((days+4)%7);
 while(days>=365+leap(y)){days-=365+leap(y);y++;}
 out->tm_year=y-1900;out->tm_yday=(int)days;static const int months[]={31,28,31,30,31,30,31,31,30,31,30,31};int m=0;
 while(m<11&&days>=months[m]+(m==1&&leap(y))){days-=months[m]+(m==1&&leap(y));m++;}
 out->tm_mon=m;out->tm_mday=(int)days+1;out->tm_isdst=0;return out;
}
