#include <stddef.h>
void*memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}
void*memset(void*d,int x,size_t n){unsigned char*a=d;for(size_t i=0;i<n;i++)a[i]=(unsigned char)x;return d;}
int memcmp(const void*a,const void*b,size_t n){const unsigned char*x=a,*y=b;for(size_t i=0;i<n;i++)if(x[i]!=y[i])return x[i]<y[i]?-1:1;return 0;}
size_t strlen(const char*s){size_t n=0;while(s[n])n++;return n;}
void*memchr(const void*s,int x,size_t n){const unsigned char*p=s;for(size_t i=0;i<n;i++)if(p[i]==(unsigned char)x)return (void*)(p+i);return 0;}
