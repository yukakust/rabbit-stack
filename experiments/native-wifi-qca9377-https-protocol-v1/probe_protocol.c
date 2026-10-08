#include "probe_protocol.h"
#include <string.h>
static int eq(const uint8_t *p,size_t n,const char *s){return strlen(s)==n&&!memcmp(p,s,n);}
static int lower_eq(const uint8_t *p,size_t n,const char *s){if(strlen(s)!=n)return 0;for(size_t i=0;i<n;i++){unsigned c=p[i];if(c>='A'&&c<='Z')c+=32;if(c!=(unsigned char)s[i])return 0;}return 1;}
void probe_close(struct probe_http *p){if(!p)return;volatile uint8_t *q=(volatile uint8_t*)p;for(size_t i=0;i<sizeof(*p);i++)q[i]=0;}
static int fail(struct probe_http *p){p->failed=1;p->active=0;return -1;}
int probe_request(struct probe_http *p,uint32_t epoch,const char *host,const uint8_t nonce[32],uint8_t *out,size_t cap,size_t *length){
 if(!p||!epoch||!host||!nonce||!out||!length||p->active||p->finished)return -1;
 size_t n=0;while(n<128&&host[n]){unsigned c=(unsigned char)host[n];if(!((c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='.'||c=='-'))return -1;n++;}if(!n||n==128||host[0]=='.'||host[n-1]=='.')return -1;
 const char *a="POST /probe HTTP/1.1\r\nHost: ",*b=":10000\r\nContent-Type: application/json\r\nContent-Length: 76\r\nConnection: close\r\n\r\n{\"nonce\":\"",*c="\"}";
 size_t needed=strlen(a)+n+strlen(b)+64+strlen(c);if(cap<needed)return -1;
 probe_close(p);p->epoch=epoch;p->active=1;const char hex[]="0123456789abcdef";
 for(size_t i=0;i<32;i++){p->nonce[2*i]=hex[nonce[i]>>4];p->nonce[2*i+1]=hex[nonce[i]&15];}p->nonce[64]=0;
 size_t pos=0;memcpy(out+pos,a,strlen(a));pos+=strlen(a);memcpy(out+pos,host,n);pos+=n;memcpy(out+pos,b,strlen(b));pos+=strlen(b);memcpy(out+pos,p->nonce,64);pos+=64;memcpy(out+pos,c,strlen(c));pos+=strlen(c);*length=pos;return 0;
}
int probe_feed(struct probe_http *p,uint32_t epoch,const uint8_t *bytes,size_t length){
 if(!p||!p->active||p->failed||p->finished||epoch!=p->epoch||(!bytes&&length)||length>sizeof(p->bytes)-p->used)return p?fail(p):-1;
 if(length)memcpy(p->bytes+p->used,bytes,length);p->used+=length;return 0;
}
int probe_finish(struct probe_http *p,uint32_t epoch){
 if(!p||!p->active||p->failed||p->finished||epoch!=p->epoch)return p?fail(p):-1;
 size_t pos=0,end=0;while(end+1<p->used&&!(p->bytes[end]==13&&p->bytes[end+1]==10))end++;
 if(end+1>=p->used||!(eq(p->bytes,end,"HTTP/1.0 200 OK")||eq(p->bytes,end,"HTTP/1.1 200 OK")))return fail(p);pos=end+2;
 unsigned have_length=0,have_type=0;size_t body_length=0;
 while(pos+1<p->used){if(p->bytes[pos]==13&&p->bytes[pos+1]==10){pos+=2;break;}
  size_t line=pos;end=pos;while(end+1<p->used&&!(p->bytes[end]==13&&p->bytes[end+1]==10))end++;if(end+1>=p->used||end>2048||line==end)return fail(p);
  size_t colon=line;while(colon<end&&p->bytes[colon]!=':'){unsigned ch=p->bytes[colon];if(!((ch>='a'&&ch<='z')||(ch>='A'&&ch<='Z')||(ch>='0'&&ch<='9')||ch=='-'))return fail(p);colon++;}if(colon==line||colon==end)return fail(p);
  size_t value=colon+1;while(value<end&&p->bytes[value]==' ')value++;for(size_t i=value;i<end;i++)if(p->bytes[i]<32||p->bytes[i]>=127)return fail(p);
  if(lower_eq(p->bytes+line,colon-line,"transfer-encoding"))return fail(p);
  if(lower_eq(p->bytes+line,colon-line,"content-length")){if(have_length++||value==end||end-value>3)return fail(p);for(size_t i=value;i<end;i++){unsigned ch=p->bytes[i];if(ch<'0'||ch>'9')return fail(p);body_length=body_length*10+ch-'0';}if(body_length>128)return fail(p);}
  if(lower_eq(p->bytes+line,colon-line,"content-type")){if(have_type++||!eq(p->bytes+value,end-value,"application/json"))return fail(p);}
  pos=end+2;
 }
 const char *a="{\"nonce\":\"",*b="\",\"proof\":\"rabbit-dell-wan-v1\"}";size_t expected=strlen(a)+64+strlen(b);
 if(!have_length||!have_type||body_length!=expected||p->used-pos!=expected)return fail(p);
 if(memcmp(p->bytes+pos,a,strlen(a))||memcmp(p->bytes+pos+strlen(a),p->nonce,64)||memcmp(p->bytes+pos+strlen(a)+64,b,strlen(b)))return fail(p);
 p->finished=1;p->active=0;return 1;
}
