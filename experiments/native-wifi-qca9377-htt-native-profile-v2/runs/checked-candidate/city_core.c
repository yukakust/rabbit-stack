/* Portable bounded fixed-point 3D rasterizer. No board/UEFI addresses or LLM code. */
#include "city_core.h"
#include "monocypher-ed25519.h"
static const uint8_t city_creator[32]={3,161,7,191,243,206,16,190,29,112,221,24,231,75,192,153,103,228,214,48,155,165,13,95,29,220,134,100,18,85,49,184};
static const int16_t sine[65]={0,25,50,75,100,125,150,175,200,224,249,273,297,321,345,369,392,415,438,460,483,505,526,548,569,590,610,630,650,669,688,706,724,742,759,775,792,807,822,837,851,865,878,891,903,915,926,936,946,955,964,972,980,987,993,999,1004,1009,1013,1016,1019,1021,1023,1024,1024};
static uint32_t depth[CITY_W*CITY_H];
static uint16_t u16(const uint8_t*p){return p[0]|((uint16_t)p[1]<<8);}
static uint32_t u32(const uint8_t*p){return u16(p)|((uint32_t)u16(p+2)<<16);}
static int32_t i16(const uint8_t*p){return (int16_t)u16(p);}
static int32_t abs_i(int32_t x){return x<0?-x:x;}
int city_decode(const uint8_t*p,uint32_t n,uint32_t minimum,City*out){
 if(!p||!out||n<96||n>6816||p[0]!='R'||p[1]!='U'||p[2]!='P'||(p[4]!=4&&p[4]!=5)||p[3]!=(p[4]==4?'4':'5')||p[5]||u16(p+6)!=n||u32(p+8)<=minimum)return 1;
 uint8_t count=p[12];
 if(!count||count>CITY_MAX||(p[4]==4&&p[13])||p[13]>4||u16(p+14)!=32||n<96u+count*32u||(p[4]==4&&n!=96u+count*32u)||p[23])return 1;
 if(abs_i(i16(p+16))>20000||u16(p+18)<50||u16(p+18)>3000||abs_i(i16(p+20))>20000||(u32(p+24)|u32(p+28))>0xffffff)return 1;
 if(crypto_ed25519_check(p+n-64,city_creator,p,n-64))return 1;
 for(unsigned i=0;i<count;i++){
  const uint8_t*q=p+32+i*32;CityBuilding*b=&out->buildings[i];
  if(!u16(q)||q[2]<1||q[2]>3||q[3]||abs_i(i16(q+4))>20000||i16(q+6)<0||i16(q+6)>3000||abs_i(i16(q+8))>20000||
    !u16(q+10)||u16(q+10)>3000||!u16(q+12)||u16(q+12)>3000||!u16(q+14)||u16(q+14)>3000||(u32(q+16)|u32(q+20))>0xffffff||u32(q+24)||u32(q+28))return 1;
  for(unsigned j=0;j<i;j++)if(out->buildings[j].id==u16(q))return 1;
  b->id=u16(q);b->kind=q[2];b->position=(CityVec){i16(q+4),i16(q+6),i16(q+8)};b->w=u16(q+10);b->h=u16(q+12);b->d=u16(q+14);b->wall=u32(q+16);b->roof=u32(q+20);
 }
 out->actor_count=p[13];out->part_count=0;uint32_t offset=32u+count*32u;
 for(unsigned i=0;i<out->actor_count;i++){
  if(offset+16>n-64)return 1;
  const uint8_t*q=p+offset;CityActor*a=&out->actors[i];
  if(!u16(q)||!q[3]||q[3]>48||out->part_count+q[3]>96||abs_i(i16(q+4))>20000||u16(q+6)>7000||abs_i(i16(q+8))>20000)return 1;
  for(unsigned k=10;k<16;k++)if(q[k])return 1;
  for(unsigned k=0;k<i;k++)if(out->actors[k].id==u16(q))return 1;
  a->id=u16(q);a->yaw=q[2];a->count=q[3];a->start=out->part_count;a->position=(CityVec){i16(q+4),u16(q+6),i16(q+8)};offset+=16;
  for(unsigned j=0;j<a->count;j++){
   if(offset+48>n-64)return 1;
   q=p+offset;CityPart*b=&out->parts[out->part_count++];
   if(q[0]<1||q[0]>3||q[1]>2||u16(q+2)||abs_i(i16(q+4))>1000||abs_i(i16(q+6))>1000||abs_i(i16(q+8))>1000||
      !u16(q+10)||u16(q+10)>1000||!u16(q+12)||u16(q+12)>1000||!u16(q+14)||u16(q+14)>1000||u32(q+16)>0xffffff||
      abs_i(i16(q+20))>500||abs_i(i16(q+22))>500||abs_i(i16(q+24))>500||u16(q+26)<100||u16(q+26)>60000||u16(q+28)>=u16(q+26)||
      u16(q+30)<100||u16(q+30)>60000||!u16(q+32)||u16(q+32)>u16(q+30)||u16(q+34)>60000)return 1;
   for(unsigned k=36;k<48;k++)if(q[k])return 1;
   b->shape=q[0];b->visibility=q[1];b->position=(CityVec){i16(q+4),i16(q+6),i16(q+8)};b->w=u16(q+10);b->h=u16(q+12);b->d=u16(q+14);b->color=u32(q+16);
   b->motion=(CityVec){i16(q+20),i16(q+22),i16(q+24)};b->period=u16(q+26);b->phase=u16(q+28);b->visible_period=u16(q+30);b->duration=u16(q+32);b->delay=u16(q+34);offset+=48;
  }
 }
 if(offset!=n-64)return 1;
 out->count=count;out->counter=u32(p+8);out->camera=(CityVec){i16(p+16),u16(p+18),i16(p+20)};out->yaw=p[22];out->sky=u32(p+24);out->ground=u32(p+28);return 0;
}
static int32_t sin_i(unsigned a){a&=255;
 if(a<=64)return sine[a];
 if(a<=128)return sine[128-a];
 if(a<=192)return -sine[a-128];
 return -sine[256-a];}
static uint32_t shade(uint32_t c,unsigned amount){uint32_t out=0;for(unsigned shift=0;shift<24;shift+=8)out|=(((c>>shift)&255)*amount/255)<<shift;return out;}
typedef struct {int32_t x,y;uint32_t inverse;} Projected;
static CityVec camera_space(const City*c,CityVec v){
 int32_t x=v.x-c->camera.x,z=v.z-c->camera.z,si=sin_i(c->yaw),co=sin_i(c->yaw+64);
 return (CityVec){(x*co-z*si)/1024,v.y-c->camera.y,(x*si+z*co)/1024};
}
static int project(CityVec v,Projected*out){
 if(v.z<50)return 1;
 int32_t px=400+(int32_t)((int64_t)v.x*500/v.z),py=167-(int32_t)((int64_t)v.y*500/v.z);
 if(px<-1000000||px>1000000||py<-1000000||py>1000000)return 1;
 out->x=px;out->y=py;out->inverse=0x1000000u/(uint32_t)v.z;return 0;
}
static CityVec intersection(CityVec a,CityVec b){
 int64_t t=50-a.z,den=b.z-a.z;
 return (CityVec){a.x+(int32_t)((int64_t)(b.x-a.x)*t/den),a.y+(int32_t)((int64_t)(b.y-a.y)*t/den),50};
}
static int64_t edge(Projected a,Projected b,int x,int y){return (int64_t)(x-a.x)*(b.y-a.y)-(int64_t)(y-a.y)*(b.x-a.x);}
static void raster(uint32_t*pixels,CityVec a,CityVec b,CityVec d,uint32_t color){
 Projected p,q,r;
 if(project(a,&p)||project(b,&q)||project(d,&r))return;
 int64_t area=edge(p,q,r.x,r.y);
 if(!area)return;
 if(area<0){Projected t=q;q=r;r=t;area=-area;}
 int minx=p.x,maxx=p.x,miny=p.y,maxy=p.y;
 if(q.x<minx)minx=q.x;
 if(r.x<minx)minx=r.x;
 if(q.x>maxx)maxx=q.x;
 if(r.x>maxx)maxx=r.x;
 if(q.y<miny)miny=q.y;
 if(r.y<miny)miny=r.y;
 if(q.y>maxy)maxy=q.y;
 if(r.y>maxy)maxy=r.y;
 if(minx<0)minx=0;
 if(miny<0)miny=0;
 if(maxx>=CITY_W)maxx=CITY_W-1;
 if(maxy>=CITY_H)maxy=CITY_H-1;
 for(int y=miny;y<=maxy;y++)for(int x=minx;x<=maxx;x++){
  int64_t w0=edge(q,r,x,y),w1=edge(r,p,x,y),w2=edge(p,q,x,y);
 if(w0<0||w1<0||w2<0)continue;
  uint32_t inverse=(uint32_t)((w0*p.inverse+w1*q.inverse+w2*r.inverse)/area),index=(uint32_t)y*CITY_W+(uint32_t)x;
  if(inverse>depth[index]){depth[index]=inverse;pixels[index]=color;}
 }
}
static void triangle(const City*c,uint32_t*pixels,CityVec a,CityVec b,CityVec d,uint32_t color){
 CityVec input[3]={camera_space(c,a),camera_space(c,b),camera_space(c,d)},clipped[4];unsigned count=0;
 for(unsigned i=0;i<3;i++){
  CityVec previous=input[(i+2)%3],current=input[i];int pin=previous.z>=50,cin=current.z>=50;
  if(pin!=cin)clipped[count++]=intersection(previous,current);
  if(cin)clipped[count++]=current;
 }
 for(unsigned i=1;i+1<count;i++)raster(pixels,clipped[0],clipped[i],clipped[i+1],color);
}
static void quad(const City*c,uint32_t*p,CityVec a,CityVec b,CityVec d,CityVec e,uint32_t color){triangle(c,p,a,b,d,color);triangle(c,p,a,d,e,color);}
static void building(const City*c,uint32_t*p,const CityBuilding*b){
 int x=b->position.x,y=b->position.y,z=b->position.z,w=b->w/2,d=b->d/2,h=b->h;
 CityVec v[8]={{x-w,y,z-d},{x+w,y,z-d},{x+w,y,z+d},{x-w,y,z+d},{x-w,y+h,z-d},{x+w,y+h,z-d},{x+w,y+h,z+d},{x-w,y+h,z+d}};
 quad(c,p,v[0],v[1],v[5],v[4],b->wall);quad(c,p,v[1],v[2],v[6],v[5],shade(b->wall,180));
 quad(c,p,v[2],v[3],v[7],v[6],shade(b->wall,210));quad(c,p,v[3],v[0],v[4],v[7],shade(b->wall,150));
 if(b->kind!=1){quad(c,p,v[4],v[5],v[6],v[7],b->roof);return;}
 CityVec ridge0={x,y+h+h/3,z-d},ridge1={x,y+h+h/3,z+d};
 triangle(c,p,v[4],v[5],ridge0,shade(b->wall,230));triangle(c,p,v[7],v[6],ridge1,shade(b->wall,200));
 quad(c,p,v[4],ridge0,ridge1,v[7],b->roof);quad(c,p,ridge0,v[5],v[6],ridge1,shade(b->roof,180));
 /* Geometric front door and windows, slightly offset from wall to avoid z-fighting. */
 int front=z-d-1;
 quad(c,p,(CityVec){x-w/6,y,front},(CityVec){x+w/6,y,front},(CityVec){x+w/6,y+h/2,front},(CityVec){x-w/6,y+h/2,front},0x594637);
 for(int side=-1;side<=1;side+=2){int cx=x+side*w/2;
  quad(c,p,(CityVec){cx-w/6,y+h/2,front},(CityVec){cx+w/6,y+h/2,front},(CityVec){cx+w/6,y+3*h/4,front},(CityVec){cx-w/6,y+3*h/4,front},0xa6d9ed);
 }
}
static CityVec actor_vertex(const CityActor*a,CityVec v){
 int si=sin_i(a->yaw),co=sin_i(a->yaw+64);
 return (CityVec){a->position.x+(v.x*co+v.z*si)/1024,a->position.y+v.y,a->position.z+(-v.x*si+v.z*co)/1024};
}
static CityVec curved_vertex(const CityPart*b,CityVec center,int lat,int lon){
 int radius=sin_i((unsigned)(lat+64)),vertical=sin_i((unsigned)lat);
 if(b->shape==3){radius=(64-lat)*1024/128;vertical=lat*1024/64;}
 return (CityVec){center.x+(int32_t)((int64_t)b->w/2*radius*sin_i((unsigned)lon)/1048576),
                   center.y+(int32_t)b->h*vertical/2048,
                   center.z+(int32_t)((int64_t)b->d/2*radius*sin_i((unsigned)(lon+64))/1048576)};
}
static void actor(const City*c,uint32_t*p,const CityActor*a,uint32_t elapsed){
 for(unsigned index=a->start;index<a->start+a->count;index++){
  const CityPart*b=&c->parts[index];int window=elapsed>=b->delay&&(elapsed-b->delay)%b->visible_period<b->duration;
  if((b->visibility==1&&!window)||(b->visibility==2&&window))continue;
  int wave=sin_i((unsigned)(((elapsed%b->period+b->phase)%b->period)*256u/b->period));
  CityVec center={b->position.x+b->motion.x*wave/1024,b->position.y+b->motion.y*wave/1024,b->position.z+b->motion.z*wave/1024};
  if(b->shape==2){
   int x=center.x,y=center.y,z=center.z,w=b->w/2,h=b->h/2,d=b->d/2;
   CityVec v[8]={{x-w,y-h,z-d},{x+w,y-h,z-d},{x+w,y-h,z+d},{x-w,y-h,z+d},{x-w,y+h,z-d},{x+w,y+h,z-d},{x+w,y+h,z+d},{x-w,y+h,z+d}};
   for(unsigned j=0;j<8;j++)v[j]=actor_vertex(a,v[j]);
   quad(c,p,v[0],v[1],v[5],v[4],b->color);quad(c,p,v[1],v[2],v[6],v[5],shade(b->color,180));
   quad(c,p,v[2],v[3],v[7],v[6],shade(b->color,210));quad(c,p,v[3],v[0],v[4],v[7],shade(b->color,150));quad(c,p,v[4],v[5],v[6],v[7],shade(b->color,240));
  }else{
   for(int ring=0;ring<6;ring++)for(int slice=0;slice<12;slice++){
    int low=-64+ring*128/6,high=-64+(ring+1)*128/6,left=slice*256/12,right=(slice+1)*256/12;
    CityVec v0=actor_vertex(a,curved_vertex(b,center,low,left)),v1=actor_vertex(a,curved_vertex(b,center,low,right));
    CityVec v2=actor_vertex(a,curved_vertex(b,center,high,right)),v3=actor_vertex(a,curved_vertex(b,center,high,left));
    unsigned light=170+(unsigned)(sin_i((unsigned)(left+64))+1024)*70/2048+(unsigned)ring*3;
    quad(c,p,v0,v1,v2,v3,shade(b->color,light));
   }
  }
 }
}
void city_render(const City*c,uint32_t*p,uint32_t elapsed){
 int si=sin_i(c->yaw),co=sin_i(c->yaw+64);
 for(int y=0;y<CITY_H;y++)for(int x=0;x<CITY_W;x++){
  unsigned index=(unsigned)y*CITY_W+(unsigned)x;depth[index]=0;p[index]=c->sky;
  if(y>167){int distance=c->camera.y*500/(y-167);int side=(x-400)*distance/500;
   int wx=c->camera.x+(int32_t)(((int64_t)side*co+(int64_t)distance*si)/1024),wz=c->camera.z+(int32_t)((-(int64_t)side*si+(int64_t)distance*co)/1024);
   p[index]=shade(c->ground,(((wx+40000)/400)^((wz+40000)/400))&1?235:210);
   depth[index]=0x1000000u/(uint32_t)distance;
  }
 }
 for(unsigned i=0;i<c->count;i++)building(c,p,&c->buildings[i]);
 for(unsigned i=0;i<c->actor_count;i++)actor(c,p,&c->actors[i],elapsed);
}
