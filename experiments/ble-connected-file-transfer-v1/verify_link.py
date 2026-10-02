#!/usr/bin/env python3
"""Synthetic controller + actual C GATT/file/world runtime, not radio evidence."""
import ctypes as C
import hashlib
import struct
import unittest
import sys
from verify import Tests as Base


class LinkTests(Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lib.host_take.argtypes=[C.c_void_p,C.c_void_p];cls.lib.host_take.restype=C.c_size_t
        cls.lib.host_event.argtypes=cls.lib.host_acl.argtypes=[C.c_char_p,C.c_size_t]
        cls.lib.host_bulk.argtypes=[C.c_char_p,C.c_size_t]

    def setUp(self):super().setUp();self.lib.host_link_init()

    def event(self,p):self.lib.host_event(p,len(p))
    def acl(self,p):self.lib.host_acl(p,len(p))
    def take(self):
        out=C.create_string_buffer(255);kind=C.c_ubyte()
        n=self.lib.host_take(out,C.byref(kind));return kind.value,out.raw[:n]

    def configured(self,buffers=1,acl_size=27):
        for opcode in [0x0c03,0x0c01,0x2001,0x2002,0x2006,0x2008,0x200a]:
            kind,p=self.take();self.assertEqual(kind,1);self.assertEqual(struct.unpack_from('<H',p)[0],opcode)
            self.assertEqual(self.take()[1],b'')
            returned=b'\0'+(struct.pack('<HB',acl_size,buffers) if opcode==0x2002 else b'')
            self.event(b'\x0e'+bytes([3+len(returned)])+b'\x01'+struct.pack('<H',opcode)+returned)
        self.assertEqual(self.lib.host_link_state(),1)

    def connected(self,handle=0x40):
        payload=b'\x01\x00'+struct.pack('<H',handle)+b'\x01\x00'+bytes(6)+struct.pack('<HHH',24,0,200)+b'\0'
        self.event(b'\x3e'+bytes([len(payload)])+payload)
        self.assertEqual(self.lib.host_link_state(),2)

    def completed(self,count=1,handle=0x40):self.event(b'\x13\x05\x01'+struct.pack('<HH',handle,count))

    def request(self,att,split=None,cid=4):
        pdu=struct.pack('<HH',len(att),cid)+att
        if split:
            first=pdu[:split];rest=pdu[split:]
            self.acl(struct.pack('<HH',0x2040,len(first))+first)
            self.assertEqual(self.take()[1],b'')
            self.acl(struct.pack('<HH',0x1040,len(rest))+rest)
        else:self.acl(struct.pack('<HH',0x2040,len(pdu))+pdu)
        fragments=[]
        while True:
            kind,p=self.take()
            if not p:break
            self.assertEqual(kind,2)
            tag,length=struct.unpack_from('<HH',p)
            self.assertEqual(tag&0x0fff,0x40)
            self.assertEqual(tag>>12,1 if fragments else 0,
                             'LE replies require PB=00 first, PB=01 continuation; BC=00')
            self.assertEqual(length,len(p)-4)
            fragments.append(p[4:]);self.completed()
        combined=b''.join(fragments)
        if combined:
            self.assertEqual(struct.unpack_from('<H',combined)[0],len(combined)-4)
            self.assertEqual(struct.unpack_from('<H',combined,2)[0],cid)
        return combined[4:]

    def test_link_split_att_exchange_and_controller_credit(self):
        self.configured();self.connected()
        self.assertEqual(self.request(b'\x02\xf7\x00',split=4),b'\x03\xf7\x00')
        self.assertEqual(self.request(b'\x0a\x07\x00')[0],11)

    def test_le_reply_flags_in_both_single_and_fragmented_packets(self):
        self.configured(acl_size=8);self.connected()
        self.assertEqual(self.request(b'\x02\x17\0'),b'\x03\xf7\0')
        # Status response exceeds one controller packet. request() checks every
        # actual C header, not just its reconstructed ATT payload.
        self.assertEqual(len(self.request(b'\x0a\x07\0')),23)

    def test_connection_before_advertising_complete_is_not_lost(self):
        for opcode in [0x0c03,0x0c01,0x2001,0x2002,0x2006,0x2008]:
            self.assertEqual(struct.unpack_from('<H',self.take()[1])[0],opcode)
            returned=b'\0'+(struct.pack('<HB',251,4) if opcode==0x2002 else b'')
            self.event(b'\x0e'+bytes([3+len(returned)])+b'\x01'+struct.pack('<H',opcode)+returned)
        self.assertEqual(self.take()[1],b'\x0a\x20\x01\x01')
        self.connected()  # Asynchronous connection arrives before enable CC.
        self.event(b'\x0e\x04\x01\x0a\x20\0')
        self.assertEqual(self.lib.host_link_state(),2)
        self.assertEqual(self.request(b'\x02\xf7\0'),b'\x03\xf7\0')

    def test_link_credit_exhaustion_and_replenishment(self):
        self.configured();self.connected()
        req=struct.pack('<HH',3,4)+b'\x02\xf7\x00'
        self.acl(struct.pack('<HH',0x2040,len(req))+req)
        self.assertTrue(self.take()[1]);self.assertEqual(self.take()[1],b'')
        self.completed(2);self.assertEqual(self.lib.host_link_state(),3)

    def test_targeted_service_discovery_at_default_mtu(self):
        self.configured();self.connected()
        value=bytes.fromhex('01000000000000804946544942424152')
        request=b'\x06\x01\x00\xff\xff\x00\x28'+value
        self.assertEqual(self.request(request),b'\x07\x01\x00\x07\x00')
        self.assertEqual(self.request(request[:-1]+b'\0'),b'\x01\x06\x01\x00\x0a')
        self.assertEqual(self.request(request[:-1]),b'\x01\x06\x01\x00\x04')

    def test_link_config_timeout_failure_and_stop(self):
        self.take();self.lib.host_elapsed(10000);self.assertEqual(self.lib.host_link_state(),3)
        self.assertEqual(self.take()[1],b'');self.lib.host_stop();self.assertEqual(self.lib.host_link_state(),4)

    def test_link_fragment_overflow_foreign_handle_and_unexpected_continuation(self):
        self.configured();self.connected()
        self.acl(struct.pack('<HH',0x2041,7)+struct.pack('<HH',3,4)+b'\x02\x17\0')
        self.assertEqual(self.lib.host_link_state(),2);self.assertEqual(self.take()[1],b'')
        self.acl(struct.pack('<HH',0x1040,1)+b'\0');self.assertEqual(self.lib.host_link_state(),3)

    def test_link_full_cat_over_connected_acl(self):
        self.configured();self.connected();self.assertEqual(self.request(b'\x02\xf7\0'),b'\x03\xf7\0')
        begin=b'\x01\x01\x01\0'+self.session+struct.pack('<I',len(self.cat)+32)
        self.assertEqual(self.request(b'\x12\x03\0'+begin),b'\x13')
        stream=hashlib.sha256(self.cat).digest()+self.cat
        for offset in range(0,len(stream),240):
            write=b'\x12\x05\0'+struct.pack('<I',offset)+stream[offset:offset+240]
            self.assertEqual(self.request(write,split=27),b'\x13')
            self.assertEqual(self.lib.host_tick(),0)
        self.assertEqual(self.request(b'\x12\x03\0\x02'+self.session),b'\x13')
        status=self.request(b'\x0a\x07\0')[1:]
        self.assertEqual(status[20],2);self.assertEqual(status[28:],hashlib.sha256(self.cat).digest())
        self.assertEqual(self.lib.host_counter(),2);self.assertEqual(self.lib.host_commits(),1)

    def test_link_disconnect_reconnect_preserves_staging(self):
        self.configured();self.connected()
        begin=b'\x01\x01\x01\0'+self.session+struct.pack('<I',len(self.cat)+32)
        self.request(b'\x12\x03\0'+begin)
        data=hashlib.sha256(self.cat).digest()[:16]
        self.request(b'\x12\x05\0'+bytes(4)+data)
        self.event(b'\x05\x04\0\x40\0\x13')
        kind,p=self.take();self.assertEqual((kind,p), (1,b'\x0a\x20\x01\x01'))
        self.event(b'\x0e\x04\x01\x0a\x20\0');self.connected()
        status=self.request(b'\x0a\x07\0')[1:]
        self.assertEqual(struct.unpack_from('<I',status,12)[0],16)

    def test_link_pairing_explicitly_rejected(self):
        self.configured();self.connected()
        self.assertEqual(self.request(bytes.fromhex('01030001100000'),cid=6),b'\x05\x05')

    def test_link_usb_byte_stream_splits_and_coalescing(self):
        self.configured(buffers=4);self.connected()
        pdu=struct.pack('<HH',3,4)+b'\x02\x17\0'
        packet=struct.pack('<HH',0x2040,len(pdu))+pdu
        for byte in packet:self.lib.host_bulk(bytes([byte]),1)
        self.assertTrue(self.take()[1]);self.completed()
        self.lib.host_bulk(packet+packet,len(packet)*2)
        self.assertTrue(self.take()[1]);self.assertTrue(self.take()[1])
        self.assertEqual(self.lib.host_link_state(),2)

    def test_link_shared_controller_buffers_are_queried_not_guessed(self):
        for expected in [0x0c03,0x0c01,0x2001]:
            kind,p=self.take();self.assertEqual((kind,struct.unpack_from('<H',p)[0]),(1,expected))
            self.event(b'\x0e\x04\x01'+struct.pack('<H',expected)+b'\0')
        self.assertEqual(self.take()[1],b'\x02\x20\0')
        self.event(b'\x0e\x07\x01\x02\x20'+bytes(4))
        self.assertEqual(self.take()[1],b'\x05\x10\0')
        self.event(b'\x0e\x0b\x01\x05\x10\0'+struct.pack('<HBHH',1024,0,4,0))
        kind,p=self.take();self.assertEqual((kind,struct.unpack_from('<H',p)[0]),(1,0x2006))


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(LinkTests))
    sys.exit(not result.wasSuccessful())
