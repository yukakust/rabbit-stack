#ifndef RABBIT_ASSERT_DECL_H
#define RABBIT_ASSERT_DECL_H
void rabbit_tls_assert_failure(void);
#ifdef NDEBUG
#define assert(condition) ((void)0)
#else
#define assert(condition) ((condition)?(void)0:rabbit_tls_assert_failure())
#endif
#endif
