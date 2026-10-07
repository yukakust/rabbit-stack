#!/usr/bin/env python3
"""Offline source/signature/pure-policy checks; never a radio admission tool."""
import argparse, hashlib, importlib.util, json, pathlib, re, subprocess, tarfile

PINS={
"wireless-regdb-2026.09.03.tar.xz":"b22e0901227b820cd1c280abe681a15b773a5103a5e10dc442e94ebb34cbf58d",
"wens.hex":"6485f5ddecbecbf73113dc669fe23da07f1a5ab60fb1ad932b0062f9d7fe8753",
"regd.c":"928582bfaa3d72574eb40a69e6bc8f268ff7d37f87de805ec21c2c24beedc5c4",
"regd_common.h":"95eca0ec1ab9e7ea248b4b9cc4ad3081cc9f61eb036e7faa9959acb49b356941"}
LINUX="6b5a2b7d9bc156e505f09e698d85d6a1547c1206"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--reference",type=pathlib.Path,required=True)
    ap.add_argument("--clang",required=True);ap.add_argument("--output",type=pathlib.Path,required=True)
    ap.add_argument("--physical52",type=pathlib.Path,required=True)
    a=ap.parse_args();root=pathlib.Path(__file__).resolve().parent
    ref=a.reference.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    for name,h in PINS.items():assert sha(ref/name)==h,name
    release=ref/"wireless-regdb-2026.09.03"
    with tarfile.open(ref/"wireless-regdb-2026.09.03.tar.xz") as tar:
        for m in tar.getmembers():
            if m.isfile():
                assert not pathlib.PurePosixPath(m.name).is_absolute()
                assert ".." not in pathlib.PurePosixPath(m.name).parts
                assert (ref/m.name).read_bytes()==tar.extractfile(m).read()
    logs=[]
    def run(cmd,ok=True):
        r=subprocess.run(cmd,text=True,capture_output=True)
        logs.extend([json.dumps(cmd),r.stdout,r.stderr])
        assert (r.returncode==0)==ok,(cmd,r.stderr)
        return r.stdout
    der=bytes(int(v,16) for v in re.findall(r"0x([0-9A-Fa-f]{2})",(ref/"wens.hex").read_text()))
    (out/"trusted-wens.der").write_bytes(der)
    assert sha(out/"trusted-wens.der")=="eeb049594eb3a83e50bfb6782e7fdf9e96fbd5c2954a0bbb0931cd55321d0bcf"
    run(["openssl","x509","-inform","DER","-in",str(out/"trusted-wens.der"),"-out",str(out/"trusted-wens.pem")])
    cms=["openssl","cms","-verify","-binary","-inform","DER","-certfile",str(out/"trusted-wens.pem"),"-nointern","-noverify"]
    run([*cms,"-in",str(release/"regulatory.db.p7s"),"-content",str(release/"regulatory.db"),"-out",str(out/"verified.db")])
    assert (out/"verified.db").read_bytes()==(release/"regulatory.db").read_bytes()
    run(["python3",str(release/"db2fw.py"),str(out/"rebuilt.db"),str(release/"db.txt")])
    assert (out/"rebuilt.db").read_bytes()==(out/"verified.db").read_bytes()
    for kind in ["data","signature"]:
        source=release/("regulatory.db" if kind=="data" else "regulatory.db.p7s")
        changed=bytearray(source.read_bytes());changed[-1]^=1
        (out/("altered-"+kind)).write_bytes(changed)
        run([*cms,"-in",str(out/"altered-signature" if kind=="signature" else release/"regulatory.db.p7s"),
             "-content",str(out/"altered-data" if kind=="data" else release/"regulatory.db"),"-out",str(out/"rejected.bin")],ok=False)
    # Derive GE rule using the actual signed/rebuilt database's official parser.
    spec=importlib.util.spec_from_file_location("dbparse",release/"dbparse.py")
    parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
    with (release/"db.txt").open() as f:countries=parser.DBParser().parse(f)
    ge=[r for r in countries[b"GE"].permissions if r.freqband.start<3000]
    assert len(ge)==1
    r=ge[0];assert (r.freqband.start,r.freqband.end,r.freqband.maxbw,r.power.max_eirp,r.flags)==(2402,2482,40,20,0)
    regd=(ref/"regd.c").read_text();common=(ref/"regd_common.h").read_text()
    assert "#define ATH_2GHZ_CH01_11\tREG_RULE(2412-10, 2462+10, 40, 0, 20, 0)" in regd
    assert re.search(r"#define ATH_2GHZ_CH12_13\s+REG_RULE\(2467-10, 2472\+10, 40, 0, 20,\\\s+NL80211_RRF_NO_IR\)",regd)
    world=regd.split("static const struct ieee80211_regdomain ath_world_regdom_67_68_6A_6C =",1)[1].split("};",1)[0]
    assert "ATH_2GHZ_CH01_11" in world and "ATH_2GHZ_CH12_13" in world and "ATH_2GHZ_CH14" not in world
    assert re.search(r"case 0x6C:\s+return &ath_world_regdom_67_68_6A_6C;",regd)
    assert "WORC_WORLD = 0x6C" in common and "{WORC_WORLD, NO_CTL, NO_CTL}" in common
    location=json.loads((root/"location.json").read_text());assert location["country_alpha2"]=="GE" and location["source_kind"]=="explicit-owner-conversation-statement"
    phy=a.physical52.resolve();op=json.loads((phy/"operating52.decoded.json").read_text())
    assert sha(phy/"operating52.decoded.json")=="80f34e3863259c7a5a84eb9a93ea19d1f8de0b766f1d064e2c1f1c003c1d7e36"
    assert (op["regdomain"],op["low2"],op["high2"],op["service_valid"])==(108,2312,2732,1)
    compiler_version=run([a.clang,"--version"])
    run([a.clang,"-std=c11","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-g",
         str(root/"passive_policy.c"),str(root/"passive_policy_test.c"),"-o",str(out/"policy-test")])
    result=run([str(out/"policy-test")]);assert "PASS 199278 offline passive metadata checks" in result
    run([a.clang,"--target=x86_64-pc-win32-coff","-ffreestanding","-fno-stack-protector","-std=c11","-Wall","-Wextra","-Werror","-c",str(root/"passive_policy.c"),"-o",str(out/"policy.obj")])
    rows=[]
    for line in result.splitlines():
        if line.startswith("CHANNEL "):
            f,flags,power,regpower,gain=map(int,line.split()[1:]);assert 2402<=f-10 and f+10<=2482
            rows.append(dict(frequency_mhz=f,centre1_mhz=f,centre2_mhz=0,flags=flags,passive=1,width_mhz=20,mode=1,
                max_power_dbm=power,max_reg_power_dbm=regpower,antenna_gain_db=gain,active_probe_permitted=False))
    assert len(rows)==13
    artifact={"status":"OFFLINE-REVIEW-PROPOSAL-NOT-RF-ADMISSION","country_alpha2":"GE","board_regdomain":108,
        "target_id":"363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9",
        "board_id":{"pci_vendor":5772,"pci_device":66,"subsystem_vendor":4136,"subsystem_device":6160},
        "physical52_operating_sha256":sha(phy/"operating52.decoded.json"),"location_sha256":sha(root/"location.json"),
        "ruleset_signed_db_sha256":sha(release/"regulatory.db"),"signature_sha256":sha(release/"regulatory.db.p7s"),
        "signature_verified":True,"trust_anchor_linux_commit":LINUX,"trust_anchor_der_sha256":sha(out/"trusted-wens.der"),
        "trust_model":"explicit Linux-pinned signer certificate; CMS crypto checked; PKIX/time chain not checked; archive OpenPGP not checked",
        "sources_sha256":{n:sha(ref/n) for n in PINS},"regulatory_max_width_mhz":40,
        "hardware_capability_mhz":[2312,2732],"profile":"passive-2.4GHz-legacy11G-20MHz-world108-intersect-GE",
        "candidate_channels":rows,"country_or_board_override":False,"rf_admission_granted":False,
        "probe_absence_physically_verified":False,"legal_primary_GE_2GHz_instrument_verified":False,
        "actual_antenna_gain_measured":False,"device_action_count":0}
    (out/"policy-proposal.json").write_text(json.dumps(artifact,indent=2)+"\n")
    (out/"host.log").write_text("\n".join(logs))
    report={"status":"SIGNED-REGDB-REBUILD-PURE-PASSIVE-FILTER-ASAN-COFF-PASS","checks":199278,
        "compiler":compiler_version,"proposal_sha256":sha(out/"policy-proposal.json"),"log_sha256":sha(out/"host.log"),
        "sources_sha256":{n:sha(root/n) for n in ["passive_policy.c","passive_policy.h","passive_policy_test.c","verify_policy.py","location.json"]},
        "rf_admission_granted":False,"native_integrated":False,"wifi_connected":False,"device_action_count":0}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n");print(report["status"],report["checks"])
if __name__=="__main__":main()
