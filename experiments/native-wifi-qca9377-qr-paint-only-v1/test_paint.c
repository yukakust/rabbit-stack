#include "paint.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned checks;
#define C(x) do{checks++;if(!(x)){fprintf(stderr,"line%d %s\n",__LINE__,#x);exit(1);}}while(0)
static uint32_t a[480*270],b[480*270];
int main(void){
 PairingPanel p={0};uint8_t pin[32];for(unsigned i=0;i<32;i++)pin[i]=(uint8_t)i;
 for(unsigned trial=0;trial<6;trial++){
 uint64_t epoch=trial==5?UINT64_MAX:1+trial*123456;C(!qr_panel_bind(&p,epoch,pin,1));C(qp_live(&p,epoch,600000000));C(!qp_live(&p,epoch,600000001));C(!qp_live(&p,epoch,0));C(!qp_live(&p,epoch-1,1));
 for(unsigned i=0;i<480*270;i++)a[i]=b[i]=0x123456;
 C(!qr_panel_paint(&p,epoch,1,a,sizeof a,480,270,480,270,0,4));C(!qp_paint(&p,epoch,1,b,sizeof b,480,270,480,270,0,4));for(unsigned i=0;i<480*270;i++)C(a[i]==b[i]);
 PairingPanel v=p;v.size=22;C(!qp_live(&v,epoch,1));v=p;v.symbol[0]=21;C(!qp_live(&v,epoch,1));v=p;v.text[15]^=1;C(!qp_live(&v,epoch,1));v=p;v.spki_sha256[31]^=1;C(!qp_live(&v,epoch,1));v=p;v.expires++;C(!qp_live(&v,epoch,1));v=p;v.expires=101;C(qp_live(&v,epoch,100));C(!qp_live(&v,epoch,101));v.expires=v.created;C(!qp_live(&v,epoch,1));
 C(qp_paint(&p,epoch,1,b,40,480,270,480,0,0,4)<0);C(qp_paint(&p,epoch,1,b,sizeof b,480,270,479,0,0,4)<0);C(qp_paint(&p,epoch,1,b,sizeof b,480,270,480,479,0,4)<0);C(qp_paint(&p,epoch,1,(uint32_t*)&p,sizeof p,10,10,10,0,0,1)<0);C(qp_paint(&p,epoch,1,b,sizeof b,480,270,480,0,0,17)<0);
 qr_panel_clear(&p);
 }
 C(!qp_live(0,1,1));C(!qp_live((PairingPanel*)((unsigned char*)&p+1),1,1));printf("QR-PAINT-ONLY %u assertions; six genuine generator bit-identical public frames; identity authority=0\n",checks);return 0;
}
