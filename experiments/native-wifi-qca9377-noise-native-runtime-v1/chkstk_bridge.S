#include "reference/x86_64/chkstk.S"
/* MS-x64 spelling aliases exact compiler-rt probe; no empty fallback. */
.globl __chkstk
.set __chkstk,___chkstk_ms
#ifndef _WIN32
.section .note.GNU-stack,"",@progbits
#endif
