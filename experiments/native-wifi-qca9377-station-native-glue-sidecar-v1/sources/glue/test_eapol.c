#include "eapol_wire.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned checks;
#define C(x) do{checks++;if(!(x)){fprintf(stderr,"FAIL %d\n",__LINE__);exit(1);}}while(0)
int main(void){StaJoin s={0};s.epoch=9;s.associated=s.mapped=1;for(unsigned j=0;j<6;j++){s.peer[j]=2+j;s.own_mac[j]=12+j;}uint8_t p[1700]={2,3},out[1732];for(unsigned n=99;n<=1700;n++){p[2]=(n-4)>>8;p[3]=(n-4);memset(out,0xa5,sizeof out);C(qsg_eapol_frame(&s,9,p,n,123,out,sizeof out)==n+32);C(out[0]==8&&out[1]==1&&out[22]==0xb0&&out[23]==7);C(!memcmp(out+4,s.peer,6)&&!memcmp(out+10,s.own_mac,6)&&!memcmp(out+16,s.peer,6));C(!memcmp(out+24,"\xaa\xaa\x03\0\0\0\x88\x8e",8));C(!memcmp(out+32,p,n));uint8_t before[1732];memset(out,0xa5,sizeof out);memcpy(before,out,sizeof out);C(!qsg_eapol_frame(&s,9,p,n,123,out,n+31));C(!memcmp(before,out,sizeof out));}
 p[2]=0;p[3]=95;StaJoin b=s;b.ptk=1;C(!qsg_eapol_frame(&b,9,p,99,0,out,sizeof out));b=s;b.gtk=1;C(!qsg_eapol_frame(&b,9,p,99,0,out,sizeof out));b=s;b.pending=1;C(!qsg_eapol_frame(&b,9,p,99,0,out,sizeof out));b=s;b.quarantined=1;C(!qsg_eapol_frame(&b,9,p,99,0,out,sizeof out));C(!qsg_eapol_frame(&s,10,p,99,0,out,sizeof out));C(!qsg_eapol_frame(&s,9,p,99,4096,out,sizeof out));C(!qsg_eapol_frame(&s,9,p,99,0,p,sizeof p));p[3]=94;C(!qsg_eapol_frame(&s,9,p,99,0,out,sizeof out));printf("checks=%u EAPOL-pre-key-bytes-only physical=false\n",checks);return 0;}
