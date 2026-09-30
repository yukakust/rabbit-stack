#!/usr/bin/env python3
"""Build one UEFI image containing Rabbit God Runtime v1."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import struct
import subprocess
import tempfile
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
BASE = REPO / "experiments" / "x86-64-uefi-ble-program-loader-v0"
MEDIA_PATH = REPO / "experiments" / "x86-64-uefi-v0" / "build_image.py"
RAMPATCH_MARKER, NVM_MARKER = b"RABBIT_RAMPATCH!", b"RABBIT_NVM_BLOB!"


class BuildError(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BuildError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def transformed_source() -> str:
    source = (BASE / "program.S").read_text(encoding="utf-8")
    if source.count("cmp r12d, 8") != 2:
        raise BuildError("reviewed HCI command event budgets changed upstream")
    source = source.replace("cmp r12d, 8", "cmp r12d, 32")
    source = source.replace(
        "sub rsp, 0x708\n\n    mov rbx, [rdx + 0x30]",
        "sub rsp, 0x708\n    mov [rsp + 0x6f0], rdx       # SystemTable for Scene/Anima core\n\n    mov rbx, [rdx + 0x30]",
        1,
    )
    graphics_start = source.index("    # Bind the current GOP framebuffer")
    graphics_end = source.index("    # Emit one reviewed HCI packet", graphics_start)
    source = source[:graphics_start] + """    # Bind GOP and start the embedded reviewed Cat world.  The C core owns
    # only its bounded presentation surface and returns failure before radio setup.
    mov rcx, [rsp + 0x6f0]
    call rabbit_scene_bootstrap
    test eax, eax
    jnz scan_graphics_failed
    lea rdx, [rip + scan_graphics_bound]
    call scan_print_ascii
    lea rdx, [rip + scan_graphics_ok]
    call scan_print_ascii

""" + source[graphics_end:]
    loop_start = source.index("scan_scan_event_loop:")
    receive_start = source.index("scan_receive_event:", loop_start)
    source = source[:loop_start] + """scan_scan_event_loop:
    # One deterministic Scene/Anima tick between bounded receive attempts.
    mov rcx, [rsp + 0x6f0]
    call rabbit_scene_tick
    test eax, eax
    jnz scan_health_failed
    mov rcx, rbx
    lea rdx, [rsp + 0xc0]
    mov rax, [rcx + 8]
    call rax
    test rax, rax
    jnz scan_receive_event
    cmp word ptr [rsp + 0xc0], 0x17
    jne scan_receive_event
    mov dword ptr [rsp + 0x424], 1
    jmp scan_stop_scan

""" + source[receive_start:]
    source = source.replace("mov qword ptr [rsp + 0x20], 200\n", "mov qword ptr [rsp + 0x20], 33\n", 1)
    parser_start = source.index("scan_frame_begin:")
    ack_start = source.index("    # Build the canonical 16-byte acknowledgement:", parser_start)
    parser = r'''scan_frame_begin:
    cmp word ptr [rsp + 0x435], 192
    jne scan_scan_event_loop
    cmp byte ptr [rsp + 0x43b], 28
    jne scan_scan_event_loop
    movzx eax, byte ptr [rsp + 0x433]
    mov byte ptr [rsp + 0x440], 1
    mov byte ptr [rsp + 0x441], al
    mov byte ptr [rsp + 0x442], 0
    mov dword ptr [rsp + 0x444], 192
    mov dword ptr [rsp + 0x448], 0
    mov eax, dword ptr [rsp + 0x437]
    bswap eax
    mov dword ptr [rsp + 0x44c], eax
    jmp scan_scan_event_loop

scan_frame_chunk:
    cmp byte ptr [rsp + 0x440], 1
    jne scan_scan_event_loop
    mov al, byte ptr [rsp + 0x433]
    cmp al, byte ptr [rsp + 0x441]
    jne scan_scan_event_loop
    mov al, byte ptr [rsp + 0x434]
    cmp al, byte ptr [rsp + 0x442]
    jne scan_scan_event_loop
    mov r9d, dword ptr [rsp + 0x448]
    mov r10d, 192
    sub r10d, r9d
    jbe scan_scan_event_loop
    cmp r10d, 7
    jbe god_chunk_count_ready
    mov r10d, 7
god_chunk_count_ready:
    xor r8d, r8d
god_chunk_copy_loop:
    mov al, byte ptr [rsp + 0x435 + r8]
    mov byte ptr [rsp + 0x540 + r9], al
    inc r8d
    inc r9d
    cmp r8d, r10d
    jb god_chunk_copy_loop
    mov dword ptr [rsp + 0x448], r9d
    inc byte ptr [rsp + 0x442]
    jmp scan_scan_event_loop

scan_frame_commit:
    cmp byte ptr [rsp + 0x440], 1
    jne scan_scan_event_loop
    mov al, byte ptr [rsp + 0x433]
    cmp al, byte ptr [rsp + 0x441]
    jne scan_scan_event_loop
    mov al, byte ptr [rsp + 0x434]
    cmp al, byte ptr [rsp + 0x442]
    jne scan_scan_event_loop
    cmp word ptr [rsp + 0x439], 192
    jne scan_scan_event_loop
    cmp byte ptr [rsp + 0x43b], 0
    jne scan_scan_event_loop
    cmp dword ptr [rsp + 0x448], 192
    jne scan_scan_event_loop
    mov edx, dword ptr [rsp + 0x435]
    bswap edx
    cmp edx, dword ptr [rsp + 0x44c]
    jne scan_scan_event_loop
    mov eax, 0x811c9dc5
    xor ecx, ecx
god_capsule_hash_loop:
    movzx edx, byte ptr [rsp + 0x540 + rcx]
    xor eax, edx
    imul eax, eax, 0x01000193
    inc ecx
    cmp ecx, 192
    jb god_capsule_hash_loop
    cmp eax, dword ptr [rsp + 0x44c]
    jne scan_scan_event_loop
    cmp eax, dword ptr [rsp + 0x450]
    je scan_scan_event_loop
    lea rcx, [rsp + 0x540]
    mov edx, 192
    mov r8, [rsp + 0x6f0]
    call rabbit_capsule_verify_activate
    cmp eax, 2
    je scan_capsule_rolled_back
    test eax, eax
    jnz scan_capsule_rejected
    mov eax, dword ptr [rsp + 0x44c]
    mov dword ptr [rsp + 0x450], eax
    inc r15d
    lea rdx, [rip + scan_program_applied]
    call scan_print_ascii
    jmp scan_capsule_accepted
scan_capsule_rolled_back:
    mov dword ptr [rsp + 0x440], 0
    lea rdx, [rip + scan_rollback]
    call scan_print_ascii
    jmp scan_scan_event_loop
scan_capsule_rejected:
    mov dword ptr [rsp + 0x440], 0
    lea rdx, [rip + scan_capsule_bad]
    call scan_print_ascii
    jmp scan_scan_event_loop
scan_capsule_accepted:
'''
    source = source[:parser_start] + parser + source[ack_start:]
    source = source.replace("scan_graphics_failed:\n", "scan_health_failed:\n    lea rdx, [rip + scan_health_error]\n    call scan_print_ascii\n    jmp scan_finish\n\nscan_graphics_failed:\n", 1)
    source = source.replace("RABBIT WIRELESS PROGRAM LOADER v0.5", "RABBIT GOD RUNTIME v1.2")
    source = source.replace("RABBIT VM v1; PASSIVE RX + BOUNDED ACK; ESC TO STOP", "SCENE/ANIMA v2 + SIGNED CAPSULE + ROLLBACK")
    source = source.replace("INITIAL SQUARE DRAWN=YELLOW; VM READY", "BOOTSTRAP CAT WORLD ACTIVE; RUNTIME READY")
    source = source.replace("PROGRAM APPLIED: SHAPE + POSITION + ARROW CONTROLS", "CAPSULE HEALTHY: PROVISIONAL WORLD COMMITTED")
    insertion = 'scan_ack_sent: .asciz "ACK ADVERTISED FOR 1500 MS; PASSIVE RECEIVE RESUMED\\r\\n"\n'
    source = source.replace(insertion, insertion + 'scan_rollback: .asciz "HEALTH FAILED: PREVIOUS WORLD RESTORED\\r\\n"\nscan_capsule_bad: .asciz "CAPSULE REJECTED: ACTIVE WORLD UNCHANGED\\r\\n"\nscan_health_error: .asciz "ACTIVE WORLD HEALTH FAILED; RUNTIME STOPPED\\r\\n"\n')
    return source


def fetch_crypto(directory: Path) -> list[Path]:
    provenance = json.loads((ROOT / "crypto-provenance.json").read_text(encoding="utf-8"))
    commit = provenance["git_commit"]
    paths = []
    for upstream, expected in provenance["files"].items():
        url = f"https://raw.githubusercontent.com/LoupVaillant/Monocypher/{commit}/{upstream}"
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
        if sha256(data) != expected:
            raise BuildError(f"Monocypher hash mismatch: {upstream}")
        path = directory / Path(upstream).name
        path.write_bytes(data)
        paths.append(path)
    return paths


def compile_efi(source: str, directory: Path) -> bytes:
    compiler = shutil.which("x86_64-w64-mingw32-gcc")
    objdump = shutil.which("x86_64-w64-mingw32-objdump")
    if compiler is None or objdump is None:
        raise BuildError("x86-64 MinGW compiler and objdump are required")
    crypto = fetch_crypto(directory)
    assembly = directory / "god_runtime.S"
    assembly.write_text(source, encoding="utf-8")
    output = directory / "BOOTX64.EFI"
    command = [
        compiler, "-std=c11", "-Os", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
        "-fno-builtin", "-fno-stack-protector", "-mno-red-zone", "-nostdlib",
        "-I", str(directory), str(assembly), str(ROOT / "runtime_core.c"),
        str(directory / "monocypher.c"), str(directory / "monocypher-ed25519.c"),
        "-Wl,--subsystem,10", "-Wl,--entry,rabbit_entry", "-Wl,--no-insert-timestamp",
        "-Wl,--image-base,0", "-Wl,--file-alignment,512", "-Wl,--section-alignment,4096",
        "-o", str(output),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode:
        raise BuildError("UEFI link failed: " + completed.stderr.strip())
    inspection = subprocess.run([objdump, "-p", str(output)], check=True, capture_output=True, text=True).stdout
    if "DLL Name:" in inspection:
        raise BuildError("UEFI image imports an OS DLL")
    return output.read_bytes()


def inject_firmware(efi: bytes) -> bytes:
    import sys
    sys.path.insert(0, str(BASE))
    from fetch_firmware import fetch_all  # type: ignore

    result = bytearray(efi)
    payloads = fetch_all()
    for marker, name, size in ((RAMPATCH_MARKER, "rampatch_usb_00000302.bin", 68644), (NVM_MARKER, "nvm_usb_00000302.bin", 1998)):
        if result.count(marker) != 1:
            raise BuildError(f"firmware marker count changed: {marker!r}")
        offset = result.index(marker) + len(marker)
        if result[offset:offset + size] != bytes(size):
            raise BuildError(f"firmware placeholder changed: {name}")
        result[offset:offset + size] = payloads[name]
    pe = struct.unpack_from("<I", result, 0x3C)[0]
    struct.pack_into("<I", result, pe + 4 + 20 + 64, 0)
    return bytes(result)


def build() -> tuple[bytes, dict[str, object]]:
    media = load_module("rabbit_god_media", MEDIA_PATH)
    source = transformed_source()
    with tempfile.TemporaryDirectory(prefix="rabbit-god-runtime-") as temporary:
        efi = inject_firmware(compile_efi(source, Path(temporary)))
    image = media.build_image(efi)
    report = {
        "schema_version": 1,
        "status": "BUILT-NOT-INSTALLED",
        "source_sha256": sha256(source.encode()),
        "runtime_core_sha256": sha256((ROOT / "runtime_core.c").read_bytes()),
        "target_sha256": sha256((ROOT / "target.json").read_bytes()),
        "efi_sha256": sha256(efi),
        "image_sha256": sha256(image),
        "image_size_bytes": len(image),
        "capsule_bytes": 192,
        "creator_authentication": "Ed25519 verified inside UEFI",
        "transaction": "staging -> signature/bounds -> provisional -> one health tick -> commit-or-rollback",
        "persistent_writes": 0,
        "physical_execution_verified": False,
    }
    return image, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        image, report = build()
        args.output.write_bytes(image)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (BuildError, OSError, subprocess.SubprocessError, KeyError, ValueError) as error:
        print(f"FAIL: {error}")
        return 1
    print(f"BUILT: {args.output} ({len(image)} bytes)")
    print(f"EFI SHA256: {report['efi_sha256']}")
    print(f"IMAGE SHA256: {report['image_sha256']}")
    print("STATUS: BUILT-NOT-INSTALLED; writes_performed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
