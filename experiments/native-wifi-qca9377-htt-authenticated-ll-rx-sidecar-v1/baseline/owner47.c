#include "owner47.h"
int qca_htt_owner47_snapshot(const QcaHttRuntime*s,const QcaRadioOwners*b,QcaRadioOwners*out){
 if(!s||!b||!out||!s->port||!s->ce||!s->epoch||b->epoch!=s->epoch||s->allocated>33||b->dma_users!=s->port->dma_users)return 0;
 unsigned ce=0,total=0,allocated=0;
 for(unsigned i=0;i<14+s->allocated;i++){
  const QcaDmaBuffer*d=i<14?&s->ce[i]:&s->extra[i-14];
  if(d->port&&d->port!=s->port)return 0;
  if(d->allocated)allocated++;
  if(d->allocated||d->mapped||d->allocation_uncertain){total++;if(i<14)ce++;}
 }
 if(b->mappings!=ce||allocated!=s->port->dma_users||total>47||(total&&!s->port->claimed))return 0;
 QcaRadioOwners next=*b;next.mappings=total;next.dma_users=s->port->dma_users;*out=next;return 1;
}
