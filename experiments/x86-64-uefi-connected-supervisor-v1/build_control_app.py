#!/usr/bin/env python3
"""Build the local Mac text/voice app; no device write or permission prompt."""
import json
import os
import plistlib
import re
import subprocess
import sys
from pathlib import Path
import ask_connected_world as flow


def build(output, state):
    contents = output / 'Contents'; executable = contents / 'MacOS'; resources = contents / 'Resources'
    executable.mkdir(parents=True, exist_ok=True); resources.mkdir(exist_ok=True)
    info = {'CFBundleIdentifier': 'org.rabbit.world-control', 'CFBundleName': 'Rabbit World',
            'CFBundleDisplayName': 'Rabbit World', 'CFBundleExecutable': 'RabbitWorld',
            'CFBundlePackageType': 'APPL', 'CFBundleVersion': '1', 'CFBundleShortVersionString': '0.1',
            'LSMinimumSystemVersion': '13.0', 'NSHighResolutionCapable': True,
            'NSBluetoothAlwaysUsageDescription': 'Передавать проверенные изменения мира на ваш Dell и читать квитанцию применения.',
            'NSMicrophoneUsageDescription': 'Голосовые просьбы об изменении мира на Dell.',
            'NSSpeechRecognitionUsageDescription': 'Преобразовать просьбу в текст для того же проверенного пути изменения мира.'}
    (contents / 'Info.plist').write_bytes(plistlib.dumps(info))
    flow.save(resources / 'Configuration.json', {'python': sys.executable, 'server': str(flow.ROOT / 'world_control_server.py'),
        'state': str(state.resolve()), 'connection': str(state.resolve().parent / 'control/server.json'), 'path': os.environ['PATH']})
    flags = []
    compiler = Path(subprocess.check_output(['xcrun', '--find', 'swiftc'], text=True).strip())
    include = compiler.parent.parent / 'include/swift'
    maps = [include / 'module.modulemap', include / 'bridging.modulemap']
    # Some installed CLT versions contain TWO identical SwiftBridging definitions.
    # Hide only the redundant definition in this build's VFS; never modify the SDK.
    if all(p.exists() for p in maps):
        bodies = [re.search(r'\nmodule SwiftBridging \{[\s\S]*', p.read_text()) for p in maps]
        if all(bodies) and bodies[0].group() == bodies[1].group():
            cache = flow.ROOT / 'runs/swift-build'; cache.mkdir(exist_ok=True)
            empty = cache / 'empty.modulemap'; empty.write_text('// Redundant definition hidden for this compilation only.\n')
            overlay = cache / 'overlay.json'
            flow.save(overlay, {'version': 0, 'roots': [{'type': 'file', 'name': str(maps[0]), 'external-contents': str(empty)}]})
            flags += ['-vfsoverlay', str(overlay), '-module-cache-path', str(cache / 'modules')]
    env = os.environ.copy()
    for key in ('CPATH', 'C_INCLUDE_PATH', 'CPLUS_INCLUDE_PATH', 'SDKROOT'): env.pop(key, None)
    source_bytes = (flow.ROOT / 'RabbitWorld.swift').read_bytes()
    snapshot_dir = flow.ROOT / 'runs/swift-build'; snapshot_dir.mkdir(exist_ok=True)
    snapshot = snapshot_dir / ('Application-' + flow.sha(source_bytes)[:16] + '.swift')
    snapshot.write_bytes(source_bytes)
    subprocess.run(['xcrun', 'swiftc', '-Onone', *flags, str(snapshot), '-o', str(executable / 'RabbitWorld'),
                    '-framework', 'AppKit', '-framework', 'AVFoundation', '-framework', 'Speech'], env=env, check=True, timeout=180)
    flow.save(resources / 'Build.json', {'source_sha256': flow.sha(source_bytes), 'sdk_modified': False})
    subprocess.run(['codesign', '--force', '--sign', '-', str(output)], check=True, timeout=30)
    return output


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=flow.ROOT / 'runs/apps/Rabbit World.app')
    p.add_argument('--state', type=Path, default=flow.ROOT / 'runs/text-world/state.json')
    a = p.parse_args(); print(build(a.output.resolve(), a.state))
