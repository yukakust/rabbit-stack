"""NEW63 synthetic target drives actual authenticated native/driver entrypoints."""
import importlib.util,sys
import filter63_build as build
OLD=build.E/'native-wifi-qca9377-scan61-native-v1'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
oldbuild=load('filter63_frozen_scan61_build',OLD/'scan_build.py')
saved=sys.modules.get('scan_build');sys.modules['scan_build']=oldbuild
try:old=load('filter63_frozen_scan61_fixture',OLD/'scan_fixture.py')
finally:
 if saved is None:sys.modules.pop('scan_build',None)
 else:sys.modules['scan_build']=saved
one=build.one
def fixture(source):
 s=old.fixture(source).replace('==61','==63')
 s=s.replace('assert((persistent_fault||rx_scenario||(w->phase==2', 'fprintf(stderr,"STARTUP phase=%u err=%u transaction=%u ready=%u tx=%u rx=%u early=%u\\n",w->phase,w->error,w->transaction.phase,w->transaction.ready_seen,w->transaction.tx_complete,w->rx_count,early_credit_delivered);assert((persistent_fault||rx_scenario||(w->phase==2')
 s=s.replace('(scan_posts||rx_scenario||','(filter_posts||scan_posts||rx_scenario||')
 s=s.replace('w->rx_count==1','w->rx_count==(filter_scenario==4?2u:1u)')
 s=one(s,'  if(startup_fault==1&&w->transaction.ready_seen)',r'''
  if(filter_scenario==4&&!early_credit_delivered&&w->transaction.ready_seen&&w->rx1_posted){
   QcaInitAdapter*a=w->operating->boot->board->setup->read.full.adapter;unsigned ri=a->channels.rings[1].read;uint8_t*p=hosts[3];memset(p,0,2048);p[1]=2;p[2]=8;p[4]=8;p[8]=1;p[9]=4;p[12]=1;p[13]=1;hosts[2][ri*8+4]=16;hosts[2][ri*8+5]=0;registers[1][0x48/4]=(ri+1)&7;early_credit_delivered=1;
  }
  if(startup_fault==1&&w->transaction.ready_seen)''')
 s=s.replace('if(startup_fault==1&&w->transaction.ready_seen)', 'if(startup_fault==1&&w->transaction.ready_seen&&(filter_scenario!=4||early_credit_delivered))')
 s=s.replace('if(id==1&&index==0x40)return 0;',r'''if(id==1&&index==0x40){
    if(filter_scenario==4&&!early_credit_delivered&&qca_wmi_startup_view()->transaction.ready_seen){unsigned ri=(value-1)&7;uint8_t*p=hosts[3];memset(p,0,2048);p[1]=2;p[2]=8;p[4]=8;p[8]=1;p[9]=4;p[12]=1;p[13]=1;hosts[2][ri*8+4]=16;hosts[2][ri*8+5]=0;registers[1][0x48/4]=value;early_credit_delivered=1;}return 0;}''')
 s=s.replace('assert(argc==9);','assert(argc==10);filter_scenario=(unsigned)atoi(argv[9]);')
 s='void qca_filter63_status(unsigned char[448]);\n'+s
 s=one(s,'static unsigned native_scenario,scan_posts,credit_pending,emitted,regression_emitted;','static unsigned native_scenario,scan_posts,credit_pending,emitted,regression_emitted;static unsigned filter_scenario,overflow_emitted,mixed_emitted,early_credit_delivered;static unsigned filter_posts,echo_pending,echo_delivered,htt_posts,htt_delivered;')
 marker='  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==3&&index==0x3c&&qca_scan_native_view()->tx.phase==QCA_TX_POSTED){'
 code=r'''
  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==3&&index==0x3c){
   uint8_t status[448];qca_filter63_status(status);
   if(bw(status+8)==1){
    const QcaNativeScan*sc=qca_scan_native_view();assert(sc->tx.phase==QCA_TX_POSTED&&filter_posts<3);
    const uint32_t expected[3]={0x5001,0x5002,0x1d001};assert(bw(hosts[7]+8)==expected[filter_posts]);
    filter_posts++;registers[3][0x44/4]=value;
    credit_pending+=(sc->tx.bytes+sc->tx.credit->size-1)/sc->tx.credit->size;
    if(filter_posts==3)echo_pending=1;
    return 0;
   }
  }
  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==4&&index==0x3c){
   const uint8_t*b=hosts[9];assert(!htt_posts&&b[0]==2&&!b[1]&&b[2]==4&&!b[3]&&!bw(b+8));
   htt_posts++;registers[4][0x44/4]=value;return 0;
  }
'''
 s=one(s,marker,code+marker)
 # Exact requested target with well-formed byte-array padding.
 s=s.replace('bp(b+24,57);bp(b+48,60|(17u<<16));','bp(b+24,51);bp(b+48,52|(17u<<16));')
 s=s.replace('f[37]=16;memcpy(f+38,"SILK_56E35E_Plus",16);f[54]=3;f[55]=1;f[56]=','f[37]=10;memcpy(f+38,"iPhone (9)",10);f[48]=3;f[49]=1;f[50]=')
 s=s.replace('if(native_scenario==4)b[4]=39;emit_scan_payload(b,112);','if(native_scenario==4)b[4]=39;emit_scan_payload(b,104);')
 marker='   const QcaNativeScan*sc=qca_scan_native_view();scan_observe_active();'
 code=r'''
   if(echo_pending&&!echo_delivered&&filter_scenario!=2&&filter_scenario!=6&&p->rx.posted[1]&&registers[2][0x48/4]==a->channels.rings[2].read){
    uint8_t b[12]={0};bp(b,0x1d001);bp(b+4,4|(54u<<16));bp(b+8,filter_scenario==1?0x63000002:0x63000001);emit_scan_payload(b,12);echo_delivered=1;
   }
   if(filter_scenario==6&&echo_pending&&overflow_emitted<17&&p->rx.posted[1]&&registers[2][0x48/4]==a->channels.rings[2].read){uint8_t unknown[8]={0x22,0x22,0x22};emit_scan_payload(unknown,8);overflow_emitted++;}
   if(htt_posts&&!htt_delivered&&p->rx.posted[0]&&registers[1][0x48/4]==a->channels.rings[1].read){
    deliver_rx(1,1);unsigned ri=a->channels.rings[1].read;uint8_t*b=hosts[3];memset(b,0,24);b[0]=2;b[2]=4;b[8]=0;b[9]=56;b[10]=filter_scenario==3?2:3;hosts[2][ri*8+4]=12;hosts[2][ri*8+5]=0;htt_delivered=1;
   }
'''
 s=one(s,marker,code+marker)
 s=one(s,marker,marker+r'''
   if(filter_scenario==7&&!mixed_emitted&&sc->scan.pending.started&&p->rx.posted[0]&&registers[1][0x48/4]==a->channels.rings[1].read){
    deliver_rx(1,1);unsigned ri=a->channels.rings[1].read;uint8_t*b=hosts[3];memset(b,0,24);b[0]=2;b[2]=4;b[8]=99;hosts[2][ri*8+4]=12;hosts[2][ri*8+5]=0;mixed_emitted=1;
   }
''')
 # Frozen61 final export assertions are for a different ABI/sequence. Replace
 # that exact bounded block, retaining preceding authenticated boot checks.
 start=s.index(' { tick(60001);const QcaNativeScan*sc=');end=s.index(' printf("PERSISTENT_MOCK active_ticks=',start)
 s=s[:start]+r'''
 {tick(60001);const QcaNativeScan*sc=qca_scan_native_view();uint8_t f[448];qca_filter63_status(f);
  assert(bw(f+8+44*4)==1);
  unsigned success=(native_scenario==0||native_scenario==1||native_scenario==8)&&(filter_scenario==0||filter_scenario==4||filter_scenario==7);
  if(native_scenario==3&&!filter_scenario){assert(bw(f+8)==4&&!sc->error&&!sc->scan.ssid_seen);}
  else if(success){assert(filter_posts==3&&echo_delivered&&htt_posts==1&&htt_delivered);assert(bw(f+8)==4&&!bw(f+12));assert(sc->scan.ssid_seen&&sc->scan.has_observation&&sc->scan.stop.stop.terminal_seen);}
  else {assert(bw(f+8)==5&&sc->error);if(filter_scenario)assert(!sc->scan.ssid_seen);}
  if(filter_scenario==4){const QcaWmiStartup*w=qca_wmi_startup_view();assert(early_credit_delivered&&w->rx_count==2&&w->ready_frame_bytes==52&&bw(w->prefix+8)==2&&w->frame_bytes==16);}
  if(filter_scenario==6)assert(sc->archive_count==16);
  if(filter_scenario==7)assert(mixed_emitted);
  if(success){
  assert(sc->tx.serial==sc->tx.attempted&&sc->tx.completed==sc->tx.attempted&&sc->tx.completed>=7);
  assert(bw(f+8+31*4)==3&&bw(f+8+32*4)==56&&bw(f+8+34*4));
  }
  uint8_t page[512],copy[512];for(unsigned i=0;i<110;i++){unsigned n=qca_native_scan_export(sc,i,page,512);assert(n==(i%5==4?56u:512u));assert(qca_native_scan_export(sc,i,copy,512)==n&&!memcmp(page,copy,n));}
  if(success)assert(!memcmp(sc->scan.observation.parsed.bss.ssid,"iPhone (9)",10)&&sc->scan.observation.parsed.bss.ssid_bytes==10);
  for(unsigned slot=0;slot<sc->archive_count;slot++){
   uint8_t full[2104];unsigned used=0;for(unsigned part=0;part<5;part++){uint8_t part_bytes[512];unsigned n=qca_native_scan_export(sc,slot*5+part,part_bytes,512);assert(n==(part==4?56u:512u));memcpy(full+used,part_bytes,n);used+=n;}
   const QcaRxEvent*e=&sc->archive[slot];assert(!memcmp(full,"QFEX0001",8)&&bw(full+20)==e->completion&&bw(full+44)==e->raw_bytes);
   assert(!memcmp(full+56,e->raw,e->raw_bytes));for(unsigned j=e->raw_bytes;j<2048;j++)assert(!full[56+j]);
  }
  assert(active_status_reads);assert(!prefix_driver_model_frame(&model_sf));free(model_surface);free(model_physical);prefix_driver_model_display(0,0,0,0);
  printf("FILTER63_ACTUAL_PRODUCER_SYNTHETIC filter3/ECHO/HTT3.56/passiveSSID/raw22/all14 PASS\n");}
'''+s[end:]
 return s
