#!/usr/bin/env python3
"""Host framing checks only. Run native compiler exclusively on Yukabox."""
import argparse
import hashlib
import json
import pathlib
import subprocess
import tarfile

ARCHIVE_SHA = "912ea06f74e30a8e36fbb68064d6cdff218d8d591db0fc5d75dee6c81ac7fc0a"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--clang", required=True)
    p.add_argument("--reference", type=pathlib.Path, required=True)
    p.add_argument("--output", type=pathlib.Path, required=True)
    a = p.parse_args()
    root = pathlib.Path(__file__).resolve().parent
    a.reference = a.reference.resolve()
    a.output.mkdir(parents=True, exist_ok=True)
    archive = a.reference / "wpa_supplicant-2.11.tar.gz"
    assert sha(archive) == ARCHIVE_SHA, "upstream archive changed"
    # Every extracted reference byte must equal the pinned official archive.
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            if member.isfile():
                assert not pathlib.PurePosixPath(member.name).is_absolute()
                assert ".." not in pathlib.PurePosixPath(member.name).parts
                data = tar.extractfile(member).read()
                assert (a.reference / member.name).read_bytes() == data
    src = a.reference / "wpa_supplicant-2.11/src"
    test = a.output / "framing-test"
    obj = a.output / "eapol_frame.obj"
    commands = [
        [a.clang, "-std=c11", "-Wall", "-Wextra", "-Werror", "-g",
         "-fsanitize=address,undefined", "-isystem", str(src),
         "-isystem", str(src / "utils"), str(root / "eapol_frame.c"),
         str(root / "eapol_frame_test.c"), "-o", str(test)],
        [str(test)],
        [a.clang, "--target=x86_64-pc-win32-coff", "-std=c11", "-Wall",
         "-Wextra", "-Werror", "-ffreestanding", "-fno-stack-protector",
         "-c", str(root / "eapol_frame.c"), "-o", str(obj)],
    ]
    lines = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True, check=True)
        lines.extend([json.dumps(command), result.stdout, result.stderr])
    assert "PASS 201477 framing checks" in lines[4]
    (a.output / "host.log").write_text("\n".join(lines))
    report = {
        "status": "HOST-FRAMING-ONLY-ASAN-UBSAN-COFF-PASS",
        "checks": 201477,
        "compiler": subprocess.check_output([a.clang, "--version"], text=True),
        "archive_sha256": ARCHIVE_SHA,
        "sources": {name: sha(root / name) for name in
                    ("eapol_frame.c", "eapol_frame.h", "eapol_frame_test.c", "verify.py")},
        "oracle_header_sha256": sha(src / "common/wpa_common.h"),
        "log_sha256": sha(a.output / "host.log"),
        "device_actions": 0, "secret_reads": 0,
        "mic_verified": False, "wpa_handshake_implemented": False,
        "dell_installed": False, "wifi_connected": False,
    }
    (a.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"], report["checks"])

if __name__ == "__main__":
    main()
