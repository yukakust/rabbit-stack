#ifndef QCA63_QUERY_HANDOVER_H
#define QCA63_QUERY_HANDOVER_H
#include "scan_native.h"
#include "htt_native.h"
/* Structural owned-record move only; caller proves actual query completion.
 * Exactly three disjoint staging slots13..15, copy toward lower/equal slots,
 * immutable scalar response receipt, pointer authority revoked after move. */
int qca63_query_handover(QcaNativeScan*,QcaHttNative*);
#endif
