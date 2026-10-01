#!/usr/bin/env python3
"""Compile, sign, transmit, and await a Universal Package v3 receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from compile_world import compile_world
from transport import encode_transfer, encode_segments, fnv1a32

ROOT = Path(__file__).resolve().parent
LEGACY = ROOT.parent / "x86-64-uefi-ble-program-loader-v0"


def sender_source() -> str:
    source = (LEGACY / "mac_vm_program.m").read_text(encoding="utf-8")
    source = source.replace("@property(nonatomic) NSUInteger index;", """@property(nonatomic) NSUInteger index;
@property(nonatomic) NSUInteger segment;
@property(nonatomic, strong) NSArray<NSArray<NSString *> *> *segments;
@property(nonatomic, strong) NSArray<NSString *> *hashes;""")
    source = source.replace('for (int i = 3; i < argc; ++i) [values addObject:[NSString stringWithUTF8String:argv[i]]];', """
        NSData *frameData = [NSData dataWithContentsOfFile:[NSString stringWithUTF8String:argv[3]]];
        id frameValues = frameData ? [NSJSONSerialization JSONObjectWithData:frameData options:0 error:nil] : nil;
        if (![frameValues isKindOfClass:[NSDictionary class]]) return 2;
        NSArray *segments = frameValues[@"segments"], *hashes = frameValues[@"hashes"];
        if (![segments isKindOfClass:[NSArray class]] || ![hashes isKindOfClass:[NSArray class]]
                || !segments.count || segments.count > 342 || hashes.count != segments.count) return 2;
        for (NSArray *block in segments) {
            if (![block isKindOfClass:[NSArray class]] || !block.count || block.count > 66) return 2;
            for (id value in block) {
                if (![value isKindOfClass:[NSString class]] || [value length] != 36 || ![[NSUUID alloc] initWithUUIDString:value]) return 2;
            }
        }
        for (id hash in hashes) {
            if (![hash isKindOfClass:[NSString class]] || [hash length] != 8) return 2;
            char *end=NULL; strtoul([hash UTF8String],&end,16); if (*end) return 2;
        }
        [values addObjectsFromArray:segments[0]];
""")
    source = source.replace("        (void)sender;", """        sender.segments=segments; sender.hashes=hashes; sender.segment=0;
        sender.expectedHash=(uint32_t)strtoul([hashes[0] UTF8String],NULL,16);
        (void)sender;""")
    marker = '        fprintf(stdout, "ACK RECEIVED: TRANSFER=%02X HASH=%08X APPLIED_COUNTER=%u\\n",'
    if marker not in source:
        raise ValueError("reviewed sender receipt marker changed")
    source = source.replace(marker, """        if (self.segment+1 < self.segments.count) {
            fprintf(stdout,"BLOCK RECEIVED: %lu/%lu; staging only\\n",(unsigned long)(self.segment+1),(unsigned long)self.segments.count); fflush(stdout);
            [self.timer invalidate]; [self.peripheral stopAdvertising];
            self.segment++; self.uuids=self.segments[self.segment]; self.index=self.uuids.count;
            self.expectedHash=(uint32_t)strtoul(self.hashes[self.segment].UTF8String,NULL,16);
            // Dell resumes passive scanning after the bounded 1500ms checkpoint ACK.
            [self scheduleAdvanceAfter:1.8]; return;
        }
""" + marker)
    return (source.replace("could not advertise Rabbit VM frame", "could not advertise Rabbit Universal Package frame")
            .replace("usage: rabbit-vm-program TRANSFER HASH UUID...", "usage: rabbit-universal-package TRANSFER HASH UUID...")
            .replace("RABBIT VM PROGRAM TRANSFER STARTED", "RABBIT UNIVERSAL PACKAGE TRANSFER STARTED"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("world", nargs="?", type=Path, default=ROOT / "worlds" / "cat-chases-smooth-mouse.json")
    parser.add_argument("--counter", type=int, required=True)
    args = parser.parse_args()
    try:
        private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        package = compile_world(args.world, args.counter, private)
        frames = encode_transfer(package)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"FAIL: could not build package: {error}")
        return 1
    bundle = encode_segments(package)
    digest = fnv1a32(package)
    transfer = frames[0][3]
    print(f"WORLD={args.world}")
    print(f"PACKAGE_BYTES={len(package)}; SHA256={hashlib.sha256(package).hexdigest()}")
    print(f"PACKAGE_FNV1A32={digest:08X}; TRANSFER={transfer:02X}; COUNTER={args.counter}")
    print(f"FRAMES={len(frames)}; transport=v2; exact ACK required")
    minimum = sum(len(s)*.45+1.8 for s in bundle["segments"])
    print(f"BLOCKS={len(bundle['segments'])}; minimum {minimum:.1f} seconds; missing blocks retry locally.")
    xcrun = shutil.which("xcrun")
    if xcrun is None:
        print("FAIL: xcrun is not installed or not on PATH")
        return 1
    with tempfile.TemporaryDirectory(prefix="rabbit-universal-package-") as temporary:
        directory = Path(temporary)
        source = directory / "mac_package_sender.m"
        executable = directory / "rabbit-universal-package"
        frame_file = directory / "frames.json"
        frame_file.write_text(json.dumps(bundle), encoding="ascii")
        source.write_text(sender_source(), encoding="utf-8")
        environment = os.environ.copy()
        for name in ("CPATH", "C_INCLUDE_PATH", "CPLUS_INCLUDE_PATH", "SDKROOT"):
            environment.pop(name, None)
        command = [xcrun, "--sdk", "macosx", "clang", "-fobjc-arc", str(source), "-o", str(executable),
                   "-framework", "Foundation", "-framework", "CoreBluetooth", "-Xlinker", "-sectcreate",
                   "-Xlinker", "__TEXT", "-Xlinker", "__info_plist", "-Xlinker", str(LEGACY / "RabbitColorCommand-Info.plist")]
        print(f"SENDER_SOURCE_SHA256={hashlib.sha256(source.read_bytes()).hexdigest()}")
        if subprocess.run(command, check=False, env=environment).returncode:
            return 1
        try:
            return subprocess.run([str(executable), f"{transfer:02X}", f"{digest:08X}", str(frame_file)], check=False).returncode
        except KeyboardInterrupt:
            return 130


if __name__ == "__main__":
    raise SystemExit(main())
