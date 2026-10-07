/* Aggregate-zero lowering still calls global memset after source renaming.
 * Native54 baseline has no such symbol. Delegate to the actual tested shim. */
#include <stddef.h>
void*qca_runtime_memset(void*,int,size_t);
void*memset(void*p,int x,size_t n){return qca_runtime_memset(p,x,n);}
