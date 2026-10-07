/* Target Pack only: owner native driver uses GOP after attach, never during init.
 * Root still presents its480x270 surface; supply the exact fullscreen top-left
 * crop so the unchanged root's final copy agrees with the driver presentation. */
static uint32_t *city_physical;
static uint32_t city_stride,city_width,city_height,city_format;
static uint32_t city_picture[480*270];
static int city_display_bind(SystemTable*st){
 typedef Status(EFIAPI *Locate)(const void*,void*,void**);
 static const uint8_t guid[16]={0xde,0xa9,0x42,0x90,0xdc,0x23,0x38,0x4a,0x96,0xfb,0x7a,0xde,0xd0,0x80,0x51,0x6a};
 void*gop=0;if(((Locate)service(st,320))(guid,0,&gop)||!gop)return 1;
 uint8_t*mode=*(uint8_t**)((uint8_t*)gop+24);if(!mode)return 1;uint8_t*info=*(uint8_t**)(mode+8);if(!info)return 1;
 city_width=le32(info+4);city_height=le32(info+8);city_stride=le32(info+32);city_format=le32(info+12);city_physical=*(uint32_t**)(mode+24);
 if(city_width<480||city_height<270||city_width>3840||city_height>2160||city_stride<city_width||city_stride>16384||city_format>1||!city_physical||*(uint64_t*)(mode+32)<(uint64_t)city_stride*city_height*4){city_physical=0;return 1;}
 return 0;
}
static void city_present(Surface*s){
 if(!city_physical)return;
 int detailed=active_length&&(active_package[4]==4||active_package[4]==5);
 const uint32_t*picture=city_frame;unsigned w=CITY_W,h=CITY_H;
 if(!detailed){for(unsigned i=0;i<480*270;i++)city_picture[i]=s->pixels[i];picture=city_picture;w=480;h=270;}
 for(unsigned y=0;y<city_height;y++){
  uint32_t*dst=city_physical+y*city_stride;const uint32_t*row=picture+(uint64_t)y*h/city_height*w;
  for(unsigned x=0;x<city_width;x++){
   uint32_t c=row[(uint64_t)x*w/city_width];
   if(!city_format)c=((c&255)<<16)|(c&0xff00)|((c>>16)&255);
   dst[x]=c;
  }
 }
 for(unsigned y=0;y<270;y++)for(unsigned x=0;x<480;x++)s->pixels[y*480+x]=picture[(uint64_t)y*h/city_height*w+(uint64_t)x*w/city_width];

}
