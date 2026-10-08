"""Yukabox-only early whole EFI measurement; no hardware, real key or state."""
from pathlib import Path
import os,sys,json,hashlib,struct,tempfile
import filter63_build as build
if not sys.platform.startswith('linux'):raise SystemExit('Yukabox only')
out=build.ROOT/'runs/early-caps';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
a=build.checked.prior.actors
_,_,crypto=a.engine.prepare(out,bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7'))
payload=build.compile_driver(out,crypto);(out/'payload.efi').write_bytes(payload)
pe=struct.unpack_from('<I',payload,60)[0];report={'status':'EARLY-UNSIGNED63-WHOLE-EFI-CAPS-ONLY','payload_bytes':len(payload),'mapped_bytes':struct.unpack_from('<I',payload,pe+80)[0],'payload_sha256':hashlib.sha256(payload).hexdigest(),'build_host':'yukabox','source_compiled_only':True,'actual_native_models_passed':False,'physical':False,'owner_key_loads':0,'device_operations':0};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
