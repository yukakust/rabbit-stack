/* Platform-only symbol directives; upstream instructions are not changed. */
#define DEFINE_COMPILERRT_FUNCTION(name) .globl name; name:
#define END_COMPILERRT_FUNCTION(name)
