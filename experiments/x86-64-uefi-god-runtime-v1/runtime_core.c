#include <stdint.h>
#include <stddef.h>
#include "monocypher-ed25519.h"

#define EFI_SUCCESS 0ULL
#define EFI_UNSUPPORTED 3ULL

typedef uint64_t (__attribute__((ms_abi)) *locate_protocol_fn)(void *, void *, void **);

struct scene_state {
    uint32_t tick, counter;
    int32_t cat_x, cat_y, cat_vx, cat_vy;
    int32_t ball_x, ball_y, ball_vx, ball_vy;
    uint32_t wait_ticks, bat_count;
};

static const uint8_t trusted_creator[32] = {
    0x03,0xa1,0x07,0xbf,0xf3,0xce,0x10,0xbe,0x1d,0x70,0xdd,0x18,0xe7,0x4b,0xc0,0x99,
    0x67,0xe4,0xd6,0x30,0x9b,0xa5,0x0d,0x5f,0x1d,0xdc,0x86,0x64,0x12,0x55,0x31,0xb8
};
static const uint8_t trusted_creation[32] = {
    0xc6,0xe1,0xde,0xf6,0x49,0x77,0x69,0xbb,0xaa,0x39,0x17,0xa8,0xda,0xcb,0xa0,0x99,
    0xb0,0x16,0x76,0xaf,0x45,0x93,0x58,0xd7,0xe6,0x55,0x1f,0xb6,0xfa,0x82,0xea,0xb8
};
static const uint8_t trusted_components[32] = {
    0x4d,0x82,0xc2,0x13,0xd7,0x99,0xba,0xd7,0x12,0x25,0x74,0xbd,0x7f,0x13,0x73,0xb2,
    0x5b,0x00,0xbd,0x3b,0x2f,0x5a,0x60,0x3f,0xcc,0x89,0xaf,0xbe,0x6e,0xf8,0xd5,0xbf
};
static const uint8_t gop_guid[16] = {0xde,0xa9,0x42,0x90,0xdc,0x23,0x38,0x4a,0x96,0xfb,0x7a,0xde,0xd0,0x80,0x51,0x6a};
static const uint8_t cat0[64] = {
 0,0,1,1,1,1,0,0, 0,1,1,1,1,1,1,0, 1,1,2,1,1,2,1,1, 1,1,1,1,1,1,1,1,
 0,1,3,1,1,3,1,0, 0,0,1,1,1,1,0,0, 0,1,0,1,1,0,1,0, 1,0,0,1,1,0,0,1};
static const uint8_t cat1[64] = {
 0,0,1,1,1,1,0,0, 0,1,1,1,1,1,1,0, 1,1,2,1,1,2,1,1, 1,1,1,1,1,1,1,1,
 0,1,3,1,1,3,1,0, 0,0,1,1,1,1,0,0, 1,0,0,1,1,0,0,1, 0,1,0,1,1,0,1,0};
static const uint8_t ball[64] = {
 0,0,0,4,4,0,0,0, 0,4,4,4,4,4,4,0, 4,4,4,4,4,4,4,4, 4,3,3,4,4,4,2,4,
 4,4,4,4,4,4,4,4, 0,4,4,4,4,4,4,0, 0,0,4,4,4,4,0,0, 0,0,0,4,4,0,0,0};

static struct scene_state active, previous;
static uint32_t *framebuffer;
static uint32_t stride, width, height, pixel_format, ready, last_counter;

static uint32_t le32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static int equal(const uint8_t *a,const uint8_t *b,size_t n){uint8_t d=0;for(size_t i=0;i<n;i++)d|=a[i]^b[i];return d==0;}
static int sign_i(int value){return (value>0)-(value<0);}
static int clamp_i(int value,int lo,int hi){return value<lo?lo:(value>hi?hi:value);}

static uint32_t color(uint32_t rgb){
    uint32_t r=(rgb>>16)&255,g=(rgb>>8)&255,b=rgb&255;
    return pixel_format==0 ? r|(g<<8)|(b<<16) : b|(g<<8)|(r<<16);
}
static void fill(uint32_t rgb){
    uint32_t c=color(rgb),w=width<480?width:480,h=height<270?height:270;
    for(uint32_t y=0;y<h;y++)for(uint32_t x=0;x<w;x++)framebuffer[y*stride+x]=c;
}
static void sprite(const uint8_t *pixels,int x,int y){
    static const uint32_t palette[5]={0x121826,0xff9933,0x111111,0xffffff,0x3388ff};
    for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
        uint8_t index=pixels[sy*8+sx]; if(index==0)continue;
        for(int yy=0;yy<3;yy++)for(int xx=0;xx<3;xx++){
            int px=x*3+sx*3+xx,py=y*3+sy*3+yy;
            if(px>=0&&py>=0&&(uint32_t)px<width&&(uint32_t)py<height)framebuffer[py*stride+px]=color(palette[index]);
        }
    }
}
static int bind_gop(void *system_table){
    uint8_t *st=(uint8_t*)system_table,*bs=*(uint8_t**)(st+0x60); void *gop=0;
    locate_protocol_fn locate=*(locate_protocol_fn*)(bs+0x140);
    if(locate((void*)gop_guid,0,&gop)!=EFI_SUCCESS||!gop)return -1;
    uint8_t *mode=*(uint8_t**)((uint8_t*)gop+0x18); if(!mode)return -1;
    uint8_t *info=*(uint8_t**)(mode+8); if(!info)return -1;
    width=*(uint32_t*)(info+4);height=*(uint32_t*)(info+8);pixel_format=*(uint32_t*)(info+12);stride=*(uint32_t*)(info+32);
    framebuffer=*(uint32_t**)(mode+24);
    if(width<480||height<270||pixel_format>1||!framebuffer)return -1;
    return 0;
}
static void draw(void){fill(0x121826);sprite(ball,active.ball_x,active.ball_y);sprite((active.tick/4)&1?cat1:cat0,active.cat_x,active.cat_y);}
static int healthy(const struct scene_state *s){return s->cat_x>=0&&s->cat_x<=152&&s->cat_y>=0&&s->cat_y<=82&&s->ball_x>=0&&s->ball_x<=152&&s->ball_y>=0&&s->ball_y<=82;}
static void advance(void){
    active.tick++;active.ball_x+=active.ball_vx;active.ball_y+=active.ball_vy;
    if(active.ball_x<0||active.ball_x>152){active.ball_x=clamp_i(active.ball_x,0,152);active.ball_vx=-active.ball_vx;}
    if(active.ball_y<0||active.ball_y>82){active.ball_y=clamp_i(active.ball_y,0,82);active.ball_vy=-active.ball_vy;}
    int dx=active.ball_x-active.cat_x,dy=active.ball_y-active.cat_y,d2=dx*dx+dy*dy,speed=0;
    if(active.wait_ticks)active.wait_ticks--;else if(d2>784)speed=2;else if(d2>121)speed=3;else{
        int ax=sign_i(dx);if(!ax)ax=1;int ay=sign_i(dy);if(!ay)ay=-1;
        active.ball_vx=ax*3;active.ball_vy=ay*2;active.wait_ticks=12;active.bat_count++;
    }
    active.cat_vx=sign_i(dx)*speed;active.cat_vy=sign_i(dy)*speed;
    active.cat_x=clamp_i(active.cat_x+active.cat_vx,0,152);active.cat_y=clamp_i(active.cat_y+active.cat_vy,0,82);
}

int __attribute__((ms_abi)) rabbit_scene_bootstrap(void *system_table){
    if(bind_gop(system_table))return 1;
    active=(struct scene_state){0,0,12,58,0,0,116,34,2,1,10,0};ready=1;draw();return 0;
}
int __attribute__((ms_abi)) rabbit_scene_tick(void *system_table){
    (void)system_table;if(!ready)return 1;advance();if(!healthy(&active))return 1;draw();return 0;
}
int rabbit_capsule_verify_only(const uint8_t *c,uint32_t length,uint32_t minimum_counter){
    if(length!=192||c[0]!='R'||c[1]!='G'||c[2]!='C'||c[3]!='1'||c[4]!=1||c[5]!=1||c[6]!=30)return 1;
    uint32_t counter=le32(c+8);if(counter<=minimum_counter)return 2;
    if(!equal(c+44,trusted_creation,32)||!equal(c+92,trusted_components,32)||le32(c+124)!=3)return 3;
    if(c[82]!=3||c[83]!=2||c[84]!=2||c[85]||c[86]!=160||c[87]||c[88]!=90||c[89]||c[90]!=88||c[91]!=2)return 4;
    if(crypto_ed25519_check(c+128,trusted_creator,c,128)!=0)return 5;
    return 0;
}
int __attribute__((ms_abi)) rabbit_capsule_verify_activate(const uint8_t *c,uint32_t length,void *system_table){
    (void)system_table;
    if(rabbit_capsule_verify_only(c,length,last_counter))return 1;
    uint32_t counter=le32(c+8);
    previous=active;
    active=(struct scene_state){0,counter,c[76],c[77],0,0,c[78],c[79],(int8_t)c[80],(int8_t)c[81],10,0};
    if(c[7]||!healthy(&active)){active=previous;draw();return 2;}
    advance();
    if(!healthy(&active)){active=previous;draw();return 2;}
    draw();last_counter=counter;return 0;
}
