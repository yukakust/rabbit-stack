"""Run the installed V3 scene code on a host buffer, never hardware."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
V3 = ROOT.parent / 'x86-64-uefi-god-runtime-v3'
V1 = ROOT.parent / 'x86-64-uefi-god-runtime-v1'
HARNESS = r'''
#include <stdio.h>
#include "runtime_core.c"
static uint32_t guarded[480*270+2];
int main(int argc,char**argv){
 if(argc!=2)return 9;
 uint8_t bytes[65536];FILE*f=fopen(argv[1],"rb");if(!f)return 9;
 size_t n=fread(bytes,1,sizeof(bytes),f);fclose(f);
 guarded[0]=guarded[480*270+1]=0xdeadbeef;
 framebuffer=guarded+1;stride=width=480;height=270;pixel_format=1;ready=1;
 if(activate(bytes,(uint32_t)n)!=1)return 2;
 for(unsigned i=0;i<240;i++)if(rabbit_scene_tick(0))return 3;
 return guarded[0]!=0xdeadbeef||guarded[480*270+1]!=0xdeadbeef?4:0;
}
'''


def check_world(package_path, cache):
    """Pinned crypto, actual C signature/health/render checks for 240 ticks."""
    cache = Path(cache); cache.mkdir(parents=True, exist_ok=True)
    provenance = json.loads((V1 / 'crypto-provenance.json').read_text())
    crypto = []
    for upstream, expected in provenance['files'].items():
        path = cache / Path(upstream).name
        if not path.exists():
            url = f"https://raw.githubusercontent.com/LoupVaillant/Monocypher/{provenance['git_commit']}/{upstream}"
            with urllib.request.urlopen(url, timeout=30) as response:
                data = response.read(1024 * 1024)
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError('pinned crypto source mismatch')
            path.write_bytes(data)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('cached crypto source mismatch')
        if path.suffix == '.c': crypto.append(path)
    compiler = shutil.which('cc')
    if not compiler: raise ValueError('host C compiler required before world signing/delivery')
    source = cache / 'check.c'; source.write_text(HARNESS)
    executable = cache / 'check'
    # Rebuild, so a changed runtime/cache can never reuse a stale checker binary.
    subprocess.run([compiler, '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-Wno-attributes', '-I', str(V3), '-I', str(cache), str(source),
                    *map(str, crypto), '-o', str(executable)], check=True,
                   capture_output=True, timeout=60)
    result = subprocess.run([str(executable), str(Path(package_path).resolve())], timeout=30)
    if result.returncode: raise ValueError(f'resident C world checks failed: {result.returncode}')
    return {'runtime_core_sha256': hashlib.sha256((V3 / 'runtime_core.c').read_bytes()).hexdigest(),
            'harness_sha256': hashlib.sha256(HARNESS.encode()).hexdigest(),
            'host_ticks': 240, 'physical_execution_verified': False}
