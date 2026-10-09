#ifndef QCA_SEPARATE_LIFECYCLE47_H
#define QCA_SEPARATE_LIFECYCLE47_H
#include "lifecycle.h"
/* New47 policy uses existing owner ABI, populated by exact measured inventory. */
int qca_radio47_begin(QcaRadioLifecycle*,const QcaRadioOwners*,uint64_t);
/* Every command must refresh owners first, then consult accepts_work.
 * Failure while active permanently retains ownership until explicit recovery.
 * Malformed/stale observations fail closed to RETAINED, preserving the last
 * owner counts but revoking command and release admission.
 */
int qca_radio47_observe(QcaRadioLifecycle*,const QcaRadioOwners*,uint64_t);
int qca_radio47_accepts_work(const QcaRadioLifecycle*);
/* Caller must authenticate authorization BEFORE calling this local API.
 * Stops new command admission immediately. Deadline is in caller's monotonic
 * units (microseconds in current adapter), no sleeps inside this module.
 */
int qca_radio47_quiesce(QcaRadioLifecycle*,uint64_t,uint64_t);
/* True only after current stop proof; tells caller release MAY be attempted,
 * never that it succeeded. Release failure/timeout cannot grant unload.
 */
int qca_radio47_can_release(const QcaRadioLifecycle*);
int qca_radio47_can_unload(const QcaRadioLifecycle*);
#endif
