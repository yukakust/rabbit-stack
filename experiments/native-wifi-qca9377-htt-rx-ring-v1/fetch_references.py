"""Fetch only exact public source references; no execution or device APIs."""
from pathlib import Path
import urllib.request,json,hashlib
R=Path(__file__).resolve().parent
p=json.loads((R/'references.json').read_text());out=R/'runs/reference';out.mkdir(parents=True,exist_ok=True)
for name,h in p['files'].items():
 data=urllib.request.urlopen('https://raw.githubusercontent.com/torvalds/linux/'+p['linux_commit']+'/drivers/net/wireless/ath/ath10k/'+name,timeout=30).read()
 if hashlib.sha256(data).hexdigest()!=h:raise ValueError('exact primary reference mismatch '+name)
 (out/name).write_bytes(data)
print('Exact public references fetched; no compile or device operations')
