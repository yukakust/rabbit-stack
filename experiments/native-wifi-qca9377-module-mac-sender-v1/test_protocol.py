import struct
import unittest
from protocol import begin, data, receipt

class Protocol(unittest.TestCase):
    def setUp(self):
        self.chunk = bytearray(1000)
        self.chunk[:8] = b'RABRSN01'
        struct.pack_into('<II', self.chunk, 196, 2, 1)
        self.chunk = bytes(self.chunk)
        self.session = b'12345678'
        self.b = begin(self.chunk, self.session)
        self.raw = bytearray(80)
        self.raw[:8] = b'QMT00001'
        struct.pack_into('<QIIIIiI', self.raw, 8, 66, 3, 0, 1000, 1000, 1, 0)
        self.raw[40:48] = self.session
        self.raw[48:] = self.b[13:]
    def test_receipt(self):
        self.assertEqual(receipt(bytes(self.raw),66,self.session,self.chunk)['state'],'accepted')
        for i in list(range(16))+list(range(20,32))+list(range(36,80)):
            bad=self.raw.copy();bad[i]^=128
            with self.subTest(i=i),self.assertRaises(ValueError):receipt(bytes(bad),66,self.session,self.chunk)
        for e in (0,65,67,True):
            with self.assertRaises(ValueError):receipt(bytes(self.raw),e,self.session,self.chunk)
    def test_states(self):
        idle=b'QMT00001'+struct.pack('<Q',66)+bytes(64)
        self.assertEqual(receipt(idle,66,self.session,self.chunk)['state'],'idle')
        for state in (1,2):
            raw=self.raw.copy();struct.pack_into('<I',raw,16,state);struct.pack_into('<i',raw,32,0)
            self.assertEqual(receipt(bytes(raw),66,self.session,self.chunk)['state'],['','staging','pending'][state])
        bad=self.raw.copy();struct.pack_into('<I',bad,28,999)
        with self.assertRaises(ValueError):receipt(bytes(bad),66,self.session,self.chunk)
    def test_chunking(self):
        out=bytearray();off=0
        while off<len(self.chunk):
            p=data(self.chunk,self.session,off,23)
            self.assertLessEqual(len(p),23);self.assertEqual(p[1:9],self.session)
            self.assertEqual(struct.unpack_from('<I',p,9)[0],off)
            out.extend(p[13:]);off+=len(p)-13
        self.assertEqual(bytes(out),self.chunk)
        for x in (-1,True,len(self.chunk)):
            with self.assertRaises(ValueError):data(self.chunk,self.session,x)

if __name__=='__main__':unittest.main()
