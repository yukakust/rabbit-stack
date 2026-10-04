#!/usr/bin/env python3
"""Mac-only hidden credential entry; no radio, secret output or repository file."""
import argparse,json,os,subprocess,tempfile
from pathlib import Path
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--ssid',required=True);p.add_argument('--enter',action='store_true')
 a=p.parse_args()
 if not 1<=len(a.ssid.encode('utf-8'))<=32 or any(ord(c)<32 for c in a.ssid):p.error('SSID must contain 1..32 UTF-8 bytes without control characters')
 if not a.enter:
  print('LOCAL HIDDEN INPUT READY; NO CREDENTIAL READ OR RADIO');return 0
 folder=Path.home()/'.rabbit-owner';folder.mkdir(mode=0o700,exist_ok=True)
 if folder.is_symlink() or folder.stat().st_uid!=os.getuid():
  print('PRIVATE DIRECTORY OWNER CHECK FAILED');return 1
 folder.chmod(0o700)
 # Password travels only through a private subprocess pipe. Never put it in
 # command arguments, shell expansion, printed exceptions or public reports.
 script='''on run argv
 set promptText to "Пароль Wi-Fi для " & item 1 of argv & ". Он сохранится только локально на Mac."
 set answer to display dialog promptText with title "Rabbit — подключение Dell" default answer "" with hidden answer buttons {"Отмена", "Сохранить"} default button "Сохранить" cancel button "Отмена"
 return text returned of answer
end run
'''
 try:r=subprocess.run(['/usr/bin/osascript','-',a.ssid],input=script,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=300)
 except (OSError,subprocess.TimeoutExpired):print('LOCAL ENTRY NOT COMPLETED; NO SECRET OUTPUT');return 1
 if r.returncode:print('LOCAL ENTRY CANCELLED OR UNAVAILABLE');return 1
 secret=r.stdout.removesuffix('\n')
 if not 8<=len(secret)<=63 or any(ord(c)<32 or ord(c)>126 for c in secret):
  print('PASSWORD NOT SAVED: use an 8..63 character printable ASCII passphrase');return 1
 if folder.is_symlink() or folder.stat().st_uid!=os.getuid() or folder.stat().st_mode&0o077:
  print('PRIVATE DIRECTORY OWNER/MODE CHECK FAILED');return 1
 fd,name=tempfile.mkstemp(prefix='.wifi-',dir=folder)
 try:
  os.fchmod(fd,0o600)
  with os.fdopen(fd,'w') as f:
   json.dump({'schema':'RABBIT-WIFI-LOCAL-1','ssid':a.ssid,'security':'detect-from-scan','passphrase':secret},f,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
  os.replace(name,folder/'wifi-connection.json')
 finally:
  if os.path.exists(name):os.unlink(name)
 print('LOCAL WIFI CREDENTIAL SAVED MODE0600; PASSWORD NOT PRINTED; NO RADIO')
 return 0
if __name__=='__main__':raise SystemExit(main())
