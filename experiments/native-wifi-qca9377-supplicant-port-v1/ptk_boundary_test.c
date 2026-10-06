/* Synthetic-only test of exact build-extracted upstream install function.
 * This harness does not implement a handshake or communicate with a driver. */
#include <assert.h>
#include "utils/includes.h"
#include "utils/common.h"
#include "common/wpa_common.h"
#include "common/ieee802_11_defs.h"
#include "drivers/driver.h"
#include "rsn_supp/wpa.h"
#include "utils/eloop.h"
#include "rsn_supp/wpa_i.h"

static unsigned installs, cases;
static int install_result;
static void wpa_sm_rekey_ptk(void *a, void *b) {
    (void)a; (void)b; assert(!"test must not enter rekey callback");
}
int eloop_cancel_timeout(eloop_timeout_handler h, void *a, void *b) {
    (void)h; (void)a; (void)b; assert(!"timers are outside this test"); return -1;
}
int eloop_register_timeout(unsigned s, unsigned us, eloop_timeout_handler h,
                           void *a, void *b) {
    (void)s; (void)us; (void)h; (void)a; (void)b;
    assert(!"timers are outside this test"); return -1;
}
static int install(void *ctx, int link_id, enum wpa_alg alg,
                   const u8 *addr, int idx, int tx, const u8 *seq,
                   size_t seq_len, const u8 *key, size_t key_len,
                   enum key_flag flags) {
    unsigned i; (void)ctx;
    assert(link_id==-1 && alg==WPA_ALG_CCMP && idx==0 && tx==1);
    assert(addr[0]==2 && key_len==16 && seq_len==6);
    assert(flags==(KEY_FLAG_PAIRWISE|KEY_FLAG_RX_TX));
    for(i=0;i<6;++i) assert(seq[i]==0);
    for(i=0;i<16;++i) assert(key[i]==(u8)(0xa0+i));
    ++installs; return install_result;
}
/* Includes exact unedited upstream function bytes extracted by verifier. */
#include "upstream_install.inc"
static void reset(struct wpa_sm *sm, struct wpa_sm_ctx *ctx) {
    unsigned i;
    memset(sm,0,sizeof *sm); memset(ctx,0,sizeof *ctx);
    ctx->set_key=install; sm->ctx=ctx; sm->proto=WPA_PROTO_RSN;
    sm->pairwise_cipher=WPA_CIPHER_CCMP; sm->bssid[0]=2;
    sm->ptk.tk_len=16;
    for(i=0;i<16;++i) sm->ptk.tk[i]=(u8)(0xa0+i);
    installs=0; install_result=0;
}
int main(void) {
    struct wpa_sm sm; struct wpa_sm_ctx ctx; struct wpa_eapol_key key;
    unsigned i;
    memset(&key,0,sizeof key);
    reset(&sm,&ctx);
    assert(wpa_supplicant_install_ptk(&sm,&key,KEY_FLAG_RX_TX)==0);
    assert(installs==1 && sm.ptk.installed==1 && sm.tk_set && !sm.ptk.tk_len);
    for(i=0;i<WPA_TK_MAX_LEN;++i) assert(sm.ptk.tk[i]==0);
    ++cases;
    for(i=0;i<1000;++i) {
        assert(wpa_supplicant_install_ptk(&sm,&key,KEY_FLAG_RX_TX)==0);
        assert(installs==1 && sm.ptk.installed==1); ++cases;
    }
    reset(&sm,&ctx); install_result=-1;
    assert(wpa_supplicant_install_ptk(&sm,&key,KEY_FLAG_RX_TX)==-1);
    assert(installs==1 && !sm.ptk.installed && !sm.tk_set && sm.ptk.tk_len==16);
    for(i=0;i<16;++i) assert(sm.ptk.tk[i]==(u8)(0xa0+i)); ++cases;
    install_result=0;
    assert(wpa_supplicant_install_ptk(&sm,&key,KEY_FLAG_RX_TX)==0);
    assert(installs==2 && sm.ptk.installed); ++cases;
    for(i=0;i<=32;++i) {
        reset(&sm,&ctx); sm.ptk.tk_len=i;
        assert((wpa_supplicant_install_ptk(&sm,&key,KEY_FLAG_RX_TX)==0)==(i==16));
        assert(installs==(i==16)); ++cases;
    }
    reset(&sm,&ctx); sm.pairwise_cipher=WPA_CIPHER_NONE;
    assert(wpa_supplicant_install_ptk(&sm,&key,KEY_FLAG_RX_TX)==0);
    assert(!installs && !sm.ptk.installed); ++cases;
    reset(&sm,&ctx); sm.pairwise_cipher=0;
    assert(wpa_supplicant_install_ptk(&sm,&key,KEY_FLAG_RX_TX)==-1);
    assert(!installs && !sm.ptk.installed); ++cases;
    puts("PASS 1038 actual-upstream PTK install boundary cases");
    assert(cases==1038); return 0;
}
