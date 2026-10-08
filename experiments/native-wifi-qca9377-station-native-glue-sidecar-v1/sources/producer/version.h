#ifndef QCA_HTT_VERSION_H
#define QCA_HTT_VERSION_H
#include "htc_session.h"
typedef struct {uint16_t max_bytes;uint8_t endpoint,op_version;} QcaHttBinding;
typedef struct {uint8_t major,minor;} QcaHttVersion;
/* Logical metadata only; native caller must prove radio epoch/maps/pipe guards. */
int qca_htt_version_bind(const QcaHtcSession*,unsigned,QcaHttBinding*);
unsigned qca_htt_version_request(const QcaHttBinding*,uint8_t*,unsigned);
int qca_htt_version_conf(const QcaHttBinding*,const uint8_t*,unsigned,QcaHttVersion*);
#endif
