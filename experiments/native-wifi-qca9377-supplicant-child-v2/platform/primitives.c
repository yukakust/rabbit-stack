#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
#include <limits.h>
#define NANOPRINTF_IMPLEMENTATION
#define NANOPRINTF_USE_FIELD_WIDTH_FORMAT_SPECIFIERS 1
#define NANOPRINTF_USE_PRECISION_FORMAT_SPECIFIERS 1
#define NANOPRINTF_USE_FLOAT_FORMAT_SPECIFIERS 0
#define NANOPRINTF_USE_LARGE_FORMAT_SPECIFIERS 1
#define NANOPRINTF_USE_SMALL_FORMAT_SPECIFIERS 1
#define NANOPRINTF_USE_BINARY_FORMAT_SPECIFIERS 0
#define NANOPRINTF_USE_WRITEBACK_FORMAT_SPECIFIERS 0
#include "references/nanoprintf.h"
void*memset(void*d,int c,size_t n){uint8_t*p=d;while(n--)*p++=(uint8_t)c;return d;}
void*memcpy(void*d,const void*s,size_t n){uint8_t*p=d;const uint8_t*q=s;while(n--)*p++=*q++;return d;}
void*memmove(void*d,const void*s,size_t n){uint8_t*p=d;const uint8_t*q=s;if((uintptr_t)p<(uintptr_t)q)for(size_t j=0;j<n;j++)p[j]=q[j];else while(n){n--;p[n]=q[n];}return d;}
int memcmp(const void*a,const void*b,size_t n){const uint8_t*p=a,*q=b;for(size_t j=0;j<n;j++)if(p[j]!=q[j])return p[j]<q[j]?-1:1;return 0;}
size_t strlen(const char*p){size_t n=0;while(p[n])n++;return n;}
int strcmp(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return (unsigned char)*a-(unsigned char)*b;}
int strncmp(const char*a,const char*b,size_t n){for(size_t j=0;j<n;j++){if(a[j]!=b[j])return (unsigned char)a[j]-(unsigned char)b[j];if(!a[j])return 0;}return 0;}
char*strchr(const char*s,int c){do{if((unsigned char)*s==(unsigned char)c)return (char*)s;}while(*s++);return 0;}
char*strrchr(const char*s,int c){const char*r=0;do{if((unsigned char)*s==(unsigned char)c)r=s;}while(*s++);return (char*)r;}
char*strstr(const char*s,const char*needle){size_t n=strlen(needle);if(!n)return(char*)s;for(;*s;s++)if(!strncmp(s,needle,n))return(char*)s;return 0;}
int isspace(int c){return c==' '||(c>=9&&c<=13);}
int isdigit(int c){return c>='0'&&c<='9';}
int isprint(int c){return c>=32&&c<=126;}
int tolower(int c){return c>='A'&&c<='Z'?c+32:c;}
int toupper(int c){return c>='a'&&c<='z'?c-32:c;}
long strtol(const char*s,char**end,int base){const char*begin=s;while(isspace((unsigned char)*s))s++;int neg=0;if(*s=='-'||*s=='+')neg=*s++=='-';if((base==0||base==16)&&s[0]=='0'&&(s[1]=='x'||s[1]=='X')&&((s[2]>='0'&&s[2]<='9')||(tolower(s[2])>='a'&&tolower(s[2])<='f'))){s+=2;base=16;}if(!base)base=*s=='0'?8:10;if(base<2||base>36){if(end)*end=(char*)begin;return 0;}unsigned long limit=neg?(unsigned long)LONG_MAX+1:(unsigned long)LONG_MAX,v=0;unsigned any=0,overflow=0;for(;;s++){int c=tolower((unsigned char)*s);unsigned d=isdigit(c)?(unsigned)(c-'0'):c>='a'&&c<='z'?(unsigned)(c-'a'+10):36;if(d>=(unsigned)base)break;any=1;if(v>(limit-d)/(unsigned)base)overflow=1;else if(!overflow)v=v*(unsigned)base+d;}if(end)*end=(char*)(any?s:begin);if(overflow)return neg?LONG_MIN:LONG_MAX;if(neg){if(v==(unsigned long)LONG_MAX+1)return LONG_MIN;return -(long)v;}return (long)v;}
int atoi(const char*s){long v=strtol(s,0,10);return v>INT_MAX?INT_MAX:v<INT_MIN?INT_MIN:(int)v;}
void qsort(void*base,size_t n,size_t bytes,int(*compare)(const void*,const void*)){if(!base||!compare||!bytes||n>256||bytes>256||n>SIZE_MAX/bytes)__builtin_trap();uint8_t*p=base;for(size_t j=1;j<n;j++)for(size_t k=j;k&&compare(p+(k-1)*bytes,p+k*bytes)>0;k--)for(size_t x=0;x<bytes;x++){uint8_t t=p[(k-1)*bytes+x];p[(k-1)*bytes+x]=p[k*bytes+x];p[k*bytes+x]=t;}}
int vsnprintf(char*out,size_t n,const char*fmt,va_list ap){return npf_vsnprintf(out,n,fmt,ap);}
int snprintf(char*out,size_t n,const char*fmt,...){va_list ap;va_start(ap,fmt);int r=vsnprintf(out,n,fmt,ap);va_end(ap);return r;}
_Noreturn void abort(void){__builtin_trap();}
