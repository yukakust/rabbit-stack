#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "eapol_frame.h"
/* Independent offsets and sizes come from the downloaded upstream header. */
#include "utils/includes.h"
#include "utils/common.h"
#include "common/wpa_common.h"
#include "common/eapol_common.h"
static unsigned checks;
static uint8_t packet[RABBIT_EAPOL_MAX_BYTES + 1];
static void put16(uint8_t *p, unsigned x) { p[0]=(uint8_t)(x>>8); p[1]=(uint8_t)x; }
static void fixture(size_t n) {
    memset(packet, 0, sizeof packet);
    packet[0]=2; packet[1]=3; packet[4]=2;
    put16(packet+2, (unsigned)n-4); put16(packet+5, 2);
    put16(packet+97, (unsigned)n-99);
}
static void test(size_t n, int expected) {
    struct rabbit_eapol_view v, original;
    memset(&v, 0x5a, sizeof v); memcpy(&original, &v, sizeof v);
    assert((rabbit_eapol_key_frame(packet, n, &v)==0)==expected);
    if (!expected) assert(memcmp(&v,&original,sizeof v)==0);
    else {
        assert(v.nonce==packet+4+offsetof(struct wpa_eapol_key,key_nonce));
        assert(v.mic==packet+4+sizeof(struct wpa_eapol_key));
        assert(v.key_data==packet+4+sizeof(struct wpa_eapol_key)+16+2);
        assert(v.key_data_length==n-99);
    }
    ++checks;
}
int main(void) {
    size_t n; unsigned x; struct rabbit_eapol_view v;
    assert(sizeof(struct wpa_eapol_key)==77);
    assert(sizeof(struct ieee802_1x_hdr)==4);
    assert(offsetof(struct ieee802_1x_hdr,length)==2);
    assert(offsetof(struct wpa_eapol_key,key_info)==1);
    assert(offsetof(struct wpa_eapol_key,replay_counter)==5);
    for(n=0;n<99;++n) { fixture(99); test(n,0); }
    for(n=99;n<=RABBIT_EAPOL_MAX_BYTES;++n) { fixture(n); test(n,1); }
    fixture(RABBIT_EAPOL_MAX_BYTES+1); test(RABBIT_EAPOL_MAX_BYTES+1,0);
    for(x=0;x<=65535;++x) {
        fixture(123); put16(packet+2,x); test(123,x==119);
        fixture(123); put16(packet+97,x); test(123,x==24);
    }
    for(x=0;x<=255;++x) {
        fixture(99); packet[0]=(uint8_t)x; test(99,x>=1&&x<=3);
        fixture(99); packet[1]=(uint8_t)x; test(99,x==3);
        fixture(99); packet[4]=(uint8_t)x; test(99,x==2);
    }
    for(x=0;x<=65535;++x) {
        fixture(99); put16(packet+5,x); test(99,(x&7)==2);
    }
    fixture(99);
    for(x=0;x<8;++x) packet[9+x]=(uint8_t)(x+1);
    assert(rabbit_eapol_key_frame(packet,99,&v)==0);
    assert(v.replay_counter==UINT64_C(0x0102030405060708)); ++checks;
    assert(rabbit_eapol_key_frame(NULL,99,&v)==-1); ++checks;
    assert(rabbit_eapol_key_frame(packet,99,NULL)==-1); ++checks;
    printf("PASS %u framing checks; upstream wpa_eapol_key size/offset oracle\n", checks);
    return 0;
}
