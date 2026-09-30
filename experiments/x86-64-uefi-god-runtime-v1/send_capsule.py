#!/usr/bin/env python3
"""Compile, sign, transmit, and await the exact God Runtime capsule receipt."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from capsule import SceneConfig, encode
from transport import as_uuid, encode_transfer, fnv1a32

ROOT = Path(__file__).resolve().parent
INVENTORY = ROOT.parent / "reusable-creation-inventory-v1"
LEGACY_SENDER = ROOT.parent / "x86-64-uefi-ble-program-loader-v0"
sys.path.insert(0, str(INVENTORY))
from rabbit_inventory import build_share_package, load_json  # noqa: E402


def reviewed_capsule(config: SceneConfig) -> bytes:
    """Build the exact reviewed Inventory package and bind it into a capsule."""

    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    catalog = load_json(INVENTORY / "catalog.json")
    merge_name = "toon-cat-chases-mouse.merge.json" if config.scene == "toon-cat-mouse" else "cat-plays-with-ball.merge.json"
    merge = load_json(INVENTORY / "examples" / merge_name)
    package, _ = build_share_package(catalog, merge, private)
    package_digest = hashlib.sha256(package).hexdigest()
    if config.inventory_package_sha256 and config.inventory_package_sha256 != package_digest:
        raise ValueError("reviewed Inventory package identity changed")
    return encode(SceneConfig(
        counter=config.counter,
        inventory_package_sha256=package_digest,
        cat_x=config.cat_x,
        cat_y=config.cat_y,
        ball_x=config.ball_x,
        ball_y=config.ball_y,
        ball_vx=config.ball_vx,
        ball_vy=config.ball_vy,
        health_fault=config.health_fault,
        scene=config.scene,
    ), private)


def sender_source() -> str:
    source = (LEGACY_SENDER / "mac_vm_program.m").read_text(encoding="utf-8")
    return (source
        .replace("could not advertise Rabbit VM frame", "could not advertise Rabbit God capsule frame")
        .replace("usage: rabbit-vm-program TRANSFER HASH UUID...", "usage: rabbit-god-capsule TRANSFER HASH UUID...")
        .replace("RABBIT VM PROGRAM TRANSFER STARTED", "RABBIT GOD CAPSULE TRANSFER STARTED"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Send one signed Scene/Anima capsule to the physical Dell")
    parser.add_argument("--counter", type=int, required=True, help="strictly increasing counter for this Dell boot")
    parser.add_argument("--scene", choices=("cat-ball", "toon-cat-mouse"), default="toon-cat-mouse")
    parser.add_argument("--cat-x", type=int, default=28)
    parser.add_argument("--cat-y", type=int, default=62)
    parser.add_argument("--ball-x", "--mouse-x", dest="ball_x", type=int, default=132)
    parser.add_argument("--ball-y", "--mouse-y", dest="ball_y", type=int, default=24)
    parser.add_argument("--ball-vx", "--mouse-vx", dest="ball_vx", type=int, default=-2)
    parser.add_argument("--ball-vy", "--mouse-vy", dest="ball_vy", type=int, default=2)
    args = parser.parse_args()
    try:
        capsule = reviewed_capsule(SceneConfig(
            counter=args.counter,
            inventory_package_sha256="",
            cat_x=args.cat_x,
            cat_y=args.cat_y,
            ball_x=args.ball_x,
            ball_y=args.ball_y,
            ball_vx=args.ball_vx,
            ball_vy=args.ball_vy,
            scene=args.scene,
        ))
        frames = encode_transfer(capsule)
    except (OSError, ValueError, KeyError) as error:
        print(f"FAIL: could not build capsule: {error}")
        return 1

    uuids = [as_uuid(frame) for frame in frames]
    capsule_hash = fnv1a32(capsule)
    transfer = frames[0][3]
    print(f"CAPSULE_SHA256={hashlib.sha256(capsule).hexdigest()}")
    print(f"CAPSULE_FNV1A32={capsule_hash:08X}; TRANSFER={transfer:02X}; COUNTER={args.counter}")
    target_name = "mouse" if args.scene == "toon-cat-mouse" else "ball"
    print(f"SCENE={args.scene} cat({args.cat_x},{args.cat_y}) {target_name}({args.ball_x},{args.ball_y}) velocity({args.ball_vx},{args.ball_vy})")
    print(f"FRAMES={len(frames)}; each frame repeats for 450 ms; exact ACK required")

    xcrun = shutil.which("xcrun")
    if xcrun is None:
        print("FAIL: xcrun is not installed or not on PATH")
        return 1
    with tempfile.TemporaryDirectory(prefix="rabbit-god-capsule-") as temporary:
        directory = Path(temporary)
        source = directory / "mac_capsule_sender.m"
        executable = directory / "rabbit-god-capsule"
        source.write_text(sender_source(), encoding="utf-8")
        command = [
            xcrun, "--sdk", "macosx", "clang", "-fobjc-arc", str(source), "-o", str(executable),
            "-framework", "Foundation", "-framework", "CoreBluetooth", "-Xlinker", "-sectcreate",
            "-Xlinker", "__TEXT", "-Xlinker", "__info_plist", "-Xlinker",
            str(LEGACY_SENDER / "RabbitColorCommand-Info.plist"),
        ]
        environment = os.environ.copy()
        for name in ("CPATH", "C_INCLUDE_PATH", "CPLUS_INCLUDE_PATH", "SDKROOT"):
            environment.pop(name, None)
        print(f"SENDER_SOURCE_SHA256={hashlib.sha256(source.read_bytes()).hexdigest()}")
        if subprocess.run(command, check=False, env=environment).returncode:
            return 1
        try:
            return subprocess.run(
                [str(executable), f"{transfer:02X}", f"{capsule_hash:08X}", *uuids], check=False
            ).returncode
        except KeyboardInterrupt:
            return 130


if __name__ == "__main__":
    raise SystemExit(main())
