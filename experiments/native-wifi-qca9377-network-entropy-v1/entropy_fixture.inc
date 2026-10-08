extern unsigned int rabbit_network_rand(void);
static int entropy_first(const char*mode){
 struct rabbit_network_ops o={output,rng,0};struct rabbit_network_authorization a={64,1,1,1};
 if(!strcmp(mode,"zero")){
  rng_mode=2;assert(!rabbit_network_start(&a,&o,mac)&&sends&&rabbit_network_epoch()==1);rabbit_network_revoke();
  puts("PASS zero-valued successful entropy is valid; no fallback substituted");return 0;
 }
 assert(!strcmp(mode,"failure"));rng_mode=1;
 assert(rabbit_network_start(&a,&o,mac)==-1&&!sends&&!rabbit_network_epoch()&&!rabbit_network_ip());
 rng_mode=0;assert(rabbit_network_start(&a,&o,mac)==-1&&!sends);
 a.association_epoch=2;assert(!rabbit_network_start(&a,&o,mac)&&sends);rabbit_network_revoke();
 puts("PASS initial RNG failure; no Ethernet output/epoch/IP; failed epoch never retried");return 0;
}
static void entropy_late(void){
 struct rabbit_network_ops o={output,rng,0};struct rabbit_network_authorization a={64,3,1,1};
 assert(!rabbit_network_start(&a,&o,mac));size_t n=reply(2,0,0);assert(!rabbit_network_input(server,n,3));n=reply(5,0,0);assert(!rabbit_network_input(server,n,3));ticks(10000);assert(rabbit_network_ip());
 uint8_t arena[RABBIT_WAN_RX_CAP];assert(!rabbit_wan_open(3,"10.0.0.1",10000,arena,sizeof arena));unsigned before=sends;
 rng_mode=1;(void)rabbit_network_rand();assert(!rabbit_network_epoch()&&!rabbit_network_ip());
 assert(rabbit_wan_poll(3)==-1&&rabbit_network_tick(0)==-1&&sends==before);
 for(unsigned i=0;i<sizeof arena;i++)assert(!arena[i]);
 assert(rabbit_network_input(server,n,3)==-1&&sends==before);
 rng_mode=0;assert(rabbit_network_start(&a,&o,mac)==-1);
 a.association_epoch=4;assert(!rabbit_network_start(&a,&o,mac));rabbit_network_revoke();
 checks+=12;puts("PASS late RNG failure revokes IP/epoch/TCP, wipes BIO arena, blocks same epoch and transmission");
}
