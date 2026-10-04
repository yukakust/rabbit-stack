#!/usr/bin/env python3
"""Yukabox host/sanitizer/COFF gate. Never opens physical PCI or Bluetooth."""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from verify_port import CC

ROOT = Path(__file__).resolve().parent


def main():
    if not __debug__:
        raise SystemExit('optimized Python is forbidden for verification')
    out = ROOT / 'runs/init-core'
    out.mkdir(parents=True, exist_ok=True)
    vendor = Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/linux/drivers/net/wireless/ath/ath10k')
    subprocess.run(['python3', str(ROOT / 'verify_init_pack.py'), '--pack', str(ROOT / 'init-target.json'),
                    '--vendor', str(vendor), '--output', str(out / 'pack-report.json')], check=True)
    # Candidate C resource policy must match independently source-checked tables.
    source = (ROOT / 'channels_core.c').read_text()
    for name, expected in [('pipe_id', [0, 1, 2, 3, 4, 7, 7]),
                           ('receive', [0, 1, 1, 0, 0, 0, 1]),
                           ('capacity', [256, 2048, 2048, 2048, 256, 2048, 2048])]:
        values = re.search(r'\b' + name + r'\[7\]=\{([^}]+)\}', source).group(1)
        assert [int(v) for v in values.split(',')] == expected
    include = ['-I' + str(ROOT), '-I' + str(ROOT.parent / 'x86-64-uefi-wireless-supervisor-v1'),
               '-I' + str(ROOT.parent / 'x86-64-uefi-runtime-supervisor-v1')]
    components = [
        ('warm', ['warm_core.c', 'warm_test.c'], [None]),
        ('channels', ['channels_core.c', 'channels_test.c', 'ce_ring.c', 'ce_hw.c',
                      'ce_uefi.c', 'ce_bus.c', 'dma_buffer.c', 'warm_core.c'], list(range(27))),
        ('mapped-irq', ['boot_irq_mapped.c', 'boot_irq_mapped_test.c', 'boot_irq.c',
                        'channels_core.c', 'ce_ring.c', 'ce_hw.c', 'ce_uefi.c', 'ce_bus.c',
                        'dma_buffer.c', 'warm_core.c', 'pci_identity.c', 'power_core.c'], list(range(36))),
        ('adapter', ['init_adapter.c', 'init_adapter_test.c', 'boot_irq_mapped.c', 'boot_irq.c',
                     'channels_core.c', 'ce_ring.c', 'ce_hw.c', 'ce_uefi.c', 'ce_bus.c',
                     'dma_buffer.c', 'warm_core.c', 'reset_core.c', 'pci_identity.c', 'power_core.c'], list(range(13))),
    ]
    logs = ''
    source_names = {'verify_init_core.py', 'verify_init_pack.py', 'init-target.json', 'init_tables.py',
                    'warm_core.h', 'wake_core.h', 'channels_core.h', 'ce_bus.h', 'ce_hw.h', 'ce_ring.h',
                    'ce_uefi.h', 'dma_buffer.h', 'uefi_port.h', 'verify_port.py',
                    'boot_irq_mapped.h', 'boot_irq.h', 'pci_identity.h', 'power_core.h',
                    'init_adapter.h', 'reset_core.h'}
    for _, files, _ in components:
        source_names.update(files)
    sha = lambda data: hashlib.sha256(data).hexdigest()
    inputs = {n: sha((ROOT / n).read_bytes()) for n in sorted(source_names)}
    dependencies = ['experiments/x86-64-uefi-wireless-supervisor-v1/scene_abi.h',
                    'experiments/x86-64-uefi-runtime-supervisor-v1/abi.h']
    dependency_hashes = {n: sha((ROOT.parent.parent / n).read_bytes()) for n in dependencies}
    for name, files, scenarios in components:
        executable = out / (name + '-test')
        subprocess.run(['gcc', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
                        *include, *[str(ROOT / n) for n in files], '-o', str(executable)], check=True)
        for scenario in scenarios:
            command = [str(executable)] + ([] if scenario is None else [str(scenario)])
            run = subprocess.run(command, capture_output=True, text=True, timeout=30,
                                 env={**os.environ, 'UBSAN_OPTIONS': 'halt_on_error=1'})
            logs += run.stdout + run.stderr
            if run.returncode:
                raise RuntimeError(f'{name} scenario {scenario} failed:\n{run.stdout}{run.stderr}')
    for name in ('warm_core', 'channels_core', 'boot_irq_mapped', 'init_adapter'):
        subprocess.run([str(CC), '-target', 'x86_64-pc-win32-coff', '-ffreestanding', '-fno-stack-protector',
                        '-mno-red-zone', '-Os', '-Wall', '-Wextra', '-Werror', *include, '-c',
                        str(ROOT / (name + '.c')), '-o', str(out / (name + '.obj'))], check=True)
    assert inputs == {n: sha((ROOT / n).read_bytes()) for n in sorted(source_names)}, 'sources changed during gate'
    assert dependency_hashes == {n: sha((ROOT.parent.parent / n).read_bytes()) for n in dependencies}, 'ABI changed during gate'
    (out / 'host.log').write_text(logs)
    report = {'status': 'WARM-RESET-FULL-CHANNEL-CORE-HOST-COFF-PASS',
              'source_sha256': inputs, 'dependency_sha256': dependency_hashes,
              'pack_report_sha256': sha((out / 'pack-report.json').read_bytes()),
              'host_log_sha256': sha(logs.encode()), 'channel_scenarios': 27,
              'warm_full_channel_joint_fixture': True,
              'mapped_irq_scenarios': 36, 'legacy_no_dma_irq_guard_preserved': True,
              'native_pci_adapter_scenarios': 13,
              'cold_recovery_requires_rom_and_all_eight_stop': True,
              'warm_each_io_fault_injected': True, 'warm_each_phase_cancelled': True,
              'build_host': 'yukabox', 'native_profile_integrated': False,
              'physical_warm_reset': False, 'physical_target_writes': False,
              'firmware_uploaded': False, 'wifi_association': False}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'])


if __name__ == '__main__':
    main()
