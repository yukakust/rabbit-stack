#ifndef RABBIT_QCA_BRINGUP_H
#define RABBIT_QCA_BRINGUP_H
#include "scene_abi.h"
extern void*qca_controller,*qca_image;
void qca_start(SystemTable*,uint64_t);
void qca_poll(uint64_t);
int qca_stop(void);
#endif
