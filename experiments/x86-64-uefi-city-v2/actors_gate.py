"""Actual UEFI city/fullscreen and legacy restore gate, MOCK USB only."""
from actors_build import engine
from scene5 import city_world,compile_scene,models
compile_city,initial_city=city_world.compile_city,city_world.initial_city
import shutil,subprocess,tempfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
flow=engine.flow
ROOT,OLD,LINK,NATIVE,V3,old,prepare,compile_efi,digest=(engine.ROOT,engine.OLD,engine.LINK,engine.NATIVE,engine.V3,engine.old,engine.prepare,engine.compile_efi,engine.digest)
pack=engine.pack
CITY_PROBE=r'''
uint32_t rabbit_test_background(void){return pixels[0];}
int rabbit_test_city_display(void){
 typedef Status(EFIAPI *Locate)(const void*,void*,void**);
 static const uint8_t guid[16]={0xde,0xa9,0x42,0x90,0xdc,0x23,0x38,0x4a,0x96,0xfb,0x7a,0xde,0xd0,0x80,0x51,0x6a};
 void*gop=0;if(((Locate)service(system,320))(guid,0,&gop)||!gop)return 1;
 uint8_t*m=*(uint8_t**)((uint8_t*)gop+24),*info=*(uint8_t**)(m+8);
 uint32_t w=le32(info+4),h=le32(info+8),stride=le32(info+32),fmt=le32(info+12),*frame=*(uint32_t**)(m+24);
 uint32_t sky=fmt?0x8fc3e0:0xe0c38f;
 if(w<=480||h<=270||frame[w-1]!=sky||!frame[(h-1)*stride+w/2]||frame[(h-1)*stride+w/2]==sky)return 1;
 for(unsigned y=0;y<270;y++)for(unsigned x=0;x<480;x++){
  uint32_t c=pixels[y*480+x];if(!fmt)c=((c&255)<<16)|(c&0xff00)|((c>>16)&255);
  if(c!=frame[y*stride+x])return 1;
 }
 return 0;
}
uint32_t rabbit_test_display_hash(void){
 typedef Status(EFIAPI *Locate)(const void*,void*,void**);
 static const uint8_t guid[16]={0xde,0xa9,0x42,0x90,0xdc,0x23,0x38,0x4a,0x96,0xfb,0x7a,0xde,0xd0,0x80,0x51,0x6a};
 void*gop=0;if(((Locate)service(system,320))(guid,0,&gop)||!gop)return 0;
 uint8_t*m=*(uint8_t**)((uint8_t*)gop+24),*info=*(uint8_t**)(m+8);
 uint32_t w=le32(info+4),h=le32(info+8),hash=2166136261u;
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++)hash=(hash^physical[y*physical_stride+x])*16777619u;
 return hash;
}
'''
CITY_TEST=r'''
 if(stage(legacy_city_stream,sizeof(legacy_city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=3)return 1;
 if(stage(upgrade_stream,sizeof(upgrade_stream),2)||rabbit_test_finish()||pump())return 1;
 rabbit_test_status(status);if(status[20]!=RF_APPLIED||le32(status+24)!=2||disconnects!=2)return 1;
 say("ACTOR DRIVER RESTORED ACTUAL CITY4 SNAPSHOT");
 if(stage(city_stream,sizeof(city_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=4)return 1;
 if(rabbit_scene_tick(st))return 1;
 uint32_t hash=rabbit_test_display_hash();
 typedef Status(EFIAPI *ActorStall)(uint64_t);((ActorStall)service(st,248))(600000);
 if(rabbit_scene_tick(st)||hash==rabbit_test_display_hash())return 1;
 say("ACTOR MOTION ADVANCED BY TARGET CLOCK WITHOUT FRAME COUNT TIMING");
 ((ActorStall)service(st,248))(9450000);
 if(rabbit_scene_tick(st)||rabbit_test_city_display())return 1;
 if(rabbit_test_snapshot(before,&a)||before[20]||before[36]!=5||le32(before+12)!=4)return 1;
 say("CITY FULLSCREEN QEMU READY");
 typedef Status(EFIAPI *CityRead)(void*,void*);
 for(;;){uint16_t key[2]={0,0};if(!((CityRead)*(void**)((uint8_t*)st->input+8))(st->input,key)&&key[1]=='g')break;((ActorStall)service(st,248))(10000);}
 if(stage(actor_restore_stream,sizeof(actor_restore_stream),2)||rabbit_test_finish()||pump())return 1;
 rabbit_test_status(status);if(status[20]!=RF_APPLIED||le32(status+24)!=3||disconnects!=3)return 1;
 say("ACTOR DRIVER RESTORED ACTUAL CITY5 SNAPSHOT");
 if(stage(restored_stream,sizeof(restored_stream),1)||status[20]!=RF_APPLIED||le32(status+24)!=5)return 1;
 for(unsigned i=0;i<10;i++)if(rabbit_scene_tick(st))return 1;
 say("CITY DATA APPLIED AND LEGACY DATA RESTORED BEFORE ENGINE ROLLBACK");
'''

def qemu_gate(directory, payload, empty_boot=False):
    """Execute the exact candidate with actual UEFI LoadImage/StartImage, mock radio."""
    color="121826"
    from run_qemu import firmware
    code, variables = firmware()
    fixture = directory / ('actors-empty-boot-qemu' if empty_boot else 'actors-qemu'); fixture.mkdir()
    key = Ed25519PrivateKey.from_private_bytes(bytes(range(32, 64)))
    public = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    target, modules, crypto = prepare(fixture, public)
    world = b'' if empty_boot else flow.compile_world(V3 / 'worlds/ginger-cat-walk-v1.json', 2, flow.CREATOR)
    legacy_city=compile_city(initial_city(),3)
    actor_world=initial_city();actor_world['schema_version']=5;actor_world['actors']=[models()['rabbit.actor.roof-cat-v1']]
    city=compile_scene(actor_world,4)
    restored = flow.compile_world(V3 / "worlds/ginger-cat-walk-v1.json",5,flow.CREATOR)
    def release(p, base, counter):
        return pack(p, private=key, target=target, base_runtime=digest(base), world=world if counter==1 else restored, counter=counter)
    releases = {'world': world, 'a': release(payload, modules[1], 1),
                'city':city, 'legacy_city':legacy_city,
                'upgrade':pack(payload,private=key,target=target,base_runtime=digest(payload),world=legacy_city,counter=2),
                'actor_restore':pack(payload,private=key,target=target,base_runtime=digest(payload),world=city,counter=3),
                'restored':restored, 'b': release(modules[1], payload, 4), 'bad': release(modules[3], modules[1], 5)}
    tampered = bytearray(release(payload, modules[1], 6)); tampered[-1] ^= 1
    releases['tampered'] = bytes(tampered)
    releases['hung'] = release(modules[3], modules[1], 6)  # Referenced but never exercised by this family gate.
    header = ''.join(old.c_bytes(name + '_stream', digest(data) + data) for name, data in releases.items())
    header += old.c_bytes('base_hash', digest(modules[1])) + old.c_bytes('a_hash', digest(payload))
    (fixture / 'test_data.h').write_text(header)
    from build_image import supervisor_source
    (fixture / 'supervisor.c').write_text(supervisor_source() + CITY_PROBE)
    test = (ROOT / 'qemu_test.c').read_text()
    if empty_boot:
        test=test.replace('if(pump()||!connected||stage(world_stream,sizeof(world_stream),1)||status[20]!=RF_APPLIED)return 1;','if(pump()||!connected)return 1;')
    test = test.replace('static int test(SystemTable*st){', 'uint32_t rabbit_test_background(void); int rabbit_test_city_display(void); uint32_t rabbit_test_display_hash(void);\nstatic int test(SystemTable*st){')
    marker = 'say("CONNECTED DRIVER A COMMITTED VIA MOCK USB ACL ATT; OLD CONNECTION CONFIRMED CLOSED; RECEIPT RETAINED");'
    if test.count(marker) != 1: raise ValueError('QEMU gate anchor changed')
    test = test.replace(marker, f'if(rabbit_scene_tick(st)||rabbit_test_background()!=0x{color})return 1;\n ' + marker)
    marker='say("EXACT NATIVE RETRY RECEIPT ONLY; NO SECOND APPLY OR DISCONNECT");'
    if test.count(marker)!=1:raise ValueError('city QEMU anchor differs')
    test=test.replace(marker,marker+CITY_TEST)
    test=test.replace('le32(status+24)!=2||!same(rabbit_test_base(),base_hash,32)||disconnects!=2||pump()', 'le32(status+24)!=4||!same(rabbit_test_base(),base_hash,32)||disconnects!=4||pump()')
    test=test.replace('tampered_stream))||disconnects!=2||violations','tampered_stream))||disconnects!=4||violations')
    (fixture / 'test.c').write_text(test)
    efi = compile_efi(fixture, 'fixture', [fixture / 'test.c', fixture / 'supervisor.c', fixture / 'native_verify.c',
        NATIVE / 'transport_core.c', NATIVE / 'sha256.c', LINK / 'file_core.c', *crypto], definitions=('RABBIT_INTEGRATION_TEST',))
    image = old.load('background_media', ROOT.parent / 'x86-64-uefi-v0/build_image.py').build_image(efi)
    (fixture / 'fixture.img').write_bytes(image); shutil.copyfile(variables, fixture / 'vars.fd')
    observer = old.load('background_qmp', NATIVE / 'run_qemu.py')
    with tempfile.TemporaryDirectory(prefix='rabbit-engine-qmp-', dir='/tmp') as sockets:
        command = [shutil.which('qemu-system-x86_64'), '-machine', 'q35', '-m', '256M', '-nic', 'none', '-display', 'none',
                   '-qmp', f'unix:{sockets}/qmp.sock,server=on,wait=off', '-debugcon', f'file:{fixture}/debug.log',
                   '-drive', f'if=pflash,format=raw,unit=0,readonly=on,file={code}',
                   '-drive', f'if=pflash,format=raw,unit=1,file={fixture}/vars.fd',
                   '-drive', f'file={fixture}/fixture.img,format=raw,snapshot=on',
                   '-device', 'qemu-xhci,id=rabbit-xhci', '-device', 'usb-kbd,bus=rabbit-xhci.0']
        with (fixture / 'stderr.log').open('w') as err:
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=err)
            monitor = None
            try:
                monitor = observer.QMP(Path(sockets) / 'qmp.sock', process)
                observer.wait_for(fixture / 'debug.log', 'CONNECTED BOOTSTRAP FALLBACK ACTIVE', process)
                monitor.key('t')
                observer.wait_for(fixture / 'debug.log', 'CITY FULLSCREEN QEMU READY', process, timeout=45)
                monitor.execute('screendump',{'filename':str(fixture/'city.ppm')})
                monitor.key('g')
                observer.wait_for(fixture / 'debug.log', 'CONNECTED NATIVE INTEGRATION PASS', process, timeout=45)
                snapshot = (fixture / 'debug.log').read_bytes()
            finally:
                if monitor: monitor.close()
                process.terminate()
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired: process.kill(); process.wait()
    (fixture / 'observed.log').write_bytes(snapshot)
    result = {'status': 'EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS', 'payload_sha256': digest(payload).hex(),
              'empty_boot': empty_boot, 'background': color, 'observed_log_sha256': digest(snapshot).hex(), 'physical_verified': False,
              'bluetooth_verified': False, 'controller': 'mock USB only', 'fixture_image_sha256': digest(image).hex()}
    flow.save(fixture / 'report.json', result)
    return result
