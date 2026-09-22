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
    sub rsp, 0x68

    mov rsi, [rdx + 0x30]
    mov rbp, [rdx + 0x60]
    lea rcx, [rip + gop_guid]
    xor edx, edx
    lea r8, [rsp + 0x40]
    mov rax, [rbp + 0x140]
    call rax
    test rax, rax
    jnz cleanup

    mov rax, [rsp + 0x40]
    mov rax, [rax + 0x18]
    mov rbx, [rax + 0x18]
    mov rdx, [rax + 0x08]
    mov r14d, [rdx + 0x04]
    mov r15d, [rdx + 0x08]
    mov edi, [rdx + 0x20]
    cmp r14d, 164
    jb unsupported
    cmp r15d, 164
    jb unsupported
    cmp dword ptr [rdx + 0x0c], 0
    je rgb
    cmp dword ptr [rdx + 0x0c], 1
    je bgr
    jmp unsupported
rgb:
    mov dword ptr [rsp + 0x20], 0x0000d4ff
    jmp color_ready
bgr:
    mov dword ptr [rsp + 0x20], 0x00ffd400
color_ready:
    mov eax, [rsp + 0x20]
    mov [rsp + 0x24], eax
    mov dword ptr [rsp + 0x2c], 3
    mov dword ptr [rsp + 0x30], 0
    mov r12d, 100
    mov r13d, 100

    mov rax, rdi
    imul rax, r15
    mov rcx, rbx
    xor edx, edx
clear_loop:
    mov [rcx], edx
    add rcx, 4
    dec rax
    jnz clear_loop
    call draw_player

read_key:
    mov rcx, rsi
    lea rdx, [rsp + 0x28]
    mov rax, [rcx + 8]
    call rax
    test rax, rax
    jnz read_key
    movzx eax, word ptr [rsp + 0x28]
    cmp eax, 23
    je success
    movzx ecx, word ptr [rsp + 0x2a]
    cmp ecx, 32
    je jump
    cmp ecx, 90
    je leave_stone
    cmp ecx, 122
    je leave_stone
    cmp eax, 1
    jb read_key
    cmp eax, 4
    ja read_key
    mov [rsp + 0x2c], eax
    mov r8d, r12d
    mov r9d, r13d
    cmp eax, 1
    je candidate_up
    cmp eax, 2
    je candidate_down
    cmp eax, 3
    je candidate_right
candidate_left:
    cmp r8d, 16
    jb left_zero
    sub r8d, 16
    jmp try_candidate
left_zero:
    xor r8d, r8d
    jmp try_candidate
candidate_up:
    cmp r9d, 16
    jb up_zero
    sub r9d, 16
    jmp try_candidate
up_zero:
    xor r9d, r9d
    jmp try_candidate
candidate_down:
    mov ecx, r15d
    sub ecx, 64
    add r9d, 16
    cmp r9d, ecx
    cmova r9d, ecx
    jmp try_candidate
candidate_right:
    mov ecx, r14d
    sub ecx, 64
    add r8d, 16
    cmp r8d, ecx
    cmova r8d, ecx
try_candidate:
    call collides
    test eax, eax
    jnz read_key
    mov [rsp + 0x44], r8d
    mov [rsp + 0x48], r9d
    call erase_player
    mov r12d, [rsp + 0x44]
    mov r13d, [rsp + 0x48]
    call draw_player
    jmp read_key

jump:
    call erase_player
    call draw_stone
    mov r8d, r12d
    mov r9d, r13d
    cmp r9d, 32
    jb jump_top
    sub r9d, 32
    jmp jump_draw
jump_top:
    xor r9d, r9d
jump_draw:
    mov eax, [rsp + 0x20]
    mov r10d, 64
    mov r11d, 64
    call draw_rect
    mov ecx, 120000
    mov rax, [rbp + 0xf8]
    call rax
    mov r8d, r12d
    mov r9d, r13d
    cmp r9d, 32
    jb jump_erase_top
    sub r9d, 32
    jmp jump_erase
jump_erase_top:
    xor r9d, r9d
jump_erase:
    xor eax, eax
    mov r10d, 64
    mov r11d, 64
    call draw_rect
    call draw_stone
    call draw_player
    jmp read_key

leave_stone:
    mov eax, [rsp + 0x2c]
    mov r8d, r12d
    mov r9d, r13d
    cmp eax, 1
    je stone_up
    cmp eax, 2
    je stone_down
    cmp eax, 3
    je stone_right
stone_left:
    cmp r8d, 16
    jb read_key
    sub r8d, 16
    jmp place_left
stone_up:
    cmp r9d, 16
    jb read_key
    sub r9d, 16
    jmp place_up
stone_down:
    mov ecx, r15d
    sub ecx, 64
    cmp r9d, ecx
    jae read_key
    add r9d, 16
    jmp place_down
stone_right:
    mov ecx, r14d
    sub ecx, 64
    cmp r8d, ecx
    jae read_key
    add r8d, 16
place_right:
    mov edx, r12d
    mov ecx, r13d
    add ecx, 24
    jmp commit_stone
place_left:
    mov edx, r12d
    add edx, 48
    mov ecx, r13d
    add ecx, 24
    jmp commit_stone
place_up:
    mov edx, r12d
    add edx, 24
    mov ecx, r13d
    add ecx, 48
    jmp commit_stone
place_down:
    mov edx, r12d
    add edx, 24
    mov ecx, r13d
commit_stone:
    mov [rsp + 0x3c], edx
    mov [rsp + 0x40], ecx
    mov [rsp + 0x44], r8d
    mov [rsp + 0x48], r9d
    call erase_player
    call erase_stone
    mov edx, [rsp + 0x3c]
    mov ecx, [rsp + 0x40]
    mov [rsp + 0x34], edx
    mov [rsp + 0x38], ecx
    mov dword ptr [rsp + 0x30], 1
    mov r12d, [rsp + 0x44]
    mov r13d, [rsp + 0x48]
    call draw_stone
    call draw_player
    jmp read_key

success:
    xor eax, eax
    jmp cleanup
unsupported:
    movabs rax, 0x8000000000000003
cleanup:
    add rsp, 0x68
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbp
    pop rbx
    ret

draw_player:
    mov eax, [rsp + 0x28]
    mov r8d, r12d
    mov r9d, r13d
    mov r10d, 64
    mov r11d, 64
    jmp draw_rect
erase_player:
    xor eax, eax
    mov r8d, r12d
    mov r9d, r13d
    mov r10d, 64
    mov r11d, 64
    jmp draw_rect
draw_stone:
    cmp dword ptr [rsp + 0x38], 0
    je draw_none
    mov eax, [rsp + 0x2c]
    mov r8d, [rsp + 0x3c]
    mov r9d, [rsp + 0x40]
    mov r10d, 16
    mov r11d, 16
    jmp draw_rect
erase_stone:
    cmp dword ptr [rsp + 0x38], 0
    je draw_none
    xor eax, eax
    mov r8d, [rsp + 0x3c]
    mov r9d, [rsp + 0x40]
    mov r10d, 16
    mov r11d, 16
    jmp draw_rect
draw_none:
    ret

collides:
    xor eax, eax
    cmp dword ptr [rsp + 0x38], 0
    je no_collision
    mov edx, r8d
    add edx, 64
    cmp edx, [rsp + 0x3c]
    jbe no_collision
    mov edx, [rsp + 0x3c]
    add edx, 16
    cmp edx, r8d
    jbe no_collision
    mov edx, r9d
    add edx, 64
    cmp edx, [rsp + 0x40]
    jbe no_collision
    mov edx, [rsp + 0x40]
    add edx, 16
    cmp edx, r9d
    jbe no_collision
    mov eax, 1
no_collision:
    ret

draw_rect:
    push rax
    push r10
    push r11
    mov eax, r9d
    imul rax, rdi
    mov ecx, r8d
    add rax, rcx
    shl rax, 2
    lea rdx, [rbx + rax]
    pop r11
    pop r10
    pop rax
    mov r8d, eax
draw_row:
    mov rcx, rdx
    mov r9d, r10d
draw_pixel:
    mov [rcx], r8d
    add rcx, 4
    dec r9d
    jnz draw_pixel
    lea rdx, [rdx + rdi*4]
    dec r11d
    jnz draw_row
    ret

.balign 8
gop_guid:
    .byte 0xde,0xa9,0x42,0x90,0xdc,0x23,0x38,0x4a
    .byte 0x96,0xfb,0x7a,0xde,0xd0,0x80,0x51,0x6a
