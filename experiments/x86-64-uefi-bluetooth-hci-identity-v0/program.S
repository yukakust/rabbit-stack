.intel_syntax noprefix
.section .text
.global rabbit_entry

# Bounded Bluetooth HCI identity probe for the physically observed 0CF3:E009.
# The sole command is Read Local Version Information (opcode 0x1001). It does
# not reset the controller, scan, advertise, pair, connect, or send radio data.
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

    mov rbx, [rdx + 0x30]       # SystemTable->ConIn
    mov rbp, [rdx + 0x40]       # SystemTable->ConOut
    mov rdi, [rdx + 0x60]       # SystemTable->BootServices
    xor r13d, r13d              # selected EFI_USB_IO_PROTOCOL
    xor r14d, r14d              # selected interrupt-IN endpoint

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
    mov rax, [rsi + 0x30]       # UsbGetDeviceDescriptor
    call rax
    test rax, rax
    jnz next_handle

    mov rcx, rsi
    lea rdx, [rsp + 0x68]
    mov rax, [rsi + 0x40]       # UsbGetInterfaceDescriptor
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

    movzx r15d, byte ptr [rsp + 0x6c] # bNumEndpoints
    cmp r15d, 8
    jbe endpoints_bounded
    mov r15d, 8
endpoints_bounded:
    mov dword ptr [rsp + 0x48], 0
endpoint_loop:
    mov eax, dword ptr [rsp + 0x48]
    cmp eax, r15d
    jae next_handle
    mov rcx, rsi
    mov edx, eax
    lea r8, [rsp + 0x78]
    mov rax, [rsi + 0x48]       # UsbGetEndpointDescriptor
    call rax
    test rax, rax
    jnz next_endpoint
    mov al, [rsp + 0x7a]        # bEndpointAddress
    test al, 0x80
    jz next_endpoint
    mov dl, [rsp + 0x7b]        # bmAttributes
    and dl, 0x03
    cmp dl, 0x03                # interrupt endpoint
    jne next_endpoint
    mov r13, rsi
    movzx r14d, al
    jmp handles_done
next_endpoint:
    inc dword ptr [rsp + 0x48]
    jmp endpoint_loop

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

    lea rsi, [rip + found_template]
    lea rdx, [rsp + 0x100]
    call copy_ascii
    mov eax, r14d
    lea rdx, [rsp + 0x100 + found_endpoint - found_template]
    mov r10d, 2
    call write_hex
    lea rdx, [rsp + 0x100]
    call print_ascii

    # USB Bluetooth HCI command request: class/device OUT, three data bytes.
    mov byte ptr [rsp + 0x80], 0x20
    mov byte ptr [rsp + 0x81], 0x00
    mov word ptr [rsp + 0x82], 0x0000
    mov word ptr [rsp + 0x84], 0x0000
    mov word ptr [rsp + 0x86], 0x0003
    mov byte ptr [rsp + 0x88], 0x01 # opcode 0x1001, little-endian
    mov byte ptr [rsp + 0x89], 0x10
    mov byte ptr [rsp + 0x8a], 0x00 # parameter length
    mov dword ptr [rsp + 0x90], 0

    mov rcx, r13
    lea rdx, [rsp + 0x80]
    mov r8d, 1                 # EfiUsbDataOut
    mov r9d, 1000
    lea rax, [rsp + 0x88]
    mov [rsp + 0x20], rax
    mov qword ptr [rsp + 0x28], 3
    lea rax, [rsp + 0x90]
    mov [rsp + 0x30], rax
    mov rax, [r13 + 0x00]      # UsbControlTransfer
    call rax
    test rax, rax
    jnz command_failed

    lea rdx, [rip + command_sent]
    call print_ascii
    xor r12d, r12d

event_loop:
    cmp r12d, 8
    jae response_not_found
    mov qword ptr [rsp + 0x98], 64
    mov dword ptr [rsp + 0x90], 0
    mov rcx, r13
    mov edx, r14d
    lea r8, [rsp + 0xa0]
    lea r9, [rsp + 0x98]
    mov qword ptr [rsp + 0x20], 1000
    lea rax, [rsp + 0x90]
    mov [rsp + 0x28], rax
    mov rax, [r13 + 0x18]      # UsbSyncInterruptTransfer
    call rax
    test rax, rax
    jnz response_not_found
    cmp qword ptr [rsp + 0x98], 6
    jb next_event
    cmp byte ptr [rsp + 0xa0], 0x0e # Command Complete event
    jne next_event
    cmp byte ptr [rsp + 0xa3], 0x01
    jne next_event
    cmp byte ptr [rsp + 0xa4], 0x10
    jne next_event
    cmp qword ptr [rsp + 0x98], 14
    jb malformed_response
    cmp byte ptr [rsp + 0xa5], 0x00
    jne controller_error
    jmp print_identity
next_event:
    inc r12d
    jmp event_loop

print_identity:
    lea rsi, [rip + identity_template]
    lea rdx, [rsp + 0x100]
    call copy_ascii
    movzx eax, byte ptr [rsp + 0xa6]
    lea rdx, [rsp + 0x100 + identity_hci_version - identity_template]
    mov r10d, 2
    call write_hex
    movzx eax, word ptr [rsp + 0xa7]
    lea rdx, [rsp + 0x100 + identity_hci_revision - identity_template]
    mov r10d, 4
    call write_hex
    movzx eax, byte ptr [rsp + 0xa9]
    lea rdx, [rsp + 0x100 + identity_lmp_version - identity_template]
    mov r10d, 2
    call write_hex
    movzx eax, word ptr [rsp + 0xaa]
    lea rdx, [rsp + 0x100 + identity_manufacturer - identity_template]
    mov r10d, 4
    call write_hex
    movzx eax, word ptr [rsp + 0xac]
    lea rdx, [rsp + 0x100 + identity_lmp_subversion - identity_template]
    mov r10d, 4
    call write_hex
    lea rdx, [rsp + 0x100]
    call print_ascii
    jmp finish

target_not_found:
    lea rdx, [rip + not_found]
    call print_ascii
    jmp finish
command_failed:
    lea rdx, [rip + control_error]
    call print_ascii
    jmp finish
response_not_found:
    lea rdx, [rip + event_error]
    call print_ascii
    jmp finish
malformed_response:
    lea rdx, [rip + malformed]
    call print_ascii
    jmp finish
controller_error:
    lea rsi, [rip + status_template]
    lea rdx, [rsp + 0x100]
    call copy_ascii
    movzx eax, byte ptr [rsp + 0xa5]
    lea rdx, [rsp + 0x100 + status_value - status_template]
    mov r10d, 2
    call write_hex
    lea rdx, [rsp + 0x100]
    call print_ascii

finish:
    lea rdx, [rip + footer]
    call print_ascii
wait_key:
    mov rcx, rbx
    lea rdx, [rsp + 0xc0]
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

# RSI source, RDX destination. Includes the trailing NUL.
copy_ascii:
    mov al, [rsi]
    mov [rdx], al
    inc rsi
    inc rdx
    test al, al
    jnz copy_ascii
    ret

# RDX points to ASCII. Convert to UTF-16 and print.
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

# EAX=value, RDX=ASCII destination, R10D=hex digit count.
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

title: .asciz "\r\nRABBIT BLUETOOTH HCI IDENTITY v0.1\r\n====================================\r\nONE LOCAL INFO COMMAND; RADIO NOT USED\r\n\r\nSTAGE 1: FIND 0CF3:E009 INTERFACE 00\r\n"
found_template: .ascii "TARGET FOUND; EVENT ENDPOINT="
found_endpoint: .asciz "00\r\n"
command_sent: .asciz "STAGE 2: HCI READ LOCAL VERSION SENT (0x1001)\r\n"
identity_template:
    .ascii "STAGE 3: COMMAND COMPLETE; STATUS=00\r\nHCI VERSION="
identity_hci_version: .ascii "00 HCI REVISION="
identity_hci_revision: .ascii "0000\r\nLMP VERSION="
identity_lmp_version: .ascii "00 MANUFACTURER="
identity_manufacturer: .ascii "0000\r\nLMP SUBVERSION="
identity_lmp_subversion: .asciz "0000\r\nNO SCAN; NO ADVERTISE; NO PAIR; NO RADIO DATA\r\n"
not_found: .asciz "TARGET NOT FOUND; NO HCI COMMAND SENT\r\n"
control_error: .asciz "HCI COMMAND USB TRANSFER FAILED\r\n"
event_error: .asciz "MATCHING HCI EVENT NOT RECEIVED WITHIN BUDGET\r\n"
malformed: .asciz "MATCHING HCI EVENT WAS TOO SHORT\r\n"
status_template: .ascii "CONTROLLER RETURNED HCI STATUS="
status_value: .asciz "00\r\n"
footer: .asciz "\r\nPHOTOGRAPH THIS SCREEN. PRESS ANY KEY TO EXIT.\r\n"
hex_digits: .ascii "0123456789ABCDEF"

.balign 8
usb_io_guid:
    .byte 0xd6,0x68,0x2f,0x2b,0xd2,0x0c,0xcf,0x44
    .byte 0x8e,0x8b,0xbb,0xa2,0x0b,0x1b,0x5b,0x75
