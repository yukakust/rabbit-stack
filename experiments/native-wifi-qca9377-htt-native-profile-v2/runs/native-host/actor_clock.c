/* Target-only elapsed milliseconds. Calibrated against UEFI Stall, not frames.
 * No clock or display access during candidate init/trial. */
static uint64_t actor_epoch,actor_cycles_ms;
static uint64_t actor_tsc(void){uint32_t lo,hi;__asm__ volatile("lfence; rdtsc":"=a"(lo),"=d"(hi)::"memory");return ((uint64_t)hi<<32)|lo;}
static int city_clock_bind(SystemTable*st){
 typedef Status(EFIAPI *ClockStall)(uint64_t);
 uint64_t begin=actor_tsc();if(((ClockStall)service(st,248))(50000))return 1;
 uint64_t middle=actor_tsc();if(((ClockStall)service(st,248))(50000))return 1;
 uint64_t end=actor_tsc(),a=(middle-begin)/50,b=(end-middle)/50;
 if(a<100000||a>20000000||b<100000||b>20000000||(a>b?a-b:b-a)>(a+b)/20)return 1;
 actor_cycles_ms=(a+b)/2;actor_epoch=end;return 0;
}
static uint32_t city_clock_ms(void){return actor_cycles_ms?(uint32_t)((actor_tsc()-actor_epoch)/actor_cycles_ms):0;}
