#include <stddef.h>
/* Standard C strncpy, including exact n bound and zero padding. */
char*strncpy(char*d,const char*s,size_t n){size_t i=0;while(i<n&&s[i]){d[i]=s[i];i++;}while(i<n)d[i++]=0;return d;}
/* QR calls with bounded small counts; same standard C labs semantics. */
long labs(long x){return x<0?-x:x;}
int abs(int x){return x<0?-x:x;}
