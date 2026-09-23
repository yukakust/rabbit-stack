.intel_syntax noprefix
.section .text
.global rabbit_entry

# Read only the QCA Rome vendor target-version and setup-status values.
# No vendor OUT, HCI command, reset, firmware download, or radio operation exists.
rabbit_entry:
    push rbx
    push rbp
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15
    sub rsp, 0x398

    mov rbx, [rdx + 0x30]
    mov rbp, [rdx + 0x40]
    mov rdi, [rdx + 0x60]
    xor r13d, r13d

    lea rdx, [rip + title]
    call print_ascii

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
    cmp byte ptr [rsp + 0x6a], 0x00
    jne next_handle
    cmp byte ptr [rsp + 0x6d], 0xe0
    jne next_handle
    cmp byte ptr [rsp + 0x6e], 0x01
    jne next_handle
    cmp byte ptr [rsp + 0x6f], 0x01
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

    # USB vendor device-to-host GET_TARGET_VERSION (request 0x09), 20 bytes.
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
    mov rax, [r13 + 0x00]
    call rax
    test rax, rax
    jnz version_failed
    cmp dword ptr [rsp + 0x90], 0
    jne version_failed

    lea rsi, [rip + version_template]
    lea rdx, [rsp + 0x100]
    call copy_ascii
    mov eax, dword ptr [rsp + 0xa0]
    lea rdx, [rsp + 0x100 + rom_value - version_template]
    mov r10d, 8
    call write_hex
    mov eax, dword ptr [rsp + 0xa4]
    lea rdx, [rsp + 0x100 + patch_value - version_template]
    mov r10d, 8
    call write_hex
    mov eax, dword ptr [rsp + 0xa8]
    lea rdx, [rsp + 0x100 + ram_value - version_template]
    mov r10d, 8
    call write_hex
    movzx eax, byte ptr [rsp + 0xac]
    lea rdx, [rsp + 0x100 + chip_value - version_template]
    mov r10d, 2
    call write_hex
    movzx eax, byte ptr [rsp + 0xad]
    lea rdx, [rsp + 0x100 + platform_value - version_template]
    mov r10d, 2
    call write_hex
    movzx eax, word ptr [rsp + 0xae]
    lea rdx, [rsp + 0x100 + flag_value - version_template]
    mov r10d, 4
    call write_hex
    lea rdx, [rsp + 0x100]
    call print_ascii

    # USB vendor device-to-host CHECK_STATUS (request 0x05), one byte.
    mov byte ptr [rsp + 0x80], 0xc0
    mov byte ptr [rsp + 0x81], 0x05
    mov word ptr [rsp + 0x82], 0
    mov word ptr [rsp + 0x84], 0
    mov word ptr [rsp + 0x86], 1
    mov dword ptr [rsp + 0x90], 0
    mov rcx, r13
    lea rdx, [rsp + 0x80]
    xor r8d, r8d
    mov r9d, 1000
    lea rax, [rsp + 0xc0]
    mov [rsp + 0x20], rax
    mov qword ptr [rsp + 0x28], 1
    lea rax, [rsp + 0x90]
    mov [rsp + 0x30], rax
    mov rax, [r13 + 0x00]
    call rax
    test rax, rax
    jnz status_failed
    cmp dword ptr [rsp + 0x90], 0
    jne status_failed

    lea rsi, [rip + status_template]
    lea rdx, [rsp + 0x100]
    call copy_ascii
    movzx eax, byte ptr [rsp + 0xc0]
    lea rdx, [rsp + 0x100 + status_value - status_template]
    mov r10d, 2
    call write_hex
    lea rdx, [rsp + 0x100]
    call print_ascii
    test byte ptr [rsp + 0xc0], 0x80
    jz patch_missing
    lea rdx, [rip + patch_yes]
    jmp print_patch
patch_missing:
    lea rdx, [rip + patch_no]
print_patch:
    call print_ascii
    test byte ptr [rsp + 0xc0], 0x40
    jz syscfg_missing
    lea rdx, [rip + syscfg_yes]
    jmp print_syscfg
syscfg_missing:
    lea rdx, [rip + syscfg_no]
print_syscfg:
    call print_ascii
    lea rdx, [rip + safety]
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

finish:
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
    add rsp, 0x398
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbp
    pop rbx
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

title: .asciz "\r\nRABBIT QCA ROME STATUS v0.1\r\n============================\r\nREAD ONLY; NO DOWNLOAD OR RADIO\r\n\r\nSTAGE 1: FIND 0CF3:E009 INTERFACE 00\r\n"
target_found: .asciz "TARGET FOUND\r\nSTAGE 2: VENDOR-IN TARGET VERSION (0x09)\r\n"
version_template: .ascii "ROM="
rom_value: .ascii "00000000 PATCH="
patch_value: .ascii "00000000 RAM="
ram_value: .ascii "00000000\r\nCHIP="
chip_value: .ascii "00 PLATFORM="
platform_value: .ascii "00 FLAG="
flag_value: .asciz "0000\r\nSTAGE 3: VENDOR-IN SETUP STATUS (0x05)\r\n"
status_template: .ascii "STATUS="
status_value: .asciz "00\r\n"
patch_yes: .asciz "PATCH_UPDATED=YES\r\n"
patch_no: .asciz "PATCH_UPDATED=NO\r\n"
syscfg_yes: .asciz "SYSCFG_UPDATED=YES\r\n"
syscfg_no: .asciz "SYSCFG_UPDATED=NO\r\n"
safety: .asciz "NO DOWNLOAD; NO RESET; NO HCI; NO RADIO\r\n"
not_found: .asciz "TARGET NOT FOUND; NO VENDOR REQUEST SENT\r\n"
version_error: .asciz "TARGET VERSION READ FAILED\r\n"
status_error: .asciz "SETUP STATUS READ FAILED\r\n"
footer: .asciz "\r\nPHOTOGRAPH. PRESS ANY KEY.\r\n"
hex_digits: .ascii "0123456789ABCDEF"

.balign 8
usb_io_guid:
    .byte 0xd6,0x68,0x2f,0x2b,0xd2,0x0c,0xcf,0x44
    .byte 0x8e,0x8b,0xbb,0xa2,0x0b,0x1b,0x5b,0x75
