#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <signal.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <unistd.h>
static unsigned checks;
#define CHECK(x) do{assert(x);checks++;}while(0)
extern uint64_t qca_run_stack(uint64_t,uint64_t*,void*);
void*qca_memcpy(void*,const void*,size_t);void*qca_memset(void*,int,size_t);int qca_memcmp(const void*,const void*,size_t);size_t qca_strlen(const char*);void*qca_memchr(const void*,int,size_t);
static void memory_tests(void){
 uint8_t source[4112],a[4112],b[4112];for(unsigned j=0;j<sizeof(source);j++)source[j]=(uint8_t)(j*13+1);
 for(size_t n=0;n<=4096;n++)for(unsigned off=0;off<8;off++){
  memset(a,0x42,sizeof(a));memset(b,0x42,sizeof(b));CHECK(qca_memcpy(a+off,source+off,n)==a+off);memcpy(b+off,source+off,n);CHECK(!memcmp(a,b,sizeof(a)));
  CHECK(qca_memset(a+off,0xac,n)==a+off);memset(b+off,0xac,n);CHECK(!memcmp(a,b,sizeof(a)));
  CHECK(qca_memcmp(a,b,sizeof(a))==0);if(n){b[off+n-1]^=1;int x=qca_memcmp(a,b,sizeof(a)),y=memcmp(a,b,sizeof(a));CHECK((x<0)==(y<0)&&(x>0)==(y>0));}
  CHECK(qca_memchr(source+off,0xa4,n)==memchr(source+off,0xa4,n));
 }
 char text[4097];memset(text,'x',sizeof(text));for(size_t n=0;n<=4096;n++){text[n]=0;CHECK(qca_strlen(text)==strlen(text));text[n]='x';}
}
static void fault_case(uint8_t*low,uint8_t*top,int middle){
 pid_t pid=fork();CHECK(pid>=0);if(!pid){struct rlimit lim={0,0};setrlimit(RLIMIT_CORE,&lim);if(middle)assert(!mprotect(low+32768,4096,PROT_NONE));uint64_t out[3];qca_run_stack(middle?49152:65536,out,top);_exit(7);}
 int status;CHECK(waitpid(pid,&status,0)==pid);CHECK(WIFSIGNALED(status)&&WTERMSIG(status)==SIGSEGV);
}
int main(int argc,char**argv){
 if(argc>1&&!strcmp(argv[1],"memory")){memory_tests();printf("PASS %u real runtime memory shims ASAN/UBSAN\n",checks);return 0;}
 CHECK(sysconf(_SC_PAGESIZE)==4096);uint8_t*m=mmap(0,73728,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);CHECK(m!=MAP_FAILED);uint8_t*low=m+4096,*top=low+65536;CHECK(!mprotect(low,65536,PROT_READ|PROT_WRITE));memset(low,0x55,65536);
 const uint64_t sizes[]={0,1,4095,4096,4097,8192,16384,32768,65500};
 for(unsigned j=0;j<sizeof(sizes)/sizeof(sizes[0]);j++){uint64_t out[3]={0};CHECK(qca_run_stack(sizes[j],out,top)==sizes[j]);CHECK(out[0]==out[1]&&out[2]==UINT64_C(0x1234567812345678));}
 for(unsigned j=0;j<65536-128;j++)CHECK(low[j]==0x55);fault_case(low,top,0);fault_case(low,top,1);CHECK(!munmap(m,73728));printf("PASS %u actual LLVM probe guarded-stack/register preservation/page-crossing\n",checks);return 0;
}
