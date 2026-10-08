/* Compile-only freestanding boundary declarations. No fake implementations. */
#ifndef RABBIT_HOSTAP_NATIVE_ABI_H
#define RABBIT_HOSTAP_NATIVE_ABI_H
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdarg.h>
#include <limits.h>
#define _WIN32_WCE 1
#undef _MSC_VER
#define __BYTE_ORDER 1234
#define __LITTLE_ENDIAN 1234
#define __BIG_ENDIAN 4321
static inline uint16_t bswap_16(uint16_t v){return __builtin_bswap16(v);}
static inline uint32_t bswap_32(uint32_t v){return __builtin_bswap32(v);}
static inline uint64_t bswap_64(uint64_t v){return __builtin_bswap64(v);}
typedef intptr_t ssize_t;
typedef struct rabbit_unavailable_file FILE;
void *memcpy(void*,const void*,size_t);
void *memmove(void*,const void*,size_t);
void *memset(void*,int,size_t);
int memcmp(const void*,const void*,size_t);
size_t strlen(const char*);
int strcmp(const char*,const char*);
int strncmp(const char*,const char*,size_t);
char *strchr(const char*,int);
char *strrchr(const char*,int);
int snprintf(char*,size_t,const char*,...);
int vsnprintf(char*,size_t,const char*,va_list);
int tolower(int);
int toupper(int);
int isspace(int);
int isdigit(int);
int isprint(int);
int atoi(const char*);
long strtol(const char*,char**,int);
void qsort(void*,size_t,size_t,int(*)(const void*,const void*));
_Noreturn void abort(void);
#endif
