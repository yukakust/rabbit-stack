#include "bt_event_stream.h"
int rabbit_bt_events(RabbitBtEventStream*s,const uint8_t*p,unsigned n,RabbitBtEventReceive receive,void*context){
 if(!s||(!p&&n)||!receive||n>260||s->used>256)return -1;
 if(s->used<2){if(s->goal)return -1;}
 else if(s->goal!=2u+s->bytes[1]||s->goal>257||s->used>=s->goal)return -1;
 for(unsigned i=0;i<n;i++){
  s->bytes[s->used++]=p[i];
  if(s->used==2)s->goal=2u+s->bytes[1];
  if(s->goal&&s->used==s->goal){
   receive(context,s->bytes,s->goal);s->used=s->goal=0;
  }
 }
 return 0;
}
