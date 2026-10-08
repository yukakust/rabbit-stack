#include <stddef.h>
#include <stdint.h>
void*memset(void*d,int c,size_t n){volatile unsigned char*p=d;while(n--)*p++=(unsigned char)c;return d;}
void*memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;while(n--)*a++=*b++;return d;}
void*memmove(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;if((uintptr_t)a<(uintptr_t)b)while(n--)*a++=*b++;else{a+=n;b+=n;while(n--)*--a=*--b;}return d;}
int memcmp(const void*a,const void*b,size_t n){const unsigned char*x=a,*y=b;while(n--){if(*x!=*y)return *x<*y?-1:1;x++;y++;}return 0;}
size_t strlen(const char*s){size_t n=0;while(s[n])n++;return n;}
int strcmp(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return (unsigned char)*a-(unsigned char)*b;}
int strncmp(const char*a,const char*b,size_t n){while(n--){if(*a!=*b)return (unsigned char)*a-(unsigned char)*b;if(!*a)return 0;a++;b++;}return 0;}
char*strchr(const char*p,int c){while(*p&&(unsigned char)*p!=(unsigned char)c)p++;return (unsigned char)*p==(unsigned char)c?(char*)p:0;}
void*memchr(const void*p,int c,size_t n){const unsigned char*s=p;while(n--){if(*s==(unsigned char)c)return (void*)s;s++;}return 0;}
void rabbit_tls_assert_failure(void){__builtin_trap();}
#if defined(MBEDTLS_PLATFORM_ZEROIZE_ALT)
void mbedtls_platform_zeroize(void*p,size_t n){volatile unsigned char*q=p;while(n--)*q++=0;}
#endif
