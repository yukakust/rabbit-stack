"""Offline derivation only: counter50 identity retained, no admission/signing."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CHECKED=ROOT.parent/'native-wifi-qca9377-wmi-native-v3'
LIFE=ROOT.parent/'native-wifi-qca9377-persistent-v1'
sys.path.insert(0,str(CHECKED));import startup_build as checked
one=checked.one
def sources(directory):
 checked.sources(directory)
 for root,names in ((ROOT,('persistent.h','persistent.c')),(LIFE,('lifecycle.h','lifecycle.c'))):
  for n in names:(directory/n).write_bytes((root/n).read_bytes())
 p=directory/'init_probe.c';s=p.read_text()
 s=one(s,'#include "startup.h"','#include "startup.h"\n#include "persistent.h"')
 s=one(s,'static QcaWmiStartup startup;','static QcaWmiStartup startup;\nstatic QcaPersistentNative persistent;')
 s=one(s,'int qca_stop(void){','int qca_stop(void){\n (void)qca_persistent_quiesce(&persistent,last_now);')
 marker='else rc=qca_wmi_startup_poll(&startup,now);'
 s=one(s,marker,'''else rc=qca_wmi_startup_poll(&startup,now);
        if(rc==1){
         if(!persistent.life.phase)rc=qca_persistent_begin(&persistent,&startup,1,now);
         else rc=qca_persistent_poll(&persistent,now);
         if(rc==1)rc=0; /* Retain exact hardware lifetime; no diagnostic teardown. */
        }''')
 s=one(s,'else if(rc<0&&startup.phase==1)(void)qca_wmi_startup_poll(&startup,now);',
  '''else if(rc<0&&startup.phase==1)(void)qca_wmi_startup_poll(&startup,now);
       if(rc<0&&persistent.life.phase)(void)qca_persistent_poll(&persistent,now);''')
 # Observe checked stop before first unmap, and final release after pin close.
 s=one(s,'if(ram_closing){if(boot_round&&qca_boot_native_close(&boot))return;(void)qca_fwp_close(&ram);return;}',
  '''if(ram_closing){
  if(boot_round&&qca_boot_native_close(&boot)){
   (void)qca_persistent_poll(&persistent,ms*1000);return;
  }
  (void)qca_persistent_poll(&persistent,ms*1000);
  (void)qca_fwp_close(&ram);return;
 }''')
 s=one(s,'if(qca_init_adapter_released(&adapter)&&!port.claimed)(void)qca_boot_native_close(&boot);',
  '''if(qca_init_adapter_released(&adapter)&&!port.claimed)(void)qca_boot_native_close(&boot);
  if(persistent.life.phase&&persistent.life.phase!=QCA_RADIO_ACTIVE)
   (void)qca_persistent_poll(&persistent,ms*1000);''')
 s+='\nconst QcaPersistentNative*qca_persistent_view(void){return &persistent;}\n'
 p.write_text(s)
