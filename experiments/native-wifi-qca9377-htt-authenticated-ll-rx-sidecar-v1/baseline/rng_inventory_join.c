#include "rng_inventory_join.h"
int qca_htt_public_rng_inventory(QcaHttRngInventory*s,const void*system,uint64_t epoch,const uint8_t code[32]){
 if(!s||!epoch||!code||s->attempted||s->session.phase||s->session.pool||s->session.pool_uncertain)return 0;
 s->attempted=1;s->epoch=epoch;s->entropy_approved=0;RngBootApi boot={0};
 if(!protected_boot_api(system,&boot)){s->error=1;return 0;}
 int rc=protected_rng_inventory(&s->session,&boot,epoch,code,&s->diagnostic);
 if(!rc)s->error=2;
 return rc;
}
int qca_htt_public_rng_cleanup(QcaHttRngInventory*s){if(!s)return 0;if(!s->attempted)return 1;if(s->session.pool&&!rng_cleanup(&s->session))return 0;return !s->session.pool&&!s->session.pool_uncertain;}
int qca_htt_public_rng_released(const QcaHttRngInventory*s){return s&&!s->session.pool&&!s->session.pool_uncertain&&!s->entropy_approved;}
