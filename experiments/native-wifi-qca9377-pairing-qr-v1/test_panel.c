#include "panel.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define C(x) do{checks++;if(!(x)){fprintf(stderr,"line%d %s\n",__LINE__,#x);exit(1);}}while(0)
static unsigned checks;
static PairingPanel p;
static uint32_t pixels[480*270];
int main(void){
 uint8_t pin[32];for(unsigned i=0;i<32;i++)pin[i]=(uint8_t)i;
 C(!qr_panel_bind(&p,65,pin,1));C(!strcmp(p.text,"RABBIT1:65:000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F"));C(qr_panel_live(&p,65,600000000));C(!qr_panel_live(&p,65,600000001));C(!qr_panel_live(&p,64,1));C(!qr_panel_live(&p,65,0));C(qr_panel_bind(&p,65,pin,1)<0);
 for(unsigned i=0;i<480*270;i++)pixels[i]=0x123456;
 C(!qr_panel_paint(&p,65,1,pixels,sizeof pixels,480,270,480,300,0,4));unsigned side=(p.size+8)*4;
 for(unsigned y=0;y<270;y++)for(unsigned x=0;x<480;x++){uint32_t v=pixels[y*480+x];if(x>=300&&x<300+side&&y<side)C(v==0||v==0xffffff);else C(v==0x123456);}
 C(qr_panel_paint(&p,65,1,pixels,sizeof pixels,480,270,480,479,0,4)<0);C(qr_panel_paint(&p,65,1,pixels,40,480,270,480,0,0,4)<0);C(qr_panel_paint(&p,65,1,(uint32_t*)&p,sizeof p,10,10,10,0,0,1)<0);C(qr_panel_paint(&p,65,1,pixels,sizeof pixels,480,270,479,0,0,4)<0);C(qr_panel_paint(&p,65,1,pixels,sizeof pixels,480,270,480,0,0,17)<0);
 printf("QR_TEXT %s\nQR_SIZE %u\n",p.text,p.size);for(unsigned y=0;y<p.size;y++){for(unsigned x=0;x<p.size;x++)putchar(qrcodegen_getModule(p.symbol,x,y)?'1':'0');putchar('\n');}
 qr_panel_clear(&p);C(!qr_panel_live(&p,65,1));memset(pin,0,32);C(qr_panel_bind(&p,65,pin,1)<0);pin[0]=1;C(qr_panel_bind(&p,65,(uint8_t*)&p,1)<0);C(qr_panel_bind(&p,65,pin,UINT64_MAX)<0);C(!qr_panel_bind(&p,UINT64_MAX,pin,1));C(strlen(p.text)==93);qr_panel_clear(&p);
 printf("PUBLIC-QR-PANEL %u assertions; identity/physical pairing authority=0\n",checks);return 0;
}
