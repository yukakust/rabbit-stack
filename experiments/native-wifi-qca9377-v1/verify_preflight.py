#!/usr/bin/env python3
import json
from pathlib import Path
import random
import struct
from firmware_preflight import Invalid,firmware,boards,select_board
ROOT=Path(__file__).resolve().parent
def tlv(kind,body):return struct.pack('<II',kind,len(body))+body+bytes((-len(body))%4)
def wrap(magic,body):return magic+b'\0'+bytes((-(len(magic)+1))%4)+body
def main():
    checks=0
    def reject(call):
        nonlocal checks
        try:call()
        except Invalid:checks+=1
        else:raise AssertionError('invalid input accepted')
    packet=wrap(b'QCA-ATH10K',tlv(0,b'test')+tlv(3,b'image')+tlv(5,struct.pack('<I',4)))
    assert firmware(packet)['wmi_op']==4;checks+=1
    for n in range(12,len(packet)):
        # Some complete prefixes are valid containers; incomplete TLVs must fail.
        if n not in (24,40):reject(lambda n=n:firmware(packet[:n]))
    reject(lambda:firmware(packet+tlv(3,b'duplicate')))
    reject(lambda:firmware(wrap(b'QCA-ATH10K',tlv(3,b''))))
    reject(lambda:firmware(packet+tlv(6,b'bad')))
    for length in (0xffffffff,0x80000000,0x1000000,100):
        changed=bytearray(packet);struct.pack_into('<I',changed,16,length)
        reject(lambda:firmware(bytes(changed)))
    board=wrap(b'QCA-ATH10K-BOARD',tlv(0,tlv(0,b'exact-board')+tlv(1,b'calibration')))
    records=boards(board);assert select_board(records,'exact-board')['bytes']==11;checks+=1
    reject(lambda:select_board(records,None));reject(lambda:select_board(records,'wrong-board'))
    reject(lambda:boards(board+tlv(0,tlv(0,b'exact-board')+tlv(1,b'other'))))
    # Deterministic malformed TLVs, exercising overflows/truncation/padding.
    randomizer=random.Random(9377)
    for _ in range(128):
        body=randomizer.randbytes(randomizer.randrange(0,128))
        value=wrap(b'QCA-ATH10K',struct.pack('<II',3,0xffffffff)+body)
        reject(lambda:firmware(value))
    f=ROOT/'vendor/firmware/ath10k/QCA9377/hw1.0'
    actual=firmware((f/'firmware-6.bin').read_bytes());calibration=boards((f/'board-2.bin').read_bytes())
    reject(lambda:select_board(calibration,None))
    report={'passed':True,'checks':checks,'physical_dell':False,'firmware':actual,
            'board_candidates':calibration,'selected_board':None,'upload_performed':False,
            'association_performed':False,'network_credentials_accessed':False}
    (ROOT/'preflight.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
if __name__=='__main__':main()
