"""Actual62 native production entrypoints with frozen56 explicit target fixture."""
import importlib.util,sys
import htt_build as build
OLD=build.E/'native-wifi-qca9377-htt-native-profile-v2';NATIVE=build.E/'native-wifi-qca9377-htt-native-v1'
saved=sys.modules['htt_build'];spec=importlib.util.spec_from_file_location('frozen_htt_native_build',NATIVE/'htt_build.py');native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native);sys.modules['htt_build']=native
saved_profile=sys.modules.get('profile_build')
try:
 spec=importlib.util.spec_from_file_location('frozen_htt56_build',OLD/'profile_build.py');oldbuild=importlib.util.module_from_spec(spec);spec.loader.exec_module(oldbuild);sys.modules['profile_build']=oldbuild
 spec=importlib.util.spec_from_file_location('frozen_htt56_fixture',OLD/'verify_native.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
finally:
 sys.modules['htt_build']=saved
 if saved_profile is not None:sys.modules['profile_build']=saved_profile
 else:sys.modules.pop('profile_build',None)
one=build.one
def fixture(source):
 s=old.fixture(source).replace('getle(status+224)==56','getle(status+224)==62').replace('getle(status+100)==56','getle(status+100)==62')
 s=s.replace('getle(status+24)==1','getle(status+24)==(qca_persistent_view()->life.phase==QCA_RADIO_CLOSED?1u:0u)')
 s='#include "prefix.h"\n#include "usb_port.h"\nvoid prefix_driver_model_bind(void*);\nint prefix_driver_model_poll(uint32_t);\n'+s
 s=one(s,'static unsigned fault;','static unsigned fault;static void*usb_methods[16];')
 s=one(s,'static void tick(unsigned ms){now_us=(uint64_t)ms*1000;qca_poll(ms);}','static void tick(unsigned ms){now_us=(uint64_t)ms*1000;assert(!prefix_driver_model_poll(ms));}')
 insert=r'''
void qca_collect(SystemTable*s){(void)s;assert(!"attach not modelled");}
static Status EFIAPI usb_control(void*io,void*r,uint32_t d,uint32_t t,void*p,size_t n,uint32_t*out){(void)io;(void)r;(void)d;(void)t;(void)p;(void)n;(void)out;assert(!"no disconnect modeled");return 0;}
static Status EFIAPI usb_bulk(void*io,uint8_t ep,void*p,size_t*n,size_t t,uint32_t*out){assert(io==usb_methods&&ep==0x82&&t==1);(void)p;(void)n;*out=0;return EFI_ERROR(18);}
static Status EFIAPI usb_event(void*io,uint8_t ep,void*p,size_t*n,size_t t,uint32_t*out){assert(io==usb_methods&&ep==0x81&&*n==260&&t==20);const uint8_t e[7]={0x13,5,1,1,0,0,0};memcpy(p,e,7);*n=7;*out=0;return 0;}
static void usb_fixture(void){usb_methods[0]=(void*)usb_control;usb_methods[1]=(void*)usb_bulk;usb_methods[3]=(void*)usb_event;prefix_driver_model_bind(usb_methods);}
'''
 s=one(s,'static void*ram_blocks[2];',insert+'\nstatic void*ram_blocks[2];')
 s=one(s,' sm_fixture();\n qca_start(&port_system,0);',' sm_fixture();usb_fixture();\n qca_start(&port_system,0);')
 return s
