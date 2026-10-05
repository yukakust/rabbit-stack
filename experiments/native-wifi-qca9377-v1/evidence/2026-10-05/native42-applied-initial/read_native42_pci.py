from pathlib import Path
import json,subprocess,sys
repo=Path("/Users/yukakust/rabbit-stack")
sys.path.insert(0,str(repo/"experiments/native-wifi-qca9377-v1"))
import native_route
from decode_diagnostic import decode
flow=native_route.flow
state_path=repo/"experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json"
out=repo/"experiments/native-wifi-qca9377-v1/runs/boot-trial-baseline/native42-initial-pci.json"
with flow.state_lock(state_path):
 state=flow.read_json(state_path);flow.current(state)
 assert state["engine"]["native_counter"]==42 and not any(state.get(k) for k in ("pending","native_pending","recovery_pending","hardware_trial_pending"))
 r=subprocess.run([str(repo/"experiments/native-wifi-qca9377-v1/runs/mac-control/read-pci")],capture_output=True,text=True,timeout=55)
 out.with_suffix(".log").write_text(r.stderr)
 if r.returncode:print(r.stderr);sys.exit(r.returncode)
 value=json.loads(r.stdout);assert value["peripheral"].upper()=="F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF" and value["writes"]==0 and value["format"]=="QPD18"
 decoded=decode(value);flow.save(out,value);flow.save(out.with_suffix(".decoded.json"),decoded)
 raw=bytes.fromhex(value["raw_hex"]);u=lambda off:int.from_bytes(raw[off:off+4],"little")
 print(json.dumps({"stage":u(128),"error":u(136),"setup_phase":u(280),"setup_error":u(284),"bmi_version":u(324),"bmi_type":u(328),"adapter_phase":u(800),"dma_users":u(220),"cleanup_slots":u(836)}))
