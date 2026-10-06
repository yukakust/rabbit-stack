from pathlib import Path
import json,subprocess,sys
repo=Path("/Users/yukakust/rabbit-stack")
state=repo/"experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json"
session=Path(sys.argv[1]).resolve();assert session.parent==state.parent and session.name.startswith("firmware-ram-")
command=["python3",str(repo/"experiments/native-wifi-qca9377-service-start-v1/operating_route.py"),"asset-deliver","--state",str(state),"--session",str(session)]
def progress():
 report=json.loads((session/"report.json").read_text());n=report["completed_chunks"]
 if n==len(report["packets"]):return 751436
 digest=report["packets"][n]["packet_sha256"];floor=0
 for step in report["sender_steps"]:
  if step["chunk"]!=n:continue
  log=Path(step["log"])
  if not log.exists():continue
  for line in log.read_text().splitlines():
   try:value=json.loads(line)
   except ValueError:continue
   if value.get("packet_sha256")==digest and value.get("peripheral","").upper()=="F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF" and value.get("error")==0:
    floor=max(floor,value.get("received",0))
 return n*65536+max(0,min(65536,floor-224))
stalls=0
for attempt in range(24):
 before=progress();print(f"EXACT SESSION RESUME {attempt+1}; confirmed data floor={before}",flush=True)
 result=subprocess.run(command,cwd=repo)
 after=progress()
 if result.returncode==0:print("ALL EXACT ASSET RECEIPTS VERIFIED; READ QWOP AND QWBT NEXT",flush=True);sys.exit(0)
 if result.returncode!=1:print("STOP: unexpected sender result; preserve exact session",flush=True);sys.exit(result.returncode)
 stalls=stalls+1 if after<=before else 0
 print(f"Saved session retained; data floor={after}; stalled attempts={stalls}",flush=True)
 if stalls>=2:print("STOP: no confirmed progress twice; observation required",flush=True);sys.exit(1)
print("STOP: bounded resume budget reached; preserve exact session",flush=True);sys.exit(1)
