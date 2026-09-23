.intel_syntax noprefix
.section .text
.global rabbit_entry

# One-boot composition: initialize exact QCA Rome 3.2 controller RAM, then chain
# into a bounded receive-only BLUE/YELLOW command runtime. Exactly one reset is
# used after the transient RAM load. No active scan, advertising, pairing,
# connection, Dell radio transmit, or persistent write exists.
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
    mov [rsp + 0x488], rdx       # preserve SystemTable for the chained receiver

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
    lea rdx, [rip + chain_message]
    call print_ascii
    mov rdx, [rsp + 0x488]
    add rsp, 0x498
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbp
    pop rbx
    jmp scan_entry

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

title: .asciz "\r\nRABBIT BLE COLOR COMMAND v0.1\r\n=============================\r\nTRANSIENT RAM; ONE POST-LOAD HCI RESET\r\n\r\nSTAGE 1: FIND 0CF3:E009 INTERFACE 00\r\n"
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
chain_message: .asciz "STAGE 5: BEGIN BOUNDED PASSIVE RABBIT RECEIVE\r\n"
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

# ---- chained receiver; reached only after both QCA setup bits are ready ----
# Chained bounded receive-only Bluetooth LE beacon probe for the observed 0CF3:E009.
# It configures event masks, enables passive scan for at most 20 seconds, and
# accepts only the exact Rabbit UUID. Passive scan transmits no radio packets.
scan_entry:
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

    lea rdx, [rip + scan_title]
    call scan_print_ascii

    # LocateHandleBuffer(ByProtocol, UsbIoGuid, NULL, &count, &handles).
    mov qword ptr [rsp + 0x30], 0
    mov qword ptr [rsp + 0x38], 0
    mov ecx, 2
    lea rdx, [rip + scan_usb_io_guid]
    xor r8d, r8d
    lea r9, [rsp + 0x30]
    lea rax, [rsp + 0x38]
    mov [rsp + 0x20], rax
    mov rax, [rdi + 0x138]
    call rax
    test rax, rax
    jnz scan_target_not_found

    cmp qword ptr [rsp + 0x30], 64
    jbe scan_count_bounded
    mov qword ptr [rsp + 0x30], 64
scan_count_bounded:
    xor r12d, r12d

scan_handle_loop:
    cmp r12, [rsp + 0x30]
    jae scan_handles_done
    mov rax, [rsp + 0x38]
    mov rcx, [rax + r12 * 8]
    lea rdx, [rip + scan_usb_io_guid]
    lea r8, [rsp + 0x40]
    mov rax, [rdi + 0x98]
    call rax
    test rax, rax
    jnz scan_next_handle
    mov rsi, [rsp + 0x40]

    mov rcx, rsi
    lea rdx, [rsp + 0x50]
    mov rax, [rsi + 0x30]       # UsbGetDeviceDescriptor
    call rax
    test rax, rax
    jnz scan_next_handle

    mov rcx, rsi
    lea rdx, [rsp + 0x68]
    mov rax, [rsi + 0x40]       # UsbGetInterfaceDescriptor
    call rax
    test rax, rax
    jnz scan_next_handle

    cmp word ptr [rsp + 0x58], 0x0cf3
    jne scan_next_handle
    cmp word ptr [rsp + 0x5a], 0xe009
    jne scan_next_handle
    cmp byte ptr [rsp + 0x6a], 0x00
    jne scan_next_handle
    cmp byte ptr [rsp + 0x6d], 0xe0
    jne scan_next_handle
    cmp byte ptr [rsp + 0x6e], 0x01
    jne scan_next_handle
    cmp byte ptr [rsp + 0x6f], 0x01
    jne scan_next_handle

    movzx r15d, byte ptr [rsp + 0x6c] # bNumEndpoints
    cmp r15d, 8
    jbe scan_endpoints_bounded
    mov r15d, 8
scan_endpoints_bounded:
    mov dword ptr [rsp + 0x48], 0
scan_endpoint_loop:
    mov eax, dword ptr [rsp + 0x48]
    cmp eax, r15d
    jae scan_next_handle
    mov rcx, rsi
    mov edx, eax
    lea r8, [rsp + 0x78]
    mov rax, [rsi + 0x48]       # UsbGetEndpointDescriptor
    call rax
    test rax, rax
    jnz scan_next_endpoint
    mov al, [rsp + 0x7a]        # bEndpointAddress
    test al, 0x80
    jz scan_next_endpoint
    mov dl, [rsp + 0x7b]        # bmAttributes
    and dl, 0x03
    cmp dl, 0x03                # interrupt endpoint
    jne scan_next_endpoint
    mov r13, rsi
    movzx r14d, al
    jmp scan_handles_done
scan_next_endpoint:
    inc dword ptr [rsp + 0x48]
    jmp scan_endpoint_loop

scan_next_handle:
    inc r12d
    jmp scan_handle_loop

scan_handles_done:
    mov rcx, [rsp + 0x38]
    test rcx, rcx
    jz scan_handles_freed
    mov rax, [rdi + 0x48]
    call rax
scan_handles_freed:
    test r13, r13
    jz scan_target_not_found

    lea rsi, [rip + scan_found_template]
    lea rdx, [rsp + 0x100]
    call scan_copy_ascii
    mov eax, r14d
    lea rdx, [rsp + 0x100 + scan_found_endpoint - scan_found_template]
    mov r10d, 2
    call scan_write_hex
    lea rdx, [rsp + 0x100]
    call scan_print_ascii

    # Bind the current GOP framebuffer and draw the initial yellow square.
    # The runtime accepts only pixel formats 0 (RGB) and 1 (BGR).
    call scan_init_graphics
    test eax, eax
    jnz scan_graphics_failed
    xor eax, eax
    mov dword ptr [rsp + 0x418], eax # no wireless command applied yet
    mov eax, 2                       # yellow
    call scan_draw_square
    lea rdx, [rip + scan_graphics_ok]
    call scan_print_ascii

    # Emit one reviewed HCI packet on USB endpoint 0 and accept only its
    # matching successful Command Complete event.
    .macro send_hci_command packet, packet_end, opcode_lo, opcode_hi
    mov byte ptr [rsp + 0x80], 0x20
    mov byte ptr [rsp + 0x81], 0x00
    mov word ptr [rsp + 0x82], 0x0000
    mov word ptr [rsp + 0x84], 0x0000
    mov word ptr [rsp + 0x86], \packet_end - \packet
    mov dword ptr [rsp + 0x90], 0

    mov rcx, r13
    lea rdx, [rsp + 0x80]
    mov r8d, 1
    mov r9d, 1000
    lea rax, [rip + \packet]
    mov [rsp + 0x20], rax
    mov qword ptr [rsp + 0x28], \packet_end - \packet
    lea rax, [rsp + 0x90]
    mov [rsp + 0x30], rax
    mov rax, [r13 + 0x00]      # UsbControlTransfer
    call rax
    test rax, rax
    jnz scan_command_failed

    xor r12d, r12d
.Levent_loop\@:
    cmp r12d, 8
    jae scan_response_not_found
    mov qword ptr [rsp + 0x98], 80
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
    jnz scan_response_not_found
    cmp qword ptr [rsp + 0x98], 6
    jb .Lnext_event\@
    cmp byte ptr [rsp + 0xa0], 0x0e
    jne .Lnext_event\@
    cmp byte ptr [rsp + 0xa3], \opcode_lo
    jne .Lnext_event\@
    cmp byte ptr [rsp + 0xa4], \opcode_hi
    jne .Lnext_event\@
    cmp byte ptr [rsp + 0xa5], 0x00
    jne scan_controller_error
    jmp .Lcommand_complete\@
.Lnext_event\@:
    inc r12d
    jmp .Levent_loop\@
.Lcommand_complete\@:
    .endm

    # Apply the newly loaded transient firmware exactly once. Linux's generic HCI
    # initialization performs this reset after the QCA USB setup callback returns.
    send_hci_command scan_cmd_hci_reset, scan_cmd_hci_reset_end, 0x03, 0x0c
    mov ecx, 100000
    mov rax, [rdi + 0xf8]
    call rax
    test rax, rax
    jnz scan_command_failed
    lea rdx, [rip + scan_reset_ok]
    call scan_print_ascii

    send_hci_command scan_cmd_event_mask, scan_cmd_event_mask_end, 0x01, 0x0c
    lea rdx, [rip + scan_event_mask_ok]
    call scan_print_ascii
    send_hci_command scan_cmd_le_event_mask, scan_cmd_le_event_mask_end, 0x01, 0x20
    lea rdx, [rip + scan_le_event_mask_ok]
    call scan_print_ascii
    send_hci_command scan_cmd_scan_parameters, scan_cmd_scan_parameters_end, 0x0b, 0x20
    lea rdx, [rip + scan_scan_parameters_ok]
    call scan_print_ascii
    send_hci_command scan_cmd_scan_enable, scan_cmd_scan_enable_end, 0x0c, 0x20
    lea rdx, [rip + scan_scan_on]
    call scan_print_ascii

    xor r15d, r15d             # bit 0 BLUE seen; bit 1 YELLOW seen
    xor r12d, r12d
    mov dword ptr [rsp + 0xf0], 0 # successful scan transfers
    mov dword ptr [rsp + 0xf4], 0 # LE Meta events
    mov dword ptr [rsp + 0xf8], 0 # LE Advertising Reports
scan_scan_event_loop:
    cmp r12d, 600              # 600 * 200 ms = at most 120 seconds
    jae scan_stop_scan
    mov qword ptr [rsp + 0x98], 80
    mov dword ptr [rsp + 0x90], 0
    mov rcx, r13
    mov edx, r14d
    lea r8, [rsp + 0xa0]
    lea r9, [rsp + 0x98]
    mov qword ptr [rsp + 0x20], 200
    lea rax, [rsp + 0x90]
    mov [rsp + 0x28], rax
    mov rax, [r13 + 0x18]      # UsbSyncInterruptTransfer
    call rax
    inc r12d
    test rax, rax
    jnz scan_scan_event_loop        # bounded timeout or transient receive failure
    inc dword ptr [rsp + 0xf0]
    cmp qword ptr [rsp + 0x98], 3
    jb scan_scan_event_loop
    cmp byte ptr [rsp + 0xa0], 0x3e # LE Meta Event
    jne scan_scan_event_loop
    inc dword ptr [rsp + 0xf4]
    cmp byte ptr [rsp + 0xa2], 0x02 # LE Advertising Report
    jne scan_scan_event_loop
    inc dword ptr [rsp + 0xf8]
    cmp qword ptr [rsp + 0x98], 20
    jb scan_scan_event_loop

    mov rcx, [rsp + 0x98]
    sub rcx, 15
    xor edx, edx
scan_scan_uuid_search:
    lea rsi, [rsp + 0xa0 + rdx]
    mov rax, [rsi]
    cmp rax, qword ptr [rip + scan_blue_uuid_le]
    jne scan_check_blue_canonical
    mov rax, [rsi + 8]
    cmp rax, qword ptr [rip + scan_blue_uuid_le + 8]
    je scan_blue_found
scan_check_blue_canonical:
    mov rax, [rsi]
    cmp rax, qword ptr [rip + scan_blue_uuid_canonical]
    jne scan_check_yellow_le
    mov rax, [rsi + 8]
    cmp rax, qword ptr [rip + scan_blue_uuid_canonical + 8]
    je scan_blue_found
scan_check_yellow_le:
    mov rax, [rsi]
    cmp rax, qword ptr [rip + scan_yellow_uuid_le]
    jne scan_check_yellow_canonical
    mov rax, [rsi + 8]
    cmp rax, qword ptr [rip + scan_yellow_uuid_le + 8]
    je scan_yellow_found
scan_check_yellow_canonical:
    mov rax, [rsi]
    cmp rax, qword ptr [rip + scan_yellow_uuid_canonical]
    jne scan_scan_uuid_next
    mov rax, [rsi + 8]
    cmp rax, qword ptr [rip + scan_yellow_uuid_canonical + 8]
    je scan_yellow_found
scan_scan_uuid_next:
    inc rdx
    cmp rdx, rcx
    jb scan_scan_uuid_search
    jmp scan_scan_event_loop

scan_blue_found:
    or r15d, 1
    cmp dword ptr [rsp + 0x418], 1
    je scan_after_command
    mov dword ptr [rsp + 0x418], 1
    mov eax, 1
    call scan_draw_square
    lea rdx, [rip + scan_blue_received]
    call scan_print_ascii
    jmp scan_after_command

scan_yellow_found:
    or r15d, 2
    cmp dword ptr [rsp + 0x418], 2
    je scan_after_command
    mov dword ptr [rsp + 0x418], 2
    mov eax, 2
    call scan_draw_square
    lea rdx, [rip + scan_yellow_received]
    call scan_print_ascii

scan_after_command:
    cmp r15d, 3
    je scan_stop_scan
    jmp scan_scan_event_loop

scan_stop_scan:
    send_hci_command scan_cmd_scan_disable, scan_cmd_scan_disable_end, 0x0c, 0x20
    lea rdx, [rip + scan_scan_off]
    call scan_print_ascii
    lea rsi, [rip + scan_rx_template]
    lea rdx, [rsp + 0x100]
    call scan_copy_ascii
    mov eax, dword ptr [rsp + 0xf0]
    lea rdx, [rsp + 0x100 + scan_rx_value - scan_rx_template]
    mov r10d, 2
    call scan_write_hex
    mov eax, dword ptr [rsp + 0xf4]
    lea rdx, [rsp + 0x100 + scan_le_value - scan_rx_template]
    mov r10d, 2
    call scan_write_hex
    mov eax, dword ptr [rsp + 0xf8]
    lea rdx, [rsp + 0x100 + scan_adv_value - scan_rx_template]
    mov r10d, 2
    call scan_write_hex
    lea rdx, [rsp + 0x100]
    call scan_print_ascii
    cmp r15d, 3
    jne scan_commands_incomplete
    lea rdx, [rip + scan_both_received]
    call scan_print_ascii
    jmp scan_finish
scan_commands_incomplete:
    lea rdx, [rip + scan_command_window_closed]
    call scan_print_ascii
    jmp scan_finish

scan_graphics_failed:
    lea rdx, [rip + scan_graphics_error]
    call scan_print_ascii
    jmp scan_finish

scan_target_not_found:
    lea rdx, [rip + scan_not_found]
    call scan_print_ascii
    jmp scan_finish
scan_command_failed:
    lea rdx, [rip + scan_control_error]
    call scan_print_ascii
    jmp scan_finish
scan_response_not_found:
    lea rdx, [rip + scan_event_error]
    call scan_print_ascii
    jmp scan_finish
scan_malformed_response:
    lea rdx, [rip + scan_malformed]
    call scan_print_ascii
    jmp scan_finish
scan_controller_error:
    lea rsi, [rip + scan_status_template]
    lea rdx, [rsp + 0x100]
    call scan_copy_ascii
    movzx eax, byte ptr [rsp + 0xa5]
    lea rdx, [rsp + 0x100 + scan_status_value - scan_status_template]
    mov r10d, 2
    call scan_write_hex
    lea rdx, [rsp + 0x100]
    call scan_print_ascii

scan_finish:
    lea rdx, [rip + scan_footer]
    call scan_print_ascii
scan_wait_key:
    mov rcx, rbx
    lea rdx, [rsp + 0xc0]
    mov rax, [rcx + 8]
    call rax
    test rax, rax
    jnz scan_wait_key
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
scan_copy_ascii:
    mov al, [rsi]
    mov [rdx], al
    inc rsi
    inc rdx
    test al, al
    jnz scan_copy_ascii
    ret

# RDX points to ASCII. Convert to UTF-16 and print.
scan_print_ascii:
    lea r8, [rsp + 0x200]
    mov r9, r8
scan_convert_ascii:
    movzx eax, byte ptr [rdx]
    inc rdx
    mov word ptr [r9], ax
    add r9, 2
    test al, al
    jnz scan_convert_ascii
    mov rcx, rbp
    mov rdx, r8
    mov rax, [rcx + 8]
    sub rsp, 0x28
    call rax
    add rsp, 0x28
    ret

# EAX=value, RDX=ASCII destination, R10D=hex digit count.
scan_write_hex:
    mov r8d, eax
    lea r9d, [r10d * 4 - 4]
    lea r11, [rip + scan_hex_digits]
scan_hex_loop:
    mov eax, r8d
    mov ecx, r9d
    shr eax, cl
    and eax, 0x0f
    mov al, [r11 + rax]
    mov [rdx], al
    inc rdx
    sub r9d, 4
    jns scan_hex_loop
    ret

# Locate the UEFI Graphics Output Protocol and retain the current linear
# framebuffer. Return EAX=0 on success, EAX=1 on an unsupported display.
scan_init_graphics:
    lea rcx, [rip + scan_gop_guid]
    xor edx, edx
    lea r8, [rsp + 0x400]
    mov rax, [rdi + 0x140]      # BootServices->LocateProtocol
    call rax
    test rax, rax
    jnz scan_gop_bad
    mov rax, [rsp + 0x400]
    test rax, rax
    jz scan_gop_bad
    mov rax, [rax + 0x18]       # GOP->Mode
    test rax, rax
    jz scan_gop_bad
    mov rdx, [rax + 0x08]       # Mode->Info
    test rdx, rdx
    jz scan_gop_bad
    mov ecx, [rdx + 0x0c]       # PixelFormat
    cmp ecx, 1
    ja scan_gop_bad
    mov r8d, [rdx + 0x04]       # HorizontalResolution
    mov r9d, [rdx + 0x08]       # VerticalResolution
    cmp r8d, 128
    jb scan_gop_bad
    cmp r9d, 128
    jb scan_gop_bad
    mov r10d, [rdx + 0x20]      # PixelsPerScanLine
    mov r11, [rax + 0x18]       # FrameBufferBase
    test r11, r11
    jz scan_gop_bad
    mov [rsp + 0x408], r11
    mov [rsp + 0x410], r10d
    mov [rsp + 0x414], ecx
    sub r8d, 128
    shr r8d, 1
    mov [rsp + 0x41c], r8d
    sub r9d, 128
    shr r9d, 1
    mov [rsp + 0x420], r9d
    xor eax, eax
    ret
scan_gop_bad:
    mov eax, 1
    ret

# EAX=1 blue, EAX=2 yellow. Draw a centered 128x128 square directly into GOP.
scan_draw_square:
    push rsi
    mov ecx, [rsp + 0x414 + 8]
    cmp eax, 1
    jne scan_color_yellow
    mov esi, 0x00ff0000         # RGB framebuffer: blue
    test ecx, ecx
    jz scan_color_ready
    mov esi, 0x000000ff         # BGR framebuffer: blue
    jmp scan_color_ready
scan_color_yellow:
    mov esi, 0x0000ffff         # RGB framebuffer: yellow
    test ecx, ecx
    jz scan_color_ready
    mov esi, 0x00ffff00         # BGR framebuffer: yellow
scan_color_ready:
    mov r8, [rsp + 0x408 + 8]
    mov r9d, [rsp + 0x410 + 8]
    mov r10d, [rsp + 0x41c + 8]
    mov r11d, [rsp + 0x420 + 8]
    xor ecx, ecx
scan_draw_row:
    mov eax, r11d
    add eax, ecx
    imul rax, r9
    add rax, r10
    lea rax, [r8 + rax * 4]
    xor edx, edx
scan_draw_pixel:
    mov [rax + rdx * 4], esi
    inc edx
    cmp edx, 128
    jb scan_draw_pixel
    inc ecx
    cmp ecx, 128
    jb scan_draw_row
    pop rsi
    ret

scan_title: .asciz "\r\nRABBIT BLE COLOR COMMAND v0.1\r\n================\r\nPASSIVE RX: BLUE OR YELLOW; NO PAIR OR CONNECT\r\n\r\nSTAGE 1: FIND 0CF3:E009 INTERFACE 00\r\n"
scan_found_template: .ascii "TARGET FOUND; EVENT ENDPOINT="
scan_found_endpoint: .asciz "00\r\n"
scan_graphics_ok: .asciz "DISPLAY READY; INITIAL SQUARE=YELLOW\r\n"
scan_reset_ok: .asciz "STAGE 2: POST-LOAD HCI RESET: OK\r\n"
scan_event_mask_ok: .asciz "STAGE 2: LE META MASK: OK\r\n"
scan_le_event_mask_ok: .asciz "STAGE 3: ADV REPORT MASK: OK\r\n"
scan_scan_parameters_ok: .asciz "STAGE 4: PASSIVE PARAMETERS: OK\r\n"
scan_scan_on: .asciz "STAGE 5: PASSIVE COMMAND WINDOW; MAX 120 SECONDS\r\n"
scan_scan_off: .asciz "STAGE 6: PASSIVE SCAN OFF\r\n"
scan_rx_template: .ascii "RX/LE/ADV (HEX)="
scan_rx_value: .ascii "00/"
scan_le_value: .ascii "00/"
scan_adv_value: .asciz "00\r\n"
scan_blue_received: .asciz "COMMAND BLUE RECEIVED; SQUARE=BLUE\r\n"
scan_yellow_received: .asciz "COMMAND YELLOW RECEIVED; SQUARE=YELLOW\r\n"
scan_both_received: .asciz "BLUE AND YELLOW VERIFIED; WINDOW CLOSED EARLY\r\nNO PAIR; NO CONNECT; NO DELL RADIO TRANSMIT\r\n"
scan_command_window_closed: .asciz "COMMAND WINDOW CLOSED; FINAL COLOR PRESERVED\r\nNO PAIR; NO CONNECT; NO DELL RADIO TRANSMIT\r\n"
scan_graphics_error: .asciz "SUPPORTED GOP FRAMEBUFFER NOT FOUND; RADIO NOT ENABLED\r\n"
scan_not_found: .asciz "TARGET NOT FOUND; NO HCI COMMAND SENT\r\n"
scan_control_error: .asciz "HCI COMMAND USB TRANSFER FAILED\r\n"
scan_event_error: .asciz "MATCHING HCI EVENT NOT RECEIVED WITHIN BUDGET\r\n"
scan_malformed: .asciz "MATCHING HCI EVENT WAS TOO SHORT\r\n"
scan_status_template: .ascii "CONTROLLER RETURNED HCI STATUS="
scan_status_value: .asciz "00\r\n"
scan_footer: .asciz "\r\nPHOTOGRAPH. PRESS ANY KEY.\r\n"
scan_hex_digits: .ascii "0123456789ABCDEF"

.balign 8
# Apply the volatile QCA setup before configuring receive-only scanning.
scan_cmd_hci_reset: .byte 0x03,0x0c,0x00
scan_cmd_hci_reset_end:
# Event code 0x3E (LE Meta Event) is bit 61 of the general event mask.
scan_cmd_event_mask: .byte 0x01,0x0c,0x08, 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x20
scan_cmd_event_mask_end:
# LE Advertising Report is bit 1 of the LE event mask.
scan_cmd_le_event_mask: .byte 0x01,0x20,0x08, 0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00
scan_cmd_le_event_mask_end:
# Passive scan, 10 ms interval/window, public own address, accept all.
scan_cmd_scan_parameters: .byte 0x0b,0x20,0x07, 0x00,0x10,0x00,0x10,0x00,0x00,0x00
scan_cmd_scan_parameters_end:
scan_cmd_scan_enable: .byte 0x0c,0x20,0x02, 0x01,0x00
scan_cmd_scan_enable_end:
scan_cmd_scan_disable: .byte 0x0c,0x20,0x02, 0x00,0x00
scan_cmd_scan_disable_end:

.balign 8
# CoreBluetooth may expose each 128-bit UUID in little-endian AD order.
scan_blue_uuid_le:
    .byte 0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x80
    .byte 0x45,0x4c,0x54,0x49,0x42,0x42,0x41,0x52
scan_blue_uuid_canonical:
    .byte 0x52,0x41,0x42,0x42,0x49,0x54,0x4c,0x45
    .byte 0x80,0x00,0x00,0x00,0x00,0x00,0x00,0x02
scan_yellow_uuid_le:
    .byte 0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x80
    .byte 0x45,0x4c,0x54,0x49,0x42,0x42,0x41,0x52
scan_yellow_uuid_canonical:
    .byte 0x52,0x41,0x42,0x42,0x49,0x54,0x4c,0x45
    .byte 0x80,0x00,0x00,0x00,0x00,0x00,0x00,0x03

.balign 8
scan_gop_guid:
    .byte 0xde,0xa9,0x42,0x90,0xdc,0x23,0x38,0x4a
    .byte 0x96,0xfb,0x7a,0xde,0xd0,0x80,0x51,0x6a

.balign 8
scan_usb_io_guid:
    .byte 0xd6,0x68,0x2f,0x2b,0xd2,0x0c,0xcf,0x44
    .byte 0x8e,0x8b,0xbb,0xa2,0x0b,0x1b,0x5b,0x75
