# x86-64 UEFI jump-and-stone v0

This experiment is the first world requested in ordinary language after the physical
interactive substrate worked. Its reviewed v0 meaning is explicit:

- a yellow `64 x 64` player starts at `(100,100)`;
- arrows move it by 16 pixels;
- Space draws it 32 pixels upward for 120 ms and returns it to the same logical position;
- `Z` leaves one yellow `16 x 16` stone behind the last movement direction and moves
  the player one step forward;
- a later `Z` relocates that single persistent stone;
- ordinary movement cannot overlap the stone, but can route around it;
- Escape returns success.

The world is semantic JSON. Its Target Pack separately binds graphics, keyboard, and
delay to UEFI GOP framebuffer access, Simple Text Input, and Boot Services `Stall()`.
The artifact consumes 1,064 reviewed x86-64 code/data bytes stored visibly in
`program.hex`; `program.S` is the auditable symbolic source used to review those bytes.

Build and test without touching physical media:

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-jump-stone-v0
python3 verify.py
python3 run_qemu.py
```

On 2026-09-22 the owner verified arrows, Space, `Z`, blocked movement through the stone,
movement around it, a second `Z`, and Escape under QEMU 11.1.1. Exact-bound evidence is
in `evidence/qemu-macos-arm64-observed.json`. Physical Dell execution was deliberately
skipped at this checkpoint, so it remains explicitly unobserved rather than inferred.

Reviewed identities:

```text
world SHA-256:   94a67cd0e7b83e56a12f07bf32ffc783af694220fcb2a746943e074435998cc0
target SHA-256:  d84e054883f0165aed09c4177f26fabdf076eca1ca2024cb94a08a50313e0822
program SHA-256: 4c22fa9be1fd0a6495b909ac35765914cea95bc4d91dafd4f17144ecedf53331
EFI SHA-256:     1b5b816e533360f71917307e92cb3a8ef8afe4efbfe6cfd2fc3e199f40eea639
image SHA-256:   a319494061ec42f7a756e073c623de0f0d3983fa4fa9a260059c1bfd1de5a7aa
```
