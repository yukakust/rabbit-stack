import config_read_fixture as prior

def fixture(source):
 s=prior.fixture(source)
 s=s.replace('get(780)==0x20','get(780)==0')
 s=s.replace('assert(scenario<=18||(scenario>=100&&scenario<=110))','assert(scenario<=18||(scenario>=100&&scenario<=110)||(scenario>=200&&scenario<=244))')
 s=s.replace('static Status EFIAPI read_config', 'static uint8_t target_ram[65536];static unsigned cpu_issued;\nstatic Status EFIAPI read_config')
 s=s.replace('baseline();config[1]|=', 'baseline();\n const uint32_t initial_state[9]={initial==220?0:initial==221?0x401ee0:initial==222?0x404d91:0x404d90,initial==223?0x404d90:0x404e50,8,0,0,0,0,3,1};\n for(unsigned k=0;k<36;k++)target_ram[0x1ee0+k]=(uint8_t)(initial_state[k/4]>>(8*(k%4)));\n target_ram[0x8cc]=initial==224?0x10:0;\n target_ram[0x8f8]=0xe0;target_ram[0x8f9]=0x1e;target_ram[0x8fa]=0x40;\n config[1]|=')
 start=s.index('  if(id==7&&index==0x3c&&(config[1]&4)){');end=s.index('  if(!id&&index==0x3c',start)
 s=s[:start]+'  if(id==7&&index==0x3c&&(config[1]&4)){\n   unsigned si=(value-1)&7,ri=(registers[7][0x40/4]-1)&7;\n   const uint8_t*tx=hosts[10]+si*8;uint8_t*rx=hosts[12]+ri*8;\n   uint32_t src=0,dst=0;for(unsigned j=0;j<4;j++){src|=(uint32_t)tx[j]<<(j*8);dst|=(uint32_t)rx[j]<<(j*8);}\n   unsigned bytes=tx[4]|((unsigned)tx[5]<<8);int write=src==0x10b000;\n   uint32_t address=(write?dst:src);assert(address>=0xd1100000&&address<0xd1110000);\n   unsigned offset=address&0xffff;\n   assert(allocations==14&&boot_regs[2]==0&&!(boot_regs[0]&0x800)&&!tx[6]&&!tx[7]);\n   assert(write||dst==0x10d000);assert(bytes<=204);\n   int setup=get(280)==1||write;unsigned op=get(288);\n   if(write){\n    assert(setup&&!(op&1)&&get(300)<=5);\n    if(offset==0x8cc)assert(op==8&&get(292)==15&&get(296)==15);\n    for(unsigned j=0;j<bytes;j++)target_ram[offset+j]=hosts[11][j];\n   }\n   int timeout=scenario==101||scenario==102||(scenario==106&&offset==0x1ee0)||(scenario==107&&offset==0x900)||(scenario==108&&offset==0x8cc)||(scenario>=200&&scenario<=209&&setup&&op==(unsigned)(scenario-200));\n   if(scenario!=101)registers[7][0x44/4]=value;\n   if(!timeout){\n    registers[7][0x48/4]=registers[7][0x40/4];\n    rx[4]=(scenario==103||(scenario==109&&offset==0x1ee0))?5:(uint8_t)bytes;\n    if(!write){for(unsigned j=0;j<bytes;j++)hosts[13][j]=target_ram[offset+j];\n     if(scenario==104&&offset==0x8f8)hosts[13][1]=0x20;\n     if(scenario>=210&&scenario<=214&&setup&&op==(unsigned)(2*(scenario-210)+1))hosts[13][0]^=1;\n    }\n   }\n   if(scenario==105||(scenario==110&&offset==0x1ee0))config[1]&=~4u;\n  }\n'+s[end:]
 start=s.index('  if(!id&&index==0x3c');end=s.index('  return 0;',start)
 s=s[:start]+'  if(!id&&index==0x3c&&(config[1]&4)){\n   assert(get(296)==31&&cpu_issued);assert(hosts[1][0]==8&&!hosts[1][1]);\n   registers[0][0x44/4]=value;\n   if(scenario!=240){\n    registers[1][0x48/4]=registers[1][0x40/4];unsigned ri=(registers[1][0x40/4]-1)&7;\n    hosts[2][ri*8+4]=scenario==241?13:12;\n    uint32_t words[3]={12,scenario==242?0:0x05020001,7};\n    for(unsigned j=0;j<12;j++)hosts[3][j]=(uint8_t)(words[j/4]>>(8*(j%4)));\n   }\n  }\n'+s[end:]
 s=s.replace('boot_regs[index]=v;', 'if(off==0x3a000&&(v&0x2000)){cpu_issued=1;assert(get(292)==31&&get(296)==31);if(scenario==243)config[1]&=~4u;v&=~0x2000u;}boot_regs[index]=v;')
 s=s.replace('if(initial>=106){','if(initial>=106&&initial<=110){')
 s=s.replace('initial==18||initial==100','initial==18||initial==100||initial==244')
 s=s.replace(')?4000u:1u)', ')?4000u:((initial==244&&get(316)==1)?4000u:1u))')
 s=s.replace('tick(ms);','{tick(ms);if(initial>=230&&initial<=239&&get(280)==1&&get(288)==(unsigned)(initial-230))(void)qca_stop();}')
 s=s.replace('qca_diagnostic[3]=17;', 'qca_diagnostic[3]=18;').replace('QPD17_MOCK=', 'QPD18_MOCK=')
 needle=' assert(!(config[1]&4));\n qca_diagnostic[0]'
 extra=' if(initial==0||initial==1||initial==5||initial==18||initial==100||initial==244){assert(get(280)==4&&!get(284)&&get(292)==31&&get(296)==31&&get(300)==5&&get(304)&&get(316)==2&&get(324)==0x05020001&&get(328)==7);}\n if(initial>=200&&initial<=224){assert(get(280)==5&&get(284));if(initial>=220)assert(!get(300));}\n assert(!(config[1]&4));\n qca_diagnostic[0]'
 assert needle in s;s=s.replace(needle,extra)
 return s
