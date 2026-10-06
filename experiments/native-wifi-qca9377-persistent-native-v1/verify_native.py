#!/usr/bin/env python3
"""Actual native entrypoints, simulated PCI/DMA target. Run on Yukabox only."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
import persistent_build as build
import startup_fixture
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from firmware_chunk_format import packets
import verify_setup_probe as prior
from verify_port import CC
ROOT=build.ROOT;BASE=build.checked.BASE
sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(source):
 s=startup_fixture.fixture(source)
 s='#include "persistent.h"\nconst QcaPersistentNative*qca_persistent_view(void);\n'+s
 s=build.one(s,'static unsigned startup_fault,init_posts;','static unsigned startup_fault,init_posts;static unsigned persistent_fault,active_ticks,stopped;')
 s=build.one(s,'assert(argc==5);startup_fault=', 'assert(argc==6);persistent_fault=(unsigned)atoi(argv[5]);assert(persistent_fault<=5);startup_fault=')
 marker='  tick(ms);const QcaBootNative*b=qca_boot_view();'
 code=r'''
  const QcaPersistentNative*p=qca_persistent_view();
  if(p->life.phase==QCA_RADIO_ACTIVE){
   active_ticks++;
   QcaInitAdapter*a=p->startup->operating->boot->board->setup->read.full.adapter;
   assert(allocations==14&&!dma_frees&&!unmaps&&r->asset.pinned&&a->mapped.irq->port->dma_users==14);
   assert(a->channels.rings[3].owned&&a->bus.owned&&qca_radio_accepts_work(&p->life));
   if(active_ticks==200){
    if(persistent_fault==1)a->channels.rings[3].fault=1;
    else if(persistent_fault==2)a->channels.buffers[7].valid=0;
    else if(persistent_fault==3)((QcaFirmwarePort*)r)->asset.poisoned=1;
    else if(persistent_fault==4)a->channels.routes[3].pipe=0;
    else if(persistent_fault==5)((QcaPersistentNative*)p)->life.last=UINT64_MAX;
    else {assert(qca_stop());stopped=1;assert(!qca_radio_accepts_work(&p->life));}
   }
  }
'''
 s=build.one(s,marker,code+marker+'''\n  if(qca_persistent_view()->error)fprintf(stderr,"PERSISTENT_BEGIN_ERROR=%u\\n",qca_persistent_view()->error);\n''')
 s=build.one(s,'get(128)==((startup_fault==0||startup_fault==1||startup_fault==15)?5u:6u)',
  'get(128)==6u')
 s=build.one(s,'assert(w->phase==2&&!w->error&&w->transaction.phase==QCA_INIT_RUNNING&&w->transaction.ready_seen&&w->transaction.tx_complete);',
  'assert((persistent_fault||(w->phase==2&&!w->error&&w->transaction.phase==QCA_INIT_RUNNING))&&w->transaction.ready_seen&&w->transaction.tx_complete);')
 s=build.one(s,'assert(o->phase==2&&!o->error&&o->service_valid&&o->service.build==',
  'assert((persistent_fault||(o->phase==2&&!o->error))&&o->service_valid&&o->service.build==')
 marker=' printf("WMI_INIT_MOCK'
 start=s.index(marker)
 s=s[:start]+r'''
 const QcaPersistentNative*p=qca_persistent_view();
 fprintf(stderr,"PERSISTENT_FINAL phase=%u error=%u life_error=%u active=%u stop=%u polls=%u\n",p->life.phase,p->error,p->life.error,active_ticks,p->stop_latched,p->polls);
 if(startup_fault==0||startup_fault==1||startup_fault==15){
  assert(active_ticks==200);
  if(!persistent_fault){assert(stopped&&p->life.phase==QCA_RADIO_CLOSED&&qca_persistent_unload_safe(p));}
  else {assert(p->life.phase==QCA_RADIO_RETAINED&&!qca_persistent_unload_safe(p)&&!qca_radio_accepts_work(&p->life));}
 }else assert(!active_ticks&&!p->life.phase);
 printf("PERSISTENT_MOCK active_ticks=%u fault=%u startup=%u phase=%u polls=%u ALL14 RELEASE PASS\n",active_ticks,persistent_fault,startup_fault,p->life.phase,p->polls);
'''+s[start:]
 return s
def main():
 if sys.platform!='linux':raise SystemExit('Native C checks are Yukabox-only')
 out=ROOT/'runs/native-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 assets=out/'fixture-assets';assets.mkdir(exist_ok=True)
 data=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes()
 policy=build.checked.policy();assert sha(data)==policy['digest']
 # Fixed public test owner only; owner runtime key is never accessed.
 key=Ed25519PrivateKey.from_private_bytes(bytes([97])*32);public=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
 for i,p in enumerate(packets(data,key,target=bytes.fromhex(policy['target']),generation=policy['generation'],target_type=policy['type'],target_version=policy['version'],kind=policy['kind'])):(assets/f'chunk-{i}.bin').write_bytes(p)
 native=out/'init_probe.c';old='.owner={'+','.join(str(n) for n in bytes.fromhex(policy['owner']))+'}'
 native.write_text(build.one(native.read_text(),old,'.owner={'+','.join(str(n) for n in public)+'}'))
 (out/'fixture.c').write_text(fixture((BASE/'init_probe_test.c').read_text()))
 inc=['-I'+str(n) for n in (out,BASE,build.checked.prior.actors.OLD,build.checked.prior.actors.NATIVE,BASE/'runs/firmware-chunks')]
 files=prior.prior.FILES+('full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','operating.c','startup.c','startup_gatt.c','init_transaction.c','init_wire.c','memory_plan.c','resources.c','available.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c','persistent.c','lifecycle.c')
 crypto=[BASE/'runs/firmware-chunks'/n for n in ('monocypher.c','monocypher-ed25519.c')];exe=out/'test'
 subprocess.run([str(CC),'-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(build.checked.prior.actors.NATIVE/'sha256.c'),*map(str,crypto),'-o',str(exe)],check=True)
 log='';cases=[(s,0) for s in range(22)]+[(0,f) for f in range(1,6)]
 for startup,fault in cases:
  r=subprocess.run([str(exe),'0',str(assets),'35',str(startup),str(fault)],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=r.stdout+r.stderr;(out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'case{startup}/{fault}: {r.stdout[-1500:]}\n{r.stderr[-4000:]}')
 for n in ('persistent','lifecycle','init_probe'):
  subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/(n+'.c')),'-o',str(out/(n+'.obj'))],check=True)
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for directory in (ROOT,build.LIFE,build.CHECKED) for p in directory.glob('*') if p.is_file()}
 compiled={p.name:sha(p.read_bytes()) for p in [out/'fixture.c',*[out/n for n in files],build.checked.prior.actors.NATIVE/'sha256.c',*crypto]}
 report={'status':'PERSISTENT-ACTUAL-NATIVE-ENTRYPOINTS-ASAN-COFF-PASS','scenarios':len(cases),'source_sha256':inputs,'compiled_fixture_sources_sha256':compiled,'host_log_sha256':sha(log.encode()),'actual_native_entrypoints':True,'physical_verified':False,'signing_admitted':False,'station_ready':False,'rx_pump_implemented':False,'active_ticks_per_success':200,'production_ready_fallback':False,'all14_release_after_explicit_stop':True,'ce3_fault_rejected':True}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
