#!/usr/bin/env python3
"""Pinned public driver/firmware research. No device or owner key access."""
import base64
import hashlib
import json
from pathlib import Path
import urllib.request
ROOT=Path(__file__).resolve().parent
LINUX='6b5a2b7d9bc156e505f09e698d85d6a1547c1206'
FIRMWARE='f9b926a6e1d67e09e54adc329c4e76be5f24a895'
def main():
    dest=ROOT/'vendor';dest.mkdir(exist_ok=True)
    sources={
        'linux':('https://kernel.googlesource.com/pub/scm/linux/kernel/git/netdev/net',LINUX,
          ['drivers/net/wireless/ath/ath10k/'+n for n in ('hw.h','pci.c','core.c','bmi.c','bmi.h','ce.c','ce.h','wmi.h','htt.h')]),
        'firmware':('https://kernel.googlesource.com/pub/scm/linux/kernel/git/firmware/linux-firmware',FIRMWARE,
          ['ath10k/QCA9377/hw1.0/firmware-6.bin','ath10k/QCA9377/hw1.0/board-2.bin',
           'ath10k/QCA9377/hw1.0/notice_ath10k_firmware-6.txt','LICENSE.QualcommAtheros_ath10k','WHENCE'])}
    report={'physical_dell':False,'upload_performed':False,'sources':{},'files':{}}
    for group,(base,commit,paths) in sources.items():
        report['sources'][group]={'repository':base,'commit':commit}
        for path in paths:
            url=f'{base}/+/{commit}/{path}?format=TEXT'
            with urllib.request.urlopen(url,timeout=30) as response:
                encoded=response.read(12*1024*1024+1)
            if len(encoded)>12*1024*1024:raise ValueError('upstream file too large')
            data=base64.b64decode(encoded,validate=True)
            target=dest/group/path;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
            report['files'][group+'/'+path]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    (ROOT/'materials.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
if __name__=='__main__':main()
