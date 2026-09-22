.intel_syntax noprefix
.section .text
.global rabbit_entry

# Read-only network inventory for x86-64 UEFI systems.
# It checks three firmware protocols and reads PCI configuration headers through
# the legacy CF8/CFC mechanism. It never writes PCI configuration data.
rabbit_entry:
    push rbx
    push rbp
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15
    sub rsp, 0x158

    mov rbx, [rdx + 0x30]       # SystemTable->ConIn
    mov rbp, [rdx + 0x40]       # SystemTable->ConOut
    mov rdi, [rdx + 0x60]       # SystemTable->BootServices

    mov rcx, rbp
    mov rax, [rcx + 0x30]       # ConOut->ClearScreen
    call rax
    lea rdx, [rip + title]
    call print_ascii

    lea rcx, [rip + snp_guid]
    xor edx, edx
    lea r8, [rsp + 0x20]
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
    lea r8, [rsp + 0x28]
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
    lea r8, [rsp + 0x30]
    mov rax, [rdi + 0x140]
    call rax
    test rax, rax
    lea rdx, [rip + wifi2_no]
    jnz print_wifi2
    lea rdx, [rip + wifi2_yes]
print_wifi2:
    call print_ascii
    lea rdx, [rip + pci_heading]
    call print_ascii

    xor r12d, r12d              # bus
    xor r15d, r15d              # network-device count
bus_loop:
    xor r13d, r13d              # device
device_loop:
    xor r14d, r14d              # function
function_loop:
    mov eax, 0x80000000
    mov ecx, r12d
    shl ecx, 16
    or eax, ecx
    mov ecx, r13d
    shl ecx, 11
    or eax, ecx
    mov ecx, r14d
    shl ecx, 8
    or eax, ecx
    mov r10d, eax
    mov dx, 0x0cf8
    out dx, eax                 # select PCI config address only
    mov dx, 0x0cfc
    in eax, dx                  # vendor/device read
    cmp ax, 0xffff
    je next_function
    test ax, ax
    jz next_function
    mov [rsp + 0x38], eax

    mov eax, r10d
    or eax, 8
    mov dx, 0x0cf8
    out dx, eax
    mov dx, 0x0cfc
    in eax, dx                  # revision/prog-if/subclass/class read
    mov [rsp + 0x3c], eax
    shr eax, 24
    cmp al, 2                   # PCI base class: network controller
    jne next_function

    inc r15d
    lea rsi, [rip + pci_template]
    lea rdx, [rsp + 0x50]
copy_template:
    mov al, [rsi]
    mov [rdx], al
    inc rsi
    inc rdx
    test al, al
    jnz copy_template

    mov eax, r12d
    lea rdx, [rsp + 0x50 + pci_bus - pci_template]
    mov r10d, 2
    call write_hex
    mov eax, r13d
    lea rdx, [rsp + 0x50 + pci_device - pci_template]
    mov r10d, 2
    call write_hex
    mov eax, r14d
    lea rdx, [rsp + 0x50 + pci_function - pci_template]
    mov r10d, 1
    call write_hex
    mov eax, [rsp + 0x38]
    movzx eax, ax
    lea rdx, [rsp + 0x50 + pci_vendor - pci_template]
    mov r10d, 4
    call write_hex
    mov eax, [rsp + 0x38]
    shr eax, 16
    lea rdx, [rsp + 0x50 + pci_product - pci_template]
    mov r10d, 4
    call write_hex
    mov eax, [rsp + 0x3c]
    shr eax, 16
    and eax, 0xff
    lea rdx, [rsp + 0x50 + pci_subclass - pci_template]
    mov r10d, 2
    call write_hex
    lea rdx, [rsp + 0x50]
    call print_ascii

next_function:
    inc r14d
    cmp r14d, 8
    jb function_loop
    inc r13d
    cmp r13d, 32
    jb device_loop
    inc r12d
    cmp r12d, 256
    jb bus_loop

    lea rsi, [rip + count_template]
    lea rdx, [rsp + 0x50]
copy_count:
    mov al, [rsi]
    mov [rdx], al
    inc rsi
    inc rdx
    test al, al
    jnz copy_count
    mov eax, r15d
    lea rdx, [rsp + 0x50 + count_digits - count_template]
    mov r10d, 2
    call write_hex
    lea rdx, [rsp + 0x50]
    call print_ascii
    lea rdx, [rip + footer]
    call print_ascii

wait_key:
    mov rcx, rbx
    lea rdx, [rsp + 0x40]
    mov rax, [rcx + 8]
    call rax
    test rax, rax
    jnz wait_key
    xor eax, eax
    add rsp, 0x158
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbp
    pop rbx
    ret

# RDX points to a zero-terminated ASCII string. Convert it to UTF-16 on the
# stack, then call EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL.OutputString().
print_ascii:
    lea r8, [rsp + 0xa0]
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
    call rax
    ret

# EAX=value, RDX=ASCII destination, R10D=number of hexadecimal digits.
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

title:       .asciz "RABBIT NETWORK PROBE\r\n====================\r\n"
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
