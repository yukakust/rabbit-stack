from pathlib import Path
import json,hashlib,importlib.util
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source={};artifacts={}
for p in R.rglob('*'):
 if not p.is_file():continue
 name=p.relative_to(R);parts=name.parts
 if '__pycache__' in parts or 'evidence' in parts or 'tmp' in parts or p.suffix in ('.img','.fd'):continue
 (artifacts if 'runs' in parts else source)[str(name)]=sha(p)
(R/'evidence').mkdir(exist_ok=True)
(R/'evidence/freeze.json').write_text(json.dumps({'status':'ROLE2-MODULE-PARENT-SOFTWARE-FROZEN','source_sha256':source,'artifact_sha256':artifacts,'physical_admission':False,'generation_reserved':False,'entropy_approved':False,'media_images':'hashes in actual QEMU report; reproducible, not retained'},indent=2)+'\n')
spec=importlib.util.spec_from_file_location('role2_final',R/'check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checked=m.checked();checked['freeze_sha256']=sha(R/'evidence/freeze.json');checked['native_report_sha256']=sha(R/'parent-projection/runs/native-projection/report.json');checked['qemu_child_report_sha256']=sha(R/'runs/qemu/report.json');checked['parent_qemu_report_sha256']=sha(R/'parent-projection/runs/native-projection/qemu-report.json')
(R/'evidence/checked-report.json').write_text(json.dumps(checked,indent=2)+'\n');print(json.dumps(checked,indent=2))
