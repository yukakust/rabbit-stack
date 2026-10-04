"""Actual native entrypoints; exact helper bytes and synthetic device replies."""
import setup_fixture
def fixture(source):
 s=setup_fixture.fixture(source).replace('get(328)==7','get(328)==8')
 s=s.replace('(scenario>=200&&scenario<=244))','(scenario>=200&&scenario<=244)||(scenario>=500&&scenario<=507))')
 s=s.replace('#include "bringup.h"','#include "bringup.h"\nvoid qca_board_status(uint8_t[160]);\n#include "board_helper.h"')
 if 'void qca_board_status' not in s:s='void qca_board_status(uint8_t[160]);\n'+s
 insertion=r'''
static uint8_t board_entry[24],board_table[32];
static struct {Guid guid;void*address;} board_config;
static uint32_t board_word(const uint8_t*p){uint32_t v=0;for(unsigned i=0;i<4;i++)v|=(uint32_t)p[i]<<(8*i);return v;}
static Status EFIAPI board_map(uint64_t*n,void*p,uint64_t*k,uint64_t*d,uint32_t*v){
 assert(*n==65536);memset(p,0,40);*n=40;*d=40;*k=1;*v=1;
 uint64_t pages=UINT64_MAX/4096;memcpy((uint8_t*)p+24,&pages,8);return 0;
}
static void smbios_fixture(void){
 port_system.header.signature=0x5453595320494249ull;port_system.header.size=sizeof(port_system);
 ((TableHeader*)boot)->signature=0x56524553544f4f42ull;((TableHeader*)boot)->size=sizeof(boot);boot[56/8]=(void*)board_map;
 const Guid g={0xf2fd1544,0x9794,0x4a2c,{0x99,0x2e,0xe5,0xbb,0xcf,0x20,0xe3,0x94}};
 board_config.guid=g;board_config.address=board_entry;port_system.configuration=&board_config;port_system.tables=1;
 const uint8_t table[]={0xf8,9,0,0,0,0,0,0,1,'B','D','F','_','D','E','L','L',0,0,127,4,0,0,0,0};
 memcpy(board_table,table,sizeof(table));memcpy(board_entry,"_SM3_",5);board_entry[6]=24;board_entry[7]=3;
 uint32_t n=sizeof(table);memcpy(board_entry+12,&n,4);uint64_t address=(uintptr_t)board_table;memcpy(board_entry+16,&address,8);
 unsigned sum=0;for(unsigned i=0;i<24;i++)sum+=board_entry[i];board_entry[5]=(uint8_t)(0u-sum);if(scenario==505)board_entry[5]^=1;
}
'''
 s=s.replace('static uint8_t target_ram', 'static unsigned helper_bytes,helper_packets,helper_stream,helper_closed,helper_executed;\nstatic uint32_t board_word(const uint8_t*);\nstatic uint8_t target_ram')
 s=s.replace('int main(int argc,char**argv){',insertion+'\nint main(int argc,char**argv){')
 s=s.replace(' qca_start(&port_system,0);',' smbios_fixture();\n qca_start(&port_system,0);')
 start=s.index('  if(!id&&index==0x3c');end=s.index('  return 0;',start)
 s=s[:start]+r'''
  if(!id&&index==0x3c&&(config[1]&4)){
   assert(get(296)==31&&cpu_issued);uint32_t op=board_word(hosts[1]);
   registers[0][0x44/4]=value;
   if(op==8){
    if(scenario!=240){
     registers[1][0x48/4]=registers[1][0x40/4];unsigned ri=(registers[1][0x40/4]-1)&7;
     hosts[2][ri*8+4]=scenario==241?13:12;
     uint32_t words[3]={12,scenario==242?0:scenario==507?0x05020002:0x05020001,scenario==506?7:8};
     for(unsigned j=0;j<12;j++)hosts[3][j]=(uint8_t)(words[j/4]>>(8*(j%4)));
    }
   }else{
    uint8_t snapshot[160];qca_board_status(snapshot);assert(allocations==14&&board_word(snapshot+100)==0x05020001&&board_word(snapshot+104)==8);
    if(op==13){
     uint32_t address=board_word(hosts[1]+4);if(address==0x1234){assert(!helper_stream);helper_stream=1;}
     else{assert(!address&&helper_stream&&helper_bytes==24196&&!helper_closed);helper_closed=1;}
    }else if(op==14){
     assert(helper_stream&&!helper_closed);unsigned bytes=board_word(hosts[1]+4);assert(bytes>0&&bytes<=248&&!(bytes&3));
     for(unsigned j=0;j<bytes;j++){unsigned off=helper_bytes+j;assert(hosts[1][8+j]==(off<sizeof(board_helper)?board_helper[off]:0));}
     helper_bytes+=bytes;helper_packets++;if(scenario==500&&helper_packets==2)registers[0][0x44/4]=(value-1)&7;
     if(scenario==503&&helper_packets==2)config[1]&=~4u;
    }else{
     assert(op==4&&board_word(hosts[1]+4)==0x1234&&board_word(hosts[1]+8)==0x10&&helper_closed&&helper_bytes==24196&&!helper_executed++);
     if(scenario!=501){
      registers[1][0x48/4]=registers[1][0x40/4];unsigned ri=(registers[1][0x40/4]-1)&7;
      hosts[2][ri*8+4]=scenario==502?3:4;uint32_t result=0x400;for(unsigned j=0;j<4;j++)hosts[3][j]=(uint8_t)(result>>(8*j));
     }
    }
   }
  }
''' +s[end:]
 s=s.replace('tick(ms);','{tick(ms);if(initial==504&&helper_packets==2)(void)qca_stop();}')
 marker=' assert(!(config[1]&4));\n qca_diagnostic[0]'
 extra=r'''
 uint8_t observation[160];qca_board_status(observation);
 assert(!memcmp(observation+128,board_helper_digest,32));
 if(initial==0){assert(helper_bytes==24196&&helper_packets==98&&helper_executed==1&&board_word(observation+8)==5&&board_word(observation+16)==101&&board_word(observation+28)==0x400&&board_word(observation+48)==1&&!memcmp(observation+68,"DELL",4));}
 if(initial>=500&&initial<=507){assert(get(128)==6&&!get(220)&&allocations==dma_frees&&unmaps==allocations);if(initial>=505)assert(!helper_packets&&!helper_executed);}
 printf("QBDI_MOCK=");for(unsigned i=0;i<160;i++)printf("%02x",observation[i]);puts("");
 assert(!(config[1]&4));
 qca_diagnostic[0]'''
 assert marker in s;s=s.replace(marker,extra)
 return s
