#!/usr/bin/env python3
"""Run only on Yukabox: checked C policy, not native/radio evidence."""
import argparse, hashlib, json, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser();p.add_argument('--clang',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    if sys.platform!='linux':raise SystemExit('Native C checks are Yukabox-only')
    out=pathlib.Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    def run(args):
        r=subprocess.run(args,check=True,text=True,capture_output=True);return r.stdout+r.stderr
    common=[a.clang,'-std=c11','-O1','-g','-Wall','-Wextra','-Werror']
    run(common+['-fsanitize=address,undefined','-fno-omit-frame-pointer',str(ROOT/'lifecycle.c'),str(ROOT/'lifecycle_test.c'),'-o',str(out/'test')])
    log=run([str(out/'test')]);(out/'host.log').write_text(log)
    run(common+['--target=x86_64-pc-windows-msvc','-ffreestanding','-fno-stack-protector','-mno-red-zone','-c',str(ROOT/'lifecycle.c'),'-o',str(out/'lifecycle.obj')])
    report={'status':'PURE-PERSISTENT-LIFECYCLE-HOST-PASS','physical':False,'integrated':False,'station_ready':False,
      'log':log.strip(),'inputs':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['lifecycle.h','lifecycle.c','lifecycle_test.c','verify.py']}}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
