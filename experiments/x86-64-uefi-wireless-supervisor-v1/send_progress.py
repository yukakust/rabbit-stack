"""Mac-local journal; correlated receipts are NOT authenticated attestation."""
import json
import errno
import os
import re
import selectors
import signal
import subprocess
import tempfile
import time
from pathlib import Path

EVENT = re.compile(r'^NATIVE CHECKPOINT block=(\d+) hash=([0-9A-F]{8}) family=(22|21)$')


class Progress:
    def __init__(self, path, identity, hashes, resume=False, restart=False):
        self.path = Path(path)
        self.identity, self.hashes = identity, hashes
        self.confirmed = 0
        self.complete = False
        if self.path.is_symlink():
            raise ValueError('progress journal must not be a symlink')
        if self.path.exists():
            if not resume and not restart:
                raise ValueError('journal exists: use --resume; after a confirmed Dell reboot use --restart-after-reboot')
            saved = json.loads(self.path.read_text())
            if not isinstance(saved, dict) or saved.get('schema') != 1 or saved.get('identity') != identity:
                raise ValueError('journal belongs to another release/world/owner/target/base/transport')
            confirmed, complete = saved.get('confirmed'), saved.get('complete')
            if (type(confirmed) is not int or not 0 <= confirmed <= len(hashes)
                    or type(complete) is not bool or complete != (confirmed == len(hashes))):
                raise ValueError('invalid journal progress')
            if not restart:
                self.confirmed, self.complete = confirmed, complete
        elif resume:
            raise ValueError('--resume requires an existing journal')
        self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {'schema': 1, 'identity': self.identity, 'confirmed': self.confirmed,
                'complete': self.complete, 'receipt_authenticated': False}
        descriptor, temporary = tempfile.mkstemp(prefix='.progress-', dir=self.path.parent)
        try:
            with os.fdopen(descriptor, 'w') as output:
                json.dump(data, output, sort_keys=True, indent=2)
                output.write('\n'); output.flush(); os.fsync(output.fileno())
            os.replace(temporary, self.path)
            directory = os.open(self.path.parent, os.O_RDONLY)
            try:
                try: os.fsync(directory)
                except OSError as error:
                    # Some macOS/filesystem combinations do not support directory
                    # fsync. The file was fsynced and atomically renamed already.
                    if error.errno not in (errno.EINVAL, errno.ENOTSUP): raise
            finally: os.close(directory)
        finally:
            if os.path.exists(temporary): os.unlink(temporary)

    def accept(self, line):
        event = EVENT.fullmatch(line.strip())
        if not event:
            return False
        block, hash_value, family = int(event[1]), event[2], event[3]
        if (not 1 <= block <= len(self.hashes) or hash_value != self.hashes[block-1]
                or family != ('21' if block == len(self.hashes) else '22')
                or block not in (self.confirmed, self.confirmed+1)):
            raise ValueError('unexpected checkpoint event; refusing to advance local journal')
        self.confirmed = block
        self.complete = block == len(self.hashes)
        self.save()
        return True

    def configure(self, bundle, frame_ms, attempts):
        # Probe the next unconfirmed checkpoint: it may already be complete if its
        # receipt was lost. If incomplete, replay that block (including duplicates).
        # Old checkpoints are NOT acknowledged after the receiver advances sequence.
        bundle.update(start_block=self.confirmed, probe=bool(self.confirmed),
                      frame_ms=frame_ms, max_attempts=attempts)


def run_logged(command, journal, timeout):
    """Drain byte streams without blocking on a partial line; terminate child on Ctrl-C."""
    log_path = journal.path.with_suffix('.log')
    print('PROGRESS: '+str(journal.path), flush=True)
    print('LOG: '+str(log_path), flush=True)
    start = time.monotonic()
    with log_path.open('ab') as log:
        log.write(b'\n--- sender session ---\n'); log.flush()
        child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        pending = b''
        selector = selectors.DefaultSelector()
        selector.register(child.stdout, selectors.EVENT_READ)
        try:
            while selector.get_map():
                if time.monotonic()-start > timeout:
                    print('TIMEOUT: delivery unknown; journal retained.'); return 4
                for key, _ in selector.select(.25):
                    chunk = os.read(key.fd, 65536)
                    if not chunk:
                        selector.unregister(key.fileobj); break
                    log.write(chunk); log.flush()
                    pending += chunk
                    while b'\n' in pending:
                        line, pending = pending.split(b'\n', 1)
                        text = line.decode('utf-8', errors='replace')
                        print(text, flush=True)
                        if journal.accept(text):
                            print(f'PROGRESS SAVED: {journal.confirmed}/{len(journal.hashes)}', flush=True)
            code = child.wait(timeout=3)
            if code == 0 and not journal.complete:
                raise ValueError('sender exited without an exact final receipt; delivery unknown')
            return code
        except KeyboardInterrupt:
            print('\nSTOPPED: confirmed progress retained; use --resume only in the same Dell boot.')
            return 130
        finally:
            selector.close()
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try: child.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL); child.wait()
            child.stdout.close()


def resumable_source(source):
    """Patch only the Mac adapter, retaining installed receiver byte compatibility."""
    def replace(old, new):
        nonlocal source
        if source.count(old) != 1:
            raise ValueError('reviewed native sender marker changed: '+old[:60])
        source = source.replace(old, new)
    replace('@property(nonatomic) NSUInteger segment;', '''@property(nonatomic) NSUInteger segment;
@property(nonatomic) NSUInteger attempts;
@property(nonatomic) NSUInteger maximumAttempts;
@property(nonatomic) BOOL probing;
@property(nonatomic) double frameSeconds;''')
    replace('        [values addObjectsFromArray:segments[0]];', '''        NSNumber *startValue=frameValues[@"start_block"], *probeValue=frameValues[@"probe"];
        NSNumber *frameValue=frameValues[@"frame_ms"], *attemptValue=frameValues[@"max_attempts"];
        if (![startValue isKindOfClass:[NSNumber class]] || ![probeValue isKindOfClass:[NSNumber class]]
            || ![frameValue isKindOfClass:[NSNumber class]] || ![attemptValue isKindOfClass:[NSNumber class]]) return 2;
        NSUInteger startBlock=startValue.unsignedIntegerValue;
        if (startBlock>=segments.count || frameValue.intValue<450 || frameValue.intValue>2000
            || attemptValue.intValue<1 || attemptValue.intValue>100) return 2;
        BOOL probe=probeValue.boolValue;
        [values addObjectsFromArray:probe ? @[ [segments[startBlock] lastObject] ] : segments[startBlock]];''')
    replace('sender.segments=segments; sender.hashes=hashes; sender.segment=0;', '''sender.segments=segments; sender.hashes=hashes; sender.segment=startBlock;
        sender.maximumAttempts=attemptValue.unsignedIntegerValue; sender.frameSeconds=frameValue.doubleValue/1000.;
        sender.probing=probe;
        if (probe) { fprintf(stdout,"RESUME PROBE: next checkpoint %lu; if no ACK, replay this unconfirmed block without BEGIN\\n",(unsigned long)(startBlock+1)); fflush(stdout); }''')
    replace('[hashes[0] UTF8String]', '[hashes[startBlock] UTF8String]')
    replace('    NSString *uuid = self.uuids[self.index];', '''    if (self.index==0) {
        self.attempts++;
        fprintf(stdout,"BLOCK ATTEMPT: block=%lu/%lu attempt=%lu/%lu expected=%08X\\n",
            (unsigned long)(self.segment+1),(unsigned long)self.segments.count,
            (unsigned long)self.attempts,(unsigned long)self.maximumAttempts,self.expectedHash); fflush(stdout);
        if (self.attempts>self.maximumAttempts) {
            fprintf(stderr,"STALLED: no matching checkpoint ACK; missing ordered frame or missed ACK or lost receiver RAM. Inspect log/Dell; do not infer application.\\n");
            [self.timer invalidate]; [self.peripheral stopAdvertising]; [self.central stopScan]; exit(4);
        }
    }
    NSString *uuid = self.uuids[self.index];''')
    replace('        if (bytes[3] != self.expectedTransfer || programHash != self.expectedHash\n                || checksum != RabbitFNV1a(bytes, 12)) continue;', '''        if (bytes[3] != self.expectedTransfer || programHash != self.expectedHash
                || checksum != RabbitFNV1a(bytes, 12)) {
            fprintf(stdout,"ACK IGNORED: transfer=%02X hash=%08X family=%02X checksum=%s; expected transfer=%02X hash=%08X\\n",
                bytes[3],programHash,bytes[2],checksum==RabbitFNV1a(bytes,12)?"ok":"bad",self.expectedTransfer,self.expectedHash);
            fflush(stdout); continue;
        }''')
    replace('        if (bytes[2] != (finalBlock ? 0x21 : 0x22)) continue;', '''        if (bytes[2] != (finalBlock ? 0x21 : 0x22)) {
            fprintf(stdout,"ACK IGNORED: wrong native receipt family=%02X\\n",bytes[2]); fflush(stdout); continue;
        }
        fprintf(stdout,"NATIVE CHECKPOINT block=%lu hash=%08X family=%02X\\n",(unsigned long)(self.segment+1),programHash,bytes[2]); fflush(stdout);''')
    replace('            self.segment++; self.uuids=self.segments[self.segment];', '            self.probing=NO; self.attempts=0; self.segment++; self.uuids=self.segments[self.segment];')
    replace('    if (self.index == self.uuids.count) self.index = 0;', '''    if (self.index == self.uuids.count) {
        if (self.probing) {
            self.probing=NO; self.uuids=self.segments[self.segment]; self.attempts=0;
            fprintf(stdout,"RESUME REPLAY: checkpoint probe had no ACK; replaying unconfirmed block (partial assembly is allowed)\\n"); fflush(stdout);
        }
        self.index=0;
    }''')
    # Startup and per-frame timer must both use the explicitly bounded user timing.
    if source.count('[self scheduleAdvanceAfter:0.45]') != 2:
        raise ValueError('reviewed sender timing markers changed')
    return source.replace('[self scheduleAdvanceAfter:0.45]', '[self scheduleAdvanceAfter:self.frameSeconds]')
