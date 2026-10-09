#ifndef RABBIT_CITY_CORE_H
#define RABBIT_CITY_CORE_H
#include <stdint.h>
#define CITY_W 800
#define CITY_H 450
#define CITY_MAX 64
typedef struct {int32_t x,y,z;} CityVec;
typedef struct {uint16_t id;uint8_t kind;CityVec position;uint16_t w,h,d;uint32_t wall,roof;} CityBuilding;
typedef struct {uint8_t shape,visibility;CityVec position,motion;uint16_t w,h,d,period,phase,visible_period,duration,delay;uint32_t color;} CityPart;
typedef struct {uint16_t id;uint8_t yaw,count,start;CityVec position;} CityActor;
typedef struct {uint32_t counter,sky,ground;uint8_t count,yaw,actor_count,part_count;CityVec camera;CityBuilding buildings[CITY_MAX];CityActor actors[4];CityPart parts[96];} City;
int city_decode(const uint8_t*,uint32_t,uint32_t,City*);
void city_render(const City*,uint32_t*,uint32_t);
#endif
