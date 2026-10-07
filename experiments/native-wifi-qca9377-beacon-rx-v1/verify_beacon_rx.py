#!/usr/bin/env python3
"""Pinned firmware envelope oracle + unchanged beacon helper, host only."""
import argparse,hashlib,json,pathlib,re,subprocess
LINUX="6b5a2b7d9bc156e505f09e698d85d6a1547c1206"
PINS={"wmi-tlv.c":"02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb",
"wmi-tlv.h":"16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9",
"wmi.c":"68a4fedc3d0cd815c209dda9c0eb3aa3869bd3d35847c633e0c458ba53c320f4",
"wmi.h":"fff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c",
"ieee80211.h":"572535ac04d9dda668501b0233746d0e5c143195d85c02ed3be2532a37c0e8d7"}
SESSION_PINS={"beacon_info.c":"10001c0b5c54748370aaa713be275ebe0476f282d2686f40a0267d4f1ab5d38c",
"beacon_info.h":"98edfe74b4ff64292ab1e8279dced824d06aa8b98639792387b72b732f197a30",
"beacon_info_test.c":"31950de6edf28b70a6cb98f0b69ac3b0dd4bc30296d10ca848f84ef5e3567ddb"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--reference",type=pathlib.Path,required=True)
 ap.add_argument("--session",type=pathlib.Path,required=True);ap.add_argument("--clang",required=True)
 ap.add_argument("--output",type=pathlib.Path,required=True);a=ap.parse_args()
 root=pathlib.Path(__file__).resolve().parent;ref=a.reference.resolve();ses=a.session.resolve()
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 for name,h in PINS.items():assert sha(ref/name)==h,name
 for name,h in SESSION_PINS.items():assert sha(ses/name)==h,name
 names=["beacon_rx.c","beacon_rx.h","beacon_rx_test.c","verify_beacon_rx.py"]
 inputs={n:sha(root/n) for n in names}
 text=(ref/"wmi-tlv.h").read_text()
 services=re.search(r"enum wmi_tlv_service \{.*?\n\};",text,re.S);assert services
 assert "MGMT_RX" not in services.group()
 assert "WMI_TLV_SERVICE_MGMT_TX_HTT" in services.group() and "WMI_TLV_SERVICE_MGMT_TX_WMI" in services.group()
 oracle="#include <stdint.h>\n#include <stddef.h>\ntypedef uint32_t __le32;\n#define __packed __attribute__((packed))\n"
 m=re.search(r"^#define WMI_TLV_EV[^\n]+",text,re.M);assert m;oracle+=m.group()+"\n"
 for name in ["wmi_tlv_grp_id","wmi_tlv_event_id","wmi_tlv_tag"]:
  m=re.search(r"enum "+name+r" \{.*?\n\};",text,re.S);assert m;oracle+=m.group()+"\n"
 m=re.search(r"^#define WMI_TLV_MGMT_RX_NUM_RSSI[^\n]+",text,re.M);assert m;oracle+=m.group()+"\n"
 m=re.search(r"struct wmi_tlv_mgmt_rx_ev \{.*?\n\} __packed;",text,re.S);assert m;oracle+=m.group()+"\n"
 for line in (ref/"wmi.h").read_text().splitlines():
  if re.match(r"#define WMI_RX_STATUS_(OK|ERR_CRC|ERR_DECRYPT|ERR_MIC|ERR_KEY_CACHE_MISS|EXT_INFO)\b",line):oracle+=line+"\n"
 (out/"upstream-mgmt.h").write_text(oracle)
 c=(ref/"wmi-tlv.c").read_text();w=(ref/"wmi.c").read_text()
 body=c.split("static int ath10k_wmi_tlv_op_pull_mgmt_rx_ev",1)[1].split("static int ath10k_wmi_tlv_op_pull_ch_info_ev",1)[0]
 for field in ["channel","buf_len","status","snr","phy_mode","rate"]:assert f"arg->{field} = ev->{field};" in body
 assert "tb[WMI_TLV_TAG_STRUCT_MGMT_RX_HDR]" in body and "tb[WMI_TLV_TAG_ARRAY_BYTE]" in body
 assert "if (skb->len < (frame - skb->data) + msdu_len)" in body
 assert "Firmware is guaranteed to report all essential management frames via" in w
 assert "WMI while it can deliver some extra via HTT" in w
 dispatch=c.split("static void ath10k_wmi_tlv_op_rx",1)[1]
 assert "case WMI_TLV_MGMT_RX_EVENTID:" in dispatch and "ath10k_wmi_event_mgmt_rx(ar, skb);" in dispatch
 # Preserve the unchanged helper's independent 802.11 layout oracle.
 ieee=(ref/"ieee80211.h").read_text()
 beacon="#include <stdint.h>\n#define ETH_ALEN 6\n#define __packed __attribute__((packed))\ntypedef uint8_t u8;typedef uint16_t __le16;typedef uint64_t __le64;\n"
 for name in ["IEEE80211_STYPE_BEACON","IEEE80211_STYPE_PROBE_RESP","WLAN_CAPABILITY_PRIVACY"]:
  m=re.search(r"^#define "+name+r"\b[^\n]+",ieee,re.M);assert m;beacon+=m.group()+"\n"
 for name in ["WLAN_EID_SSID","WLAN_EID_DS_PARAMS","WLAN_EID_RSN","WLAN_EID_HT_OPERATION"]:
  m=re.search(r"\b"+name+r"\s*=\s*([0-9]+)",ieee);assert m;beacon+="#define "+name+" "+m[1]+"\n"
 start=ieee.index("struct ieee80211_mgmt {");common_end=ieee.index("\tunion {",start)
 beacon+=ieee[start:common_end]+" union {\n"
 for name in ["beacon","probe_resp"]:
  end=ieee.index("} __packed "+name+";",common_end)+len("} __packed "+name+";")
  begin=ieee.rfind("\t\tstruct {",common_end,end);assert begin>common_end;beacon+=ieee[begin:end]+"\n"
 beacon+=" } u;\n} __packed;\n";(out/"upstream-beacon.h").write_text(beacon)
 logs=[]
 def run(cmd):
  r=subprocess.run(cmd,text=True,capture_output=True,check=True)
  logs.extend([json.dumps(cmd),r.stdout,r.stderr]);return r.stdout
 flags=["-O1","-g","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-fno-sanitize-recover=all","-I"+str(root),"-I"+str(ses),"-I"+str(out)]
 run([a.clang,*flags,str(root/"beacon_rx.c"),str(ses/"beacon_info.c"),str(root/"beacon_rx_test.c"),"-o",str(out/"rx-test")])
 result=run([str(out/"rx-test")]);m=re.fullmatch(r"PASS ([0-9]+) pinned-layout WMI beacon RX checks\n",result);assert m
 checks=int(m[1]);assert checks==459252,checks
 run([a.clang,*flags,str(ses/"beacon_info.c"),str(ses/"beacon_info_test.c"),"-o",str(out/"beacon-test")])
 helper=run([str(out/"beacon-test")]);assert "9117 groups PASS" in helper
 for source in [root/"beacon_rx.c",ses/"beacon_info.c"]:
  run([a.clang,"-target","x86_64-pc-win32-coff","-ffreestanding","-fno-stack-protector","-mno-red-zone","-Os","-Wall","-Wextra","-Werror","-I"+str(ses),"-c",str(source),"-o",str(out/(source.stem+".obj"))])
 version=run([a.clang,"--version"]);(out/"host.log").write_text("\n".join(logs))
 assert inputs=={n:sha(root/n) for n in names},"local sources changed during proof"
 for name,h in PINS.items():assert sha(ref/name)==h,name
 for name,h in SESSION_PINS.items():assert sha(ses/name)==h,name
 report={"status":"PINNED-WMI-MGMT-RX-BEACON-ADAPTER-ASAN-COFF-PASS","checks":checks,"unchanged_beacon_checks":9117,
  "linux_commit":LINUX,"reference_sha256":PINS,"session_sha256":SESSION_PINS,
  "source_sha256":inputs,
  "mgmt_oracle_sha256":sha(out/"upstream-mgmt.h"),"beacon_oracle_sha256":sha(out/"upstream-beacon.h"),
  "compiler":version,"host_log_sha256":sha(out/"host.log"),"firmware_event_id":28673,
  "expected_header_bytes":40,"native_integrated":False,"device_actions":0,"radio_scanned":False,
  "physical_mgmt_format_observed":False,"physical_ssid_discovered":False,"security_validated":False,"wifi_connected":False}
 (out/"report.json").write_text(json.dumps(report,indent=2)+"\n");print(result.strip());print(report["status"])
if __name__=="__main__":main()
