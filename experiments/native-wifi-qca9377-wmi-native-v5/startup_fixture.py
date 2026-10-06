"""Extend unchanged actual native47 fixture with explicit INIT target events."""
from operating_fixture import fixture as previous
from startup_build import one
from pathlib import Path
import re,struct
READY=r'''
   unsigned ri=(registers[2][0x40/4]-1)&7;uint8_t*p=hosts[5];memset(p,0,2048);
   p[0]=1;p[2]=44;bp(p+8,2);bp(p+12,36|(35u<<16));
   bp(p+16,startup_fault==4?0:0x01000000);bp(p+20,startup_fault==15?53:574);
   bp(p+24,startup_fault==16?0:0x5f414351);bp(p+28,0x4c4d);p[40]=startup_fault==6?1:2;p[45]=1;
   bp(p+48,startup_fault==5?1:0);
   unsigned length=52;
   if(startup_fault==22){bp(p+12,52|(35u<<16));p[2]=60;length=68;}
   if(startup_fault==0||startup_fault==13){
    p[1]=2;p[2]=52;p[4]=8;p[52]=1;p[53]=4;p[56]=1;p[57]=startup_fault==13?3:1;length=60;
   }
   if(startup_fault==17)p[0]=2;
   hosts[4][ri*8+4]=(uint8_t)length;hosts[4][ri*8+5]=0;registers[2][0x48/4]=registers[2][0x40/4];
'''
def fixture(source):
 s=previous(source)
 table=(Path(__file__).resolve().parent.parent/'native-wifi-qca9377-v1/init_tables_native.h').read_text()
 values=[int(v,0) for v in re.findall(r'0x[0-9a-fA-F]+|\b\d+\b',re.search(r'qca_setup_services\[204\]=\{(.*?)\};',table,re.S)[1])]
 rows=[struct.unpack('<III',bytes(values[i:i+12])) for i in range(0,len(values),12)]
 tx=[pipe for service,direction,pipe in rows if service==256 and direction==2];assert tx==[3]
 s='#define FW_WMI_TX '+str(tx[0])+'\n#include "startup.h"\nconst QcaWmiStartup*qca_wmi_startup_view(void);\nsize_t qca_wmi_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);\n'+s
 s=one(s,'static unsigned fault;','static unsigned fault;static unsigned startup_fault,init_posts;')
 s=one(s,'assert(argc==4);fault=','assert(argc==5);startup_fault=(unsigned)atoi(argv[4]);assert(startup_fault<=22);fault=')
 marker='  if(main_done&&id==2&&index==0x40&&available_delivered){'
 code=r'''
  if(main_done&&qca_wmi_startup_view()->phase==1){
   if(id==0&&index==0x3c)assert(!"WMI INIT incorrectly sent on CE0");
   if(id==1&&index==0x40)return 0;
   if(id==2&&index==0x40){
    if(startup_fault==9)return 1;
    if(startup_fault==14&&qca_wmi_startup_view()->transaction.ready_seen){
'''+READY+r'''
    }
    return 0;
   }
   if(id==FW_WMI_TX&&index==0x3c){
    const uint8_t*t=hosts[7];init_posts++;assert(init_posts==1&&t[0]==1&&t[1]==1);
    assert((t[2]|((unsigned)t[3]<<8))==220&&t[8]==1&&!t[9]&&!t[10]&&!t[11]);
    unsigned ti=(value-1)&7;assert((hosts[6][ti*8+6]|((unsigned)hosts[6][ti*8+7]<<8))==4);
    /* Exact reference resource words and no extra mapped host chunks. */
    assert(t[48]==4&&t[52]==33&&t[40]==0&&t[41]==0&&t[42]==0&&t[43]==0);
    if(startup_fault!=1&&startup_fault!=3&&startup_fault!=14)registers[FW_WMI_TX][0x44/4]=value;
    if(startup_fault!=2){
'''+READY+r'''
    }
    if(startup_fault==7)a_dummy_marker=0;
    if(startup_fault==8)return 1; /* Ambiguous INIT TX doorbell. */
    return 0;
   }
  }
'''
 # Mutate actual bookkeeping only in the explicitly mocked target test.
 code=code.replace('if(startup_fault==7)a_dummy_marker=0;','if(startup_fault==7){QcaWmiStartup*w=(QcaWmiStartup*)qca_wmi_startup_view();w->operating->boot->board->setup->read.full.adapter->channels.rings[3].cookie[(value-1)&7]=0x999;}')
 s=one(s,marker,code+marker)
 marker='  tick(ms);const QcaBootNative*b=qca_boot_view();'
 s=one(s,marker,r'''
  const QcaWmiStartup*w=qca_wmi_startup_view();
  if(startup_fault==1&&w->transaction.ready_seen)registers[FW_WMI_TX][0x44/4]=registers[FW_WMI_TX][0x3c/4];
  if(startup_fault==10&&w->tx_posted)qca_wmi_startup_cancel((QcaWmiStartup*)w);
  if(startup_fault==18&&w->transaction.phase==QCA_INIT_RESERVED)qca_wmi_startup_cancel((QcaWmiStartup*)w);
  if(startup_fault==19&&w->tx_posted)((QcaWmiStartup*)w)->last=UINT64_MAX;
  if(startup_fault==21&&w->tx_posted)assert(qca_stop());
  if(startup_fault==20&&w->tx_posted)((QcaWmiStartup*)w)->operating->boot->asset->poisoned=1;
'''+marker)
 # Modify validated SERVICE_READY requests/map before the INIT candidate starts.
 marker='     if(fault==40)bp(p+20,0);'
 assert s.count(marker)==2
 s=s.replace(marker,marker+r'''
     if(startup_fault==11){
      bp(p+88,1);bp(p+316,20|(18u<<16));bp(p+320,16|(34u<<16));
      bp(p+324,0);bp(p+328,8);bp(p+332,0);bp(p+336,1);
      p[2]=76;p[3]=1;hosts[4][ri*8+4]=84;hosts[4][ri*8+5]=1;
     }
     if(startup_fault==12){bp(p+184,4|(16u<<16));bp(p+192,18u<<16);p[2]=188;p[3]=0;hosts[4][ri*8+4]=196;hosts[4][ri*8+5]=0;}
''')
 s=one(s,'if(!fault||fault==16||fault==24||fault==32||fault==35)assert(o->phase==2&&!o->error','if(startup_fault==20)assert(o->phase==3&&o->error==2);else if(!fault||fault==16||fault==24||fault==32||fault==35)assert(o->phase==2&&!o->error')
 # Parent handshake remains successful for all startup scenarios. Outer stage
 # may fault, but every actual DMA owner/pin must still be released.
 s=one(s,'get(128)==(fault&&fault!=16&&fault!=24&&fault!=32&&fault!=35?6u:5u)', 'get(128)==((startup_fault==0||startup_fault==1||startup_fault==15||startup_fault==22)?5u:6u)')
 marker=' printf("OPERATING_MOCK phase%u/error%u tx%u rx%u fault%u SAFE RELEASE PASS\\n",o->phase,o->error,o->tx_count,o->rx_count,fault);'
 extra=r'''
 const QcaWmiStartup*w=qca_wmi_startup_view();
 if(startup_fault==0||startup_fault==1||startup_fault==15||startup_fault==22){
  assert(w->phase==2&&!w->error&&w->transaction.phase==QCA_INIT_RUNNING&&w->transaction.ready_seen&&w->transaction.tx_complete);
  assert(w->transaction.ready.mac[0]==2&&w->transaction.ready.mac[5]==1&&w->transaction.ready.abi_minor==(startup_fault==15?53u:574u));
  fprintf(stderr,"INIT COUNTS tx=%u rx=%u posted=%u available=%u outstanding=%u\n",w->tx_count,w->rx_count,w->tx_posted,o->control.credit.available,o->control.credit.outstanding);
  assert(w->tx_count==1&&w->rx_count==1&&!w->tx_posted&&o->control.credit.available==(o->control.credit.total-(startup_fault==0?0u:1u))&&o->control.credit.outstanding==(startup_fault==0?0u:1u));
 }else{
  assert(w->phase==3&&w->error);
  if(startup_fault==11||startup_fault==12)assert(!w->transaction.phase&&!init_posts);
  if(startup_fault==18)assert(w->transaction.phase==QCA_INIT_CANCELLED&&!init_posts&&o->control.credit.available==o->control.credit.total);
  if(startup_fault==8||startup_fault==9)assert(w->error==(startup_fault==8?18u:14u));
 }
 uint8_t init_request[7]={0x10,26,0,255,255,0,0x28},init_reply[247];
 assert(qca_wmi_att(247,init_request,7,init_reply,sizeof(init_reply))==22&&init_reply[2]==26&&init_reply[4]==28&&init_reply[6]==0x26);
 init_request[0]=8;init_request[1]=27;init_request[6]=0x28;init_request[5]=3;
 assert(qca_wmi_att(247,init_request,7,init_reply,sizeof(init_reply))==23&&init_reply[2]==27&&init_reply[5]==28&&init_reply[7]==0x27);
 init_request[0]=0x0a;init_request[1]=28;
 assert(qca_wmi_att(247,init_request,3,init_reply,sizeof(init_reply))==245&&!memcmp(init_reply+1,"QWIN0002",8));
 assert(!memcmp(init_reply+117,w->prefix,128));
 assert(init_reply[97]==w->reject_reason&&init_reply[105]==w->prefix_bytes);
 if(startup_fault==4||startup_fault==5||startup_fault==6||startup_fault==14)assert(w->reject_reason);
 assert(init_reply[9]==w->phase&&init_reply[13]==w->error&&init_reply[57]==w->transaction.ready.mac[0]);
 init_request[0]=0x0c;init_request[3]=244;init_request[4]=0;
 assert(qca_wmi_att(247,init_request,5,init_reply,sizeof(init_reply))==1);
 init_request[3]=245;assert(qca_wmi_att(247,init_request,5,init_reply,sizeof(init_reply))==5&&init_reply[4]==7);
 init_request[0]=0x12;assert(qca_wmi_att(247,init_request,3,init_reply,sizeof(init_reply))==5&&init_reply[4]==3);
 init_request[0]=0x52;assert(!qca_wmi_att(247,init_request,3,init_reply,sizeof(init_reply)));
 printf("WMI_INIT_MOCK phase%u/error%u transaction%u tx%u rx%u fault%u ALL14 RELEASED PASS\n",w->phase,w->error,w->transaction.phase,w->tx_count,w->rx_count,startup_fault);
'''
 s=one(s,marker,extra+marker)
 return s
