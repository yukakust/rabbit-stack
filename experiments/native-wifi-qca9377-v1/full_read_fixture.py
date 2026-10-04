"""Native14-map CE7 fixtures; never included in production sources."""
def fixture(source):
 s=source.replace('qca_diagnostic[888]','qca_diagnostic[924]').replace('assert(scenario<=18)','assert(scenario<=18||(scenario>=100&&scenario<=105))')
 start=s.index('  if(id==7&&index==0x3c&&(config[1]&4)){');end=s.index('  if(!id&&index==0x3c',start)
 s=s[:start]+'''  if(id==7&&index==0x3c&&(config[1]&4)){
   unsigned si=(value-1)&7,ri=(registers[7][0x40/4]-1)&7;
   const uint8_t*tx=hosts[10]+si*8,*rx=hosts[12]+ri*8;
   uint32_t addr=(uint32_t)tx[0]|((uint32_t)tx[1]<<8)|((uint32_t)tx[2]<<16)|((uint32_t)tx[3]<<24);
   uint32_t response=(uint32_t)rx[0]|((uint32_t)rx[1]<<8)|((uint32_t)rx[2]<<16)|((uint32_t)rx[3]<<24);
   assert(addr==0xd11008f8&&tx[4]==4&&!tx[5]&&!tx[6]&&!tx[7]);
   assert(response==0x10d000&&!rx[4]&&!rx[5]&&!rx[6]&&!rx[7]);
   assert(allocations==14&&boot_regs[2]==0&&!(boot_regs[0]&0x800));
   if(scenario!=101){registers[7][0x44/4]=value;}
   if(scenario!=101&&scenario!=102){
    registers[7][0x48/4]=registers[7][0x40/4];
    hosts[12][ri*8+4]=scenario==103?5:4;
    uint32_t result=scenario==104?0x00402000:0x00401ee0;
    for(unsigned k=0;k<4;k++)hosts[13][k]=(uint8_t)(result>>(8*k));
   }
   if(scenario==105)config[1]&=~4u;
  }
'''+s[end:]
 s=s.replace('ms<(initial==18?60000u:15000u)','ms<((initial==18||initial>=100)?60000u:15000u)')
 s=s.replace(')?600u:1u',')?600u:((initial==100&&get(888)==1)?4000u:1u)')
 s=s.replace('initial==0||initial==1||initial==5||initial==18','initial==0||initial==1||initial==5||initial==18||initial==100')
 s=s.replace("qca_diagnostic[3]=15;","qca_diagnostic[3]=16;").replace('QPD15_MOCK=','QPD16_MOCK=').replace('i<888','i<924')
 needle=' assert(!(config[1]&4));\n qca_diagnostic[0]';extra=''' if(initial==0||initial==1||initial==5||initial==18||initial==100){
  assert(get(888)==2&&!get(892)&&get(896)==0x00401ee0&&get(900)==4&&get(904)&&get(908)&&get(912)==3&&get(916));
  if(initial==100)assert(get(920)>=3000000);
 }
 if(initial>=101){assert(get(892)&&!get(220)&&!get(236)&&!get(816)&&!get(852));}
 assert(!(config[1]&4));
 qca_diagnostic[0]'''
 assert needle in s;s=s.replace(needle,extra)
 return s
