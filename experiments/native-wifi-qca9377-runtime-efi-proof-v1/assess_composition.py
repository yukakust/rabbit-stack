"""Offline native54 baseline reproduction + retained callable Noise composition.
No candidate builder, counter change, key load, signature, RF or state workflow.
"""
import pathlib,subprocess,hashlib,json,struct,os
ROOT=pathlib.Path(__file__).resolve().parent
MIRROR=pathlib.Path('/home/yuka/rabbit-world/parallel-scan-native-profile-v1/source')
BASE=MIRROR/'experiments/native-wifi-qca9377-scan-native-profile-v1/runs/checked-candidate'
EXPECTED='3eefea77fbab35bca609216e4a418c2abad695f1a8a83da8aa2ee147bbfefca3'
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
NAMES='init_probe init_adapter warm_core channels_core boot_irq_mapped full_read config_read config_setup bmi_transport diag_ce reset_core power_core uefi_port wake_core rom_ready ce_ring ce_hw ce_uefi ce_bus dma_buffer pcie_link boot_irq firmware_port firmware_channel firmware_gatt firmware_chunks bmi_loader board_query board_smbios boot_image boot_transport boot_native boot_gatt operating operating_gatt startup startup_gatt init_transaction init_wire memory_plan resources available htc_wire htc_session htc_credit htc_control wmi_boot_info wmi_scan persistent lifecycle rx trial profile_gatt'.split()
EXTRA='coordinator tx channel_wire vdev_wire station_scan dispatch scan_stop owned_stop beacon_rx beacon_info scan_native scan_gatt'.split()
def main():
 assert sha(BASE/'persistent-profile.efi')==EXPECTED
 out=ROOT/'runs/composition';out.mkdir(parents=True,exist_ok=True);d=out/'baseline';d.mkdir(exist_ok=True)
 copied={}
 for p in BASE.iterdir():
  if p.is_file() and p.suffix in ('.c','.h'):(d/p.name).write_bytes(p.read_bytes());copied[str(p)]=sha(p)
 old=MIRROR/'experiments/x86-64-uefi-wireless-supervisor-v1';native=MIRROR/'experiments/x86-64-uefi-runtime-supervisor-v1';v3=MIRROR/'experiments/x86-64-uefi-god-runtime-v3';link=MIRROR/'experiments/ble-connected-file-transfer-v1'
 sources=[d/'driver.c',d/'city_core.c',d/'pci_collect.c',d/'pci_identity.c',*[d/(n+'.c') for n in NAMES],d/'usb_port.c',d/'bt_event_stream.c',d/'ble_recovery_link.c',d/'diagnostic_gatt.c',link/'file_core.c',native/'sha256.c',d/'monocypher.c',d/'monocypher-ed25519.c',*[d/(n+'.c') for n in EXTRA]]
 flags=['-std=c11','-Os','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-nostdlib','-I',str(old),'-I',str(native),'-I',str(v3),'-I',str(d),'-ffunction-sections','-fno-asynchronous-unwind-tables','-fno-unwind-tables','-DSCENE_REVISION=1','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13']
 ld=['-Wl,--gc-sections','-Wl,--strip-all','-Wl,--subsystem,11','-Wl,--entry,module_entry','-Wl,--no-insert-timestamp','-Wl,--image-base,0','-Wl,--file-alignment,512','-Wl,--section-alignment,4096']
 logs=[];tmp=out/"compiler-tmp";tmp.mkdir(exist_ok=True);env=os.environ.copy();env["TMPDIR"]=str(tmp)
 def run(cmd):
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=180,env=env);logs.extend([json.dumps(cmd),r.stdout,r.stderr]);assert not r.returncode,r.stderr;return r.stdout
 baseline=out/'reproduced54.efi';run(['x86_64-w64-mingw32-gcc',*flags,*map(str,sources),*ld,'-o',str(baseline)])
 assert sha(baseline)==EXPECTED,(sha(baseline),EXPECTED)
 # Fresh runtime objects are copied, not changed. Share already pinned Monocypher
 # and baseline memory functions; keep our native memory under explicit namespace.
 port=ROOT/'dependencies/port';rt=ROOT/'runs/runtime';objects=sorted((port/'runs/port').glob('coff-*.obj'),key=lambda p:int(p.stem.split('-')[1]))
 # Exact object-list provenance: port verifier source order.
 report=json.loads((port/'runs/port/report.json').read_text());paths=list(report['coff_objects'])
 keep=[];noise=pathlib.Path('/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c');mono=pathlib.Path('/home/yuka/rabbit-world/parallel-secure-provision-v1/reference')
 rename=['-Dmemcpy=qca_runtime_memcpy','-Dmemset=qca_runtime_memset','-Dmemcmp=qca_runtime_memcmp','-Dmemchr=qca_runtime_memchr','-Dstrlen=qca_runtime_strlen']
 inc=['-I'+str(port/'compat'),'-I'+str(port),'-I'+str(port/'dependencies/rng'),'-I'+str(noise/'include'),'-I'+str(noise/'src'),'-I'+str(noise/'src/protocol'),'-I'+str(mono)]
 alloc=['-Dnoise_new_object=qca_noise_new_object','-Dnoise_free=qca_noise_free','-Dmalloc=qca_port_malloc','-Dcalloc=qca_port_calloc','-Dfree=qca_port_free']
 for i,path in enumerate(paths):
  p=pathlib.Path(path)
  if p.name=='monocypher.c':continue
  defs=alloc if p.parent==noise/'src/protocol' or p.parent==noise/'src/backend/ref' or p.name in ['dh_monocypher.c','cipher_monocypher.c'] else []
  if p.name=='util.c':defs=['-Dnoise_new_object=qca_unused_new','-Dnoise_free=qca_unused_free','-Dmalloc=qca_port_malloc','-Dcalloc=qca_port_calloc','-Dfree=qca_port_free']
  obj=out/f'noise-{i}.obj';run([CC,'-target','x86_64-pc-win32-coff','-DWIN32=1','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-Os',*inc,*defs,*rename,'-c',str(p),'-o',str(obj)]);keep.append(obj)
  # Budget-only callable root retains the exact tested EFI helper, renamed only.
 # It is NOT invoked by Rabbit or wired into admission.
 entry=out/'retained-test-root.obj';run([CC,'-target','x86_64-pc-win32-coff','-DWIN32=1','-Defi_main=qca_offline_public_vector_test',*rename,'-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-Os','-I'+str(port/'compat'),'-I'+str(port),'-I'+str(port/'dependencies/rng'),'-I/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c/include','-c',str(ROOT/'efi_smoke.c'),'-o',str(entry)])
 bridge=out/'compiler-memory-bridge.obj';run([CC,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-builtin','-Os','-c',str(ROOT/'compiler_memory_bridge.c'),'-o',str(bridge)])
 combined=out/'offline-retained-runtime.efi'
 run(['x86_64-w64-mingw32-gcc',*flags,*map(str,sources),*[str(p) for p in keep],str(rt/'chkstk.obj'),str(entry),str(bridge),*ld,'-Wl,-u,qca_offline_public_vector_test','-o',str(combined)])
 def mapped(p):b=p.read_bytes();o=struct.unpack_from('<I',b,60)[0];return struct.unpack_from('<I',b,o+24+56)[0]
 assert all(sha(pathlib.Path(p))==h for p,h in copied.items())
 (out/'host.log').write_text('\n'.join(logs))
 r={'status':'OFFLINE-NATIVE54-EXACT-BASELINE-COMPOSITION-LINKED-MAPPED-BUDGET-REJECTED' if mapped(combined)>4194304 else 'OFFLINE-NATIVE54-EXACT-BASELINE-COMPOSITION-BUDGET-PASS','baseline_sha256':EXPECTED,'baseline_bytes':baseline.stat().st_size,'baseline_mapped_bytes':mapped(baseline),'composition_sha256':sha(combined),'composition_bytes':combined.stat().st_size,'composition_mapped_bytes':mapped(combined),'incremental_file_bytes':combined.stat().st_size-baseline.stat().st_size,'efi_file_limit':262144,'efi_mapped_limit':4194304,'within_file_limit':combined.stat().st_size<=262144,'within_mapped_limit':mapped(combined)<=4194304,'budget_admitted':combined.stat().st_size<=262144 and mapped(combined)<=4194304,'mapped_excess_bytes':max(0,mapped(combined)-4194304),'original_staged_source_sha256':copied,'assessor_source_sha256':sha(pathlib.Path(__file__)),'compiler_memory_bridge_sha256':sha(ROOT/'compiler_memory_bridge.c'),'compiler_tmp_owned_directory':True,'noise_memory_calls_namespaced':True,'shared_monocypher_source_sha256':sha(d/'monocypher.c'),'host_log_sha256':sha(out/'host.log'),'runtime_invoked_by_rabbit':False,'combined_efi_executed':False,'counter_changed':False,'candidate_generated_or_signed':False,'real_rng_or_credentials':False,'physical_operations':False}
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['baseline_bytes'],r['composition_bytes'],r['within_file_limit'])
if __name__=='__main__':main()
