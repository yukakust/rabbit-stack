#include <stdint.h>
#include <stddef.h>
#include "monocypher-ed25519.h"

#define EFI_SUCCESS 0ULL
#define MAX_PACKAGE 65535
#define MAX_OBJECTS 16
#define MAX_PROGRAM_BYTES 32

typedef uint64_t (__attribute__((ms_abi)) *locate_protocol_fn)(void *, void *, void **);

struct object_state { uint8_t id,sprite,program,frame,target; int16_t x,y; int8_t vx,vy; };

static const uint8_t trusted_creator[32] = {
    0x03,0xa1,0x07,0xbf,0xf3,0xce,0x10,0xbe,0x1d,0x70,0xdd,0x18,0xe7,0x4b,0xc0,0x99,
    0x67,0xe4,0xd6,0x30,0x9b,0xa5,0x0d,0x5f,0x1d,0xdc,0x86,0x64,0x12,0x55,0x31,0xb8
};
static const uint8_t gop_guid[16] = {0xde,0xa9,0x42,0x90,0xdc,0x23,0x38,0x4a,0x96,0xfb,0x7a,0xde,0xd0,0x80,0x51,0x6a};
static uint8_t staging[MAX_PACKAGE], active_package[MAX_PACKAGE];
static uint8_t decoded_frame[128*128];
static uint16_t palette_count(const uint8_t *p){return p[4]==3?(p[12]?p[12]:256):p[12];}
static uint32_t staging_length,staging_received,staging_hash,last_hash,receipt_hash,last_counter,active_length,tick;
static uint16_t next_sequence;
static uint8_t staging_transfer,receiving,object_count;
static struct object_state objects[MAX_OBJECTS], provisional[MAX_OBJECTS];
static uint32_t *framebuffer;
static uint32_t stride,width,height,pixel_format,ready;

static uint16_t le16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint32_t le32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint32_t be32(const uint8_t *p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static uint32_t fnv(const uint8_t *p,uint32_t n){uint32_t h=0x811c9dc5;for(uint32_t i=0;i<n;i++)h=(h^p[i])*0x01000193;return h;}
static int sign_i(int value){return (value>0)-(value<0);}
static int clamp_i(int value,int lo,int hi){return value<lo?lo:(value>hi?hi:value);}

static uint32_t color(uint32_t rgb){
    uint32_t r=(rgb>>16)&255,g=(rgb>>8)&255,b=rgb&255;
    return pixel_format==0?r|(g<<8)|(b<<16):b|(g<<8)|(r<<16);
}
static int bind_gop(void *system_table){
    uint8_t *st=(uint8_t*)system_table,*bs=*(uint8_t**)(st+0x60);void *gop=0;
    locate_protocol_fn locate=*(locate_protocol_fn*)(bs+0x140);
    if(locate((void*)gop_guid,0,&gop)!=EFI_SUCCESS||!gop)return -1;
    uint8_t *mode=*(uint8_t**)((uint8_t*)gop+0x18);if(!mode)return -1;
    uint8_t *info=*(uint8_t**)(mode+8);if(!info)return -1;
    width=*(uint32_t*)(info+4);height=*(uint32_t*)(info+8);pixel_format=*(uint32_t*)(info+12);stride=*(uint32_t*)(info+32);framebuffer=*(uint32_t**)(mode+24);
    uint64_t fbsize=*(uint64_t*)(mode+32);
    return width<480||height<270||width>8192||height>8192||stride<width||stride>16384||fbsize<(uint64_t)stride*height*4||pixel_format>1||!framebuffer?-1:0;
}
static void fill(uint32_t rgb){
    uint32_t c=color(rgb),w=width<480?width:480,h=height<270?height:270;
    for(uint32_t y=0;y<h;y++)for(uint32_t x=0;x<w;x++)framebuffer[y*stride+x]=c;
}

static const uint8_t *find_sprite(const uint8_t *p,uint8_t id,uint8_t *w,uint8_t *h,uint8_t *frames,uint16_t *bytes){
    uint16_t cursor=le16(p+18),end=le16(p+20);
    for(uint8_t i=0;i<p[13]&&cursor+8<=end;i++){
        uint8_t sid=p[cursor],sw=p[cursor+1],sh=p[cursor+2],sf=p[cursor+3];uint16_t n=le16(p+cursor+4);
        if(cursor+8+n>end)return 0;
        if(sid==id){*w=sw;*h=sh;*frames=sf;*bytes=n;return p+cursor+8;}
        cursor=(uint16_t)(cursor+8+n);
    }
    return 0;
}
static const uint8_t *find_program(const uint8_t *p,uint8_t id,uint8_t *length){
    uint16_t cursor=le16(p+22),end=le16(p+24);
    for(uint8_t i=0;i<p[15]&&cursor+2<=end;i++){
        uint8_t pid=p[cursor],n=p[cursor+1];cursor+=2;if(cursor+n>end)return 0;
        if(pid==id){*length=n;return p+cursor;}cursor=(uint16_t)(cursor+n);
    }
    return 0;
}
static int object_index(struct object_state *state,uint8_t count,uint8_t id){for(uint8_t i=0;i<count;i++)if(state[i].id==id)return i;return -1;}
static uint8_t pixel_at(const uint8_t *packed,uint32_t index){uint8_t b=packed[index>>1];return (index&1)?(b&15):(b>>4);}
static void sprite_display(const uint8_t *p,const uint8_t *pixels,uint8_t sw,uint8_t sh,uint8_t *dw,uint8_t *dh){
    *dw=p[4]==3?pixels[-2]:sw;*dh=p[4]==3?pixels[-1]:sh;
}
static void draw_sprite(const uint8_t *p,const struct object_state *o){
    uint8_t sw=0,sh=0,frames=0,dw=0,dh=0;uint16_t bytes=0;
    const uint8_t *pixels=find_sprite(p,o->sprite,&sw,&sh,&frames,&bytes);
    if(!pixels||!frames)return;
    sprite_display(p,pixels,sw,sh,&dw,&dh);
    uint32_t base=(uint32_t)(o->frame%frames)*sw*sh;
    if(p[4]==3){
        uint32_t pos=0,begin=base,end=base+(uint32_t)sw*sh;
        for(uint32_t i=0;i<bytes;i+=2){
            uint32_t next=pos+pixels[i];
            for(uint32_t k=pos>begin?pos:begin;k<next&&k<end;k++)decoded_frame[k-begin]=pixels[i+1];
            pos=next;if(pos>=end)break;
        }
    }
    for(uint32_t y=0;y<(uint32_t)dh*3;y++)for(uint32_t x=0;x<(uint32_t)dw*3;x++){
        int px=o->x*3+(int)x,py=o->y*3+(int)y;
        if(px<0||py<0||px>=480||py>=270)continue;
        uint32_t source=(y*sh/(dh*3))*sw+(x*sw/(dw*3));
        uint8_t index=p[4]==3?decoded_frame[source]:pixel_at(pixels,base+source);
        if(!index||index>=palette_count(p))continue;
        uint32_t off=le16(p+16)+(uint32_t)index*(p[4]==3?4:3);
        uint32_t rgb=((uint32_t)p[off]<<16)|((uint32_t)p[off+1]<<8)|p[off+2];
        uint32_t c=color(rgb),a=p[4]==3?p[off+3]:255;
        uint32_t *dst=framebuffer+(uint32_t)py*stride+(uint32_t)px;
        if(a==255)*dst=c;
        else if(a){uint32_t old=*dst,result=0;
            for(uint32_t shift=0;shift<24;shift+=8){
                uint32_t channel=(((c>>shift)&255)*a+((old>>shift)&255)*(255-a)+127)/255;
                result|=channel<<shift;
            }*dst=result;
        }
    }
}
static void draw_scene(const uint8_t *p,struct object_state *state,uint8_t count){fill(0x121826);for(uint8_t i=0;i<count;i++)draw_sprite(p,&state[i]);}

static int validate_program(const uint8_t *code,uint8_t n,const uint8_t *ids,uint8_t id_count){
    uint8_t cursor=0,steps=0;
    while(cursor<n&&steps++<16){uint8_t op=code[cursor++];if(op==0)return cursor==n?0:1;if(op==1||op==2)continue;if(op==5){if(cursor>=n||!code[cursor++])return 1;continue;}if(op==3||op==4||op==6){if(cursor+2>n||!code[cursor+1]||code[cursor+1]>8)return 1;uint8_t target=code[cursor];int found=0;for(uint8_t i=0;i<id_count;i++)found|=ids[i]==target;if(!found)return 1;cursor+=2;continue;}return 1;}return 1;
}
static int validate_package(const uint8_t *p,uint32_t length,uint32_t minimum_counter,struct object_state *state,uint8_t *count){
    if(length<96||length>MAX_PACKAGE||p[0]!='R'||p[1]!='U'||p[2]!='P'||!((p[3]=='2'&&p[4]==2)||(p[3]=='3'&&p[4]==3))||(p[5]&0xfe)||le16(p+6)!=length||le32(p+8)<=minimum_counter)return 1;
    uint16_t pc=palette_count(p);uint8_t sc=p[13],oc=p[14],prc=p[15];uint16_t po=le16(p+16),so=le16(p+18),oo=le16(p+20),pro=le16(p+22),sig=le16(p+24);
    if(!pc||(p[4]==2&&pc>16)||!sc||sc>16||!oc||oc>16||!prc||prc>16||po!=32||so!=32+pc*(p[4]==3?4:3)||!(so<=oo&&oo<=pro&&pro<=sig)||(uint32_t)sig+64U!=length||le16(p+26)!=33||le16(p+28)!=160||le16(p+30)!=90)return 1;
    if(crypto_ed25519_check(p+sig,trusted_creator,p,sig)!=0)return 1;
    uint8_t sprite_ids[16]={0},object_ids[16]={0},program_ids[16]={0};uint16_t cursor=so;uint32_t decoded_budget=0;
    if(p[4]==3&&(p[32]||p[33]||p[34]||p[35]))return 1;
    for(uint8_t i=0;i<sc;i++){
        if(cursor+8>oo)return 1;
        uint8_t id=p[cursor],w=p[cursor+1],h=p[cursor+2],frames=p[cursor+3];
        uint16_t n=le16(p+cursor+4);
        if(!id||!w||!h||!frames||frames>16||cursor+8U+n>oo)return 1;
        uint32_t expected=(uint32_t)w*h*frames;decoded_budget+=expected;
        if(decoded_budget>262144)return 1;
        if(p[4]==3){
            if(w>128||h>128||!p[cursor+6]||p[cursor+6]>64||!p[cursor+7]||p[cursor+7]>64||(n&1))return 1;
            uint32_t sum=0;for(uint32_t k=0;k<n;k+=2){
                uint8_t run=p[cursor+8+k],index=p[cursor+9+k];
                if(!run||index>=pc||sum+run>expected)return 1;
                sum+=run;
            }if(sum!=expected)return 1;
        }else{
            if(w>16||h>16||le16(p+cursor+6)||n!=(expected+1)/2)return 1;
            for(uint32_t k=0;k<expected;k++)if(pixel_at(p+cursor+8,k)>=pc)return 1;
        }
        for(uint8_t j=0;j<i;j++)if(sprite_ids[j]==id)return 1;
        sprite_ids[i]=id;cursor=(uint16_t)(cursor+8+n);
    }if(cursor!=oo||pro-oo!=(uint16_t)oc*16)return 1;
    for(uint8_t i=0;i<oc;i++){cursor=(uint16_t)(oo+i*16);struct object_state *o=&state[i];o->id=p[cursor];o->sprite=p[cursor+1];o->program=p[cursor+2];o->frame=p[cursor+3];o->x=(int16_t)le16(p+cursor+4);o->y=(int16_t)le16(p+cursor+6);o->vx=(int8_t)p[cursor+8];o->vy=(int8_t)p[cursor+9];o->target=p[cursor+10];if(!o->id||o->frame||o->x<0||o->y<0||o->vx<-8||o->vx>8||o->vy<-8||o->vy>8||p[cursor+11]||le16(p+cursor+12)||le16(p+cursor+14)||o->x>=160||o->y>=90)return 1;for(uint8_t j=0;j<i;j++)if(object_ids[j]==o->id)return 1;object_ids[i]=o->id;int found=0;for(uint8_t j=0;j<sc;j++)found|=sprite_ids[j]==o->sprite;if(!found)return 1;}
    cursor=pro;
    for(uint8_t i=0;i<prc;i++){if(cursor+2>sig)return 1;uint8_t id=p[cursor],n=p[cursor+1];cursor+=2;if(!id||!n||n>MAX_PROGRAM_BYTES||cursor+n>sig||validate_program(p+cursor,n,object_ids,oc))return 1;for(uint8_t j=0;j<i;j++)if(program_ids[j]==id)return 1;program_ids[i]=id;cursor=(uint16_t)(cursor+n);}if(cursor!=sig)return 1;
    for(uint8_t i=0;i<oc;i++){int found=0;for(uint8_t j=0;j<prc;j++)found|=program_ids[j]==state[i].program;if(!found||(state[i].target!=0xff&&object_index(state,oc,state[i].target)<0))return 1;}
    *count=oc;return 0;
}
int rabbit_package_verify_only(const uint8_t *p,uint32_t length,uint32_t minimum_counter){uint8_t count=0;return validate_package(p,length,minimum_counter,provisional,&count);}
static int step_scene(const uint8_t *p,struct object_state *state,uint8_t count,uint32_t now){
    for(uint8_t i=0;i<count;i++){
        uint8_t n=0;const uint8_t *code=find_program(p,state[i].program,&n);if(!code)return 1;uint8_t cursor=0,steps=0;
        while(cursor<n&&steps++<16){uint8_t op=code[cursor++];if(op==0)break;if(op==1){state[i].x+=state[i].vx;state[i].y+=state[i].vy;continue;}if(op==2){uint8_t sw=0,sh=0,sf=0;uint16_t bytes=0;const uint8_t *sp=find_sprite(p,state[i].sprite,&sw,&sh,&sf,&bytes);if(!sp)return 1;uint8_t dw=0,dh=0;sprite_display(p,sp,sw,sh,&dw,&dh);int maxx=160-dw,maxy=90-dh;if(state[i].x<0||state[i].x>maxx){state[i].x=clamp_i(state[i].x,0,maxx);state[i].vx=-state[i].vx;}if(state[i].y<0||state[i].y>maxy){state[i].y=clamp_i(state[i].y,0,maxy);state[i].vy=-state[i].vy;}continue;}if(op==5){uint8_t period=code[cursor++];if(!(now%period))state[i].frame++;continue;}uint8_t target=code[cursor++],magnitude=code[cursor++];int ti=object_index(state,count,target);if(ti<0)return 1;int dx=state[ti].x-state[i].x,dy=state[ti].y-state[i].y;if(op==3||op==4){int direction=op==3?1:-1;state[i].vx=(int8_t)(sign_i(dx)*magnitude*direction);state[i].vy=(int8_t)(sign_i(dy)*magnitude*direction);}else if(op==6&&dx*dx+dy*dy<144){state[ti].vx=(int8_t)(sign_i(dx)*magnitude);state[ti].vy=(int8_t)(sign_i(dy)*magnitude);}}
        if(state[i].x<-16||state[i].x>160||state[i].y<-16||state[i].y>90)return 1;
    }return 0;
}

int __attribute__((ms_abi)) rabbit_scene_bootstrap(void *system_table){if(bind_gop(system_table))return 1;fill(0x121826);ready=1;return 0;}
int __attribute__((ms_abi)) rabbit_scene_tick(void *system_table){(void)system_table;if(!ready)return 1;if(active_length){tick++;if(step_scene(active_package,objects,object_count,tick))return 1;draw_scene(active_package,objects,object_count);}return 0;}

static int activate(const uint8_t *p,uint32_t length){
    uint8_t count=0;if(validate_package(p,length,last_counter,provisional,&count))return 3;if(p[5]&1)return 2;
    struct object_state health[MAX_OBJECTS];for(uint8_t i=0;i<count;i++)health[i]=provisional[i];if(step_scene(p,health,count,tick+1))return 2;
    for(uint32_t i=0;i<length;i++)active_package[i]=p[i];
    for(uint8_t i=0;i<count;i++)objects[i]=health[i];
    active_length=length;object_count=count;last_counter=le32(p+8);tick++;draw_scene(active_package,objects,object_count);return 1;
}
int __attribute__((ms_abi)) rabbit_package_frame(const uint8_t *f,void *system_table){
    (void)system_table;if(f[0]!='R'||f[1]!='P'||(f[2]>>4)!=2||fnv(f,12)!=be32(f+12))return 0;uint8_t kind=f[2]&15,transfer=f[3];uint16_t seq=le16(f+4);
    if(kind==1){uint16_t length=le16(f+6);uint32_t hash=be32(f+8);if(seq||!length)return 0;
        if(receiving&&length==staging_length&&hash==staging_hash&&transfer==staging_transfer)return 0;
        receiving=1;staging_transfer=transfer;next_sequence=0;staging_length=length;staging_received=0;staging_hash=hash;return 0;}
    if(!receiving){
        if(kind==3&&active_length&&seq==(active_length+5)/6&&le16(f+10)==active_length&&be32(f+6)==last_hash&&transfer==staging_transfer){receipt_hash=last_hash;return 5;}
        return 0;
    }
    if(transfer!=staging_transfer)return 0;
    if(kind==3){uint32_t length=le16(f+10),hash=be32(f+6);
        if(!length||length>staging_length||length>staging_received||seq!=(length+5)/6||fnv(staging,length)!=hash)return 0;
        if(length<staging_length){receipt_hash=hash;return 4;}
        if(seq!=next_sequence||staging_received!=staging_length||hash!=staging_hash)return 0;
        receiving=0;
        if(active_length==staging_length&&last_hash==hash){
            uint32_t same=1;for(uint32_t i=0;i<active_length;i++)same&=active_package[i]==staging[i];
            if(same){receipt_hash=hash;return 5;}
        }
        int result=activate(staging,staging_length);if(result==1){last_hash=hash;receipt_hash=hash;}return result;
    }
    if(seq!=next_sequence)return 0;
    if(kind==2){uint32_t remaining=staging_length-staging_received,count=remaining<6?remaining:6;if(!remaining)return 0;for(uint32_t i=0;i<count;i++)staging[staging_received++]=f[6+i];next_sequence++;return 0;}
    return 0;
}
uint32_t __attribute__((ms_abi)) rabbit_package_last_hash(void){return receipt_hash;}
