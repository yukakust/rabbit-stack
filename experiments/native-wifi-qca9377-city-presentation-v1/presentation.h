#ifndef RABBIT_CITY_PRESENTATION_H
#define RABBIT_CITY_PRESENTATION_H
#include <stdint.h>
#include <stddef.h>
/* Presentation owns no DMA, receiver, cryptographic authority or scene state. */
typedef struct {unsigned width,height,stride,format,ready,busy;uint16_t x[2][3840],y[2][2160];} CityPresentation;
typedef void (*CityService)(void*);
int city_presentation_bind(CityPresentation*,unsigned,unsigned,unsigned,unsigned);
int city_presentation_draw(CityPresentation*,uint32_t*,size_t,uint32_t*,const uint32_t*,unsigned,CityService,void*);
int city_presentation_close(CityPresentation*);
#endif
