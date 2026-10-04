"""Two actual native hardware lifetimes; target RAM/DMA is explicit host mock."""
import receiver_fixture

def one(s,a,b):
 if s.count(a)!=1:raise ValueError(f'fixture marker count {s.count(a)}: {a[:80]}')
 return s.replace(a,b)

def fixture(source):
 s=receiver_fixture.fixture(source)
 s='#include "boot_native.h"\n#include "boot_assets.h"\nconst QcaBootNative*qca_boot_view(void);\nunsigned qca_boot_round(void);\nvoid qca_boot_status(uint8_t[160]);\nstatic unsigned fault;\n'+s
 s=one(s,'static uint8_t target_ram[65536];','''static uint32_t bw(const uint8_t*p){uint32_t v=0;for(unsigned i=0;i<4;i++)v|=(uint32_t)p[i]<<(8*i);return v;}
static void bp(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
static unsigned streams,stream_bytes,stream_open,executions,main_done,uart_off,board_written,board_read;
static uint8_t target_ram[65536];
static void reset_target(void){
 memset(target_ram,0,sizeof(target_ram));const uint32_t words[9]={0x404d90,0x404e50,8,0,0,0,0,3,1};
 for(unsigned i=0;i<9;i++){bp(target_ram+0x1ee0+4*i,words[i]);}
 bp(target_ram+0x8f8,0x401ee0);
 bp(target_ram+0x854,fault==4?0: fault==5?0x404d90:0x408000);
}''')
 s=one(s,'if(!value&&scenario!=4){memset(registers,0,sizeof(registers));','if(!value&&scenario!=4){if(qca_boot_round())reset_target();memset(registers,0,sizeof(registers));')
 start=s.index('  if(!id&&index==0x3c');end=s.index('  return 0;',start)
 s=s[:start]+r'''
  if(!id&&index==0x3c&&(config[1]&4)){
   assert(get(296)==31&&cpu_issued&&allocations==14);const uint8_t*tx=hosts[1];uint32_t op=bw(tx);unsigned reply_n=0;
   if(op==8){reply_n=12;bp(hosts[3],12);bp(hosts[3]+4,0x05020001);bp(hosts[3]+8,8);}
   else{
    assert(qca_boot_round());
    if(op==13){unsigned address=bw(tx+4);if(address){assert(address==0x1234&&!stream_open);streams++;stream_open=1;stream_bytes=0;}
     else{assert(stream_open&&stream_bytes==(streams<=2?24196:727128));stream_open=0;}}
    else if(op==14){
     assert(stream_open&&streams>=1&&streams<=3);unsigned n=bw(tx+4);assert(n&&n<=248&&!(n&3));
     const uint8_t*asset=streams<=2?boot_helper:qca_boot_view()->plan.assets.main;unsigned total=streams<=2?sizeof(boot_helper):727125;
     assert(asset&&stream_bytes+n<=((total+3)&~3u));for(unsigned i=0;i<n;i++)assert(tx[8+i]==(stream_bytes+i<total?asset[stream_bytes+i]:0));stream_bytes+=n;
    }else if(op==4){
     assert(!stream_open&&bw(tx+4)==0x1234&&executions<2);assert(bw(tx+8)==(executions?0:0x10));executions++;reply_n=4;bp(hosts[3],fault==1&&executions==2?1:0);
    }else if(op==2||op==3){
     unsigned addr=bw(tx+4),n=bw(tx+8);assert(addr>=0x400800&&addr<0x410000&&n&&n<=244&&addr-0x400000+n<=65536);unsigned off=addr-0x400000;
     if(op==3){memcpy(target_ram+off,tx+12,n);if(addr>=0x408000){assert(addr==0x408000+board_written&&n<=8124-board_written&&!memcmp(tx+12,boot_board+board_written,n));board_written+=n;}
      if(addr==0x400814){assert(streams==3&&!stream_open&&!bw(tx+12));uart_off++;}}
     else{reply_n=n;memcpy(hosts[3],target_ram+off,n);if(addr>=0x408000)board_read+=n;}
    }else{assert(op==1&&streams==3&&!stream_open&&uart_off==1&&board_written==8124&&board_read==8124);main_done++;}
   }
   registers[0][0x44/4]=value;
   if(reply_n){registers[1][0x48/4]=registers[1][0x40/4];unsigned ri=(registers[1][0x40/4]-1)&7;hosts[2][ri*8+4]=(uint8_t)reply_n;hosts[2][ri*8+5]=(uint8_t)(reply_n>>8);}
  }
  if(id==1&&index==0x40&&main_done&&fault!=3){
   unsigned ri=(value-1)&7;memset(hosts[3],0,20);hosts[3][2]=12;hosts[3][8]=fault==2?2:1;hosts[3][10]=8;hosts[3][12]=0;hosts[3][13]=1;hosts[3][14]=9;hosts[3][16]=1;hosts[3][17]=1;
   hosts[2][ri*8+4]=20;hosts[2][ri*8+5]=0;registers[1][0x48/4]=value;
  }
''' +s[end:]
 # A valid SMBIOS3 table with no optional board suffix. Actual collection runs.
 insertion=r'''
static uint8_t sm_entry[24],sm_table[6]={127,4,0,0,0,0};
static struct {Guid guid;void*address;} sm_config;
static Status EFIAPI sm_map(uint64_t*n,void*p,uint64_t*k,uint64_t*d,uint32_t*v){
 assert(*n==65536);memset(p,0,40);*n=40;*d=40;*k=1;*v=1;uint64_t pages=UINT64_MAX/4096;memcpy((uint8_t*)p+24,&pages,8);return 0;
}
static void sm_fixture(void){
 const Guid g={0xf2fd1544,0x9794,0x4a2c,{0x99,0x2e,0xe5,0xbb,0xcf,0x20,0xe3,0x94}};
 sm_config.guid=g;sm_config.address=sm_entry;port_system.configuration=&sm_config;port_system.tables=1;boot[56/8]=(void*)sm_map;
 memcpy(sm_entry,"_SM3_",5);sm_entry[6]=24;sm_entry[7]=3;uint32_t n=sizeof(sm_table);memcpy(sm_entry+12,&n,4);uint64_t a=(uintptr_t)sm_table;memcpy(sm_entry+16,&a,8);
 unsigned sum=0;for(unsigned i=0;i<24;i++)sum+=sm_entry[i];sm_entry[5]=(uint8_t)(0u-sum);
}
'''
 s=one(s,'static void*ram_blocks[2];',insertion+'\nstatic void*ram_blocks[2];')
 start=s.index(' const uint8_t*data;size_t bytes;assert(!qca_fw_pin');end=s.index('\n}\n',start)
 s=s[:start]+r'''
 assert(allocations==14&&dma_frees==14&&unmaps==14&&opens==closes&&!(config[1]&4));
 allocations=dma_frees=unmaps=0;memset(hosts,0,sizeof(hosts));unsigned cancel_called=0;
 for(unsigned ms=15001;ms<60000;ms++){
  tick(ms);const QcaBootNative*b=qca_boot_view();
  if((fault==6&&b->plan.phase==7)||(fault==7&&b->plan.phase==17)){if(!cancel_called++){assert(qca_stop()&&!ram_frees&&r->asset.pinned);}}
  if(get(128)==18&&b->plan.submitted&&b->phase!=6&&b->phase!=5){
   assert(r->asset.pinned);
   uint8_t request[4]={0x12,6,0,0},reply[8]={0};
   assert(qca_ram_att(247,request,4,reply,8)==5&&reply[4]==3);
   request[0]=0x52;assert(qca_ram_att(247,request,4,reply,8)==0);
  }
  if(qca_boot_round()&&(get(128)==5||get(128)==6))break;
 }
 const QcaBootNative*b=qca_boot_view();fprintf(stderr,"SECOND phase=%u error=%u plan=%u/%u streams=%u exec=%u stage=%u/%u pins=%u alloc=%u free=%u open=%u close=%u\n",b->phase,b->error,b->plan.phase,b->plan.error,streams,executions,get(128),get(136),r->asset.pinned,allocations,dma_frees,opens,closes);
 assert(qca_boot_round()&&get(128)==(fault?6u:5u)&&allocations==14&&dma_frees==14&&unmaps==14&&opens==closes&&!r->asset.pinned);
 if(!fault)assert(b->phase==5&&b->plan.phase==20&&!b->error&&b->ready_bytes==20&&executions==2&&streams==3&&main_done==1);
 else if(fault<=5)assert(b->phase==6&&b->error);
 else assert(b->phase==1&&!b->error&&!main_done);
 uint8_t status[160];qca_boot_status(status);printf("QWBT_MOCK=");for(unsigned i=0;i<160;i++)printf("%02x",status[i]);puts("");
 /* Actual callback must return legacy writes to the resident after cleanup,
    including fault/cancellation paths; the completed RAM asset stays sealed. */
 for(unsigned opcode=0x12;opcode<=0x52;opcode+=0x40){
  uint8_t request[4]={(uint8_t)opcode,0,0,0},reply[247]={0};
  for(unsigned handle=1;handle<=12;handle++){
   request[1]=(uint8_t)handle;assert(qca_ram_att(247,request,4,reply,247)==SIZE_MAX);
  }
  for(unsigned handle=13;handle<=19;handle++){
   request[1]=(uint8_t)handle;size_t n=qca_ram_att(247,request,4,reply,247);
   assert(n==(opcode==0x12?5u:0u));if(n)assert(reply[4]==3);
  }
 }
 puts("LEGACY WRITES BLOCKED WHILE OWNED; DELEGATED AFTER COMPLETE CLEANUP; ASSET SEALED PASS");
 assert(!qca_stop()&&ram_frees==2&&!qca_fwp_owned(r));
 printf("ACTUAL ENTRYPOINT TWO LIFETIMES fault%u PASS; SYNTHETIC RADIO/HTC ONLY\n",fault);
''' +s[end:]
 s=one(s,'assert(argc==3);','assert(argc==4);fault=(unsigned)atoi(argv[3]);assert(fault<=7);')
 s=one(s,' qca_start(&port_system,0);',' sm_fixture();\n qca_start(&port_system,0);')
 start=s.index(' if(initial==0){upload_fixture(argv[2]);}')
 s=s[:start]+''' assert(initial==0&&get(128)==5&&!(config[1]&4));upload_fixture(argv[2]);return 0;\n}\n'''
 return s
