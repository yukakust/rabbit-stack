"""Yukabox-only NEW actual producer47/pool model, not hardware admission."""
from pathlib import Path
import os,sys,tempfile,subprocess,shutil,json,hashlib
import runtime_native_prototype as model
ROOT=model.ROOT;BASE=model.BASE;b=model.b

def fixture(source):
 s='#include "phase_arena.h"\n'+source
 start=s.index('static Status EFIAPI allocate(void*');end=s.index('static Status EFIAPI flush(',start)
 s=s[:start]+r'''
static void*extra_hosts[33];static uint64_t extra_sizes[33];
static Status EFIAPI allocate(void*p,uint32_t type,uint32_t memory,uint64_t pages,void**out,uint64_t attrs){
 assert(p==pci&&!type&&memory==4&&!attrs&&!(config[1]&4)&&allocations<47);
 if(allocations<14){assert(pages==1);*out=hosts[allocations];}
 else{unsigned j=allocations-14;assert(pages==(j==32?3:16));assert(!extra_hosts[j]);*out=extra_hosts[j]=aligned_alloc(4096,(size_t)pages*4096);extra_sizes[j]=pages*4096;assert(*out);}
 allocations++;return 0;
}
static Status EFIAPI map(void*p,uint32_t op,void*host,uint64_t*n,uint64_t*addr,void**token){
 assert(p==pci&&op==2&&!(config[1]&4));unsigned i;
 for(i=0;i<14;i++)if(host==hosts[i]){assert(*n==4096);*addr=0x100000+i*4096;*token=host;return 0;}
 for(i=0;i<33;i++)if(host==extra_hosts[i]){assert(*n==extra_sizes[i]);*addr=0x200000+i*0x20000;*token=host;return 0;}
 assert(!"unowned map");return EFI_ERROR(7);
}
static Status EFIAPI unmap(void*p,void*token){assert(p==pci&&token&&!(config[1]&4));unmaps++;return 0;}
static Status EFIAPI free_buffer(void*p,uint64_t pages,void*host){
 assert(p==pci&&host&&!(config[1]&4));unsigned i;
 for(i=0;i<14;i++)if(host==hosts[i]){assert(pages==1);dma_frees++;return 0;}
 for(i=0;i<33;i++)if(host==extra_hosts[i]){assert(pages*4096==extra_sizes[i]);free(host);extra_hosts[i]=0;extra_sizes[i]=0;dma_frees++;return 0;}
 assert(!"unowned free");return EFI_ERROR(7);
}
''' +s[end:]
 for name in ('allocations','dma_frees','unmaps') :s=s.replace(name+'==14',name+'==47')
 s=s.replace('dma_users==14','dma_users==47')
 marker='static uint8_t*packet_file('
 i=s.index(marker)
 s=s[:i]+r'''
static void*phase_pool,*inventory_pool;static unsigned phase_allocs,phase_frees,inventory_allocs,inventory_frees,info_calls,rng_calls,locate_calls;
static RngStatus EFIAPI public_info(RngProtocol*p,size_t*n,RngGuid*out);
static RngStatus EFIAPI forbidden_rng(RngProtocol*p,RngGuid*g,size_t n,uint8_t*out){(void)p;(void)g;(void)n;(void)out;rng_calls++;assert(!"GetRNG forbidden");return EFI_ERROR(7);}
static RngProtocol inventory_protocol={public_info,forbidden_rng};
static RngStatus EFIAPI public_info(RngProtocol*p,size_t*n,RngGuid*out){assert(p==&inventory_protocol&&n);info_calls++;if(!out){*n=16;return EFI_ERROR(5);}assert(*n==16);*out=rng_ctr_guid;return 0;}
static RngStatus EFIAPI public_locate(RngGuid*g,void*r,void**out){assert(g&&!r&&out&&!memcmp(g,&rng_protocol_guid,16));locate_calls++;*out=&inventory_protocol;return 0;}
extern int runtime_rng_public(RngPublicDiagnostic*);
static Status EFIAPI pool_dispatch(uint32_t kind,uint64_t n,void**out){
 if(kind==4)return ram_allocate(kind,n,out);
 if(kind==2&&n<=256){assert(n==16&&!inventory_pool&&!inventory_allocs);*out=inventory_pool=malloc((size_t)n);assert(*out);inventory_allocs++;return 0;}
 assert(kind==2&&!phase_pool&&!phase_allocs&&!allocations&&n>94016&&n<200000);
 *out=phase_pool=malloc((size_t)n);assert(*out);phase_allocs++;return 0;
}
static Status EFIAPI pool_release(void*p){
 if(p==inventory_pool){assert(p&&inventory_allocs==1&&!inventory_frees);free(p);inventory_pool=0;inventory_frees++;return 0;}
 if(p==phase_pool){assert(p&&phase_allocs==1&&!phase_frees&&allocations==47&&dma_frees==47&&unmaps==47);free(p);phase_pool=0;phase_frees++;return 0;}
 return ram_release(p);
}
extern int runtime_phase_retire(void);
extern const QcaHttPhaseOwner*runtime_phase_model(void);
''' +s[i:]
 s=s.replace('boot[64/8]=ram_allocate;boot[72/8]=ram_release;', 'boot[64/8]=pool_dispatch;boot[72/8]=pool_release;boot[320/8]=public_locate;')
 s=s.replace('upload_fixture(argv[2]);return 0;', r'''upload_fixture(argv[2]);
 assert(phase_allocs==1&&!phase_frees&&phase_pool&&qca_scan_native_view());
 assert(locate_calls==1&&info_calls==2&&rng_calls==0&&inventory_allocs==1&&inventory_frees==1&&!inventory_pool);
 RngPublicDiagnostic rd;assert(runtime_rng_public(&rd)&&rd.phase==2&&rd.algorithm_count==1&&!rd.owned_pool_count&&!rd.uncertain_pool_count);
 uint8_t captured[544];qca_filter64_status(captured);assert(captured[244]==64);
 const QcaHttPhaseOwner*po=runtime_phase_model();const QcaHttRuntime*rt=&po->arena->runtime;const QcaPersistentNative*pp=qca_persistent_view();
 fprintf(stderr,"RETIRE phase%u runtime%u detachable%d port claimed%u dma%u wake%u link%u irq%u scanRadio%p life%u ticket%llu reserved%u queryOwner%p epoch%llu/%llu\n",po->phase,rt->phase,qca_htt_runtime_detachable(rt),rt->port->claimed,rt->port->dma_users,rt->port->wake_owned,rt->port->link_owned,rt->port->boot_irq_owned,(void*)po->arena->scan.radio,pp->life.phase,(unsigned long long)po->arena->scan.tx.ticket,po->arena->scan.tx.credit?po->arena->scan.tx.credit->reserved:0,(void*)pp->htt_owner,(unsigned long long)rt->epoch,(unsigned long long)po->epoch);
 assert(runtime_phase_retire()&&phase_frees==1&&!phase_pool&&!qca_scan_native_view());
 uint8_t absent[544];qca_filter64_status(absent);assert(absent[244]==64&&!absent[8]);
 assert(runtime_phase_retire());puts("ACTUAL TWO ACQUISITIONS 47 MAPS EACH; CAPTURE RETAINED; DETACH BEFORE POOL FREE PASS");return 0;''')
 return s

def main():
 if sys.platform!='linux':raise SystemExit('Native C Yukabox only')
 out=ROOT/'runs/producer-proof';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
 extra=model.sources(out)
 sys.path.insert(0,str(b.BASE));import verify_port
 assets=BASE/'runs/native-host/fixture-assets';assert assets.exists()
 old=BASE/'runs/native-host';(out/'fixture.c').write_text(fixture((old/'fixture.c').read_text()))
 p=out/'init_probe.c';s=p.read_text();s=b.one(s,'.owner={'+','.join(str(n) for n in bytes.fromhex(b.policy()['owner']))+'}', '.owner={'+','.join(str(n) for n in __import__('cryptography.hazmat.primitives.asymmetric.ed25519',fromlist=['Ed25519PrivateKey']).Ed25519PrivateKey.from_private_bytes(bytes([97])*32).public_key().public_bytes(__import__('cryptography.hazmat.primitives.serialization',fromlist=['Encoding']).Encoding.Raw,__import__('cryptography.hazmat.primitives.serialization',fromlist=['PublicFormat']).PublicFormat.Raw))+'}');p.write_text(s)
 for n in ('monocypher.c','monocypher-ed25519.c','monocypher.h','monocypher-ed25519.h','file_core.c','sha256.c'):shutil.copyfile(old/n,out/n)
 inc=['-I'+str(x) for x in (out,b.BASE,b.checked.prior.actors.OLD,b.checked.prior.actors.NATIVE,b.BASE/'runs/firmware-chunks',b.checked.prior.actors.LINK,ROOT.parent/'x86-64-uefi-connected-supervisor-v1')]
 files=list(b.FILES)+['driver.c','city_core.c','pci_identity.c','usb_port.c','bt_event_stream.c','ble_recovery_link.c','diagnostic_gatt.c','file_core.c','sha256.c','monocypher.c','monocypher-ed25519.c']
 subprocess.run([str(verify_port.CC),'-DRABBIT_PREFIX_DRIVER_MODEL','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-DSCENE_REVISION=1','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],*map(str,extra),'-o',str(out/'test')],check=True)
 log='';cases=[0,4,8,9,2]
 for case in cases:
  r=subprocess.run([str(out/'test'),'0',str(assets),'35','1' if case==4 else '0','0','0','0',str(ROOT.parent/'native-wifi-qca9377-scan61-native-v1/runs/world19.rup'),str(case)],capture_output=True,text=True,timeout=120)
  log+=r.stdout+r.stderr;(out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'case{case}: {r.stdout[-1600:]}\n{r.stderr[-5000:]}')
 for name in ['init_probe','init_adapter','channels_core','persistent','lifecycle','driver','dma_runtime','guarded_dma','owner47','phase_arena','runtime_pool','rng_inventory_join']:
  subprocess.run([str(verify_port.CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/(name+'.c')),'-o',str(out/(name+'.obj'))],check=True)
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 report={'status':'ACTUAL-PHASE-POOL-PRODUCER-47-TWO-ACQUISITIONS-ASAN-PASS','cases':cases,'compiled_sources_sha256':{p.name:sha(p) for p in [out/'fixture.c',*[out/n for n in files],*extra,*out.glob('*.h')]},'coff_objects_sha256':{p.name:sha(p) for p in out.glob('*.obj')},'source_sha256':{p.name:sha(p) for p in ROOT.iterdir() if p.is_file()},'host_log_sha256':sha(out/'host.log'),'physical':False,'RX_RING_CFG_published':False,'data_plane':False,'GetRNG_calls':0};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
