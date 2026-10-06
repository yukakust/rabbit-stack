"""Offline native52 + reviewed persistent bridge + bounded RX pump."""
import importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CHECKED=ROOT.parent/'native-wifi-qca9377-wmi-native-v5'
BRIDGE=ROOT.parent/'native-wifi-qca9377-persistent-native-v1'
sys.path.insert(0,str(CHECKED));import startup_build as checked
spec=importlib.util.spec_from_file_location('reviewed_persistent_build',BRIDGE/'persistent_build.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
prior.checked=checked;prior.CHECKED=CHECKED;one=checked.one
def sources(directory):
 prior.sources(directory) # Exact reviewed transformations on native52 sources.
 for n in ('rx.h','rx.c'):(directory/n).write_bytes((ROOT/n).read_bytes())
 p=directory/'persistent.h';s=p.read_text()
 s=one(s,'#include "lifecycle.h"','#include "lifecycle.h"\n#include "rx.h"')
 s=one(s,'QcaWmiStartup *startup; QcaRadioLifecycle life;','QcaWmiStartup *startup; QcaRadioLifecycle life; QcaPersistentRx rx;')
 p.write_text(s)
 p=directory/'persistent.c';s=p.read_text()
 s=one(s,'if(!qca_radio_begin(&s->life,&o,now)){s->error=31;return -1;}',
  '''if(!qca_radio_begin(&s->life,&o,now)){s->error=31;return -1;}
 if(!qca_rx_begin(&s->rx,w,&s->life,now)){
  s->error=32;(void)qca_radio_observe(&s->life,0,now);return -1;
 }''')
 s=one(s,'if(s->polls!=UINT32_MAX)s->polls++;',
  '''if(qca_radio_accepts_work(&s->life)&&qca_rx_poll(&s->rx,&s->life,now)<0){
  s->error=33;(void)qca_radio_observe(&s->life,0,now);return -1;
 }
 if(s->polls!=UINT32_MAX)s->polls++;''')
 p.write_text(s)
