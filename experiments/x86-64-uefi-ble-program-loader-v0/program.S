.intel_syntax noprefix
.section .text
.global rabbit_entry

# One-boot composition: initialize exact QCA Rome 3.2 controller RAM, then chain
# into a transactional receive-only Rabbit VM runtime. Exactly one reset is
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

title: .asciz "\r\nRABBIT WIRELESS PROGRAM LOADER v0.3\r\n===================================\r\nTRANSIENT RAM; ONE POST-LOAD HCI RESET\r\n\r\nSTAGE 1: FIND 0CF3:E009 INTERFACE 00\r\n"
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
chain_message: .asciz "STAGE 5: BEGIN TRANSACTIONAL RABBIT VM RECEIVE\r\n"
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
    # Keep the same 8-mod-16 frame size as the proven runtime.  scan_entry is
    # reached by JMP, so 0x700 would invert Microsoft-x64 call alignment.
    sub rsp, 0x708

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
    # The runtime accepts only pixel formats 0 (RGB) and 1 (BGR).  The same
    # 16-byte RAM slot later holds a validated Rabbit VM program.
    call scan_init_graphics
    test eax, eax
    jnz scan_graphics_failed
    lea rdx, [rip + scan_graphics_bound]
    call scan_print_ascii
    mov dword ptr [rsp + 0x454], 1   # active built-in scene
    mov byte ptr [rsp + 0x458], 1    # square
    mov byte ptr [rsp + 0x459], 0xff # red
    mov byte ptr [rsp + 0x45a], 0xff # green
    mov byte ptr [rsp + 0x45b], 0x00 # blue
    mov byte ptr [rsp + 0x45c], 128  # size
    mov byte ptr [rsp + 0x45d], 1    # arrow controls
    mov byte ptr [rsp + 0x45e], 16   # movement step
    mov eax, 1
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

    xor r15d, r15d             # validated programs applied
    xor r12d, r12d
    mov dword ptr [rsp + 0x424], 0 # set only by local Escape cleanup
    mov dword ptr [rsp + 0x440], 0 # no transfer in progress
    mov dword ptr [rsp + 0x450], 0 # checksum of last applied program
    mov dword ptr [rsp + 0xf0], 0 # successful scan transfers
    mov dword ptr [rsp + 0xf4], 0 # LE Meta events
    mov dword ptr [rsp + 0xf8], 0 # LE Advertising Reports
scan_scan_event_loop:
    # Long-lived runtime: poll local keyboard between bounded 200 ms USB reads.
    # Escape is scan code 0x17 and is the only normal termination request.
    mov rcx, rbx
    lea rdx, [rsp + 0xc0]
    mov rax, [rcx + 8]         # ConIn->ReadKeyStroke
    call rax
    test rax, rax
    jnz scan_receive_event
    cmp word ptr [rsp + 0xc0], 0x17
    jne scan_handle_local_key
    mov dword ptr [rsp + 0x424], 1
    jmp scan_stop_scan
scan_handle_local_key:
    # Arrow scan codes are Up=1, Down=2, Right=3, Left=4.  They operate only
    # when the active, validated program enabled the built-in arrow capability.
    movzx eax, word ptr [rsp + 0xc0]
    cmp eax, 1
    jb scan_receive_event
    cmp eax, 4
    ja scan_receive_event
    cmp dword ptr [rsp + 0x454], 1
    jne scan_receive_event
    test byte ptr [rsp + 0x45d], 1
    jz scan_receive_event
    mov byte ptr [rsp + 0x45f], al
    xor eax, eax
    call scan_draw_square            # erase the old shape
    movzx eax, byte ptr [rsp + 0x45f]
    movzx ecx, byte ptr [rsp + 0x45e]
    cmp eax, 1
    je scan_move_up
    cmp eax, 2
    je scan_move_down
    cmp eax, 3
    je scan_move_right
scan_move_left:
    cmp dword ptr [rsp + 0x41c], ecx
    jb scan_move_left_zero
    sub dword ptr [rsp + 0x41c], ecx
    jmp scan_move_draw
scan_move_left_zero:
    mov dword ptr [rsp + 0x41c], 0
    jmp scan_move_draw
scan_move_up:
    cmp dword ptr [rsp + 0x420], ecx
    jb scan_move_up_zero
    sub dword ptr [rsp + 0x420], ecx
    jmp scan_move_draw
scan_move_up_zero:
    mov dword ptr [rsp + 0x420], 0
    jmp scan_move_draw
scan_move_right:
    mov edx, dword ptr [rsp + 0x428]
    movzx r8d, byte ptr [rsp + 0x45c]
    sub edx, r8d
    add dword ptr [rsp + 0x41c], ecx
    cmp dword ptr [rsp + 0x41c], edx
    jbe scan_move_draw
    mov dword ptr [rsp + 0x41c], edx
    jmp scan_move_draw
scan_move_down:
    mov edx, dword ptr [rsp + 0x42c]
    movzx r8d, byte ptr [rsp + 0x45c]
    sub edx, r8d
    add dword ptr [rsp + 0x420], ecx
    cmp dword ptr [rsp + 0x420], edx
    jbe scan_move_draw
    mov dword ptr [rsp + 0x420], edx
scan_move_draw:
    mov eax, 1
    call scan_draw_square

scan_receive_event:
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
    cmp word ptr [rsi], 0x5052      # canonical bytes "RP"
    je scan_copy_frame_canonical
    cmp word ptr [rsi + 14], 0x5250 # reversed UUID ends "P R"
    je scan_copy_frame_reversed
scan_scan_uuid_next:
    inc rdx
    cmp rdx, rcx
    jb scan_scan_uuid_search
    jmp scan_scan_event_loop

scan_copy_frame_canonical:
    xor r8d, r8d
scan_copy_frame_canonical_loop:
    mov al, [rsi + r8]
    mov [rsp + 0x430 + r8], al
    inc r8d
    cmp r8d, 16
    jb scan_copy_frame_canonical_loop
    jmp scan_validate_frame

scan_copy_frame_reversed:
    xor r8d, r8d
scan_copy_frame_reversed_loop:
    mov r9d, 15
    sub r9d, r8d
    mov al, [rsi + r9]
    mov [rsp + 0x430 + r8], al
    inc r8d
    cmp r8d, 16
    jb scan_copy_frame_reversed_loop

scan_validate_frame:
    cmp word ptr [rsp + 0x430], 0x5052 # RP
    jne scan_scan_event_loop
    movzx r8d, byte ptr [rsp + 0x432]
    mov r9d, r8d
    shr r9d, 4
    cmp r9d, 1                         # transport version 1
    jne scan_scan_event_loop

    # FNV-1a-32 over frame bytes 0..11; result is carried big-endian.
    mov eax, 0x811c9dc5
    xor ecx, ecx
scan_frame_checksum_loop:
    movzx edx, byte ptr [rsp + 0x430 + rcx]
    xor eax, edx
    imul eax, eax, 0x01000193
    inc ecx
    cmp ecx, 12
    jb scan_frame_checksum_loop
    mov edx, dword ptr [rsp + 0x43c]
    bswap edx
    cmp eax, edx
    jne scan_scan_event_loop

    and r8d, 0x0f
    cmp r8d, 1
    je scan_frame_begin
    cmp r8d, 2
    je scan_frame_chunk
    cmp r8d, 3
    je scan_frame_commit
    jmp scan_scan_event_loop

scan_frame_begin:
    cmp word ptr [rsp + 0x435], 24     # VM v1 scene is three instructions
    jne scan_scan_event_loop
    cmp byte ptr [rsp + 0x43b], 3
    jne scan_scan_event_loop
    movzx eax, byte ptr [rsp + 0x433]
    mov byte ptr [rsp + 0x440], 1
    mov byte ptr [rsp + 0x441], al     # transfer id
    mov byte ptr [rsp + 0x442], 0      # next chunk sequence
    mov dword ptr [rsp + 0x444], 24
    mov dword ptr [rsp + 0x448], 0
    mov eax, dword ptr [rsp + 0x437]   # program hash, big-endian
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
    mov r9d, dword ptr [rsp + 0x448]   # received
    mov r10d, dword ptr [rsp + 0x444]  # total
    sub r10d, r9d                       # remaining
    jbe scan_scan_event_loop
    cmp r10d, 7
    jbe scan_chunk_count_ready
    mov r10d, 7
scan_chunk_count_ready:
    xor r8d, r8d
scan_chunk_copy_loop:
    mov al, byte ptr [rsp + 0x435 + r8]
    mov byte ptr [rsp + 0x460 + r9], al
    inc r8d
    inc r9d
    cmp r8d, r10d
    jb scan_chunk_copy_loop
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
    cmp word ptr [rsp + 0x439], 24
    jne scan_scan_event_loop
    cmp byte ptr [rsp + 0x43b], 0
    jne scan_scan_event_loop
    cmp dword ptr [rsp + 0x448], 24
    jne scan_scan_event_loop
    mov edx, dword ptr [rsp + 0x435]
    bswap edx
    cmp edx, dword ptr [rsp + 0x44c]
    jne scan_scan_event_loop

    mov eax, 0x811c9dc5
    xor ecx, ecx
scan_program_hash_loop:
    movzx edx, byte ptr [rsp + 0x460 + rcx]
    xor eax, edx
    imul eax, eax, 0x01000193
    inc ecx
    cmp ecx, 24
    jb scan_program_hash_loop
    cmp eax, dword ptr [rsp + 0x44c]
    jne scan_scan_event_loop
    cmp eax, dword ptr [rsp + 0x450]
    je scan_scan_event_loop

    # Validate the three fixed-width Rabbit VM v1 instructions.
    cmp byte ptr [rsp + 0x460], 1      # DEFINE_SHAPE
    jne scan_scan_event_loop
    movzx ecx, byte ptr [rsp + 0x461]
    cmp ecx, 1
    jb scan_scan_event_loop
    cmp ecx, 2
    ja scan_scan_event_loop
    movzx ecx, byte ptr [rsp + 0x465] # size
    cmp ecx, 8
    jb scan_scan_event_loop
    cmp ecx, 128
    ja scan_scan_event_loop
    cmp byte ptr [rsp + 0x466], 1     # flags: none or arrows
    ja scan_scan_event_loop
    movzx edx, byte ptr [rsp + 0x467] # step
    cmp edx, 1
    jb scan_scan_event_loop
    cmp edx, 64
    ja scan_scan_event_loop
    cmp byte ptr [rsp + 0x468], 2     # SET_POSITION
    jne scan_scan_event_loop
    cmp word ptr [rsp + 0x46d], 0
    jne scan_scan_event_loop
    cmp byte ptr [rsp + 0x46f], 0
    jne scan_scan_event_loop
    cmp dword ptr [rsp + 0x470], 0xff # END + three zero bytes
    jne scan_scan_event_loop
    cmp dword ptr [rsp + 0x474], 0
    jne scan_scan_event_loop
    movzx edx, word ptr [rsp + 0x469] # x
    add edx, ecx
    cmp edx, dword ptr [rsp + 0x428]
    ja scan_scan_event_loop
    movzx edx, word ptr [rsp + 0x46b] # y
    add edx, ecx
    cmp edx, dword ptr [rsp + 0x42c]
    ja scan_scan_event_loop

    xor eax, eax
    call scan_draw_square             # erase previous scene
    movzx eax, byte ptr [rsp + 0x461]
    mov byte ptr [rsp + 0x458], al
    mov eax, dword ptr [rsp + 0x462]
    mov dword ptr [rsp + 0x459], eax  # RGB, size
    mov ax, word ptr [rsp + 0x466]
    mov word ptr [rsp + 0x45d], ax    # flags, step
    movzx eax, word ptr [rsp + 0x469]
    mov dword ptr [rsp + 0x41c], eax
    movzx eax, word ptr [rsp + 0x46b]
    mov dword ptr [rsp + 0x420], eax
    mov dword ptr [rsp + 0x454], 1
    mov eax, dword ptr [rsp + 0x44c]
    mov dword ptr [rsp + 0x450], eax
    mov dword ptr [rsp + 0x440], 0
    inc r15d
    mov eax, 1
    call scan_draw_square
    lea rdx, [rip + scan_program_applied]
    call scan_print_ascii
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
    cmp dword ptr [rsp + 0x424], 1
    jne scan_commands_incomplete
    lea rdx, [rip + scan_escape_message]
    call scan_print_ascii
    jmp scan_return
scan_commands_incomplete:
    lea rdx, [rip + scan_runtime_error_cleanup]
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
scan_return:
    xor eax, eax
    add rsp, 0x708
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
    # This is a nested Microsoft-x64/UEFI call. Reserve its 32-byte shadow space
    # plus alignment; scan_entry itself already owns the persistent state slots.
    sub rsp, 0x28
    lea rcx, [rip + scan_gop_guid]
    xor edx, edx
    lea r8, [rsp + 0x430]
    mov rax, [rdi + 0x140]      # BootServices->LocateProtocol
    call rax
    test rax, rax
    jnz scan_gop_bad
    mov rax, [rsp + 0x430]
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
    mov [rsp + 0x438], r11
    mov [rsp + 0x440], r10d
    mov [rsp + 0x444], ecx
    mov [rsp + 0x458], r8d
    mov [rsp + 0x45c], r9d
    sub r8d, 128
    shr r8d, 1
    mov [rsp + 0x44c], r8d
    sub r9d, 128
    shr r9d, 1
    mov [rsp + 0x450], r9d
    xor eax, eax
    add rsp, 0x28
    ret
scan_gop_bad:
    mov eax, 1
    add rsp, 0x28
    ret

# EAX=0 erases the old bounding box; EAX=1 draws the active VM shape.
scan_draw_square:
    push rsi
    push r12
    push rdi
    mov edi, eax
    xor esi, esi
    test edi, edi
    jz scan_color_ready
    movzx eax, byte ptr [rsp + 0x459 + 0x20] # red
    movzx edx, byte ptr [rsp + 0x45a + 0x20] # green
    movzx esi, byte ptr [rsp + 0x45b + 0x20] # blue
    mov ecx, [rsp + 0x414 + 0x20]
    test ecx, ecx
    jnz scan_color_bgr
    shl esi, 16                 # RGB pixel memory is R,G,B,0
    shl edx, 8
    or esi, edx
    or esi, eax
    jmp scan_color_ready
scan_color_bgr:
    shl eax, 16                 # BGR pixel memory is B,G,R,0
    shl edx, 8
    or esi, edx
    or esi, eax
scan_color_ready:
    mov r8, [rsp + 0x408 + 0x20]
    mov r9d, [rsp + 0x410 + 0x20]
    mov r10d, [rsp + 0x41c + 0x20]
    mov r11d, [rsp + 0x420 + 0x20]
    movzx r12d, byte ptr [rsp + 0x45c + 0x20]
    xor ecx, ecx
scan_draw_row:
    mov eax, r11d
    add eax, ecx
    imul rax, r9
    add rax, r10
    lea rax, [r8 + rax * 4]
    xor edx, edx
scan_draw_pixel:
    test edi, edi
    jz scan_write_pixel
    cmp byte ptr [rsp + 0x458 + 0x20], 2
    jne scan_write_pixel
    cmp edx, ecx                  # simple right triangle: x <= row
    ja scan_skip_pixel
scan_write_pixel:
    mov [rax + rdx * 4], esi
scan_skip_pixel:
    inc edx
    cmp edx, r12d
    jb scan_draw_pixel
    inc ecx
    cmp ecx, r12d
    jb scan_draw_row
    pop rdi
    pop r12
    pop rsi
    ret

scan_title: .asciz "\r\nRABBIT WIRELESS PROGRAM LOADER v0.3\r\n===================================\r\nRABBIT VM v1; PASSIVE RX; ESC TO STOP\r\n\r\nSTAGE 1: FIND 0CF3:E009 INTERFACE 00\r\n"
scan_found_template: .ascii "TARGET FOUND; EVENT ENDPOINT="
scan_found_endpoint: .asciz "00\r\n"
scan_graphics_bound: .asciz "DISPLAY FRAMEBUFFER BOUND\r\n"
scan_graphics_ok: .asciz "INITIAL SQUARE DRAWN=YELLOW; VM READY\r\n"
scan_reset_ok: .asciz "STAGE 2: POST-LOAD HCI RESET: OK\r\n"
scan_event_mask_ok: .asciz "STAGE 2: LE META MASK: OK\r\n"
scan_le_event_mask_ok: .asciz "STAGE 3: ADV REPORT MASK: OK\r\n"
scan_scan_parameters_ok: .asciz "STAGE 4: PASSIVE PARAMETERS: OK\r\n"
scan_scan_on: .asciz "STAGE 5: WIRELESS PROGRAM RUNTIME ON; ESC TO STOP\r\n"
scan_scan_off: .asciz "STAGE 6: PASSIVE SCAN OFF\r\n"
scan_rx_template: .ascii "RX/LE/ADV (HEX)="
scan_rx_value: .ascii "00/"
scan_le_value: .ascii "00/"
scan_adv_value: .asciz "00\r\n"
scan_program_applied: .asciz "PROGRAM APPLIED: SHAPE + POSITION + ARROW CONTROLS\r\n"
scan_escape_message: .asciz "LOADER STOPPED BY ESC; FINAL VM STATE PRESERVED\r\nNO NATIVE CODE; NO PAIR; NO CONNECT; NO DELL RADIO TRANSMIT\r\n"
scan_runtime_error_cleanup: .asciz "RUNTIME STOPPED AFTER CLEANUP ERROR PATH\r\nNO PAIR; NO CONNECT; NO DELL RADIO TRANSMIT\r\n"
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
scan_gop_guid:
    .byte 0xde,0xa9,0x42,0x90,0xdc,0x23,0x38,0x4a
    .byte 0x96,0xfb,0x7a,0xde,0xd0,0x80,0x51,0x6a

.balign 8
scan_usb_io_guid:
    .byte 0xd6,0x68,0x2f,0x2b,0xd2,0x0c,0xcf,0x44
    .byte 0x8e,0x8b,0xbb,0xa2,0x0b,0x1b,0x5b,0x75
