.intel_syntax noprefix
.section .text
.global rabbit_entry

# Load two exact, hash-pinned QCA Rome 3.2 firmware payloads into controller RAM.
# The program has no controller reset, HCI, scan, advertising, pairing, connection,
# radio receive/transmit, internal-storage write, or firmware/flash write path.
rabbit_entry:
    push rbx
    push rbp
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15
    sub rsp, 0x498

    mov rbx, [rdx + 0x30]
    mov rbp, [rdx + 0x40]
    mov rdi, [rdx + 0x60]
    xor r13d, r13d
    lea rdx, [rip + title]
    call print_ascii

    # Locate at most 64 USB I/O handles and bind only 0CF3:E009 interface 00.
    mov qword ptr [rsp + 0x30], 0
    mov qword ptr [rsp + 0x38], 0
    mov ecx, 2
    lea rdx, [rip + usb_io_guid]
    xor r8d, r8d
    lea r9, [rsp + 0x30]
    lea rax, [rsp + 0x38]
    mov [rsp + 0x20], rax
    mov rax, [rdi + 0x138]
    call rax
    test rax, rax
    jnz target_not_found
    cmp qword ptr [rsp + 0x30], 64
    jbe count_bounded
    mov qword ptr [rsp + 0x30], 64
count_bounded:
    xor r12d, r12d
handle_loop:
    cmp r12, [rsp + 0x30]
    jae handles_done
    mov rax, [rsp + 0x38]
    mov rcx, [rax + r12 * 8]
    lea rdx, [rip + usb_io_guid]
    lea r8, [rsp + 0x40]
    mov rax, [rdi + 0x98]
    call rax
    test rax, rax
    jnz next_handle
    mov rsi, [rsp + 0x40]
    mov rcx, rsi
    lea rdx, [rsp + 0x50]
    mov rax, [rsi + 0x30]
    call rax
    test rax, rax
    jnz next_handle
    mov rcx, rsi
    lea rdx, [rsp + 0x68]
    mov rax, [rsi + 0x40]
    call rax
    test rax, rax
    jnz next_handle
    cmp word ptr [rsp + 0x58], 0x0cf3
    jne next_handle
    cmp word ptr [rsp + 0x5a], 0xe009
    jne next_handle
    cmp byte ptr [rsp + 0x6a], 0
    jne next_handle
    cmp byte ptr [rsp + 0x6d], 0xe0
    jne next_handle
    cmp byte ptr [rsp + 0x6e], 1
    jne next_handle
    cmp byte ptr [rsp + 0x6f], 1
    jne next_handle
    mov r13, rsi
    jmp handles_done
next_handle:
    inc r12d
    jmp handle_loop

handles_done:
    mov rcx, [rsp + 0x38]
    test rcx, rcx
    jz handles_freed
    mov rax, [rdi + 0x48]
    call rax
handles_freed:
    test r13, r13
    jz target_not_found
    lea rdx, [rip + target_found]
    call print_ascii

    # Read target version and require exact Rome 3.2 ROM before any device write.
    mov byte ptr [rsp + 0x80], 0xc0
    mov byte ptr [rsp + 0x81], 0x09
    mov word ptr [rsp + 0x82], 0
    mov word ptr [rsp + 0x84], 0
    mov word ptr [rsp + 0x86], 20
    mov dword ptr [rsp + 0x90], 0
    mov rcx, r13
    lea rdx, [rsp + 0x80]
    xor r8d, r8d
    mov r9d, 1000
    lea rax, [rsp + 0xa0]
    mov [rsp + 0x20], rax
    mov qword ptr [rsp + 0x28], 20
    lea rax, [rsp + 0x90]
    mov [rsp + 0x30], rax
    mov rax, [r13]
    call rax
    test rax, rax
    jnz version_failed
    cmp dword ptr [rsp + 0x90], 0
    jne version_failed
    cmp dword ptr [rsp + 0xa0], 0x00000302
    jne wrong_rom
    lea rdx, [rip + rom_ok]
    call print_ascii

    # Read initial setup status.
    call read_status
    test eax, eax
    jnz status_failed
    lea rsi, [rip + before_template]
    lea rdx, [rsp + 0x100]
    call copy_ascii
    movzx eax, byte ptr [rsp + 0xc0]
    lea rdx, [rsp + 0x100 + before_value - before_template]
    mov r10d, 2
    call write_hex
    lea rdx, [rsp + 0x100]
    call print_ascii

    test byte ptr [rsp + 0xc0], 0x80
    jnz patch_ready
    lea rdx, [rip + patch_start]
    call print_ascii
    mov rcx, r13
    lea rdx, [rip + rampatch_blob]
    mov r8d, 68644
    mov r9d, 28
    call download_blob
    test eax, eax
    jnz patch_failed
    lea rdx, [rip + patch_done]
    call print_ascii
patch_ready:

    # Match Linux: read target version again after rampatch.
    mov byte ptr [rsp + 0x80], 0xc0
    mov byte ptr [rsp + 0x81], 0x09
    mov word ptr [rsp + 0x82], 0
    mov word ptr [rsp + 0x84], 0
    mov word ptr [rsp + 0x86], 20
    mov dword ptr [rsp + 0x90], 0
    mov rcx, r13
    lea rdx, [rsp + 0x80]
    xor r8d, r8d
    mov r9d, 1000
    lea rax, [rsp + 0xa0]
    mov [rsp + 0x20], rax
    mov qword ptr [rsp + 0x28], 20
    lea rax, [rsp + 0x90]
    mov [rsp + 0x30], rax
    mov rax, [r13]
    call rax
    test rax, rax
    jnz version_failed
    cmp dword ptr [rsp + 0x90], 0
    jne version_failed
    cmp dword ptr [rsp + 0xa0], 0x00000302
    jne wrong_rom

    # Initial status is authoritative for whether NVM needs loading.
    test byte ptr [rsp + 0xc0], 0x40
    jnz nvm_ready
    lea rdx, [rip + nvm_start]
    call print_ascii
    mov rcx, r13
    lea rdx, [rip + nvm_blob]
    mov r8d, 1998
    mov r9d, 4
    call download_blob
    test eax, eax
    jnz nvm_failed
    lea rdx, [rip + nvm_done]
    call print_ascii
nvm_ready:

    # Prove the controller's post-load state without resetting or using HCI/radio.
    call read_status
    test eax, eax
    jnz status_failed
    lea rsi, [rip + after_template]
    lea rdx, [rsp + 0x100]
    call copy_ascii
    movzx eax, byte ptr [rsp + 0xc0]
    lea rdx, [rsp + 0x100 + after_value - after_template]
    mov r10d, 2
    call write_hex
    lea rdx, [rsp + 0x100]
    call print_ascii
    test byte ptr [rsp + 0xc0], 0x80
    jz post_missing
    test byte ptr [rsp + 0xc0], 0x40
    jz post_missing
    lea rdx, [rip + success]
    call print_ascii
    jmp finish

post_missing:
    lea rdx, [rip + post_not_ready]
    call print_ascii
    jmp finish
target_not_found:
    lea rdx, [rip + not_found]
    call print_ascii
    jmp finish
version_failed:
    lea rdx, [rip + version_error]
    call print_ascii
    jmp finish
status_failed:
    lea rdx, [rip + status_error]
    call print_ascii
    jmp finish
wrong_rom:
    lea rdx, [rip + wrong_rom_message]
    call print_ascii
    jmp finish
patch_failed:
    lea rdx, [rip + patch_error]
    call print_ascii
    jmp finish
nvm_failed:
    lea rdx, [rip + nvm_error]
    call print_ascii

finish:
    lea rdx, [rip + safety]
    call print_ascii
    lea rdx, [rip + footer]
    call print_ascii
wait_key:
    mov rcx, rbx
    lea rdx, [rsp + 0xd0]
    mov rax, [rcx + 8]
    call rax
    test rax, rax
    jnz wait_key
    xor eax, eax
    add rsp, 0x498
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbp
    pop rbx
    ret

# Read QCA_CHECK_STATUS into caller [rsp+0xc0]. Return eax=0 on success.
read_status:
    sub rsp, 0x38
    mov byte ptr [rsp + 0x80 + 0x40], 0xc0
    mov byte ptr [rsp + 0x81 + 0x40], 0x05
    mov word ptr [rsp + 0x82 + 0x40], 0
    mov word ptr [rsp + 0x84 + 0x40], 0
    mov word ptr [rsp + 0x86 + 0x40], 1
    mov dword ptr [rsp + 0x90 + 0x40], 0
    mov rcx, r13
    lea rdx, [rsp + 0x80 + 0x40]
    xor r8d, r8d
    mov r9d, 1000
    lea rax, [rsp + 0xc0 + 0x40]
    mov [rsp + 0x20], rax
    mov qword ptr [rsp + 0x28], 1
    lea rax, [rsp + 0x90 + 0x40]
    mov [rsp + 0x30], rax
    mov rax, [r13]
    call rax
    test rax, rax
    jnz read_status_bad
    cmp dword ptr [rsp + 0x90 + 0x40], 0
    jne read_status_bad
    xor eax, eax
    add rsp, 0x38
    ret
read_status_bad:
    mov eax, 1
    add rsp, 0x38
    ret

# rcx=USB I/O, rdx=blob, r8=size, r9=header size. Return eax=0 on success.
download_blob:
    push r12
    push r13
    push r14
    push r15
    sub rsp, 0x68
    mov r12, rcx
    mov r14, rdx
    mov r15, r8
    mov r13, r9

    mov byte ptr [rsp + 0x40], 0x40
    mov byte ptr [rsp + 0x41], 0x01
    mov word ptr [rsp + 0x42], 0
    mov word ptr [rsp + 0x44], 0
    mov word ptr [rsp + 0x46], r13w
    mov dword ptr [rsp + 0x50], 0
    mov rcx, r12
    lea rdx, [rsp + 0x40]
    mov r8d, 1
    mov r9d, 3000
    mov [rsp + 0x20], r14
    mov [rsp + 0x28], r13
    lea rax, [rsp + 0x50]
    mov [rsp + 0x30], rax
    mov rax, [r12]
    call rax
    test rax, rax
    jnz download_bad
    cmp dword ptr [rsp + 0x50], 0
    jne download_bad
    add r14, r13
    sub r15, r13

    mov ecx, 20000
    mov rax, [rdi + 0xf8]
    call rax
    test rax, rax
    jnz download_bad

bulk_loop:
    test r15, r15
    jz download_good
    mov r13, r15
    cmp r13, 4096
    jbe chunk_ready
    mov r13d, 4096
chunk_ready:
    mov [rsp + 0x58], r13
    mov dword ptr [rsp + 0x50], 0
    mov rcx, r12
    mov edx, 2
    mov r8, r14
    lea r9, [rsp + 0x58]
    mov qword ptr [rsp + 0x20], 3000
    lea rax, [rsp + 0x50]
    mov [rsp + 0x28], rax
    mov rax, [r12 + 8]
    call rax
    test rax, rax
    jnz download_bad
    cmp dword ptr [rsp + 0x50], 0
    jne download_bad
    cmp [rsp + 0x58], r13
    jne download_bad
    add r14, r13
    sub r15, r13
    jmp bulk_loop
download_good:
    xor eax, eax
    jmp download_return
download_bad:
    mov eax, 1
download_return:
    add rsp, 0x68
    pop r15
    pop r14
    pop r13
    pop r12
    ret

copy_ascii:
    mov al, [rsi]
    mov [rdx], al
    inc rsi
    inc rdx
    test al, al
    jnz copy_ascii
    ret

print_ascii:
    lea r8, [rsp + 0x200]
    mov r9, r8
convert_ascii:
    movzx eax, byte ptr [rdx]
    inc rdx
    mov word ptr [r9], ax
    add r9, 2
    test al, al
    jnz convert_ascii
    mov rcx, rbp
    mov rdx, r8
    mov rax, [rcx + 8]
    sub rsp, 0x28
    call rax
    add rsp, 0x28
    ret

write_hex:
    mov r8d, eax
    lea r9d, [r10d * 4 - 4]
    lea r11, [rip + hex_digits]
hex_loop:
    mov eax, r8d
    mov ecx, r9d
    shr eax, cl
    and eax, 0x0f
    mov al, [r11 + rax]
    mov [rdx], al
    inc rdx
    sub r9d, 4
    jns hex_loop
    ret

title: .asciz "\r\nRABBIT QCA RAM LOAD v0.1\r\n=========================\r\nTRANSIENT CONTROLLER RAM ONLY; RADIO OFF\r\n\r\nSTAGE 1: FIND 0CF3:E009 INTERFACE 00\r\n"
target_found: .asciz "TARGET FOUND\r\nSTAGE 2: REQUIRE ROM=00000302\r\n"
rom_ok: .asciz "ROM MATCH: OK\r\n"
before_template: .ascii "STATUS BEFORE="
before_value: .asciz "00\r\n"
patch_start: .asciz "STAGE 3: LOAD HASH-PINNED RAMPATCH TO RAM\r\n"
patch_done: .asciz "RAMPATCH TRANSFER: OK\r\n"
nvm_start: .asciz "STAGE 4: LOAD HASH-PINNED NVM TO RAM\r\n"
nvm_done: .asciz "NVM TRANSFER: OK\r\n"
after_template: .ascii "STATUS AFTER="
after_value: .asciz "00\r\n"
success: .asciz "PATCH_UPDATED=YES; SYSCFG_UPDATED=YES\r\n"
post_not_ready: .asciz "POST-LOAD STATUS NOT READY; STOPPED\r\n"
not_found: .asciz "TARGET NOT FOUND; NO DEVICE WRITE SENT\r\n"
version_error: .asciz "TARGET VERSION READ FAILED; STOPPED\r\n"
status_error: .asciz "SETUP STATUS READ FAILED; STOPPED\r\n"
wrong_rom_message: .asciz "ROM MISMATCH; NO DEVICE WRITE SENT\r\n"
patch_error: .asciz "RAMPATCH TRANSFER FAILED; STOPPED\r\n"
nvm_error: .asciz "NVM TRANSFER FAILED; STOPPED\r\n"
safety: .asciz "NO RESET; NO HCI; NO SCAN; NO RADIO; POWER-OFF ROLLBACK\r\n"
footer: .asciz "\r\nPHOTOGRAPH. PRESS ANY KEY.\r\n"
hex_digits: .ascii "0123456789ABCDEF"

.balign 8
usb_io_guid:
    .byte 0xd6,0x68,0x2f,0x2b,0xd2,0x0c,0xcf,0x44
    .byte 0x8e,0x8b,0xbb,0xa2,0x0b,0x1b,0x5b,0x75

.balign 16
rampatch_marker: .ascii "RABBIT_RAMPATCH!"
rampatch_blob:
    .zero 68644
nvm_marker: .ascii "RABBIT_NVM_BLOB!"
nvm_blob:
    .zero 1998
