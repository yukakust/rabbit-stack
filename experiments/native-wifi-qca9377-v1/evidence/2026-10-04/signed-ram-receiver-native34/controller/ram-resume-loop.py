import subprocess,json,pathlib,time
p=pathlib.Path('/Users/yukakust/rabbit-stack/experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/firmware-ram-y_iygsqw')
for attempt in range(30):
 before=json.loads((p/'report.json').read_text())
 r=subprocess.run(['python3','/tmp/rabbit-asset-single-controller.py'])
 report=json.loads((p/'report.json').read_text())
 if r.returncode==0:break
 latest=max(p.glob('chunk-*.log'),key=lambda q:q.stat().st_mtime).read_text()
 if not ('bounded timeout' in latest or 'connection has timed out unexpectedly' in latest):raise SystemExit('Non-timeout failure: preserve exact session; inspect before retry')
 print('Bounded same-session resume',attempt+1,'accepted',report['completed_chunks'],flush=True)
 time.sleep(3)
else:raise SystemExit('Bounded retry count exhausted; preserve exact session')
