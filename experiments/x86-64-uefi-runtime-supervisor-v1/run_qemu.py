#!/usr/bin/env python3
"""Automated QEMU native swaps, failure gates and watchdog-reset observation."""
import argparse
import json
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time

from build_image import ROOT, build, digest


class QMP:
    def __init__(self, path, process):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        deadline = time.monotonic()+15
        while True:
            try:
                self.socket.connect(str(path)); break
            except OSError:
                if process.poll() is not None or time.monotonic()>deadline:
                    raise RuntimeError("QEMU QMP did not become available")
                time.sleep(.05)
        self.socket.settimeout(15)
        self.file = self.socket.makefile("rwb")
        self.read()
        self.execute("qmp_capabilities")

    def read(self):
        line = self.file.readline()
        if not line:
            raise RuntimeError("QEMU monitor closed")
        return json.loads(line)

    def execute(self, command, arguments=None):
        self.file.write(json.dumps({"execute":command,"arguments":arguments or {}}).encode()+b"\n")
        self.file.flush()
        while True:
            result=self.read()
            if "error" in result:
                raise RuntimeError("QMP error: " + str(result["error"]))
            if "return" in result:
                return result["return"]

    def key(self, character):
        self.execute("send-key",{"keys":[{"type":"qcode","data":character}],"hold-time":80})

    def close(self):
        self.file.close();self.socket.close()


def wait_for(path, marker, process, *, timeout=30, count=1):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        text=path.read_text(errors="replace") if path.exists() else ""
        if text.count(marker)>=count:
            return text
        if process.poll() is not None:
            raise RuntimeError("QEMU exited before " + marker)
        time.sleep(.05)
    raise RuntimeError("QEMU timeout before " + marker + "; log:\n" + text)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ovmf-code",type=Path,default=Path("/usr/share/OVMF/OVMF_CODE_4M.fd"))
    parser.add_argument("--ovmf-vars",type=Path,default=Path("/usr/share/OVMF/OVMF_VARS_4M.fd"))
    parser.add_argument("--archive",action="store_true",help="save current generated observation JSON/log under evidence (no executable binaries)")
    args=parser.parse_args()
    qemu=shutil.which("qemu-system-x86_64")
    if not qemu or not args.ovmf_code.is_file() or not args.ovmf_vars.is_file():
        raise RuntimeError("QEMU and explicit compatible OVMF CODE/VARS paths are required")
    image,bindings=build()
    image2,bindings2=build()
    if image!=image2 or bindings!=bindings2:
        raise RuntimeError("repeated probe builds are not deterministic")
    ROOT.joinpath("runs").mkdir(exist_ok=True)
    output=Path(tempfile.mkdtemp(prefix="q-",dir=ROOT/"runs"))
    disk=output/"probe.img";disk.write_bytes(image)
    variables=output/"vars.fd";shutil.copyfile(args.ovmf_vars,variables)
    log=output/"debug.log";qmp_path=output/"qmp.sock"
    stderr=(output/"qemu.stderr").open("wb")
    command=[qemu,"-machine","q35","-m","256M","-nic","none","-display","none",
             "-qmp",f"unix:{qmp_path},server=on,wait=off","-debugcon",f"file:{log}",
             "-drive",f"if=pflash,format=raw,unit=0,readonly=on,file={args.ovmf_code}",
             "-drive",f"if=pflash,format=raw,unit=1,file={variables}",
             "-drive",f"file={disk},format=raw,snapshot=on",
             "-device","qemu-xhci,id=rabbit-xhci","-device","usb-kbd,bus=rabbit-xhci.0"]
    process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=stderr)
    monitor=None
    try:
        monitor=QMP(qmp_path,process)
        wait_for(log,"BOOTSTRAP FALLBACK ACTIVE",process)
        monitor.key("t")
        text=wait_for(log,"NATIVE RAM UPDATE DEMO PASS",process)
        markers=["NATIVE A COMMITTED", "NATIVE B COMMITTED",
                 "EXACT RETRY REPEATED RECEIPT ONLY",
                 "FAILED NATIVE HEALTH RETAINED EXACT B AND STATE",
                 "TAMPERED SIGNATURE REJECTED BEFORE LOADIMAGE",
                 "STALE RUNTIME COUNTER REJECTED BEFORE LOADIMAGE",
                 "INCOMPATIBLE SIGNED MODULE ABI RETAINED B"]
        if not all(marker in text for marker in markers):
            raise RuntimeError("missing native update observation")
        committed_screenshot=output/"committed.ppm"
        monitor.execute("screendump",{"filename":str(committed_screenshot)})
        print("PASS: two actual signed native drivers, receipt-only retry and exact unhealthy-state retention",flush=True)
        started=time.monotonic();monitor.key("h")
        wait_for(log,"STARTING SIGNED HUNG INIT",process)
        wait_for(log,"NATIVE HUNG INIT ENTERED",process)
        text=wait_for(log,"BOOTSTRAP FALLBACK ACTIVE",process,count=2)
        elapsed=time.monotonic()-started
        reboot_tail=text.split("STARTING SIGNED HUNG INIT",1)[1]
        if "NATIVE A COMMITTED" in reboot_tail or "NATIVE B COMMITTED" in reboot_tail:
            raise RuntimeError("a volatile candidate was automatically relaunched after reset")
        fallback_screenshot=output/"fallback.ppm"
        monitor.execute("screendump",{"filename":str(fallback_screenshot)})
        report={"schema_version":1,"status":"OBSERVED-QEMU-NATIVE-RAM-SWAPS-AND-WATCHDOG-FALLBACK",
                "bindings":bindings,"observer_sha256":digest(Path(__file__).read_bytes()).hex(),
                "host_verifier_sha256":digest((ROOT/"verify.py").read_bytes()).hex(),
                "qemu_version":subprocess.check_output([qemu,"--version"],text=True).splitlines()[0],
                "ovmf_code_sha256":digest(args.ovmf_code.read_bytes()).hex(),
                "ovmf_initial_vars_sha256":digest(args.ovmf_vars.read_bytes()).hex(),
                "observed_markers":markers+["NATIVE HUNG INIT ENTERED"],"hung_init_to_bootstrap_seconds":round(elapsed,3),
                "debug_log_sha256":digest(log.read_bytes()).hex(),
                "committed_screenshot_sha256":digest(committed_screenshot.read_bytes()).hex(),
                "fallback_screenshot_sha256":digest(fallback_screenshot.read_bytes()).hex(),
                "physical_verified":False,"bluetooth_verified":False,
                "native_memory_isolation":False,
                "recovery_scope":"reviewed infinite init loop with interrupts enabled; not arbitrary native corruption/disabled watchdog",
                "guest_persistent_writes":0,"host_mutations":"generated images, ephemeral OVMF variable store, logs and screenshots only"}
        (output/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
        if args.archive:
            evidence=ROOT/"evidence";evidence.mkdir(exist_ok=True)
            (evidence/"qemu-observed.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
            (evidence/"qemu-observed.log").write_bytes(log.read_bytes())
        print("PASS: hung native init triggered firmware watchdog reset; immutable bootstrap returned",flush=True)
        print("OBSERVED: " + str(output/"report.json"),flush=True)
    finally:
        if monitor:
            try: monitor.execute("quit")
            except (OSError,RuntimeError): pass
            monitor.close()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:process.kill();process.wait()
        stderr.close()


if __name__=="__main__":
    main()
