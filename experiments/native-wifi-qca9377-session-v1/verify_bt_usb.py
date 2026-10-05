#!/usr/bin/env python3
"""Isolated actual USB poll/close mock integration, no physical radio."""
import importlib.util,json,subprocess,sys,unittest
from verify_htc import ROOT,CC,sha
import bt_usb_build as build
V1=ROOT.parent/'native-wifi-qca9377-v1';sys.path.insert(0,str(V1));import ble_recovery_build as ble
spec=importlib.util.spec_from_file_location('usbtests',build.LINK/'verify_usb.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
WRAPPER=r'''
static uint8_t pending_bytes[260];static unsigned qn,qp,split_size,interleave,tick,coalesce;
static Status EFIAPI interrupt(void*this,uint8_t ep,void*out,size_t*n,size_t ms,uint32_t*result){
 if(interleave&&(tick++&1)){*result=0x40;return EFI_ERROR(18);}
 if(qp==qn){
  qp=qn=0;size_t count=sizeof(pending_bytes);
  Status s=raw_interrupt(this,ep,pending_bytes,&count,ms,result);
  if(s||*result)return s;
  assert(count<=260);qn=(unsigned)count;
  if(coalesce&&last_command==0x200a&&qn==21){
   uint8_t done[6]={0x0e,4,1,0x0a,0x20,0};
   memmove(pending_bytes+6,pending_bytes,21);memcpy(pending_bytes,done,6);qn=27;
  }
 }
 unsigned count=qn-qp;if(split_size&&count>split_size)count=split_size;
 assert(count<=*n);memcpy(out,pending_bytes+qp,count);qp+=count;*n=count;*result=0;return 0;
}
static void setup(unsigned flags,unsigned split,unsigned pause,unsigned merged){
 host_setup(flags);qn=qp=tick=0;split_size=split;interleave=pause;coalesce=merged;
 assert(host_bind()==0);
}
int main(void){
 unsigned cases=0;
 for(unsigned split=1;split<=32;split++)for(unsigned pause=0;pause<=1;pause++){
  for(unsigned merged=0;merged<=1;merged++){
   setup(512,split,pause,merged);assert(host_close()==0);assert(!host_bound());assert(host_writes()==3||(merged&&host_writes()==2));cases++;
  }
  unsigned failures[]={8,16,32,64,128,256,1024};
  for(unsigned i=0;i<sizeof(failures)/sizeof(failures[0]);i++){
   setup(failures[i],split,pause,0);assert(host_close()==1);assert(host_bound());cases++;
  }
 }
 uint8_t connection[21]={0x3e,19,1,0,0x40,0,1};
 for(unsigned split=1;split<21;split++){
  setup(8,0,0,0);host_advertising();host_inject(connection,split,0,0);
  assert(host_poll(8)==0);assert(host_link_state()==RL_ADVERTISING);
  /* Unsuccessful read bytes do not enter the parser or destroy the prefix. */
  host_inject(connection+split,21-split,EFI_ERROR(18),0x40);assert(host_poll(8)==0);
  host_inject(connection+split,21-split,0,0);assert(host_poll(8)==0);assert(host_link_state()==RL_CONNECTED);cases++;
 }
 /* A poll-to-close partial event must finish in the same stream. */
 for(unsigned prefix=1;prefix<21;prefix++){
  setup(0,0,0,0);host_advertising();host_inject(connection,prefix,0,0);assert(host_poll(8)==0);
  poll_flags=0;memcpy(pending_bytes,connection+prefix,21-prefix);qn=21-prefix;qp=0;
  assert(host_close()==0);assert(!host_bound());assert(host_writes()==3);cases++;
 }
 /* Completion followed by an unfinished race must NOT permit unload. */
 setup(8,0,0,0);host_advertising();poll_flags=0;
 uint8_t done[6]={0x0e,4,1,0x0a,0x20,0};memcpy(pending_bytes,done,6);memcpy(pending_bytes+6,connection,16);qn=22;qp=0;
 assert(host_close()==1);assert(host_bound());cases++;
 /* Complete, then a coalesced hardware error: bad wins over done. */
 setup(0,0,0,0);memcpy(pending_bytes,done,6);pending_bytes[6]=0x10;pending_bytes[7]=1;pending_bytes[8]=1;qn=9;qp=0;
 assert(host_close()==1);assert(host_bound());cases++;
 printf("BT USB %u poll/close fragmentation, race, timeout and unknown-owner cases PASS; HOST ONLY\n",cases);
 return 0;
}
'''
def main():
 out=ROOT/'runs/bt-usb';build.sources(out)
 (out/'hci_link.c').write_text(ble.link_source())
 for n in ('hci_link.h','gatt_core.c','gatt_core.h','file_core.c','file_core.h'):(out/n).write_bytes((build.LINK/n).read_bytes())
 inputs={n:sha((ROOT/n).read_bytes()) for n in ('bt_usb_build.py','verify_bt_usb.py','bt_event_stream.c','bt_event_stream.h')}
 mock=base.SOURCE.replace('#include <string.h>','#include <string.h>\n#include <assert.h>\n#include <stdio.h>')
 assert mock.count('static Status EFIAPI interrupt(')==1
 mock=mock.replace('static Status EFIAPI interrupt(','static Status EFIAPI raw_interrupt(')
 mock=mock.replace('static Status EFIAPI raw_interrupt(', 'static Status EFIAPI interrupt(void*,uint8_t,void*,size_t*,size_t,uint32_t*);\nstatic Status EFIAPI raw_interrupt(')
 (out/'mock.c').write_text(mock+WRAPPER)
 native=base.NATIVE
 units=[out/'usb_port.c',out/'bt_event_stream.c',out/'hci_link.c',out/'gatt_core.c',out/'file_core.c',native/'sha256.c']
 subprocess.run([str(CC),'-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(out),'-I'+str(native),str(out/'mock.c'),*[str(x) for x in units],'-o',str(out/'usb-test')],check=True)
 r=subprocess.run([str(out/'usb-test')],capture_output=True,text=True,timeout=30);(out/'asan.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 # Existing ownership/diagnostic tests against actual derived USB implementation.
 (out/'hci_link.c').write_bytes((build.LINK/'hci_link.c').read_bytes())
 base.ROOT=out
 old=base.subprocess.run
 def run(args,**kw):
  if isinstance(args,list) and args[0]=='cc':args=[str(CC),*args[1:-2],str(out/'bt_event_stream.c'),*args[-2:]]
  return old(args,**kw)
 base.subprocess.run=run
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(base.UsbTests)
 with (out/'regression.log').open('w') as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
 assert result.wasSuccessful(),(out/'regression.log').read_text()
 (out/'hci_link.c').write_text(ble.link_source())
 for name in ('usb_port.c','bt_event_stream.c'):
  old([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(out),'-I'+str(native),'-c',str(out/name),'-o',str(out/(name+'.obj'))],check=True)
 assert inputs=={n:sha((ROOT/n).read_bytes()) for n in inputs}
 report={'status':'BT-USB-POLL-CLOSE-HOST-COFF-PASS','build_host':'yukabox','source_sha256':inputs,'baseline_usb_sha256':sha((build.LINK/'usb_port.c').read_bytes()),'baseline_usb_header_sha256':sha((build.LINK/'usb_port.h').read_bytes()),'baseline_test_sha256':sha((build.LINK/'verify_usb.py').read_bytes()),'derived_usb_sha256':sha((out/'usb_port.c').read_bytes()),'derived_header_sha256':sha((out/'usb_port.h').read_bytes()),'derived_link_sha256':sha((out/'hci_link.c').read_bytes()),'asan_log_sha256':sha((out/'asan.log').read_bytes()),'regression_log_sha256':sha((out/'regression.log').read_bytes()),'regression_tests':result.testsRun,'physical_verified':False,'installed_on_dell':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip());print(report['status'])
if __name__=='__main__':main()
