#include "probe_protocol.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
static size_t response(char *out,const char *nonce,const char *extra){char body[128];int n=snprintf(body,sizeof(body),"{\"nonce\":\"%s\",\"proof\":\"rabbit-dell-wan-v1\"}",nonce);assert(n>0&&n<128);int m=snprintf(out,2304,"HTTP/1.0 200 OK\r\nServer: BaseHTTP/0.6\r\nDate: public-fixture\r\nContent-Type: application/json\r\nContent-Length: %d\r\n%s\r\n%s",n,extra,body);assert(m>0&&m<2304);return (size_t)m;}
static void start(struct probe_http *p){uint8_t nonce[32],request[512]={0};size_t n;memset(p,0,sizeof(*p));for(size_t i=0;i<32;i++)nonce[i]=(uint8_t)i;assert(!probe_request(p,64,"yukabox.tail1e1ad1.ts.net",nonce,request,sizeof(request),&n));assert(n<512&&strstr((char*)request,"Content-Length: 76\r\n"));}
int main(void){struct probe_http p;char wire[2304],mutated[2304];start(&p);size_t n=response(wire,p.nonce,"");
 for(size_t fragment=1;fragment<=240;fragment++){start(&p);for(size_t pos=0;pos<n;){size_t k=n-pos<fragment?n-pos:fragment;assert(!probe_feed(&p,64,(uint8_t*)wire+pos,k));pos+=k;}assert(probe_finish(&p,64)==1);assert(probe_finish(&p,64)==-1);checks+=2;}
 for(size_t cut=0;cut<n;cut++){start(&p);assert(!probe_feed(&p,64,(uint8_t*)wire,cut));assert(probe_finish(&p,64)==-1);checks++;}
 const char *body=strstr(wire,"\r\n\r\n")+4;size_t off=(size_t)(body-wire);
 for(size_t i=off;i<n;i++){start(&p);memcpy(mutated,wire,n);mutated[i]^=1;assert(!probe_feed(&p,64,(uint8_t*)mutated,n));assert(probe_finish(&p,64)==-1);checks++;}
 start(&p);assert(probe_feed(&p,63,(uint8_t*)wire,n)==-1);checks++;
 start(&p);assert(probe_feed(&p,64,(uint8_t*)wire,2305)==-1);checks++;
 start(&p);assert(!probe_feed(&p,64,(uint8_t*)wire,n));assert(!probe_feed(&p,64,(uint8_t*)"x",1));assert(probe_finish(&p,64)==-1);checks++;
 const char *bad[]={"Content-Length: 111\r\n","Transfer-Encoding: chunked\r\n","Content-Type: application/json\r\n"," Bad: folded\r\n","X\t: a\r\n","X: a\t\r\n"};
 for(unsigned i=0;i<sizeof(bad)/sizeof(bad[0]);i++){start(&p);n=response(wire,p.nonce,bad[i]);assert(!probe_feed(&p,64,(uint8_t*)wire,n));assert(probe_finish(&p,64)==-1);checks++;}
 start(&p);uint8_t nonce[32]={0},req[512];size_t len;assert(probe_request(&p,64,"a\r\nb",nonce,req,sizeof(req),&len)==-1);checks++;
 probe_close(&p);for(size_t i=0;i<sizeof(p);i++)assert(((uint8_t*)&p)[i]==0);checks++;
 printf("PASS %u BOUNDED SYNTHETIC HTTP NONCE FRAMING checks; NO TLS/WAN proof\n",checks);return 0;}
