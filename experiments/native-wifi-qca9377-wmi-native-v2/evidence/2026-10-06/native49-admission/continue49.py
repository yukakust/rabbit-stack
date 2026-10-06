from pathlib import Path
import json,sys,subprocess,time
repo=Path("/Users/yukakust/rabbit-stack");root=repo/"experiments/native-wifi-qca9377-wmi-native-v2"
state=repo/"experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json"
expected=Path(sys.argv[1]).resolve();assert expected.parent==state.parent
route=root/"startup_route.py"
for attempt in range(6):
 s=json.loads(state.read_text())
 if s.get("native_pending")!=str(expected):break
 print("EXACT49 NATIVE DELIVERY",attempt+1,flush=True)
 run=subprocess.run([sys.executable,str(route),"deliver","--state",str(state)],cwd=repo)
 if run.returncode not in (0,1):raise SystemExit(run.returncode)
 if run.returncode==0:break
else:raise SystemExit("STOP bounded native resume limit; preserve exact packet")
s=json.loads(state.read_text());r=json.loads((expected/"report.json").read_text())
if s.get("native_pending") or s["engine"]["native_counter"]!=49 or r["status"]!="EXACT-APPLIED-RECEIPT" or not r["receiver_reported_applied"] or s["engine"]["payload_sha256"]!=r["payload_sha256"]:raise SystemExit("STOP exact49 receipt required")
print("EXACT49 APPLIED; INITIAL PCI READ",flush=True)
diagnostic=root/"runs/control/initial49.json"
sys.path.insert(0,str(root));import startup_route as module
for attempt in range(8):
 with module.flow.state_lock(state):
  run=subprocess.run([str(repo/"experiments/native-wifi-qca9377-operating-v1/runs/control/read-pci43"),"--read"],capture_output=True,text=True,timeout=70)
  (root/"runs/control"/f"initial49-{attempt}.log").write_text(run.stdout+run.stderr)
  if not run.returncode:module.flow.save(diagnostic,json.loads(run.stdout));break
 if "probe still active; retry read-only after cleanup" not in run.stderr:raise SystemExit("STOP initial read failed")
 time.sleep(3)
else:raise SystemExit("STOP initial probe active")
run=subprocess.run([sys.executable,str(route),"asset-prepare","--state",str(state),"--checked",str(root/"runs/checked-candidate"),"--diagnostic",str(diagnostic),"--firmware",str(repo/"experiments/native-wifi-qca9377-v1/runs/mac-control/firmware-6.bin")],cwd=repo)
if run.returncode:raise SystemExit(run.returncode)
s=json.loads(state.read_text());assets=Path(s["hardware_trial_pending"]);stalls=0;last=-1
for attempt in range(24):
 print("EXACT49 ASSET DELIVERY",attempt+1,flush=True)
 run=subprocess.run([sys.executable,str(route),"asset-deliver","--state",str(state),"--session",str(assets)],cwd=repo)
 r=json.loads((assets/"report.json").read_text())
 if run.returncode==0:break
 if run.returncode!=1:raise SystemExit(run.returncode)
 n=r["completed_chunks"];floor=n*65536
 for step in r["sender_steps"]:
  if step["chunk"]!=n:continue
  log=Path(step["log"])
  if not log.exists():continue
  for line in log.read_text().splitlines():
   try:v=json.loads(line)
   except ValueError:continue
   if v.get("packet_sha256")==r["packets"][n]["packet_sha256"] and v.get("error")==0 and v.get("peripheral","").upper()=="F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF":floor=max(floor,n*65536+max(0,v.get("received",0)-224))
 stalls=stalls+1 if floor<=last else 0;last=floor
 if stalls>=2:raise SystemExit("STOP two no-progress attempts; preserve saved session")
else:raise SystemExit("STOP bounded firmware resume limit")
print("ALL12 ASSETS ACCEPTED; WAIT ACTUAL ALL-OWNER RELEASE",flush=True)
for attempt in range(120):
 out=root/"runs/control/boot49.json"
 run=subprocess.run([sys.executable,str(repo/"experiments/native-wifi-qca9377-v1/read_boot.py"),"--read","--output",str(out)],cwd=repo)
 if run.returncode:raise SystemExit(run.returncode)
 d=json.loads(out.with_suffix(".decoded.json").read_text())
 if d["boot_round"] and d["all_loader_resources_released"]:break
 time.sleep(60)
else:raise SystemExit("STOP bounded owner observation")
subprocess.run([sys.executable,str(repo/"experiments/native-wifi-qca9377-service-layout-v1/read_diagnostic.py"),"--read","--output",str(root/"runs/control/operating49.json")],cwd=repo,check=True)
run=subprocess.run([sys.executable,str(root/"read_startup.py"),"--read","--output",str(root/"runs/control/startup49.json")],cwd=repo)
print("ACTUAL49 INIT DIAGNOSTIC CAPTURE; NO ROUTER/IP CLAIM",flush=True);raise SystemExit(run.returncode)
