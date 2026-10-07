#ifndef QCA_MINIMAL_ALLOCA_H
#define QCA_MINIMAL_ALLOCA_H
#define alloca(n) __builtin_alloca(n)
#endif
