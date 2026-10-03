#!/usr/bin/env python3
"""Apply a reviewable, idempotent source patch to the pinned test-only iPXE tree."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
IPXE='6262f1081fe185564e8ec8365a1d23597ec6e6f5'
def main():
    vendor=ROOT/'vendor/ipxe'
    if subprocess.check_output(['git','-C',str(vendor),'rev-parse','HEAD'],text=True).strip()!=IPXE:
        raise SystemExit('iPXE revision differs')
    relative='src/interface/efi/efi_init.c'
    original=subprocess.check_output(['git','-C',str(vendor),'show',f'{IPXE}:{relative}'],text=True)
    marker='\t/* Install image unload method */\n\tefi_loaded_image->Unload = efi_unload;\n'
    if original.count(marker)!=1:raise SystemExit('source anchor differs')
    modified=original.replace('#include <ipxe/efi/efi.h>',
        '#include <ipxe/efi/efi.h>\n#include <ipxe/efi/efi_download.h>\n'
        'extern int rabbit_config_install(EFI_HANDLE);\nextern void rabbit_config_uninstall(EFI_HANDLE);')
    modified=modified.replace(marker,'\t/* Install image unload method after all services succeed. */\n'+'''
\t/* Rabbit TEST profile: expose cooperative DHCP and bounded-client downloads. */
\tif ((rc = rabbit_config_install(image_handle)) != 0) {
\t\tefirc=EFIRC(rc); efi_driver_uninstall(); goto err_driver_install;
\t}
\tif ((rc = efi_download_install(image_handle)) != 0) {
\t\trabbit_config_uninstall(image_handle); efirc=EFIRC(rc);
\t\tefi_driver_uninstall(); goto err_driver_install;
\t}
\tefi_loaded_image->Unload = efi_unload;
''')
    marker='\t/* Shut down */\n\tshutdown_exit();'
    if modified.count(marker)!=1:raise SystemExit('unload source anchor differs')
    modified=modified.replace(marker,'\tefi_download_uninstall(image_handle);\n'
        '\trabbit_config_uninstall(image_handle);\n'+marker)
    destination=vendor/relative
    if destination.read_text() not in (original,modified):raise SystemExit('unrelated vendor edits')
    destination.write_text(modified)
    (vendor/'src/interface/efi/ipxe_rabbit_config.c').write_bytes((ROOT/'ipxe_rabbit_config.c').read_bytes())
    # Keep the small upstream helper's closed allocations alive until callbacks
    # return, then free them after step()/Abort. Never free an active callback.
    relative='src/interface/efi/efi_download.c'
    original=subprocess.check_output(['git','-C',str(vendor),'show',f'{IPXE}:{relative}'],text=True)
    modified=original.replace('struct efi_download_file {','struct efi_download_file {\n\tstruct list_head retired;')
    modified=modified.replace('/* xfer interface */','static LIST_HEAD(retired_downloads);\n/* xfer interface */')
    marker='\tefi_snp_release();\n}'
    if modified.count(marker)!=1:raise SystemExit('download close anchor differs')
    modified=modified.replace(marker,'\tefi_snp_release();\n\tlist_add_tail(&file->retired, &retired_downloads);\n}')
    marker='\tstep();\n\treturn EFI_SUCCESS;'
    if modified.count(marker)!=1:raise SystemExit('download poll anchor differs')
    modified=modified.replace(marker,'''
\tstep();
\tstruct efi_download_file *file, *tmp;
\tlist_for_each_entry_safe(file, tmp, &retired_downloads, retired) {
\t\tlist_del(&file->retired); free(file);
\t}
\treturn EFI_SUCCESS;''')
    destination=vendor/relative
    if destination.read_text() not in (original,modified):raise SystemExit('unrelated download edits')
    destination.write_text(modified)
if __name__=='__main__':main()
