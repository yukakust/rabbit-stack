#include <stddef.h>
#include <assert.h>
#include <stdio.h>
char*rabbit_checked_strncpy(char*,const char*,size_t);
long labs(long);
int main(void){assert(labs(-10000)==10000&&labs(0)==0&&labs(10000)==10000);char b[5]={1,1,1,1,9};assert(rabbit_checked_strncpy(b,"xy",4)==b&&b[0]=='x'&&b[1]=='y'&&!b[2]&&!b[3]&&b[4]==9);assert(rabbit_checked_strncpy(b,"longer",4)==b&&b[0]=='l'&&b[3]=='g'&&b[4]==9);assert(rabbit_checked_strncpy(b,"",0)==b&&b[4]==9);puts("PASS3boundednative-string-copycases");return 0;}
