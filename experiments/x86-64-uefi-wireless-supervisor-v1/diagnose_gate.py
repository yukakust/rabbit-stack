"""QEMU-only instrumented bootstrap; never a physical candidate."""
from build_image import *
import time
def main():
    directory=Path(tempfile.mkdtemp(prefix='diagnostic-',dir=ROOT/'runs'))
    _,_,crypto=prepare(directory,TEST_OWNER)
    source=assembly_source()
    def marker(letter):return f'    mov al, {ord(letter)}\n    out 0xe9, al\n'
    if '--plain' not in sys.argv:
        source=replace(source,'    call rabbit_supervisor_entry',marker('A')+'    call rabbit_supervisor_entry\n'+marker('B'))
        source=replace(source,'    lea rdx, [rip + title]',marker('C')+'    lea rdx, [rip + title]')
        source=replace(source,'\ntarget_not_found:\n','\ntarget_not_found:\n'+marker('D'))
    (directory/'receiver.S').write_text(source)
    efi=compile_efi(directory,'bootstrap',[directory/'receiver.S',ROOT/'supervisor.c',directory/'native_verify.c',NATIVE/'transport_core.c',NATIVE/'sha256.c',*crypto])
    efi=load('diagnostic_firmware',V1/'build_image.py').inject_firmware(efi)
    media=load('diagnostic_media',ROOT.parent/'x86-64-uefi-v0/build_image.py')
    (directory/'debug.img').write_bytes(media.build_image(efi))
    variables=Path('/usr/share/OVMF/OVMF_VARS_4M.fd');shutil.copyfile(variables,directory/'vars.fd')
    observer=load('diagnostic_qmp',NATIVE/'run_qemu.py');qemu=shutil.which('qemu-system-x86_64')
    command=[qemu,'-machine','q35','-m','256M','-nic','none','-display','none','-debugcon',f'file:{directory}/debug.log',
             '-qmp',f'unix:{directory}/qmp.sock,server=on,wait=off','-drive','if=pflash,format=raw,unit=0,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd',
             '-drive',f'if=pflash,format=raw,unit=1,file={directory}/vars.fd','-drive',f'file={directory}/debug.img,format=raw,snapshot=on',
             '-device','qemu-xhci,id=rabbit-xhci','-device','usb-kbd,bus=rabbit-xhci.0']
    process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);monitor=None
    try:
        monitor=observer.QMP(directory/'qmp.sock',process);time.sleep(20)
        print((directory/'debug.log').read_text(errors='replace'))
        print(monitor.execute('human-monitor-command',{'command-line':'info registers'}))
        monitor.execute('screendump',{'filename':str(directory/'screen.png'),'format':'png'})
        print('DIRECTORY: '+str(directory))
    finally:
        if monitor:
            try:monitor.execute('quit')
            except (OSError,RuntimeError):pass
            monitor.close()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:process.kill();process.wait()
if __name__=='__main__':main()
