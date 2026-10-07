.text
.globl qca_probe_call
qca_probe_call:
 mov %rsp,(%rsi)
 mov $0x1234567812345678,%rcx
 mov %rdi,%rax
 call __chkstk
 mov %rsp,8(%rsi)
 mov %rcx,16(%rsi)
 ret
.globl qca_run_stack
qca_run_stack:
 mov %rsp,%r11
 mov %rdx,%rsp
 and $-16,%rsp
 push %r11
 sub $8,%rsp
 call qca_probe_call
 add $8,%rsp
 pop %rsp
 ret
.section .note.GNU-stack,"",@progbits
