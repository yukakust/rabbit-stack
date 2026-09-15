# Day 01 — 32 bytes speak to a machine

## Goal

Run eight RV32I instruction words directly in QEMU. The guest contains no operating
system, firmware, C runtime, assembler output, or linker output.

QEMU and the host macOS are still present. QEMU models the CPU, RAM, UART, and a small
test device for us.

## Prerequisite on macOS

```sh
brew install qemu
qemu-system-riscv32 --version
```

## Inspect the source bytes

```sh
cat hello.hex
```

Each line is one 32-bit instruction stored as four bytes in little-endian order.

Build the raw image:

```sh
xxd -r -p hello.hex hello.bin
wc -c hello.bin
xxd -g 1 hello.bin
```

Prediction before running: `wc -c` should report `32` because there are eight
instructions and every base RV32I instruction here occupies four bytes.

## Run

```sh
qemu-system-riscv32 \
  -machine virt \
  -nographic \
  -bios none \
  -device loader,file=hello.bin,addr=0x80000000,cpu-num=0

echo $?
```

Expected result:

```text
the guest writes: A
echo prints:      0
```

The program itself writes only `A` and no newline. The shell prompt may therefore
appear immediately after the letter.

## Deterministic verification

Python is only the external measuring instrument; it is not part of the guest image.

```sh
python3 verify.py
```

Expected result:

```text
PASS: image is exactly 32 bytes
PASS: QEMU wrote exactly b'A' and exited with status 0
```

## What the bytes currently mean

| Address | Bytes | RV32I operation | Effect |
|---:|---|---|---|
| `0x80000000` | `b7 02 00 10` | `lui t0, 0x10000` | `t0 = 0x10000000` (UART) |
| `0x80000004` | `13 03 10 04` | `addi t1, zero, 65` | `t1 = 'A'` |
| `0x80000008` | `23 80 62 00` | `sb t1, 0(t0)` | send one byte to UART |
| `0x8000000c` | `b7 02 10 00` | `lui t0, 0x100` | `t0 = 0x00100000` |
| `0x80000010` | `37 53 00 00` | `lui t1, 0x5` | upper part of `0x5555` |
| `0x80000014` | `13 03 53 55` | `addi t1, t1, 0x555` | `t1 = 0x5555` |
| `0x80000018` | `23 a0 62 00` | `sw t1, 0(t0)` | ask QEMU to exit successfully |
| `0x8000001c` | `6f 00 00 00` | `jal zero, 0` | safety loop if exit is ignored |

Do not try to memorise these encodings. The next lesson derives one of them from the
RV32I bit fields and then changes `A` to `B` deliberately.
