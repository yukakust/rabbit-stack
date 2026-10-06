#!/usr/bin/env python3
"""Compile unedited mature RSN core; test a precise extracted install boundary."""
import argparse
import hashlib
import json
import pathlib
import subprocess
import tarfile

ARCHIVE_SHA = "912ea06f74e30a8e36fbb68064d6cdff218d8d591db0fc5d75dee6c81ac7fc0a"
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--clang",required=True)
    ap.add_argument("--reference",type=pathlib.Path,required=True)
    ap.add_argument("--output",type=pathlib.Path,required=True)
    a=ap.parse_args(); root=pathlib.Path(__file__).resolve().parent
    a.reference=a.reference.resolve(); a.output=a.output.resolve()
    a.output.mkdir(parents=True,exist_ok=True)
    archive=a.reference/"wpa_supplicant-2.11.tar.gz"
    assert digest(archive)==ARCHIVE_SHA
    with tarfile.open(archive) as tar:
        for m in tar.getmembers():
            if m.isfile():
                assert ".." not in pathlib.PurePosixPath(m.name).parts
                assert not pathlib.PurePosixPath(m.name).is_absolute()
                assert (a.reference/m.name).read_bytes()==tar.extractfile(m).read()
    src=a.reference/"wpa_supplicant-2.11/src"
    wpa=(src/"rsn_supp/wpa.c").read_text()
    install=wpa[wpa.index("static int wpa_supplicant_install_ptk("):
                wpa.index("\n\nstatic int wpa_supplicant_activate_ptk(")]
    auth=wpa[wpa.index("const u8 * wpa_sm_get_auth_addr(struct wpa_sm *sm)\n"):
             wpa.index("\n\n\n#ifdef CONFIG_FILS",wpa.index("const u8 * wpa_sm_get_auth_addr(struct wpa_sm *sm)\n"))]
    excerpt="static const u8 null_rsc[8] = { 0, 0, 0, 0, 0, 0, 0, 0 };\n"+auth+"\n"+install+"\n"
    (a.output/"upstream_install.inc").write_text(excerpt)
    flags=["-O2","-ffunction-sections","-fdata-sections",
           "-DCONFIG_NO_STDOUT_DEBUG","-DCONFIG_NO_WPA_MSG","-DCONFIG_NO_TKIP",
           "-isystem",str(src),"-isystem",str(src/"utils")]
    logs=[]
    def run(cmd):
        r=subprocess.run(cmd,capture_output=True,text=True,check=True)
        logs.extend([json.dumps(cmd),r.stdout,r.stderr]); return r.stdout
    run([a.clang,*flags,"-c",str(src/"rsn_supp/wpa.c"),"-o",str(a.output/"wpa.o")])
    undefined=run(["nm","-u",str(a.output/"wpa.o")])
    symbols=sorted(line.split()[-1] for line in undefined.splitlines())
    run([a.clang,*flags,"-g","-fsanitize=address,undefined","-c",
         str(src/"common/wpa_common.c"),"-o",str(a.output/"wpa_common.o")])
    run([a.clang,*flags,"-g","-fsanitize=address,undefined","-I",str(a.output),
         str(root/"ptk_boundary_test.c"),str(a.output/"wpa_common.o"),
         "-Wl,--gc-sections","-o",str(a.output/"ptk-test")])
    output=run([str(a.output/"ptk-test")])
    assert "PASS 1038 actual-upstream PTK install boundary cases" in output
    (a.output/"host.log").write_text("\n".join(logs))
    report={"status":"HOST-RSN-OBJECT-AND-EXTRACTED-PTK-BOUNDARY-PASS",
            "checks":1038,"archive_sha256":ARCHIVE_SHA,
            "full_rsn_core_object_compiled":True,"full_rsn_core_linked":False,
            "freestanding_core_compiled":False,"actual_4way_handshake_tested":False,
            "extracted_install_sha256":hashlib.sha256(install.encode()).hexdigest(),
            "extracted_auth_address_sha256":hashlib.sha256(auth.encode()).hexdigest(),
            "wpa_core_undefined_symbols":symbols,
            "sources":{n:digest(root/n) for n in ("verify.py","ptk_boundary_test.c")},
            "log_sha256":digest(a.output/"host.log"),
            "compiler":run([a.clang,"--version"]),
            "secret_reads":0,"device_actions":0,"dell_installed":False}
    (a.output/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(report["status"],len(symbols),"unresolved mature-core symbols",report["checks"],"cases")
if __name__=="__main__":main()
