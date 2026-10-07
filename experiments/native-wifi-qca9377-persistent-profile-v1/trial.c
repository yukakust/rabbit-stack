#include "trial.h"
int qca_trial_tick(QcaBoundedTrial*s,unsigned active,unsigned released,uint64_t now){
 if(!s||active>1||released>1)return 0;
 if(!s->phase){
  if(!active)return 0;
  s->started=s->last=now;s->phase=QCA_TRIAL_RUNNING;
  if(now>UINT64_MAX-10000000){s->error=2;s->phase=QCA_TRIAL_FAULT;s->stop_requested=1;return 1;}
  return 0;
 }
 if(released){s->released=1;if(!s->error&&s->stop_requested)s->phase=QCA_TRIAL_DONE;return 0;}
 if(s->stop_requested)return 0;
 if(now<s->last){s->error=1;s->phase=QCA_TRIAL_FAULT;}
 else if(!active){s->error=3;s->phase=QCA_TRIAL_FAULT;}
 else if(now-s->started>=10000000){s->expired=1;s->phase=QCA_TRIAL_STOPPING;}
 else {s->last=now;return 0;}
 s->last=now;s->stop_requested=1;return 1;
}
