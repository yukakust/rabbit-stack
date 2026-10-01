#!/usr/bin/env python3
"""Build QEMU-ONLY signed native RAM update fixtures; never install or transmit."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
CONTRACT = REPO / "experiments/runtime-update-contract-v1"
sys.path.insert(0, str(CONTRACT))
from update import digest, pack
from transport import encode


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def c_bytes(name, data):
    return f"static const uint8_t {name}[{len(data)}]={{" + ",".join(str(b) for b in data) + "};\n"


def compile_efi(directory, name, sources, *, driver=False, definitions=()):
    compiler = shutil.which("x86_64-w64-mingw32-gcc")
    inspection = shutil.which("x86_64-w64-mingw32-objdump")
    if not compiler or not inspection:
        raise RuntimeError("x86-64 MinGW GCC and objdump are required")
    output = directory / f"{name}.efi"
    args = [compiler, "-std=c11", "-Os", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
            "-fno-builtin", "-fno-stack-protector", "-mno-red-zone", "-nostdlib",
            "-I", str(ROOT), "-I", str(directory)]
    args.extend("-D" + value for value in definitions)
    args.extend(str(source) for source in sources)
    args += [f"-Wl,--subsystem,{11 if driver else 10}",
             f"-Wl,--entry,{'module_entry' if driver else 'rabbit_entry'}",
             "-Wl,--no-insert-timestamp", "-Wl,--image-base,0",
             "-Wl,--file-alignment,512", "-Wl,--section-alignment,4096", "-o", str(output)]
    completed = subprocess.run(args, capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError("UEFI compilation failed: " + completed.stderr)
    result = subprocess.run([inspection, "-p", str(output)], check=True, capture_output=True, text=True)
    if "DLL Name:" in result.stdout:
        raise RuntimeError("module/supervisor imports an OS DLL")
    return output.read_bytes()


def prepare_fixtures(directory):
    target = json.loads((ROOT / "target.json").read_text())
    if target["physical_installation_allowed"] is not False or target["key_mode"] != "public-test-fixture-key-never-install":
        raise RuntimeError("this builder may only create QEMU test-key artifacts")
    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32, 64)))
    public = private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    base = digest(b"Rabbit immutable supervisor fallback fixture v1")
    identity = digest(canonical(target))
    state0 = struct.pack("<IIII", 0, 0x9966ff, 0x52414242, 0)
    state_a = struct.pack("<IIII", 1, 0x22cc66, 0x52414242, 0)
    state_b = struct.pack("<IIII", 2, 0x3366ff, 0x52414242, 0)
    modules = {mode: compile_efi(directory, f"module-{mode}", [ROOT / "module.c"],
                               driver=True, definitions=(f"MODULE_MODE={mode}",)) for mode in range(1, 6)}
    def envelope(mode, current, snapshot, counter):
        return pack(modules[mode], private=private, target=identity,
                    base_runtime=current, state=snapshot, counter=counter)
    updates = {
        "a": envelope(1, base, state0, 1),
        "b": envelope(2, digest(modules[1]), state_a, 2),
        "unhealthy": envelope(3, digest(modules[2]), state_b, 3),
        "abi": envelope(4, digest(modules[2]), state_b, 4),
        "hang": envelope(5, digest(modules[2]), state_b, 5),
    }
    corrupted = bytearray(envelope(2, digest(modules[2]), state_b, 4))
    corrupted[-1] ^= 1
    updates["tampered"] = bytes(corrupted)
    header = "/* GENERATED QEMU-ONLY PUBLIC TEST FIXTURES; NO PRODUCTION SECRETS. */\n"
    for name, value in (("fixture_target", identity), ("fixture_owner", public), ("fixture_base", base)):
        header += c_bytes(name, value)
    for name, value in updates.items():
        header += c_bytes("frames_" + name, b"".join(encode(value)))
    (directory / "fixtures.h").write_text(header)
    return {"target": target, "identity": identity, "public": public,
            "base": base, "states": (state0, state_a, state_b), "modules": modules, "updates": updates}


def crypto(directory):
    builder = load("rabbit_native_crypto_builder", REPO / "experiments/x86-64-uefi-god-runtime-v1/build_image.py")
    builder.fetch_crypto(directory)
    return [directory / "monocypher.c", directory / "monocypher-ed25519.c"]


def build():
    ROOT.joinpath("runs").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="native-probe-", dir=os.environ.get("RABBIT_TMPDIR", str(ROOT / "runs"))) as temp:
        directory = Path(temp)
        fixture = prepare_fixtures(directory)
        efi = compile_efi(directory, "supervisor", [ROOT / "supervisor.c", ROOT / "verify_core.c", ROOT / "transport_core.c",
                         ROOT / "sha256.c", *crypto(directory)])
        media = load("rabbit_native_media", REPO / "experiments/x86-64-uefi-v0/build_image.py")
        image = media.build_image(efi)
        sources = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                   for name in ("abi.h", "module.c", "supervisor.c", "verify_core.c", "verify_core.h", "transport_core.c", "transport_core.h", "sha256.c", "sha256.h", "build_image.py", "target.json")}
        report_contracts = {name: digest((CONTRACT / name).read_bytes()).hex() for name in ("update.py", "transport.py")}
        report = {"schema_version": 1, "status": "QEMU-ONLY-NATIVE-RAM-UPDATE-PROBE-NOT-INSTALLED",
                  "physical_installation_allowed": False, "test_key_only": True,
                  "bluetooth_implemented": False, "persistent_writes": 0,
                  "efi_sha256": digest(efi).hex(), "image_sha256": digest(image).hex(),
                  "target_sha256": fixture["identity"].hex(), "source_hashes": sources,
                  "contract_hashes": report_contracts,
                  "module_hashes": {str(mode): digest(value).hex() for mode, value in fixture["modules"].items()},
                  "update_hashes": {name: digest(value).hex() for name, value in fixture["updates"].items()}}
        return image, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "runs/probe.img")
    args = parser.parse_args()
    image, report = build()
    args.output.write_bytes(image)
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    print("STOP: QEMU ONLY. No physical-media installer or Bluetooth sender exists for this probe.")


if __name__ == "__main__":
    main()
