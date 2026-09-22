.intel_syntax noprefix
.section .text
.global rabbit_entry

# Read-only UEFI USB inventory. Only UsbGetDeviceDescriptor and
# UsbGetInterfaceDescriptor are called. No transfer, port reset, HCI, pairing,
# radio, configuration, storage, or firmware mutation path exists.
rabbit_entry:
    push rbx
    push rbp
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15
    sub rsp, 0x298

    mov rbx, [rdx + 0x30]       # SystemTable->ConIn
    mov rbp, [rdx + 0x40]       # SystemTable->ConOut
    mov rdi, [rdx + 0x60]       # SystemTable->BootServices

    lea rdx, [rip + title]
    call print_ascii

    # LocateHandleBuffer(ByProtocol, UsbIoGuid, NULL, &count, &handles).
    mov qword ptr [rsp + 0x30], 0
    mov qword ptr [rsp + 0x38], 0
    mov ecx, 2
    lea rdx, [rip + usb_io_guid]
    xor r8d, r8d
    lea r9, [rsp + 0x30]
    lea rax, [rsp + 0x38]
    mov [rsp + 0x20], rax
    mov rax, [rdi + 0x138]      # BootServices->LocateHandleBuffer
    call rax
    test rax, rax
    jnz no_usb_handles

    cmp qword ptr [rsp + 0x30], 64
    jbe count_bounded
    mov qword ptr [rsp + 0x30], 64
count_bounded:
    xor r12d, r12d              # handle index
    xor r14d, r14d              # Bluetooth candidate count
    xor r15d, r15d              # successfully described interface count

handle_loop:
    cmp r12, [rsp + 0x30]
    jae handles_done
    mov rax, [rsp + 0x38]
    mov rcx, [rax + r12 * 8]
    lea rdx, [rip + usb_io_guid]
    lea r8, [rsp + 0x40]
    mov rax, [rdi + 0x98]       # BootServices->HandleProtocol
    call rax
    test rax, rax
    jnz next_handle
    mov rsi, [rsp + 0x40]       # EFI_USB_IO_PROTOCOL

    # UsbGetDeviceDescriptor(This, &device_descriptor).
    mov rcx, rsi
    lea rdx, [rsp + 0x50]
    mov rax, [rsi + 0x30]
    call rax
    test rax, rax
    jnz next_handle

    # UsbGetInterfaceDescriptor(This, &interface_descriptor).
    mov rcx, rsi
    lea rdx, [rsp + 0x68]
    mov rax, [rsi + 0x40]
    call rax
    test rax, rax
    jnz next_handle

    inc r15d
    lea rsi, [rip + usb_template]
    lea rdx, [rsp + 0x80]
copy_template:
    mov al, [rsi]
    mov [rdx], al
    inc rsi
    inc rdx
    test al, al
    jnz copy_template

    movzx eax, word ptr [rsp + 0x58]
    lea rdx, [rsp + 0x80 + usb_vendor - usb_template]
    mov r10d, 4
    call write_hex
    movzx eax, word ptr [rsp + 0x5a]
    lea rdx, [rsp + 0x80 + usb_product - usb_template]
    mov r10d, 4
    call write_hex
    movzx eax, byte ptr [rsp + 0x54]
    lea rdx, [rsp + 0x80 + usb_dev_class - usb_template]
    mov r10d, 2
    call write_hex
    movzx eax, byte ptr [rsp + 0x55]
    lea rdx, [rsp + 0x80 + usb_dev_subclass - usb_template]
    mov r10d, 2
    call write_hex
    movzx eax, byte ptr [rsp + 0x56]
    lea rdx, [rsp + 0x80 + usb_dev_protocol - usb_template]
    mov r10d, 2
    call write_hex
    movzx eax, byte ptr [rsp + 0x6a]
    lea rdx, [rsp + 0x80 + usb_interface_number - usb_template]
    mov r10d, 2
    call write_hex
    movzx eax, byte ptr [rsp + 0x6d]
    lea rdx, [rsp + 0x80 + usb_if_class - usb_template]
    mov r10d, 2
    call write_hex
    movzx eax, byte ptr [rsp + 0x6e]
    lea rdx, [rsp + 0x80 + usb_if_subclass - usb_template]
    mov r10d, 2
    call write_hex
    movzx eax, byte ptr [rsp + 0x6f]
    lea rdx, [rsp + 0x80 + usb_if_protocol - usb_template]
    mov r10d, 2
    call write_hex

    # Standard Bluetooth USB class triple may be device-level or interface-level.
    cmp byte ptr [rsp + 0x54], 0xe0
    jne check_interface_bt
    cmp byte ptr [rsp + 0x55], 0x01
    jne check_interface_bt
    cmp byte ptr [rsp + 0x56], 0x01
    je mark_bluetooth
check_interface_bt:
    cmp byte ptr [rsp + 0x6d], 0xe0
    jne print_usb
    cmp byte ptr [rsp + 0x6e], 0x01
    jne print_usb
    cmp byte ptr [rsp + 0x6f], 0x01
    jne print_usb
mark_bluetooth:
    inc r14d
    mov byte ptr [rsp + 0x80 + usb_bt_0 - usb_template], 'Y'
    mov byte ptr [rsp + 0x80 + usb_bt_1 - usb_template], 'E'
    mov byte ptr [rsp + 0x80 + usb_bt_2 - usb_template], 'S'
print_usb:
    lea rdx, [rsp + 0x80]
    call print_ascii
next_handle:
    inc r12d
    jmp handle_loop

handles_done:
    mov rcx, [rsp + 0x38]
    mov rax, [rdi + 0x48]       # BootServices->FreePool
    call rax
    jmp print_counts

no_usb_handles:
    xor r14d, r14d
    xor r15d, r15d

print_counts:
    lea rsi, [rip + count_template]
    lea rdx, [rsp + 0x80]
copy_counts:
    mov al, [rsi]
    mov [rdx], al
    inc rsi
    inc rdx
    test al, al
    jnz copy_counts
    mov eax, r15d
    lea rdx, [rsp + 0x80 + count_interfaces - count_template]
    mov r10d, 2
    call write_hex
    mov eax, r14d
    lea rdx, [rsp + 0x80 + count_bluetooth - count_template]
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
    add rsp, 0x298
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbp
    pop rbx
    ret

# RDX points to ASCII. Convert to UTF-16 in a bounded stack buffer and print.
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
    sub rsp, 0x28              # nested call: shadow space plus alignment
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

title: .asciz "\r\nRABBIT USB / BLUETOOTH PROBE v0.1\r\n==================================\r\nREAD-ONLY DESCRIPTORS; RADIO OFF\r\n\r\nUSB INTERFACES:\r\n"
usb_template:
    .ascii "VID="
usb_vendor: .ascii "0000 PID="
usb_product: .ascii "0000 DEV="
usb_dev_class: .ascii "00/"
usb_dev_subclass: .ascii "00/"
usb_dev_protocol: .ascii "00 IF="
usb_interface_number: .ascii "00 CLS="
usb_if_class: .ascii "00/"
usb_if_subclass: .ascii "00/"
usb_if_protocol: .ascii "00 BT="
usb_bt_0: .ascii "N"
usb_bt_1: .ascii "O"
usb_bt_2: .asciz " \r\n"
count_template:
    .ascii "\r\nDESCRIBED INTERFACES: "
count_interfaces: .ascii "00\r\nBLUETOOTH CANDIDATES: "
count_bluetooth: .asciz "00\r\n"
footer: .asciz "\r\nPHOTOGRAPH THIS SCREEN. PRESS ANY KEY TO EXIT.\r\n"
hex_digits: .ascii "0123456789ABCDEF"

.balign 8
# EFI_USB_IO_PROTOCOL_GUID 2B2F68D6-0CD2-44CF-8E8B-BBA20B1B5B75.
usb_io_guid:
    .byte 0xd6,0x68,0x2f,0x2b,0xd2,0x0c,0xcf,0x44
    .byte 0x8e,0x8b,0xbb,0xa2,0x0b,0x1b,0x5b,0x75
