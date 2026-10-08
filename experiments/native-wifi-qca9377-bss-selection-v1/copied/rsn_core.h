#ifndef RABBIT_PINNED_RSN_CORE_H
#define RABBIT_PINNED_RSN_CORE_H
#include <stdint.h>
typedef struct {uint32_t proto,group,pairwise,akm,capabilities,pmkids,management_group;unsigned has_group,has_pairwise;} QcaRsnFields;
/* Exact bounded framing/parser reuse from pinned hostap2.11, not supplicant.
 * No crypto, credentials, pointer export, allocation, RF or authentication. */
int qca_pinned_rsn(const uint8_t*,unsigned,QcaRsnFields*);
#endif
