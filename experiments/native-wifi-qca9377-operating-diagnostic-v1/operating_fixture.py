"""Actual generated native entrypoints and real CE code; explicit target mock."""
import boot_fixture
one=boot_fixture.one
def fixture(source):
 s=boot_fixture.fixture(source)
 s='#include "operating.h"\nconst QcaOperating*qca_operating_view(void);\n'+s
 s=one(s,'static unsigned fault;','static unsigned fault;static unsigned control_tx,rx_ready_sent;')
 marker='  if(!id&&index==0x3c&&(config[1]&4)){'
 code=r'''
  if(main_done&&id==0&&index==0x3c&&(config[1]&4)){
   const uint8_t*t=hosts[1];assert(!t[0]&&t[1]==0);unsigned msg=t[8]|((unsigned)t[9]<<8);control_tx++;
   assert(control_tx<=3&&msg==(control_tx==3?5u:2u));
   unsigned ti=(value-1)&7;assert((hosts[0][ti*8+6]|((unsigned)hosts[0][ti*8+7]<<8))==0);
   if(fault!=8)registers[0][0x44/4]=value;
   if(control_tx<3&&fault!=9){
    unsigned service=t[10]|((unsigned)t[11]<<8);assert(service==(control_tx==1?0x100u:0x300u));
    unsigned ri=(registers[1][0x40/4]-1)&7;memset(hosts[3],0,16);hosts[3][2]=8;hosts[3][8]=3;
    hosts[3][10]=(uint8_t)service;hosts[3][11]=(uint8_t)(service>>8);hosts[3][13]=control_tx==1?1:2;hosts[3][14]=0xf8;hosts[3][15]=0x0f;
    if(fault==10)hosts[3][13]=0;
    hosts[2][ri*8+4]=16;hosts[2][ri*8+5]=0;registers[1][0x48/4]=registers[1][0x40/4];
   }
   if(control_tx==1&&fault!=11){
    unsigned ri=(registers[2][0x40/4]-1)&7;uint8_t*p=hosts[5];memset(p,0,2048);p[0]=fault==12?2:1;p[2]=164;
    bp(p+8,1);bp(p+12,104|(32u<<16));bp(p+16,1234);bp(p+20,0x01000000);bp(p+24,53);bp(p+28,0x5f414351);bp(p+32,0x4c4d);bp(p+52,1);
    bp(p+120,36|(33u<<16));bp(p+124,0x60);bp(p+144,2412);bp(p+148,2472);bp(p+152,5180);bp(p+156,5825);
    bp(p+160,4|(16u<<16));bp(p+164,1);bp(p+168,18u<<16);
    if(fault==13)bp(p+20,0);
    hosts[4][ri*8+4]=172;hosts[4][ri*8+5]=0;registers[2][0x48/4]=registers[2][0x40/4];
   }
   if(fault==14)return 1; /* Unknown doorbell outcome: ownership must remain. */
   return 0;
  }
'''
 s=one(s,marker,code+marker)
 s=one(s,'if(id==1&&index==0x40&&main_done&&fault!=3){','if(id==1&&index==0x40&&main_done&&!rx_ready_sent++&&fault!=3){')
 s=one(s,'assert(fault<=7);','assert(fault<=16);')
 s=one(s,'if((fault==6&&b->plan.phase==7)||(fault==7&&b->plan.phase==17))','if((fault==6&&b->plan.phase==7)||(fault==7&&b->plan.phase==17)||(fault==15&&qca_operating_view()->control.posted))')
 old='assert(qca_boot_round()&&get(128)==(fault?6u:5u)&&allocations==14&&dma_frees==14&&unmaps==14&&opens==closes&&!r->asset.pinned);'
 s=one(s,old,'assert(qca_boot_round()&&get(128)==(fault&&fault!=16?6u:5u)&&allocations==14&&dma_frees==14&&unmaps==14&&opens==closes&&!r->asset.pinned);')
 s=one(s,'if(!fault)assert(b->phase==5','if(!fault||fault==16)assert(b->phase==5')
 s=one(s,'else assert(b->phase==1&&!b->error&&!main_done);','''else if(fault<=7)assert(b->phase==1&&!b->error&&!main_done);
 else assert(b->phase==5&&!b->error);
 const QcaOperating*o=qca_operating_view();
 if(!fault||fault==16)assert(o->phase==2&&!o->error&&o->service_valid&&o->service.build==1234&&o->control.session.phase==QCA_HTC_RUNNING&&o->tx_count==3&&o->rx_count==3);
 else if(fault>=8&&fault!=15)assert(o->phase==3&&o->error);
 printf("OPERATING_MOCK phase%u/error%u tx%u rx%u fault%u SAFE RELEASE PASS\\n",o->phase,o->error,o->tx_count,o->rx_count,fault);''')
 # Test slow responses and timeout through actual poll rather than a mock clock.
 s=one(s,'  tick(ms);const QcaBootNative*b=qca_boot_view();','''  if(fault==16&&qca_operating_view()->phase==1){
   /* RX first, TX hardware index delayed until the next cooperative poll. */
   if(qca_operating_view()->control.deferred_bytes)registers[0][0x44/4]=registers[0][0x3c/4];
  }
  tick(ms);const QcaBootNative*b=qca_boot_view();''')
 s=one(s,'if(fault!=8)registers[0][0x44/4]=value;','if(fault!=8&&(fault!=16||control_tx==3))registers[0][0x44/4]=value;')
 s=one(s,'assert(fault<=16);','assert(fault<=21);')
 marker='hosts[2][ri*8+4]=16;hosts[2][ri*8+5]=0;registers[1][0x48/4]=registers[1][0x40/4];'
 s=one(s,marker,marker+"""
    if(fault==17)hosts[2][ri*8+4]=7;
    if(fault==18)hosts[3][2]=9; /* Body length exceeds actual DMA completion. */
    if(fault==19)hosts[3][8]=1; /* Unexpected READY instead of CONNECT response. */
    if(fault==20)hosts[2][ri*8]^=4; /* Descriptor address disagreement. */
    if(fault==21)registers[1][0x48/4]=8; /* Invalid hardware index. */
 """)
 marker='printf("OPERATING_MOCK phase%u/error%u tx%u rx%u fault%u SAFE RELEASE PASS\\n",o->phase,o->error,o->tx_count,o->rx_count,fault);'
 extra="""
 if(fault==10||fault==18||fault==19){assert(o->error==4&&o->rx_diagnostic[0]==1&&o->rx_diagnostic[1]==5&&o->rx_diagnostic[7]==16&&o->rx_descriptor[4]==16);}
 if(fault==17){assert(o->error==4&&o->rx_diagnostic[1]==4&&o->rx_diagnostic[7]==7&&o->rx_prefix[7]==0);}
 if(fault==20){assert(o->error==4&&o->rx_diagnostic[1]==2&&o->rx_diagnostic[8]);}
 if(fault==21){assert(o->error==4&&o->rx_diagnostic[1]==1);}
 """
 s=one(s,marker,extra+marker)
 return s
