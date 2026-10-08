#include "query_handover.h"
static int record(const QcaRxEvent*e){return e->completion&&e->raw_bytes>=8&&e->raw_bytes<=2048&&e->bytes<=e->raw_bytes-8&&e->endpoint<=7&&(e->pipe==1||e->pipe==2);}
int qca63_query_handover(QcaNativeScan*s,QcaHttNative*q){
 if(!s||!q||!s->radio||q->radio!=s->radio||!s->epoch||q->epoch!=s->epoch||s->radio->epoch!=s->epoch||s->archive_count>13||q->archive_count>2||q->response!=&s->archive[13]||q->archive!=&s->archive[14])return 0;
 const QcaRxEvent*events[3];unsigned n=0;
 if(q->response_completion){if(q->response->completion!=q->response_completion)return 0;events[n++]=q->response;}
 else if(q->response->completion)return 0;
 for(unsigned i=0;i<q->archive_count;i++)events[n++]=&q->archive[i];
 for(unsigned i=0;i<n;i++){
  if(!record(events[i]))return 0;
  for(unsigned j=0;j<s->archive_count;j++)if(s->archive[j].completion==events[i]->completion)return 0;
  for(unsigned j=0;j<i;j++)if(events[j]->completion==events[i]->completion)return 0;
 }
 /* Sources are13,14,15 (or14,15); destination never exceeds source.
  * Earlier writes therefore cannot change a later unread source. */
 for(unsigned i=0;i<n;i++)s->archive[s->archive_count++]=*events[i];
 q->response=0;q->archive=0;return 1;
}
