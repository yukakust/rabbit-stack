#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "passive_policy.h"
static unsigned checks;
static void test(const char *ge,uint32_t reg,uint32_t lo,uint32_t hi,
                 uint32_t f,uint32_t w,int ok) {
    struct rabbit_passive_channel c, original;
    memset(&c,0x5a,sizeof c); memcpy(&original,&c,sizeof c);
    assert((rabbit_ge_world108_passive(ge,reg,lo,hi,f,w,&c)==0)==ok);
    if (!ok) assert(memcmp(&c,&original,sizeof c)==0);
    else {
        assert(c.frequency_mhz==f && c.centre1_mhz==f && c.centre2_mhz==0);
        assert(c.width_mhz==20 && c.mode==1 && c.passive==1);
        assert(c.flags==(f>=2467?2u:0u));
        assert(c.max_power_dbm==20 && c.max_reg_power_dbm==20 && !c.antenna_gain_db);
    }
    ++checks;
}
int main(void) {
    uint32_t x,f; char country[2]; struct rabbit_passive_channel c;
    for(x=0;x<=65535;++x) test("GE",108,2312,2732,x,20,x>=2412&&x<=2472&&(x-2412)%5==0);
    for(x=0;x<=65535;++x) test("GE",x,2312,2732,2412,20,x==108);
    for(x=0;x<=65535;++x) {
        country[0]=(char)(x>>8);country[1]=(char)x;
        test(country,108,2312,2732,2412,20,x==0x4745);
    }
    for(f=2412;f<=2472;f+=5) {
        for(x=0;x<=200;++x) test("GE",108,2312,2732,f,x,x==20);
        test("GE",108,f-10,f+10,f,20,1);
        test("GE",108,f-9,f+10,f,20,0);
        test("GE",108,f-10,f+9,f,20,0);
        test("GE",108,f+10,f-10,f,20,0);
    }
    test("GE",108,0,UINT32_MAX,UINT32_MAX,20,0);
    test("GE",108,UINT32_MAX,UINT32_MAX,2412,20,0);
    test("GE",108,2312,2732,2412,UINT32_MAX,0);
    test(NULL,108,2312,2732,2412,20,0);
    assert(rabbit_ge_world108_passive("GE",108,2312,2732,2412,20,NULL)==-1); ++checks;
    for(f=2412;f<=2472;f+=5) {
        assert(rabbit_ge_world108_passive("GE",108,2312,2732,f,20,&c)==0);
        printf("CHANNEL %u %u %u %u %u\n",f,c.flags,c.max_power_dbm,c.max_reg_power_dbm,c.antenna_gain_db);
    }
    printf("PASS %u offline passive metadata checks\n",checks);
    return 0;
}
