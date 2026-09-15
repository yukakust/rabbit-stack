.section __TEXT,__text,regular,pure_instructions
.globl _main
.p2align 2

_main:
    stp     x29, x30, [sp, #-16]!
    mov     x29, sp

    adrp    x0, L_prompt@PAGE
    add     x0, x0, L_prompt@PAGEOFF
    bl      _puts

    bl      _getchar

    cmp     w0, #114
    b.eq    L_red
    cmp     w0, #82
    b.eq    L_red
    cmp     w0, #98
    b.eq    L_blue
    b       L_invalid

L_red:
    adrp    x0, L_red_message@PAGE
    add     x0, x0, L_red_message@PAGEOFF
    bl      _puts
    mov     w0, #0
    b       L_return

L_blue:
    adrp    x0, L_blue_message@PAGE
    add     x0, x0, L_blue_message@PAGEOFF
    bl      _puts
    mov     w0, #0
    b       L_return

L_invalid:
    adrp    x0, L_invalid_message@PAGE
    add     x0, x0, L_invalid_message@PAGEOFF
    bl      _puts
    mov     w0, #2

L_return:
    ldp     x29, x30, [sp], #16
    ret

.section __TEXT,__cstring,cstring_literals
L_prompt:
    .asciz "Choose [r]ed or [b]lue:"
L_red_message:
    .asciz "Wake up, Neo."
L_blue_message:
    .asciz "The story ends."
L_invalid_message:
    .asciz "Invalid choice."

.subsections_via_symbols
