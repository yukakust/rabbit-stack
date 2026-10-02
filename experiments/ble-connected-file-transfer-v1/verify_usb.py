#!/usr/bin/env python3
"""Mock UEFI USB ownership/binding/cleanup checks. NEVER touches real USB."""
import ctypes as C
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
NATIVE=ROOT.parent/'x86-64-uefi-runtime-supervisor-v1'
SOURCE=r'''
#include <string.h>
#include "usb_port.h"
static SystemTable st;static void*boot[48],*io[13],*handles[2];
static RlUsb port;static RlLink link;
static int wrong,duplicate,bad_endpoint,timeout,free_count,writes,unrelated,accept_only,wrong_handle,status_only,disconnect_complete_only,connect_race,reset_timeout;
static uint16_t last_command;
static unsigned poll_flags;
static size_t interrupt_budget;
static uint8_t injected[260];static size_t injected_length;static Status injected_status;static uint32_t injected_result;
static Status EFIAPI descriptor(void*this,void*out){(void)this;uint8_t*p=out;memset(p,0,18);p[0]=18;p[1]=1;p[8]=0xf3;p[9]=0x0c;p[10]=wrong?0:9;p[11]=0xe0;return 0;}
static Status EFIAPI interface(void*this,void*out){(void)this;uint8_t*p=out;memset(p,0,9);p[0]=9;p[1]=4;p[4]=3;p[5]=0xe0;p[6]=p[7]=1;return 0;}
static Status EFIAPI endpoint(void*this,uint8_t index,void*out){(void)this;uint8_t*p=out;memset(p,0,7);p[0]=7;p[1]=5;p[2]=index==0?0x81:index==1?0x82:2;p[3]=index==0?3:2;p[4]=index==0?16:64;p[6]=index==0?1:0;if(bad_endpoint)p[2]=0;return 0;}
static Status EFIAPI locate(uint32_t type,const Guid*guid,void*key,size_t*n,void***list){(void)guid;(void)key;if(type!=2)return EFI_ERROR(2);*n=duplicate?2:1;*list=handles;return 0;}
static Status EFIAPI handle(void*h,const Guid*g,void**out){(void)h;(void)g;*out=io;return 0;}
static Status EFIAPI release(void*p){(void)p;free_count++;return 0;}
static Status EFIAPI control(void*this,void*request,uint32_t direction,uint32_t ms,void*data,size_t n,uint32_t*result){
 (void)this;(void)request;(void)ms;if(direction!=1||n<3)return EFI_ERROR(2);
 uint8_t*p=data;last_command=p[0]|((uint16_t)p[1]<<8);writes++;*result=0;return 0;
}
static Status EFIAPI interrupt(void*this,uint8_t ep,void*out,size_t*n,size_t ms,uint32_t*result){
 (void)this;interrupt_budget=ms;if(ep!=0x81)return EFI_ERROR(2);*result=0;
 /* Synthetic multi-transaction fixture, NOT a Dell timing measurement. */
 if((poll_flags&16)&&ms<2){*result=0x40;return EFI_ERROR(18);}
 if(poll_flags&1)return EFI_ERROR(7);
 if(poll_flags&4){uint8_t e[3]={0x10,1,1};memcpy(out,e,3);*n=3;return 0;}
 if(poll_flags&8){size_t count=injected_length<260?injected_length:260;memcpy(out,injected,count);*n=injected_length;*result=injected_result;return injected_status;}
 if(timeout)return EFI_ERROR(18);
 if(reset_timeout&&last_command==0x0c03)return EFI_ERROR(18);
 uint8_t*p=out;
 if(connect_race&&last_command==0x200a){
  uint8_t e[21]={0x3e,19,1,0,0x40,0,1};memcpy(p,e,21);*n=21;connect_race=0;return 0;
 }
 if(unrelated){p[0]=0x13;p[1]=1;p[2]=0;*n=3;return 0;}
 if(status_only||(accept_only&&last_command==0x0406)){
  uint8_t e[6]={0x0f,4,0,1,(uint8_t)last_command,(uint8_t)(last_command>>8)};memcpy(p,e,6);*n=6;return 0;
 }
 if(last_command==0x0406&&!accept_only&&!disconnect_complete_only){uint8_t e[6]={5,4,0,wrong_handle?0x41:0x40,0,0x13};memcpy(p,e,6);*n=6;return 0;}
 uint8_t e[6]={0x0e,4,1,(uint8_t)last_command,(uint8_t)(last_command>>8),0};memcpy(p,e,6);*n=6;return 0;
}
static Status EFIAPI bulk(void*this,uint8_t ep,void*data,size_t*n,size_t ms,uint32_t*result){(void)this;(void)ep;(void)data;(void)n;(void)ms;*result=0;return poll_flags&2?EFI_ERROR(7):EFI_ERROR(18);}
void host_setup(int flags){
 memset(&st,0,sizeof(st));memset(boot,0,sizeof(boot));memset(io,0,sizeof(io));memset(&link,0,sizeof(link));
 poll_flags=0;wrong=flags&1;duplicate=flags&2;bad_endpoint=flags&4;timeout=flags&8;unrelated=flags&16;
 accept_only=flags&32;wrong_handle=flags&64;status_only=flags&128;disconnect_complete_only=flags&256;
 connect_race=flags&512;reset_timeout=flags&1024;writes=free_count=0;
 boot[312/8]=(void*)locate;boot[152/8]=(void*)handle;boot[72/8]=(void*)release;st.boot=boot;
 io[0]=(void*)control;io[1]=(void*)bulk;io[3]=(void*)interrupt;io[6]=(void*)descriptor;io[8]=(void*)interface;io[9]=(void*)endpoint;
 handles[0]=io;handles[1]=io;link.state=RL_CONNECTED;link.connected=1;link.handle=0x40;
 if(connect_race){link.connected=0;link.state=RL_ADVERTISING;link.handle=0;}
}
int host_bind(void){return rl_usb_bind(&port,&st);}
int host_close(void){return rl_usb_close(&port,&link);}
int host_bound(void){return port.bound;}
int host_writes(void){return writes;}
int host_frees(void){return free_count;}
int host_poll(unsigned flags){poll_flags=flags;return rl_usb_poll(&port,&link);}
void host_inject(const uint8_t*p,size_t n,Status status,uint32_t result){memset(injected,0,sizeof(injected));memcpy(injected,p,n<260?n:260);injected_length=n;injected_status=status;injected_result=result;}
unsigned host_obs_sequence(void){return port.observation_sequence;}
unsigned host_obs_length(void){return port.observation.reported_length;}
unsigned host_obs_result(void){return port.observation.result;}
Status host_obs_status(void){return port.observation.status;}
unsigned host_obs_prefix(uint8_t*out){memcpy(out,port.observation.prefix,port.observation.copied);return port.observation.copied;}
unsigned host_event_reads(void){return port.event_reads;}
unsigned host_event_timeouts(void){return port.event_timeouts;}
unsigned host_polls(void){return port.polls;}
unsigned host_interrupt_budget(void){return (unsigned)interrupt_budget;}
unsigned host_link_state(void){return link.state;}
void host_advertising(void){rl_init(&link,0);link.state=RL_ADVERTISING;link.step=7;link.acl_size=123;link.buffers=link.credits=16;}
void host_configuring(void){rl_init(&link,0);}
unsigned host_event_packet(void){return port.event_packet;}
unsigned host_event_interval(void){return port.event_interval;}
unsigned host_masks(uint8_t*out){memcpy(out,port.event_mask,8);memcpy(out+8,port.le_mask,8);return port.mask_seen;}
'''


class UsbTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='rabbit-usb-mock-');d=Path(cls.temp.name)
        (d/'mock.c').write_text(SOURCE)
        subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-attributes','-fPIC','-shared','-I',str(ROOT),'-I',str(NATIVE),
            str(d/'mock.c'),str(ROOT/'usb_port.c'),str(ROOT/'hci_link.c'),str(ROOT/'gatt_core.c'),str(ROOT/'file_core.c'),str(NATIVE/'sha256.c'),'-o',str(d/'mock.so')],check=True)
        cls.lib=C.CDLL(str(d/'mock.so'))
        cls.lib.host_inject.argtypes=[C.c_char_p,C.c_size_t,C.c_uint64,C.c_uint32]
        cls.lib.host_obs_status.restype=C.c_uint64

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_exact_target_bind_is_read_only_and_releases_handles(self):
        self.lib.host_setup(0);self.assertEqual(self.lib.host_bind(),0)
        self.assertEqual(self.lib.host_writes(),0);self.assertEqual(self.lib.host_frees(),1)

    def test_complete_21_byte_connection_passes_the_actual_usb_adapter(self):
        self.lib.host_setup(8);self.lib.host_bind();self.lib.host_advertising()
        raw=bytes.fromhex('3E1301000100010000000000000018000000C80000')
        self.lib.host_inject(raw,len(raw),0,0)
        self.assertEqual(self.lib.host_poll(8),0)
        self.assertEqual(self.lib.host_interrupt_budget(),20)
        self.assertEqual(self.lib.host_link_state(),2)
        prefix=C.create_string_buffer(24)
        self.assertEqual(self.lib.host_obs_prefix(prefix),21)
        self.assertEqual(prefix.raw[:21],raw)

    def test_finite_budget_handles_synthetic_multi_transaction_event(self):
        self.lib.host_setup(8);self.lib.host_bind();self.lib.host_advertising()
        raw=bytes.fromhex('3E1301000100010000000000000018000000C80000')
        self.lib.host_inject(raw,len(raw),0,0)
        self.assertEqual(self.lib.host_poll(8|16),0)
        self.assertEqual(self.lib.host_link_state(),2)
        self.assertEqual(self.lib.host_event_packet(),16)
        self.assertEqual(self.lib.host_event_interval(),1)
        self.assertEqual(self.lib.host_interrupt_budget(),20)

    def test_mask_observations_are_actual_submitted_control_bytes(self):
        self.lib.host_setup(8);self.lib.host_bind();self.lib.host_configuring()
        output=C.create_string_buffer(16)
        self.assertEqual(self.lib.host_masks(output),0)
        self.lib.host_poll(0)  # Submit Reset; input is a timeout.
        for opcode in (0x0c03,0x0c01):
            event=b'\x0e\x04\x01'+opcode.to_bytes(2,'little')+b'\0'
            self.lib.host_inject(event,len(event),0,0)
            self.assertEqual(self.lib.host_poll(8),0)
        self.assertEqual(self.lib.host_masks(output),3)
        self.assertEqual(output.raw,bytes.fromhex('10E00400000000201F00000000000000'))

    def test_unreported_timeout_cannot_distinguish_idle_from_lost_connection(self):
        # Deliberately model a firmware timeout that does NOT report received
        # bytes. This reproduces diagnostic ambiguity, not Dell firmware behavior.
        self.lib.host_setup(8);self.lib.host_bind();self.lib.host_advertising()
        raw=bytes.fromhex('3E1301000100010000000000000018000000C80000')
        self.lib.host_inject(raw+bytes(260-len(raw)),260,0x8000000000000012,0x40)
        self.assertEqual(self.lib.host_poll(8),0)
        self.assertEqual(self.lib.host_obs_sequence(),0)
        self.assertEqual(self.lib.host_event_timeouts(),1)
        self.assertEqual(self.lib.host_link_state(),1)
        # Later disconnect is visible, but cannot establish the missing handle.
        self.lib.host_inject(b'\x05\x04\x00\x01\x00\x13',6,0,0)
        self.assertEqual(self.lib.host_poll(8),0)
        self.assertEqual(self.lib.host_event_reads(),1)
        self.assertEqual(self.lib.host_link_state(),1)

    def test_poll_diagnostic_codes_keep_unknown_radio_bound(self):
        for flags,code in ((1,3),(2,5),(4,9)):
            self.lib.host_setup(8);self.assertEqual(self.lib.host_bind(),0)
            self.assertEqual(self.lib.host_poll(flags),code)
            self.assertEqual(self.lib.host_bound(),1)

    def test_raw_event_observation_precedes_parser_rejection(self):
        self.lib.host_setup(8);self.lib.host_bind()
        # Deliberately mismatched HCI length: parser ignores it, observation
        # must still preserve exactly the successful USB bytes and length.
        raw=b'\x3e\x13\x01\x00'+bytes(range(4,12))
        self.lib.host_inject(raw,len(raw),0,0)
        self.assertEqual(self.lib.host_poll(8),0)
        self.assertEqual(self.lib.host_obs_sequence(),1)
        self.assertEqual(self.lib.host_obs_length(),len(raw))
        prefix=C.create_string_buffer(24);self.assertEqual(self.lib.host_obs_prefix(prefix),len(raw))
        self.assertEqual(prefix.raw[:len(raw)],raw)
        self.assertEqual(self.lib.host_event_reads(),1)

    def test_timeout_is_not_reported_as_valid_hci_bytes(self):
        self.lib.host_setup(8);self.lib.host_bind()
        self.assertEqual(self.lib.host_poll(0),0)
        self.assertEqual(self.lib.host_obs_sequence(),0)
        self.assertEqual(self.lib.host_event_timeouts(),1)
        self.assertEqual(self.lib.host_polls(),1)
        self.lib.host_inject(bytes(4),4,0x8000000000000012,0x40)
        self.lib.host_poll(8)
        self.assertEqual(self.lib.host_obs_sequence(),1)
        self.assertEqual(self.lib.host_obs_length(),4)
        self.assertEqual(self.lib.host_obs_status(),0x8000000000000012)
        self.assertEqual(self.lib.host_obs_result(),0x40)
        self.assertEqual(self.lib.host_obs_prefix(C.create_string_buffer(24)),0)

    def test_event_prefix_bound_and_oversized_length_have_no_unsafe_copy(self):
        self.lib.host_setup(8);self.lib.host_bind()
        raw=bytes(range(40));self.lib.host_inject(raw,40,0,0);self.lib.host_poll(8)
        prefix=C.create_string_buffer(24);self.assertEqual(self.lib.host_obs_prefix(prefix),24)
        self.assertEqual(prefix.raw,raw[:24])
        self.lib.host_inject(bytes(300),300,0,0)
        self.assertEqual(self.lib.host_poll(8),2)
        self.assertEqual(self.lib.host_obs_length(),300)
        self.assertEqual(self.lib.host_obs_prefix(prefix),0)

    def test_wrong_duplicate_and_invalid_endpoints_fail_closed(self):
        for flags in (1,2,4):
            self.lib.host_setup(flags);self.assertEqual(self.lib.host_bind(),1)
            self.assertEqual(self.lib.host_bound(),0);self.assertEqual(self.lib.host_writes(),0)
            self.assertEqual(self.lib.host_frees(),1)

    def test_shutdown_requires_matching_adv_off_and_disconnect(self):
        self.lib.host_setup(0);self.lib.host_bind();self.assertEqual(self.lib.host_close(),0)
        self.assertEqual(self.lib.host_writes(),3);self.assertEqual(self.lib.host_bound(),0)

    def test_timeout_or_unrelated_event_does_not_claim_shutdown(self):
        for flags in (8,16):
            self.lib.host_setup(flags);self.lib.host_bind();self.assertEqual(self.lib.host_close(),1)
            self.assertEqual(self.lib.host_bound(),1)

    def test_command_acceptance_does_not_prove_disconnection(self):
        self.lib.host_setup(32);self.lib.host_bind()
        self.assertEqual(self.lib.host_close(),1)
        self.assertEqual(self.lib.host_writes(),2)
        self.assertEqual(self.lib.host_bound(),1)

    def test_wrong_connection_handle_does_not_prove_disconnection(self):
        self.lib.host_setup(64);self.lib.host_bind()
        self.assertEqual(self.lib.host_close(),1)
        self.assertEqual(self.lib.host_bound(),1)

    def test_disconnect_command_complete_does_not_prove_disconnection(self):
        self.lib.host_setup(256);self.lib.host_bind()
        self.assertEqual(self.lib.host_close(),1)
        self.assertEqual(self.lib.host_bound(),1)

    def test_adv_off_status_without_complete_does_not_prove_shutdown(self):
        self.lib.host_setup(128);self.lib.host_bind()
        self.assertEqual(self.lib.host_close(),1)
        self.assertEqual(self.lib.host_writes(),1)
        self.assertEqual(self.lib.host_bound(),1)

    def test_connection_during_adv_off_is_disconnected_before_unload(self):
        self.lib.host_setup(512);self.lib.host_bind()
        self.assertEqual(self.lib.host_close(),0)
        self.assertEqual(self.lib.host_writes(),3);self.assertEqual(self.lib.host_bound(),0)

    def test_final_reset_requires_complete_before_unload(self):
        self.lib.host_setup(1024);self.lib.host_bind()
        self.assertEqual(self.lib.host_close(),1)
        self.assertEqual(self.lib.host_writes(),3);self.assertEqual(self.lib.host_bound(),1)


if __name__=='__main__':unittest.main(verbosity=2)
