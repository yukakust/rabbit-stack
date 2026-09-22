.intel_syntax noprefix
.section .text
.global rabbit_entry

# Read-only network inventory for x86-64 UEFI systems. PCI devices are obtained
# from firmware's PCI I/O protocol handles; no absent buses are probed directly.
rabbit_entry:
    push rbx
    push rbp
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15
    sub rsp, 0x198

    mov rbx, [rdx + 0x30]       # SystemTable->ConIn
    mov rbp, [rdx + 0x40]       # SystemTable->ConOut
    mov rdi, [rdx + 0x60]       # SystemTable->BootServices

    lea rdx, [rip + title]
    call print_ascii
    lea rdx, [rip + stage_protocols]
    call print_ascii

    lea rcx, [rip + snp_guid]
    xor edx, edx
    lea r8, [rsp + 0x40]
    mov rax, [rdi + 0x140]      # BootServices->LocateProtocol
    call rax
    test rax, rax
    lea rdx, [rip + snp_no]
    jnz print_snp
    lea rdx, [rip + snp_yes]
print_snp:
    call print_ascii

    lea rcx, [rip + wifi1_guid]
    xor edx, edx
    lea r8, [rsp + 0x40]
    mov rax, [rdi + 0x140]
    call rax
    test rax, rax
    lea rdx, [rip + wifi1_no]
    jnz print_wifi1
    lea rdx, [rip + wifi1_yes]
print_wifi1:
    call print_ascii

    lea rcx, [rip + wifi2_guid]
    xor edx, edx
    lea r8, [rsp + 0x40]
    mov rax, [rdi + 0x140]
    call rax
    test rax, rax
    lea rdx, [rip + wifi2_no]
    jnz print_wifi2
    lea rdx, [rip + wifi2_yes]
print_wifi2:
    call print_ascii
    lea rdx, [rip + stage_pci]
    call print_ascii
    lea rdx, [rip + pci_heading]
    call print_ascii

    # LocateHandleBuffer(ByProtocol, PciIoGuid, NULL, &count, &handles).
    mov qword ptr [rsp + 0x30], 0
    mov qword ptr [rsp + 0x38], 0
    mov ecx, 2                   # ByProtocol
    lea rdx, [rip + pci_io_guid]
    xor r8d, r8d
    lea r9, [rsp + 0x30]
    lea rax, [rsp + 0x38]
    mov [rsp + 0x20], rax       # fifth Microsoft-x64 argument
    mov rax, [rdi + 0x138]      # BootServices->LocateHandleBuffer
    call rax
    test rax, rax
    jnz no_pci_handles

    xor r12d, r12d              # handle index
    xor r15d, r15d              # network-controller count
handle_loop:
    cmp r12, [rsp + 0x30]
    jae handles_done
    mov rax, [rsp + 0x38]
    mov rcx, [rax + r12 * 8]
    lea rdx, [rip + pci_io_guid]
    lea r8, [rsp + 0x40]
    mov rax, [rdi + 0x98]       # BootServices->HandleProtocol
    call rax
    test rax, rax
    jnz next_handle
    mov rsi, [rsp + 0x40]       # EFI_PCI_IO_PROTOCOL

    # Pci.Read(This, Uint32, offset 0, count 4, 16-byte header buffer).
    mov rcx, rsi
    mov edx, 2                  # EfiPciIoWidthUint32
    xor r8d, r8d
    mov r9d, 4
    lea rax, [rsp + 0x68]
    mov [rsp + 0x20], rax
    mov rax, [rsi + 0x30]       # Pci.Read
    call rax
    test rax, rax
    jnz next_handle
    cmp byte ptr [rsp + 0x73], 2 # PCI base class byte
    jne next_handle

    # GetLocation(This, &segment, &bus, &device, &function).
    mov rcx, rsi
    lea rdx, [rsp + 0x48]
    lea r8, [rsp + 0x50]
    lea r9, [rsp + 0x58]
    lea rax, [rsp + 0x60]
    mov [rsp + 0x20], rax
    mov rax, [rsi + 0x70]       # PciIo->GetLocation
    call rax
    test rax, rax
    jnz next_handle

    inc r15d
    lea rsi, [rip + pci_template]
    lea rdx, [rsp + 0x80]
copy_template:
    mov al, [rsi]
    mov [rdx], al
    inc rsi
    inc rdx
    test al, al
    jnz copy_template
    mov eax, [rsp + 0x50]
    lea rdx, [rsp + 0x80 + pci_bus - pci_template]
    mov r10d, 2
    call write_hex
    mov eax, [rsp + 0x58]
    lea rdx, [rsp + 0x80 + pci_device - pci_template]
    mov r10d, 2
    call write_hex
    mov eax, [rsp + 0x60]
    lea rdx, [rsp + 0x80 + pci_function - pci_template]
    mov r10d, 1
    call write_hex
    movzx eax, word ptr [rsp + 0x68]
    lea rdx, [rsp + 0x80 + pci_vendor - pci_template]
    mov r10d, 4
    call write_hex
    movzx eax, word ptr [rsp + 0x6a]
    lea rdx, [rsp + 0x80 + pci_product - pci_template]
    mov r10d, 4
    call write_hex
    movzx eax, byte ptr [rsp + 0x72]
    lea rdx, [rsp + 0x80 + pci_subclass - pci_template]
    mov r10d, 2
    call write_hex
    lea rdx, [rsp + 0x80]
    call print_ascii
next_handle:
    inc r12d
    jmp handle_loop

handles_done:
    mov rcx, [rsp + 0x38]
    mov rax, [rdi + 0x48]       # BootServices->FreePool
    call rax
    jmp print_count
no_pci_handles:
    xor r15d, r15d
print_count:
    lea rsi, [rip + count_template]
    lea rdx, [rsp + 0x80]
copy_count:
    mov al, [rsi]
    mov [rdx], al
    inc rsi
    inc rdx
    test al, al
    jnz copy_count
    mov eax, r15d
    lea rdx, [rsp + 0x80 + count_digits - count_template]
    mov r10d, 2
    call write_hex
    lea rdx, [rsp + 0x80]
    call print_ascii
    lea rdx, [rip + footer]
    call print_ascii

wait_key:
    mov rcx, rbx
    lea rdx, [rsp + 0x78]
    mov rax, [rcx + 8]
    call rax
    test rax, rax
    jnz wait_key
    xor eax, eax
    add rsp, 0x198
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbp
    pop rbx
    ret

# RDX points to ASCII. Convert to UTF-16 in the stack buffer, then print.
print_ascii:
    lea r8, [rsp + 0xd0]
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
    # This helper is itself reached by CALL. Reserve the Microsoft x64 ABI's
    # 32-byte shadow space plus 8 bytes for 16-byte pre-call alignment before
    # entering firmware. Without this, firmware may overwrite our return address.
    sub rsp, 0x28
    call rax
    add rsp, 0x28
    ret

# EAX=value, RDX=ASCII destination, R10D=hexadecimal digit count.
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

title:       .asciz "\r\nRABBIT NETWORK PROBE v0.4\r\n=========================\r\nSTAGE 1: TEXT OK\r\n"
stage_protocols: .asciz "STAGE 2: PROTOCOL CHECKS\r\n"
stage_pci:   .asciz "STAGE 3: PCI HANDLES\r\n"
snp_yes:     .asciz "UEFI SIMPLE NETWORK: YES\r\n"
snp_no:      .asciz "UEFI SIMPLE NETWORK: NO\r\n"
wifi1_yes:   .asciz "UEFI WIFI v1: YES\r\n"
wifi1_no:    .asciz "UEFI WIFI v1: NO\r\n"
wifi2_yes:   .asciz "UEFI WIFI v2: YES\r\n"
wifi2_no:    .asciz "UEFI WIFI v2: NO\r\n"
pci_heading: .asciz "\r\nPCI NETWORK CONTROLLERS:\r\n"
pci_template:
    .ascii "B="
pci_bus:      .ascii "00 D="
pci_device:   .ascii "00 F="
pci_function: .ascii "0 VEN="
pci_vendor:   .ascii "0000 DEV="
pci_product:  .ascii "0000 SUB="
pci_subclass: .asciz "00\r\n"
count_template:
    .ascii "TOTAL: "
count_digits: .asciz "00\r\n"
footer:       .asciz "\r\nPHOTOGRAPH THIS SCREEN. PRESS ANY KEY TO EXIT.\r\n"
hex_digits:   .ascii "0123456789ABCDEF"

.p2align 3
snp_guid:
    .byte 0xb9,0x32,0x98,0xa1,0x25,0xac,0xd3,0x11,0x9a,0x2d,0x00,0x90,0x27,0x3f,0xc1,0x4d
wifi1_guid:
    .byte 0xc9,0x5b,0xa5,0x0d,0xf8,0x45,0xb4,0x4b,0x87,0x19,0x52,0x24,0xf1,0x8a,0x4d,0x45
wifi2_guid:
    .byte 0xbf,0xb9,0x0f,0x1b,0x9d,0x69,0xdd,0x4f,0xa7,0xc3,0x25,0x46,0x68,0x1b,0xf6,0x3b
pci_io_guid:
    .byte 0x00,0xb2,0xf5,0x4c,0xb8,0x68,0xa5,0x4c,0x9e,0xec,0xb2,0x3e,0x3f,0x50,0x02,0x9a
