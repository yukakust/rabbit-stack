#include "query_handover.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static QcaNativeScan scan,before;static QcaHttNative query,qbefore;static QcaPersistentNative radio;
static void setup(unsigned count,unsigned extras,unsigned response){
 memset(&scan,0,sizeof(scan));memset(&query,0,sizeof(query));memset(&radio,0,sizeof(radio));
 radio.epoch=31;scan.radio=query.radio=&radio;scan.epoch=query.epoch=31;
 scan.archive_count=count;query.archive_count=extras;query.response=&scan.archive[13];query.archive=&scan.archive[14];
 for(unsigned i=0;i<count;i++){scan.archive[i].completion=i+1;scan.archive[i].raw_bytes=12;scan.archive[i].bytes=4;scan.archive[i].pipe=2;scan.archive[i].raw[8]=(uint8_t)i;}
 for(unsigned i=0;i<3;i++){QcaRxEvent*e=&scan.archive[13+i];if((i==0&&!response)||(i>0&&i>extras))continue;e->completion=100+i;e->raw_bytes=16;e->bytes=0;e->pipe=1;e->endpoint=2;e->raw[1]=2;e->raw[8]=(uint8_t)(200+i);}
 query.response_completion=response?100:0;
}
int main(void){unsigned checks=0;
 for(unsigned count=0;count<=13;count++)for(unsigned extras=0;extras<=2;extras++)for(unsigned response=0;response<=1;response++){
  setup(count,extras,response);QcaRxEvent original[3];memcpy(original,&scan.archive[13],sizeof(original));
  assert(qca63_query_handover(&scan,&query));assert(scan.archive_count==count+extras+response&&!query.response&&!query.archive);
  unsigned at=count;if(response)assert(!memcmp(&scan.archive[at++],&original[0],sizeof(QcaRxEvent)));
  for(unsigned i=0;i<extras;i++)assert(!memcmp(&scan.archive[at++],&original[i+1],sizeof(QcaRxEvent)));
  memset(&scan.archive[13],0xa5,3*sizeof(QcaRxEvent));assert(query.response_completion==(response?100u:0u));assert(!qca63_query_handover(&scan,&query));checks++;
 }
 for(unsigned kind=0;kind<8;kind++){
  setup(13,2,1);
  if(kind==0)query.epoch++;
  if(kind==1)radio.epoch++;
  if(kind==2)scan.archive_count=14;
  if(kind==3)scan.archive[14].completion=100;
  if(kind==4)scan.archive[0].completion=100;
  if(kind==5)scan.archive[15].bytes=9;
  if(kind==6)query.response_completion=99;
  if(kind==7)query.response=&scan.archive[12];
  before=scan;qbefore=query;assert(!qca63_query_handover(&scan,&query));assert(!memcmp(&scan,&before,sizeof(scan))&&!memcmp(&query,&qbefore,sizeof(query)));checks++;
 }
 printf("ACTUAL63_HANDOVER %u combinations/negative checks PASS; synthetic only\n",checks);
}
