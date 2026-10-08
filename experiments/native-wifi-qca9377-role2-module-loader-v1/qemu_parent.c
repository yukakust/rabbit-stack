/* OVMF-only parent fixture: no immutable Dell bootstrap change. */
#include "loader.h"
#include "parent.h"
#include "fixture.h"
static RsnParentLease lease;static unsigned borrow_rejections;
static ModArtifact artifact;static ModLoader loader;static ModBudget budget;
static uint8_t memory[MOD_FILE_MAX],arena[131072] __attribute__((aligned(16)));
static struct {unsigned clock,entropy,send,key,protect,revoked;} provider;
static void say(const char*s){while(*s){__asm__ volatile("outb %0,%1"::"a"((uint8_t)*s++),"Nd"((uint16_t)0xe9));}}
static void hex_status(uint64_t v){const char*h="0123456789abcdef";for(int n=60;n>=0;n-=4){char q[2]={h[(v>>n)&15],0};say(q);}say("\n");}
static int EFIAPI clock_fixture(void*c,uint64_t*out){(void)c;provider.clock++;if(lease.busy){if(rsn_parent_close(&lease)!=0)borrow_rejections++;else return -1;}*out=1;return 0;}
static int EFIAPI entropy_fixture(void*c,uint8_t*out,size_t n){(void)c;provider.entropy++;for(size_t i=0;i<n;i++)out[i]=(uint8_t)(i+1);return 0;}
/* Fail closed: this lifecycle fixture has NO NIC, key install or port backend. */
static int EFIAPI send_fixture(void*c,uint64_t e,const uint8_t p[6],uint16_t proto,const uint8_t*b,size_t n){(void)c;(void)e;(void)p;(void)proto;(void)b;(void)n;provider.send++;return -1;}
static int EFIAPI key_fixture(void*c,uint64_t e,int a,const uint8_t*p,int i,int tx,const uint8_t*s,size_t sn,const uint8_t*k,size_t kn,unsigned f){(void)c;(void)e;(void)a;(void)p;(void)i;(void)tx;(void)s;(void)sn;(void)k;(void)kn;(void)f;provider.key++;return -1;}
static int EFIAPI protect_fixture(void*c,uint64_t e,const uint8_t p[6],int t,int kt){(void)c;(void)e;(void)p;(void)t;(void)kt;provider.protect++;return -1;}
static void EFIAPI state_fixture(void*c,uint64_t e,unsigned s){(void)c;(void)e;(void)s;}
static void EFIAPI revoke_fixture(void*c,uint64_t e,unsigned s){(void)c;(void)e;(void)s;provider.revoked++;}
#define CHECK(x,msg) do{if(!(x)){say("FAIL " msg "\n");return EFI_ERROR(3);}}while(0)
Status EFIAPI probe_entry(void*parent,SystemTable*st){
 ModEfi e;CHECK(!mod_efi_bind(&e,st,parent),"EFI BIND");
 budget.mapped=2224128;budget.epoch=7;budget.last_counter=1;for(unsigned i=0;i<32;i++)budget.parent_hash[i]=fixture_policy.parent_hash[i];
 CHECK(!mod_begin(&artifact,&fixture_policy,memory,sizeof memory),"BEGIN");
 for(unsigned i=0;i<FIXTURE_CHUNKS;i++)CHECK(!mod_accept(&artifact,fixture_frames[i],fixture_sizes[i]),"SIGNED CHUNK");say("REAL OWNER FIXTURE SIGNATURES VERIFIED ROLE2\n");
 int loaded=mod_load(&loader,&artifact,&budget,&e);if(loaded){say("LOAD STATUS ");hex_status(loader.status);say("LOAD STAGE ");hex_status(loader.stage);say(loader.quarantine?"QUARANTINED\n":"RETIRED\n");}CHECK(!loaded,"LOAD START PRIVATE OPTIONS");say("REAL UEFI LOAD START PRIVATE ROLE2 OPTIONS PASS\n");CHECK(!rsn_parent_bind(&lease,&loader),"PARENT BIND");CHECK(!rsn_parent_can_unload(&lease),"LIVE PARENT UNLOAD");
 RsnChildStatus status={.epoch=7};CHECK(!rsn_parent_call(&lease,RSN_CHILD_STATUS,&status)&&!status.opened&&!status.allocations,"UNINITIALIZED STATUS");
 static const uint8_t ssid[]="iPhone (9)",rsn[]={48,20,1,0,0,15,172,4,1,0,0,15,172,4,1,0,0,15,172,2,0,0};
 static uint8_t pmk[32];RsnChildOpen open={0};open.epoch=7;open.rx_floor=1;open.arena=arena;open.arena_bytes=sizeof arena;open.ssid=ssid;open.ssid_bytes=10;open.rsn=rsn;open.rsn_bytes=sizeof rsn;open.pmk=pmk;open.pmk_bytes=32;open.auth_timeout_us=5000000;
 open.peer[0]=2;open.peer[5]=1;open.own[0]=2;open.own[5]=2;
 open.providers.context=&provider;open.providers.context_bytes=sizeof provider;open.providers.source_sha256[0]=1;open.providers.monotonic_us=clock_fixture;open.providers.wall_us=clock_fixture;open.providers.random=entropy_fixture;open.providers.send_owned=send_fixture;open.providers.install_confirmed=key_fixture;open.providers.protect_confirmed=protect_fixture;open.providers.state=state_fixture;open.providers.revoked=revoke_fixture;
 RsnChildOpen bad=open;bad.epoch=8;CHECK(rsn_parent_call(&lease,RSN_CHILD_OPEN,&bad)!=0,"STALE OPEN ACCEPTED");bad=open;bad.pmk=arena;CHECK(rsn_parent_call(&lease,RSN_CHILD_OPEN,&bad)!=0,"ARENA PMK ALIAS ACCEPTED");bad=open;bad.providers.context=&bad;bad.providers.context_bytes=sizeof bad;CHECK(rsn_parent_call(&lease,RSN_CHILD_OPEN,&bad)!=0,"TRANSIENT PROVIDER ACCEPTED");
 CHECK(!rsn_parent_call(&lease,RSN_CHILD_OPEN,&open),"MATURE OPEN");status=(RsnChildStatus){.epoch=7};CHECK(!rsn_parent_call(&lease,RSN_CHILD_STATUS,&status)&&status.opened&&status.allocations,"MATURE OPEN STATUS");
 CHECK(loader.image->unload&&loader.image->unload(loader.handle)!=0,"OPEN UNLOAD ALLOWED");say("REAL MATURE SUPPLICANT OPEN AND UNLOAD REFUSAL PASS SYNTHETIC PROVIDERS\n");
 CHECK(!loader.registration.dispatch(0,0),"CLOSE");status=(RsnChildStatus){.epoch=7};CHECK(!rsn_parent_call(&lease,RSN_CHILD_STATUS,&status)&&!status.opened&&!status.borrowed&&!status.allocations&&!status.timers,"CLOSE OWNERS");
 for(unsigned i=0;i<sizeof arena;i++)CHECK(!arena[i],"ARENA WIPE");
 CHECK(!provider.send&&!provider.key&&!provider.protect,"FALSE NIC BACKEND USE");
 CHECK(!rsn_parent_close(&lease)&&rsn_parent_can_unload(&lease)&&!artifact.memory&&budget.mapped==2224128,"UNLOAD BEFORE WIPE");CHECK(borrow_rejections>0,"NO ACTUAL PROVIDER BORROW CASE");for(unsigned i=0;i<sizeof memory;i++)CHECK(!memory[i],"ARTIFACT WIPE");
 say("MODULE CHILD QEMU PASS ROLE2 NO PHYSICAL NIC ENTROPY AUTH CLAIM\n");return 0;
}
