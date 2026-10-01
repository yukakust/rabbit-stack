#!/usr/bin/env python3
"""Owner-local key provisioning / explicit reviewed signing; no send or execution."""
import argparse
import os
from pathlib import Path
import stat

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, PublicFormat
from update import MAX_BYTES, HEADER, SIGNATURE_BYTES, UpdateError, digest, pack

REPO = Path(__file__).resolve().parents[2]


def outside_repo(path):
    path = Path(path).absolute()
    if path.resolve().is_relative_to(REPO):
        raise UpdateError("private runtime key must be stored outside this repository")
    return path


def create(private_path, public_path):
    private_path = outside_repo(private_path)
    public_path = Path(public_path).absolute()
    if private_path.resolve() == public_path.resolve():
        raise UpdateError("private and public outputs must differ")
    if public_path.exists() or public_path.is_symlink():
        raise UpdateError("public-key output already exists; refusing overwrite")
    key = Ed25519PrivateKey.generate()
    private = key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    public = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    # Explicit create-only owner-local secret; never print its contents.
    fd = os.open(private_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(private)
        output.flush()
        os.fsync(output.fileno())
    # If this fails, preserve the secret; do not silently delete/regenerate identity.
    fd = os.open(public_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as output:
        output.write(public)
    return digest(public).hex()


def load_private(path):
    path = outside_repo(path)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid():
            raise UpdateError("private key must be an owner-only regular file")
        data = source.read(33)
    if len(data) != 32:
        raise UpdateError("private key must contain exactly 32 raw bytes")
    return Ed25519PrivateKey.from_private_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate")
    generate.add_argument("--private", type=Path, required=True)
    generate.add_argument("--public", type=Path, required=True)
    sign = commands.add_parser("sign")
    for name in ("private", "payload", "state", "output"):
        sign.add_argument("--" + name, type=Path, required=True)
    for name in ("target-sha256", "base-runtime-sha256", "reviewed-payload-sha256"):
        sign.add_argument("--" + name, required=True)
    sign.add_argument("--counter", type=int, required=True)
    args = parser.parse_args()
    if args.command == "generate":
        fingerprint = create(args.private, args.public)
        print("OWNER KEY CREATED; public-key SHA256=" + fingerprint)
        print("Private bytes remain owner-local. No image changed or packet sent.")
        return
    with args.payload.open("rb") as source:
        payload = source.read(MAX_BYTES - HEADER.size - SIGNATURE_BYTES + 1)
    if len(payload) > MAX_BYTES - HEADER.size - SIGNATURE_BYTES:
        raise UpdateError("native payload exceeds the signed RAM budget")
    if digest(payload).hex() != args.reviewed_payload_sha256.lower():
        raise UpdateError("payload differs from the explicitly reviewed SHA-256")
    data = pack(payload, private=load_private(args.private),
                target=bytes.fromhex(args.target_sha256),
                base_runtime=bytes.fromhex(args.base_runtime_sha256),
                state=args.state.read_bytes(), counter=args.counter)
    # Create-only output, never silently replace another signed release.
    with args.output.open("xb") as output:
        output.write(data)
    print("SIGNED-NOT-SENT; update SHA256=" + digest(data).hex())
    print("A signature is not a safety review. Bootstrap/BLE integration remains pending.")


if __name__ == "__main__":
    main()
