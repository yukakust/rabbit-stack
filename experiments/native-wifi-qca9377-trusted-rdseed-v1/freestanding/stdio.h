#ifndef RABBIT_STDIO_DECL_H
#define RABBIT_STDIO_DECL_H
#include <stddef.h>
#include <stdarg.h>
typedef struct RabbitUnavailableFILE FILE;
int snprintf(char*,size_t,const char*,...);int vsnprintf(char*,size_t,const char*,va_list);
/* Declaration only for MinGW's unused compatibility formatter; no fake body.
 * Reachable OS calls remain forbidden by the final no-import link check. */
int vsnprintf_s(char*,size_t,size_t,const char*,va_list);
#endif
