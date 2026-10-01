/* Explicit emulator-only radio substitute. Exercises the actual supervisor
 * dispatcher and resident drivers, NOT a physical Bluetooth success claim. */
#include "scene_abi.h"
#include "test_frames.h"
int rabbit_test_snapshot(uint8_t*,uint32_t*);
const uint8_t *rabbit_test_base(void);
uint32_t rabbit_test_pixel(unsigned);
void EFIAPI rabbit_scene_shutdown(void);
static uint8_t before[SNAPSHOT_MAX],after[SNAPSHOT_MAX],ack[16];
static uint32_t le32(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static int same(const uint8_t*a,const uint8_t*b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return !x;}
static void say(const char*s){for(unsigned i=0;s[i];i++)__asm__ volatile("outb %0,%1"::"a"((uint8_t)s[i]),"Nd"((uint16_t)0xe9));__asm__ volatile("outb %0,%1"::"a"((uint8_t)'\n'),"Nd"((uint16_t)0xe9));}
static int receive(const uint8_t*p,size_t n,SystemTable*st){int result=0;for(size_t i=0;i<n;i+=16)result=rabbit_package_frame(p+i,st);rabbit_receipt_write(ack);return result;}
static int check_snapshot(uint32_t old_tick,uint32_t counter){
 uint32_t n=0;if(rabbit_test_snapshot(after,&n))return 1;
 return n!=32+sizeof(test_world)+32||le32(after+8)!=old_tick+1||le32(after+12)!=counter||le32(after+16)!=sizeof(test_world)||!same(after+32,test_world,sizeof(test_world));
}
Status EFIAPI rabbit_entry(void*h,SystemTable*st){
 rabbit_supervisor_entry(h,st);
 if(rabbit_scene_bootstrap(st)){say("FAIL BOOTSTRAP");return EFI_ERROR(2);}
 say("SCENE BASELINE DRIVER LOADED; QEMU RADIO SUBSTITUTE ONLY");
 if(receive(frames_world,sizeof(frames_world),st)!=4||ack[2]!=0x11){say("FAIL WORLD");return EFI_ERROR(2);}
 for(unsigned i=0;i<120;i++)if(rabbit_scene_tick(st)){say("FAIL TICK");return EFI_ERROR(2);}
 uint32_t n=0;if(rabbit_test_snapshot(before,&n)){say("FAIL SNAPSHOT");return EFI_ERROR(2);}
 uint32_t tick=le32(before+8);
 /* Stage a prefix, lose its ACK and retry it while the world keeps moving. */
 if(receive(frames_prefix,sizeof(frames_prefix),st)!=4||ack[2]!=0x22||
    receive(frames_prefix,sizeof(frames_prefix),st)!=4||ack[2]!=0x22){say("FAIL PREFIX RETRY");return EFI_ERROR(2);}
 if(rabbit_scene_tick(st)){say("FAIL TICK WHILE STAGING");return EFI_ERROR(2);}tick++;
 if(receive(frames_a,sizeof(frames_a),st)!=4||ack[2]!=0x21||check_snapshot(tick,1)||!same(rabbit_test_base(),module_a_hash,32)||rabbit_test_pixel(269*480)!=0x3366ff){say("FAIL NATIVE A");return EFI_ERROR(2);}
 say("SIGNED ENGINE A COMMITTED; LIVE WORLD AND COUNTER RETAINED; STAGING DID NOT FREEZE TIME");
 if(rabbit_test_snapshot(before,&n)){say("FAIL SNAPSHOT A");return EFI_ERROR(2);}
 if(receive(frames_a,sizeof(frames_a),st)!=4||ack[2]!=0x21){say("FAIL DUPLICATE ACK");return EFI_ERROR(2);}
 uint32_t m=0;if(rabbit_test_snapshot(after,&m)||m!=n||!same(before,after,n)){say("FAIL REPEATED EFFECT");return EFI_ERROR(2);}
 say("LOST FINAL RECEIPT RETRY DID NOT EXECUTE AGAIN");tick=le32(before+8);
 if(receive(frames_b,sizeof(frames_b),st)!=4||ack[2]!=0x21||check_snapshot(tick,1)||!same(rabbit_test_base(),module_b_hash,32)){say("FAIL NATIVE B");return EFI_ERROR(2);}
 say("SIGNED ENGINE B COMMITTED IN SAME BOOT; PREVIOUS DRIVER UNLOADED");
 if(rabbit_test_snapshot(before,&n)){say("FAIL SNAPSHOT B");return EFI_ERROR(2);}
 if(receive(frames_bad,sizeof(frames_bad),st)!=4||ack[2]!=0x23||rabbit_test_snapshot(after,&m)||m!=n||!same(before,after,n)||!same(rabbit_test_base(),module_b_hash,32)){say("FAIL HEALTH RETENTION");return EFI_ERROR(2);}
 say("FAILED NATIVE HEALTH RETAINED EXACT OLD LIVE SCENE");
 if(receive(frames_tampered,sizeof(frames_tampered),st)!=4||ack[2]!=0x23||rabbit_test_snapshot(after,&m)||m!=n||!same(before,after,n)){say("FAIL SIGNATURE RETENTION");return EFI_ERROR(2);}
 say("TAMPERED OWNER SIGNATURE REJECTED; SCENE UNCHANGED");
 say("WIRELESS DISPATCH AND SCENE NATIVE INTEGRATION PASS; NO PHYSICAL BLUETOOTH CLAIM");
 typedef Status(EFIAPI *Stall)(uint64_t);
 for(;;){if(rabbit_scene_tick(st)){say("FAIL CONTINUED SCENE");return EFI_ERROR(2);}((Stall)service(st,248))(33000);}
}
