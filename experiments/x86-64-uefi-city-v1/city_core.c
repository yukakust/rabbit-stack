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
 if(!p||!out||n<96||n>2144||p[0]!='R'||p[1]!='U'||p[2]!='P'||p[3]!='4'||p[4]!=4||p[5]||u16(p+6)!=n||u32(p+8)<=minimum)return 1;
 uint8_t count=p[12];
 if(!count||count>CITY_MAX||p[13]||u16(p+14)!=32||n!=96u+count*32u||p[23])return 1;
 if(abs_i(i16(p+16))>20000||u16(p+18)<50||u16(p+18)>3000||abs_i(i16(p+20))>20000||(u32(p+24)|u32(p+28))>0xffffff)return 1;
 if(crypto_ed25519_check(p+n-64,city_creator,p,n-64))return 1;
 for(unsigned i=0;i<count;i++){
  const uint8_t*q=p+32+i*32;CityBuilding*b=&out->buildings[i];
  if(!u16(q)||q[2]<1||q[2]>3||q[3]||abs_i(i16(q+4))>20000||i16(q+6)<0||i16(q+6)>3000||abs_i(i16(q+8))>20000||
    !u16(q+10)||u16(q+10)>3000||!u16(q+12)||u16(q+12)>3000||!u16(q+14)||u16(q+14)>3000||(u32(q+16)|u32(q+20))>0xffffff||u32(q+24)||u32(q+28))return 1;
  for(unsigned j=0;j<i;j++)if(out->buildings[j].id==u16(q))return 1;
  b->id=u16(q);b->kind=q[2];b->position=(CityVec){i16(q+4),i16(q+6),i16(q+8)};b->w=u16(q+10);b->h=u16(q+12);b->d=u16(q+14);b->wall=u32(q+16);b->roof=u32(q+20);
 }
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
 int32_t px=240+(int32_t)((int64_t)v.x*300/v.z),py=100-(int32_t)((int64_t)v.y*300/v.z);
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
void city_render(const City*c,uint32_t*p){
 int si=sin_i(c->yaw),co=sin_i(c->yaw+64);
 for(int y=0;y<CITY_H;y++)for(int x=0;x<CITY_W;x++){
  unsigned index=(unsigned)y*CITY_W+(unsigned)x;depth[index]=0;p[index]=c->sky;
  if(y>100){int distance=c->camera.y*300/(y-100);int side=(x-240)*distance/300;
   int wx=c->camera.x+(side*co+distance*si)/1024,wz=c->camera.z+(-side*si+distance*co)/1024;
   p[index]=shade(c->ground,(((wx+40000)/400)^((wz+40000)/400))&1?235:210);
   depth[index]=0x1000000u/(uint32_t)distance;
  }
 }
 for(unsigned i=0;i<c->count;i++)building(c,p,&c->buildings[i]);
}
