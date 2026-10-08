"""Actual frozen63 producer outputs, synthetic target only; Yukabox native C."""
from pathlib import Path
import hashlib,json,os,sys,tempfile,subprocess,importlib.util,shutil
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent;NATIVE=ROOT.parent/'native-wifi-qca9377-filter64-native-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PIN='1689fc687e78f23c752be7dd35a8b14e8c8ea6fa3e4f24ec7cabe3ac58bac86c'
INSTRUMENT=r'''
unsigned qca_scan_export(unsigned,uint8_t*,unsigned);
static void oracle_hex(FILE*f,const uint8_t*p,unsigned n){for(unsigned i=0;i<n;i++)fprintf(f,"%02x",p[i]);}
static void oracle_capture(void){
 const char*path=getenv("ORACLE_CAPTURE");assert(path);FILE*f=fopen(path,"wb");assert(f);
 fprintf(f,"{\"format\":\"QF641-QSCN1-QFEX1\",\"peripheral\":\"F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF\",\"writes\":0,\"fixture_kind\":\"synthetic-actual-C-producer\",\"physical\":false,\"native_scenario\":%u,\"filter_scenario\":%u,\"pipeline_hex\":[",native_scenario,filter_scenario);
 for(unsigned pass=0;pass<3;pass++){uint8_t value[544];qca_filter64_status(value);fprintf(f,"%s\"",pass?",":"");oracle_hex(f,value,544);fprintf(f,"\"");}
 fprintf(f,"],\"status_hex\":[");
 for(unsigned pass=0;pass<3;pass++){uint8_t value[416];qca_scan_status(value);fprintf(f,"%s\"",pass?",":"");oracle_hex(f,value,416);fprintf(f,"\"");}
 fprintf(f,"],\"pages_hex\":[");
 for(unsigned pass=0;pass<2;pass++){fprintf(f,"%s[",pass?",":"");for(unsigned page=0;page<110;page++){uint8_t value[512];unsigned n=qca_scan_export(page,value,512);assert(n==(page%5==4?56u:512u));fprintf(f,"%s\"",page?",":"");oracle_hex(f,value,n);fprintf(f,"\"");}fprintf(f,"]");}
 fprintf(f,"]}\n");assert(!fflush(f));assert(!fclose(f));
}
'''
def main():
 if not sys.platform.startswith('linux'):raise SystemExit('Native C/ASAN/COFF Yukabox only')
 nrpath=NATIVE/'runs/native-host/report.json';assert sha(nrpath)==PIN;nr=json.loads(nrpath.read_text());src=NATIVE/'runs/native-host';out=ROOT/'runs/producer';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
 inputs=nr['compiled_fixture_sources_sha256']
 for name,h in inputs.items():
  assert sha(src/name)==h,name;shutil.copyfile(src/name,out/name)
 candidate=json.loads((NATIVE/'runs/checked-candidate/report.json').read_text());supplemental={}
 for p in src.iterdir():
  if p.suffix not in ('.c','.h') or p.name in inputs:continue
  h=sha(p);assert candidate['generated_compiler_sources_sha256'].get(p.name)==h,p.name
  supplemental[p.name]=h;shutil.copyfile(p,out/p.name)
 fixture=(out/'fixture.c').read_text();needle='static void upload_fixture(const char*dir){';assert fixture.count(needle)==1;fixture=fixture.replace(needle,INSTRUMENT+'\n'+needle)
 needle=' printf("PERSISTENT_MOCK active_ticks=';assert fixture.count(needle)==1;fixture=fixture.replace(needle,' oracle_capture();\n'+needle);(out/'fixture.c').write_text(fixture)
 spec=importlib.util.spec_from_file_location('oracle_frozen64_build',NATIVE/'filter64_build.py');build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build);sys.path.insert(0,str(build.BASE));import verify_port
 inc=['-I'+str(x) for x in (out,build.BASE,build.checked.prior.actors.OLD,build.checked.prior.actors.NATIVE,build.BASE/'runs/firmware-chunks',build.checked.prior.actors.LINK,ROOT.parent/'x86-64-uefi-connected-supervisor-v1')]
 files=list(build.FILES)+['driver.c','city_core.c','pci_identity.c','usb_port.c','bt_event_stream.c','ble_recovery_link.c','diagnostic_gatt.c','file_core.c','sha256.c','monocypher.c','monocypher-ed25519.c']
 command=[str(verify_port.CC),'-DRABBIT_PREFIX_DRIVER_MODEL','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-DSCENE_REVISION=1','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],'-o',str(out/'test')];subprocess.run(command,check=True)
 cases=[(0,0),(0,4),(0,8),(0,9),(0,2)];logs='';caps={}
 for scenario,filter_case in cases:
  capture=out/f'capture-scan{scenario}-filter{filter_case}.json';env={**os.environ,'ORACLE_CAPTURE':str(capture),'UBSAN_OPTIONS':'halt_on_error=1'}
  run=subprocess.run([str(out/'test'),'0',str(src/'fixture-assets'),'35','1' if filter_case==4 else '0','0','0',str(scenario),str(NATIVE.parent/'native-wifi-qca9377-scan61-native-v1/runs/world19.rup'),str(filter_case)],capture_output=True,text=True,timeout=90,env=env);logs+=run.stdout+run.stderr;(out/'host.log').write_text(logs);assert run.returncode==0,run.stderr
  raw=json.loads(capture.read_text());assert raw['fixture_kind']=='synthetic-actual-C-producer' and len(raw['pages_hex'])==2 and all(len(p)==110 for p in raw['pages_hex']);caps[capture.name]=sha(capture)
 coff=[str(verify_port.CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DRABBIT_PREFIX_DRIVER_MODEL','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/'init_probe.c'),'-o',str(out/'init_probe.obj')];subprocess.run(coff,check=True)
 unchanged={name:h for name,h in inputs.items() if name!='fixture.c'}
 for name,h in unchanged.items():assert sha(out/name)==h,name
 report={'status':'FROZEN64-ACTUAL-C-PRODUCER-HOST-ORACLE-ASAN-COFF-PASS','fixture_kind':'synthetic-actual-C-producer','build_host':'yukabox','native_report_sha256':PIN,'native_payload_sha256':'d40efd8c0b08a9289f0caaa64d931519a253559c53ef732af8961ed91ad49965','original_fixture_sha256':inputs['fixture.c'],'instrumented_fixture_sha256':sha(out/'fixture.c'),'unchanged_production_inputs_sha256':unchanged,'supplemental_exact_candidate_sources_sha256':supplemental,'instrumentation_source_sha256':sha(Path(__file__)),'compile_command':command,'coff_command':coff,'coff_object_sha256':sha(out/'init_probe.obj'),'test_executable_sha256':sha(out/'test'),'host_log_sha256':sha(out/'host.log'),'captures_sha256':caps,'scenario_ids':cases,'physical':False,'BLE':False,'private_key_loads':0,'device_operations':0,'signing_admitted':False,'wifi_connected':False};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
