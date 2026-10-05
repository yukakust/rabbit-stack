from pathlib import Path
import subprocess,time,json,os,sys
base=Path(__file__).resolve().parent
command=["/usr/sbin/networksetup","-setairportpower","en0"]
initial=subprocess.run(["/usr/sbin/networksetup","-getairportpower","en0"],capture_output=True,text=True,check=True)
assert initial.stdout.strip().endswith(": On")
# Restore watchdog owns its own session and survives this controller's exit.
watchdog=subprocess.Popen([sys.executable,"-c","import time,subprocess;time.sleep(60);subprocess.run(['/usr/sbin/networksetup','-setairportpower','en0','on'],timeout=20)"],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
start=time.monotonic();events=[]
try:
 r=subprocess.run(command+["off"],capture_output=True,text=True,timeout=15)
 power=subprocess.run(["/usr/sbin/networksetup","-getairportpower","en0"],capture_output=True,text=True,timeout=10)
 events.append({"action":"off","exit":r.returncode,"power":power.stdout.strip(),"stderr":r.stderr})
 if r.returncode!=0 or not power.stdout.strip().endswith(": Off"):raise RuntimeError("Wi-Fi power-off not confirmed; no experimental radio started")
 time.sleep(3)
 r=subprocess.run([sys.executable,str(base/"try_wifi_off_cached16.py")],cwd="/Users/yukakust/rabbit-stack",capture_output=True,text=True,timeout=38)
 events.append({"action":"radio_trial","exit":r.returncode,"stdout":r.stdout,"stderr":r.stderr})
 elapsed=time.monotonic()-start
 if elapsed<45:time.sleep(45-elapsed)
finally:
 r=subprocess.run(command+["on"],capture_output=True,text=True,timeout=20)
 power=subprocess.run(["/usr/sbin/networksetup","-getairportpower","en0"],capture_output=True,text=True,timeout=10)
 events.append({"action":"restore","exit":r.returncode,"power":power.stdout.strip(),"stderr":r.stderr})
 (base/"wifi-off-trial.json").write_text(json.dumps({"events":events,"elapsed_seconds":time.monotonic()-start,"watchdog_pid":watchdog.pid,"private_key_read":False,"dell_reboot":False},indent=2)+"\n")
 print(json.dumps(events),flush=True)
 if power.stdout.strip().endswith(": On"):
  watchdog.terminate();watchdog.wait(timeout=10)
 else:print("RESTORE NOT CONFIRMED; watchdog remains active",flush=True)
