#include "board_smbios.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t entry[24],table[64];static void*boot[8];
static struct {Guid guid;void*address;} configuration;
static unsigned mode;
static Status EFIAPI memory_map(uint64_t*n,void*p,uint64_t*k,uint64_t*d,uint32_t*v){
 assert(*n==65536);memset(p,0,40);*n=40;*d=mode==2?39:40;*k=1;*v=1;
 uint32_t type=mode==3?11:0;memcpy(p,&type,4);uint64_t pages=UINT64_MAX/4096;memcpy((uint8_t*)p+24,&pages,8);return mode==1?1:0;
}
static void crc(void){entry[5]=0;unsigned sum=0;for(unsigned i=0;i<24;i++)sum+=entry[i];entry[5]=(uint8_t)(0u-sum);}
int main(void){
 QcaBoardSmbios s={0};unsigned tests=0;
 uint8_t normal[]={0xf8,9,0,0,0,0,0,0,1,'B','D','F','_','D','E','L','L',0,0,127,4,0,0,0,0};
 assert(!qca_board_smbios_parse(&s,normal,sizeof(normal))&&s.state==3&&!strcmp(s.variant,"DELL"));tests++;
 for(unsigned n=1;n<sizeof(normal);n++){assert(qca_board_smbios_parse(&s,normal,n)==-1&&s.state==4);tests++;}
 uint8_t bad[80];memcpy(bad,normal,sizeof(normal));bad[1]=3;assert(qca_board_smbios_parse(&s,bad,sizeof(normal))==-1);tests++;
 memcpy(bad,normal,sizeof(normal));bad[13]=1;assert(qca_board_smbios_parse(&s,bad,sizeof(normal))==-1);tests++;
 memcpy(bad,normal,sizeof(normal));bad[9]='X';assert(qca_board_smbios_parse(&s,bad,sizeof(normal))==-1);tests++;
 memcpy(bad,normal,19);memcpy(bad+19,normal,sizeof(normal));assert(qca_board_smbios_parse(&s,bad,19+sizeof(normal))==-1&&s.error==5);tests++;
 memcpy(bad,normal,sizeof(normal));bad[8]=0;assert(!qca_board_smbios_parse(&s,bad,sizeof(normal))&&s.state==2&&!s.variant[0]);tests++;
 SystemTable st={0};st.header.signature=0x5453595320494249ull;st.header.size=sizeof(st);st.boot=boot;
 ((TableHeader*)boot)->signature=0x56524553544f4f42ull;((TableHeader*)boot)->size=sizeof(boot);boot[7]=(void*)memory_map;
 assert(!qca_board_smbios_collect(&s,&st)&&s.state==1);tests++;
 const Guid guid={0xf2fd1544,0x9794,0x4a2c,{0x99,0x2e,0xe5,0xbb,0xcf,0x20,0xe3,0x94}};configuration.guid=guid;configuration.address=entry;st.tables=1;st.configuration=&configuration;
 memcpy(table,normal,sizeof(normal));memcpy(entry,"_SM3_",5);entry[6]=24;entry[7]=3;uint32_t size=sizeof(normal);memcpy(entry+12,&size,4);uint64_t address=(uintptr_t)table;memcpy(entry+16,&address,8);crc();
 assert(!qca_board_smbios_collect(&s,&st)&&s.state==3&&!strcmp(s.variant,"DELL"));tests++;
 for(mode=1;mode<=3;mode++){assert(qca_board_smbios_collect(&s,&st)==-1&&s.state==4);tests++;}mode=0;
 entry[5]^=1;assert(qca_board_smbios_collect(&s,&st)==-1&&s.error==16);tests++;
 printf("SMBIOS %u malformed/truncated/ambiguous/map/checksum cases PASS; MOCK ONLY\n",tests);
}
