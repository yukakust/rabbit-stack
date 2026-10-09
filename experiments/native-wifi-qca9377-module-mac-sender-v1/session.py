"""Durable public chunk delivery; never signs or reads owner/WiFi key material."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
from protocol import validate_chunk, receipt

ROOT=Path(__file__).resolve().parent
STACK=ROOT.parent.parent
STATE=STACK/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def durable(p, data):
    # New sessions are exclusive; existing signed bytes never replaced.
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())

def prepare(directory, chunk_path, epoch, peripheral, previous=None):
    chunk=Path(chunk_path).read_bytes();validate_chunk(chunk)
    if type(epoch) is not int or not 0<epoch<2**64:raise ValueError('epoch')
    import uuid
    peer=str(uuid.UUID(peripheral))
    d=Path(directory).resolve();d.mkdir(mode=0o700,parents=False,exist_ok=False)
    nonce=secrets.token_bytes(8)
    while not any(nonce):nonce=secrets.token_bytes(8)
    durable(d/'chunk.bin',chunk);durable(d/'session.bin',nonce)
    prior=None
    if previous:
        raw=Path(previous).read_bytes()
        if len(raw)!=80 or raw[:8]!=b'QMT00001':raise ValueError('previous public receipt')
        import struct
        e,s,error,length,received,result,reserved=struct.unpack_from('<QIIIIiI',raw,8)
        if e!=epoch or s!=3 or error or not 289<=length<=65824 or received!=length or result<0 or reserved or not any(raw[40:48]) or not any(raw[48:]):raise ValueError('previous receipt not canonical accepted')
        durable(d/'previous.bin',raw);prior=sha(d/'previous.bin')
    meta={'schema':'public-module-saved-session-v1','epoch':epoch,'peripheral':peer,
          'chunk_sha256':sha(d/'chunk.bin'),'session_sha256':sha(d/'session.bin'),
          'previous_sha256':prior,'signatures_created':0,'private_key_reads':0,
          'execution_authority':False,'credential_route':False}
    durable(d/'session.json',(json.dumps(meta,indent=2)+'\n').encode())
    fd=os.open(d,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
    return meta

def resume(directory, executable):
    d=Path(directory).resolve();m=json.loads((d/'session.json').read_text())
    if m['schema']!='public-module-saved-session-v1' or m['signatures_created'] or m['private_key_reads'] or m['execution_authority'] or m['credential_route']:raise ValueError('public session only')
    for name,key in [('chunk.bin','chunk_sha256'),('session.bin','session_sha256')]:
        if sha(d/name)!=m[key]:raise ValueError('saved bytes changed')
    prior=d/'previous.bin' if m['previous_sha256'] else None
    if prior and sha(prior)!=m['previous_sha256']:raise ValueError('prior receipt changed')
    # Same shared physical-state lock as all admitted Dell controllers.
    with (STATE/'state.lock').open('a+b') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        # Whole-candidate admission must be constructed by Root before this API
        # is called; this public transport deliberately cannot approve a driver.
        args=[str(Path(executable).resolve()),str(d/'chunk.bin'),str(d/'session.bin'),
              str(m['epoch']),m['peripheral'],str(d/'receipt.bin'),str(prior) if prior else '-',
              '--public-signed-module-only']
        log=d/('delivery-'+secrets.token_hex(8)+'.log')
        with log.open('xb') as out:p=subprocess.run(args,stdout=out,stderr=subprocess.STDOUT,timeout=620)
        if (d/'receipt.bin').exists():
            result=receipt((d/'receipt.bin').read_bytes(),m['epoch'],(d/'session.bin').read_bytes(),(d/'chunk.bin').read_bytes())
            if p.returncode==0 and result['state']!='accepted':raise ValueError('no exact accepted receipt')
        else:
            result=None
            if p.returncode==0:raise ValueError('missing accepted receipt')
        return p.returncode,result,log
