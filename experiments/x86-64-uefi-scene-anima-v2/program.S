.intel_syntax noprefix
.section .text
.global rabbit_entry
rabbit_entry:
    push rbx
    push rbp
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15
    sub rsp, 0x88

    mov rsi, [rdx + 0x30]             # SystemTable->ConIn
    mov rbp, [rdx + 0x60]             # SystemTable->BootServices
    lea rcx, [rip + gop_guid]
    xor edx, edx
    lea r8, [rsp + 0x30]
    mov rax, [rbp + 0x140]            # LocateProtocol
    call rax
    test rax, rax
    jnz cleanup

    mov rax, [rsp + 0x30]
    mov rax, [rax + 0x18]             # GOP->Mode
    mov rbx, [rax + 0x18]             # FrameBufferBase
    mov rdx, [rax + 0x08]             # Mode->Info
    mov r14d, [rdx + 0x04]
    mov r15d, [rdx + 0x08]
    mov edi, [rdx + 0x20]             # PixelsPerScanLine
    cmp r14d, 480
    jb unsupported
    cmp r15d, 270
    jb unsupported
    cmp dword ptr [rdx + 0x0c], 0
    je use_rgb
    cmp dword ptr [rdx + 0x0c], 1
    je use_bgr
    jmp unsupported
use_rgb:
    lea rax, [rip + palette_rgb]
    mov [rsp + 0x20], rax
    jmp start_scene
use_bgr:
    lea rax, [rip + palette_bgr]
    mov [rsp + 0x20], rax

start_scene:
    lea r12, [rip + trace_data]
    mov r13d, 241
    call clear_scene

frame_loop:
    movzx r8d, byte ptr [r12 + 2]     # ball x
    movzx r9d, byte ptr [r12 + 3]     # ball y
    lea r10, [rip + ball_sprite]
    mov rcx, [rsp + 0x20]
    call draw_sprite

    movzx r8d, byte ptr [r12 + 0]     # cat x
    movzx r9d, byte ptr [r12 + 1]     # cat y
    cmp byte ptr [r12 + 4], 0
    jne cat_frame_one
    lea r10, [rip + cat_sprite_zero]
    jmp draw_cat
cat_frame_one:
    lea r10, [rip + cat_sprite_one]
draw_cat:
    mov rcx, [rsp + 0x20]
    call draw_sprite

    mov ecx, 33333
    mov rax, [rbp + 0xf8]             # BootServices->Stall
    call rax

    mov rcx, rsi
    lea rdx, [rsp + 0x40]
    mov rax, [rsi + 0x08]             # ReadKeyStroke (nonblocking)
    call rax
    test rax, rax
    jnz next_frame
    cmp word ptr [rsp + 0x40], 23     # Esc scan code
    je success

next_frame:
    # Erase both old 8x8 regions, then draw both new regions. This avoids a
    # whole-scene black intermediate frame while preserving overlap order.
    movzx r8d, byte ptr [r12 + 2]
    movzx r9d, byte ptr [r12 + 3]
    lea r10, [rip + blank_sprite]
    mov rcx, [rsp + 0x20]
    call draw_sprite
    movzx r8d, byte ptr [r12 + 0]
    movzx r9d, byte ptr [r12 + 1]
    lea r10, [rip + blank_sprite]
    mov rcx, [rsp + 0x20]
    call draw_sprite
    add r12, 5
    dec r13d
    jnz frame_loop
    lea r12, [rip + trace_data]
    mov r13d, 241
    jmp frame_loop

success:
    xor eax, eax
    jmp cleanup
unsupported:
    movabs rax, 0x8000000000000003
cleanup:
    add rsp, 0x88
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbp
    pop rbx
    ret

# Fill only the reviewed 480x270 presentation rectangle.
clear_scene:
    # The palette pointer lives at caller rsp+0x20; CALL added eight bytes.
    mov rcx, [rsp + 0x28]
    mov r8d, [rcx]
    mov rdx, rbx
    mov r9d, 270
clear_row:
    mov rax, rdx
    mov ecx, 480
clear_pixel:
    mov [rax], r8d
    add rax, 4
    dec ecx
    jnz clear_pixel
    lea rdx, [rdx + rdi*4]
    dec r9d
    jnz clear_row
    ret

# Input: R8D/R9D logical x/y, R10 sprite indices, RCX selected palette.
# Every logical asset pixel becomes one 3x3 target pixel block.
draw_sprite:
    push rcx
    push r10
    mov eax, r9d
    imul eax, eax, 3
    imul rax, rdi
    imul r8d, r8d, 3
    add rax, r8
    shl rax, 2
    lea rdx, [rbx + rax]
    xor r8d, r8d                    # sprite row
sprite_row:
    xor r9d, r9d                    # vertical repeat
sprite_vertical:
    mov rax, rdx
    xor r11d, r11d                  # sprite column
sprite_column:
    lea r10d, [r11 + r8*8]
    mov rcx, [rsp]
    movzx r10d, byte ptr [rcx + r10]
    mov rcx, [rsp + 8]
    mov r10d, [rcx + r10*4]
    mov [rax], r10d
    mov [rax + 4], r10d
    mov [rax + 8], r10d
    add rax, 12
    inc r11d
    cmp r11d, 8
    jb sprite_column
    lea rdx, [rdx + rdi*4]
    inc r9d
    cmp r9d, 3
    jb sprite_vertical
    inc r8d
    cmp r8d, 8
    jb sprite_row
    add rsp, 16
    ret

.balign 8
gop_guid:
    .byte 0xde,0xa9,0x42,0x90,0xdc,0x23,0x38,0x4a
    .byte 0x96,0xfb,0x7a,0xde,0xd0,0x80,0x51,0x6a

# Index 0 background, 1 orange, 2 near-black, 3 white, 4 blue.
palette_rgb:
    .long 0x00261812, 0x003399ff, 0x00111111, 0x00ffffff, 0x00ff8833
palette_bgr:
    .long 0x00121826, 0x00ff9933, 0x00111111, 0x00ffffff, 0x003388ff

cat_sprite_zero:
    .byte 0,0,1,1,1,1,0,0, 0,1,1,1,1,1,1,0
    .byte 1,1,2,1,1,2,1,1, 1,1,1,1,1,1,1,1
    .byte 0,1,3,1,1,3,1,0, 0,0,1,1,1,1,0,0
    .byte 0,1,0,1,1,0,1,0, 1,0,0,1,1,0,0,1
cat_sprite_one:
    .byte 0,0,1,1,1,1,0,0, 0,1,1,1,1,1,1,0
    .byte 1,1,2,1,1,2,1,1, 1,1,1,1,1,1,1,1
    .byte 0,1,3,1,1,3,1,0, 0,0,1,1,1,1,0,0
    .byte 1,0,0,1,1,0,0,1, 0,1,0,1,1,0,1,0
ball_sprite:
    .byte 0,0,0,4,4,0,0,0, 0,4,4,4,4,4,4,0
    .byte 4,4,4,4,4,4,4,4, 4,3,3,4,4,4,2,4
    .byte 4,4,4,4,4,4,4,4, 0,4,4,4,4,4,4,0
    .byte 0,0,4,4,4,4,0,0, 0,0,0,4,4,0,0,0
blank_sprite:
    .fill 64, 1, 0

.balign 8
trace_data:
    # Patched with the exact 241 * 5-byte canonical hosted trace during review.
    .fill 1205, 1, 0xa5
