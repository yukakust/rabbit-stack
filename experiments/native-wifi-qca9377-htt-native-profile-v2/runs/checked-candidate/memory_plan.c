#include "memory_plan.h"
int qca_wmi_memory_plan(const QcaWmiServiceInfo*info,const QcaWmiResources*r,QcaWmiMemoryPlan*out){
 if(!info||!r||!out||info->memory_count>16||!r->vdevs||r->vdevs>16||!r->peers||r->peers>2048||r->active_peers>r->peers||!r->budget_bytes||r->budget_bytes>16u*1024*1024)return -1;
 QcaWmiMemoryPlan p={0};
 for(unsigned i=0;i<info->memory_count;i++){
  const QcaWmiMemoryRequest*q=&info->memory[i];
  if(!q->unit_size||q->unit_size>0xfffffffcu||(q->unit_flags&~7u))return -1;
  for(unsigned j=0;j<i;j++)if(p.item[j].id==q->id)return -1;
  uint32_t units=q->units,stride=(q->unit_size+3u)&~3u;
  /* Pinned Linux priority and extra self unit; zero active peers falls back
   * to the configured peer count. Unknown flags are never ignored. */
  if(q->unit_flags&4)units=(r->active_peers?r->active_peers:r->peers)+1;
  else if(q->unit_flags&2)units=r->peers+1;
  else if(q->unit_flags&1)units=r->vdevs+1;
  if(!units)return -1;
  uint64_t bytes=(uint64_t)stride*units;
  if(bytes>r->budget_bytes-p.total_bytes)return -1;
  p.item[i]=(QcaWmiMemoryItem){q->id,stride,units,(uint32_t)bytes};
  p.total_bytes+=(uint32_t)bytes;p.count++;
 }
 *out=p;return 0;
}
