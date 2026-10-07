#ifndef QCA_MINIMAL_STRING_H
#define QCA_MINIMAL_STRING_H
#include <stddef.h>
void *memcpy(void*,const void*,size_t);void *memset(void*,int,size_t);int memcmp(const void*,const void*,size_t);size_t strlen(const char*);void *memchr(const void*,int,size_t);
#endif
