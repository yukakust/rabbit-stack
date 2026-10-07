extern uint8_t qca_diagnostic[888];
/* Pure framebuffer diagnostics; never a HCI/PCI reader or command source. */
static unsigned glyph(unsigned c,unsigned row){
 static const uint8_t digit[16][7]={
 {14,17,19,21,25,17,14},{4,12,4,4,4,4,14},{14,17,1,2,4,8,31},{30,1,1,14,1,1,30},
 {2,6,10,18,31,2,2},{31,16,16,30,1,1,30},{14,16,16,30,17,17,14},{31,1,2,4,8,8,8},
 {14,17,17,14,17,17,14},{14,17,17,15,1,1,14},{14,17,17,31,17,17,17},{30,17,17,30,17,17,30},
 {14,17,16,16,16,17,14},{30,17,17,17,17,17,30},{31,16,16,30,16,16,31},{31,16,16,30,16,16,16}};
 if(c>='0'&&c<='9'){return digit[c-'0'][row];}
 if(c>='A'&&c<='F'){return digit[c-'A'+10][row];}
 switch(c){
 case 'G':{const uint8_t v[7]={14,17,16,23,17,17,14};return v[row];}case 'H':return row==3?31:17;
 case 'I':return row==0||row==6?14:4;case 'L':return row==6?31:16;case 'M':return row==1?27:row==2?21:17;
 case 'N':return row==2?25:row==3?21:row==4?19:17;case 'O':return digit[0][row];
 case 'P':return row==0||row==3?30:row<3?17:16;case 'Q':return row==4?21:row==5?18:digit[0][row];
 case 'R':return row==0||row==3?30:row<3?17:row==4?20:row==5?18:17;
 case 'S':{const uint8_t v[7]={15,16,16,14,1,1,30};return v[row];}case 'T':return row==0?31:4;
 case 'U':return row==6?14:17;case 'V':return row<5?17:row==5?10:4;
 case 'W':return row==4||row==5?21:row==6?10:17;case 'X':return row==2||row==4?10:row==3?4:17;
 case '/':return row<2?1:row<4?2:row<6?4:8;default:return 0;
 }
}
static void overlay_pixel(Surface*s,unsigned x,unsigned y,uint32_t color){
 if(city_physical&&x<city_width&&y<city_height){uint32_t c=color;if(!city_format)c=((c&255)<<16)|(c&0xff00)|((c>>16)&255);city_physical[y*city_stride+x]=c;}
 if(s&&s->pixels&&x<s->width&&y<s->height)s->pixels[y*s->stride+x]=color;
}
static void overlay_text(Surface*s,unsigned y,const char*t,unsigned scale){
 for(unsigned j=0;t[j]&&j<52;j++)for(unsigned row=0;row<7;row++)for(unsigned col=0;col<5;col++){
  unsigned bit=glyph((unsigned)t[j],row)&(1u<<(4-col));
  for(unsigned a=0;a<scale;a++)for(unsigned b=0;b<scale;b++)overlay_pixel(s,8+j*6*scale+col*scale+a,y+row*scale+b,bit?0xf0f8e0:0x152025);
 }
}
static unsigned append(char*out,unsigned n,const char*label,uint32_t value){
 while(*label&&n<64){out[n++]=*label++;}
 for(unsigned i=0;i<8;i++){out[n++]="0123456789ABCDEF"[(value>>(28-4*i))&15];}
 out[n]=0;return n;
}
static void prefix_overlay(Surface*s){
 QcaPrefix*p=qca_prefix_view();if(p->frames!=UINT32_MAX)p->frames++;
 if(qca_diagnostic[4]!=15)return;
 uint8_t bytes[240];qca_prefix_status(bytes);uint32_t f[58];for(unsigned i=0;i<58;i++)f[i]=le32(bytes+8+4*i);
 unsigned scale=city_width>=960?3:2;char line[96];unsigned n=append(line,0,"FULLBOOT 60 FRAME ",p->frames);overlay_text(s,8,line,scale);
 n=append(line,0,"BOOT ",f[12]);n=append(line,n," MAIN ",f[14]);append(line,n," STOP ",f[2]);overlay_text(s,8+9*scale,line,scale);
 n=append(line,0,"OWNERS ",f[22]);append(line,n," RELEASE ",f[4]);overlay_text(s,8+18*scale,line,scale);
 n=append(line,0,"BLE ",p->ble_state);append(line,n," CMD ",p->pending);overlay_text(s,8+27*scale,line,scale);
 n=append(line,0,"USB READ ",p->usb_reads);append(line,n," WAIT ",p->usb_timeouts);overlay_text(s,8+36*scale,line,scale);
 n=append(line,0,"CE ",f[15]);n=append(line,n,"/",f[16]);append(line,n," HCI ",p->raw_count);overlay_text(s,8+45*scale,line,scale);
 n=append(line,0,"POLL MAX US ",(uint32_t)p->max_poll_us);append(line,n," FAULT ",p->usb_fault);overlay_text(s,8+54*scale,line,scale);
}

static int EFIAPI prefix_tick_frame(Surface*s){int rc=scene_tick(s);if(!rc)prefix_overlay(s);return rc;}
static int EFIAPI prefix_frame(const uint8_t*f,Surface*s){int rc=scene_frame(f,s);if(!rc)prefix_overlay(s);return rc;}
