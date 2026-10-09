#import <Foundation/Foundation.h>
#include <stdlib.h>
#include <assert.h>
static _Noreturn void hostExit(int code){@throw [NSException exceptionWithName:@"Exit" reason:[NSString stringWithFormat:@"%d",code] userInfo:nil];}
#define exit hostExit
#define main module_sender_program_main
#include "sender.m"
#undef main
#undef exit
@interface FakeModulePeer:NSObject
@property NSMutableArray*actions;
@end
@implementation FakeModulePeer
- (NSUInteger)maximumWriteValueLengthForType:(CBCharacteristicWriteType)t{(void)t;return 244;}
- (void)writeValue:(NSData*)b forCharacteristic:(CBCharacteristic*)c type:(CBCharacteristicWriteType)t{(void)c;assert(t==CBCharacteristicWriteWithResponse);[self.actions addObject:b];}
- (void)readValueForCharacteristic:(CBCharacteristic*)c{(void)c;[self.actions addObject:@"read"];}
@end
@interface TestModuleSender:ModuleSender
@end
@implementation TestModuleSender
- (void)fail:(NSString*)s{@throw [NSException exceptionWithName:@"Stopped" reason:s userInfo:nil];}
@end
static unsigned checks;
static CBMutableCharacteristic*character(unsigned x,NSData*v){return [[CBMutableCharacteristic alloc]initWithType:[CBUUID UUIDWithString:[NSString stringWithFormat:@"52414242-4954-4649-8000-0000000000%02X",x]] properties:CBCharacteristicPropertyRead|CBCharacteristicPropertyWrite value:v permissions:CBAttributePermissionsReadable|CBAttributePermissionsWriteable];}
static TestModuleSender*make(NSString*dir){
 TestModuleSender*s=[TestModuleSender new];NSMutableData*b=[NSMutableData dataWithLength:1000];memcpy(b.mutableBytes,"RABRSN01",8);w32((uint8_t*)b.mutableBytes+196,2);w32((uint8_t*)b.mutableBytes+200,1);s.chunk=b;s.session=[@"12345678" dataUsingEncoding:NSUTF8StringEncoding];uint8_t h[32];CC_SHA256(b.bytes,(CC_LONG)b.length,h);s.digest=[NSData dataWithBytes:h length:32];s.epoch=66;s.phase=1;s.receiptPath=[dir stringByAppendingPathComponent:@"receipt.bin"];FakeModulePeer*p=[FakeModulePeer new];p.actions=[NSMutableArray array];s.peer=(CBPeripheral*)p;s.status=character(0x24,nil);s.control=character(0x22,nil);s.data=character(0x23,nil);return s;
}
static NSMutableData*raw(TestModuleSender*s,unsigned state){NSMutableData*d=[NSMutableData dataWithLength:80];uint8_t*r=d.mutableBytes;memcpy(r,"QMT00001",8);r[8]=66;w32(r+16,state);if(state){w32(r+24,1000);w32(r+28,state==1?500:1000);w32(r+32,state==3?1:0);memcpy(r+40,s.session.bytes,8);memcpy(r+48,s.digest.bytes,32);}return d;}
static void update(TestModuleSender*s,NSData*d){((CBMutableCharacteristic*)s.status).value=d;[s peripheral:s.peer didUpdateValueForCharacteristic:s.status error:nil];}
static void stop(void(^f)(void)){@try{f();assert(!"must stop");}@catch(NSException*e){assert([e.name isEqual:@"Stopped"]);checks++;}}
int main(int argc,const char**argv){@autoreleasepool{
 assert(argc==2);NSString*dir=@(argv[1]);[[NSFileManager defaultManager]createDirectoryAtPath:dir withIntermediateDirectories:YES attributes:nil error:nil];
 TestModuleSender*s=make(dir);update(s,raw(s,0));assert(s.phase==2&&[(NSData*)((FakeModulePeer*)s.peer).actions.lastObject length]==45);checks++;
 s=make(dir);update(s,raw(s,1));assert(s.phase==3&&s.offset==500&&s.confirmed==500);NSData*p=((FakeModulePeer*)s.peer).actions.lastObject;assert(p.length==244&&r32((const uint8_t*)p.bytes+9)==500);checks++;
 s=make(dir);update(s,raw(s,2));assert(s.phase==6&&s.confirmed==1000);checks++;
 s=make(dir);@try{update(s,raw(s,3));assert(!"accepted exit");}@catch(NSException*e){assert([e.name isEqual:@"Exit"]&&[e.reason isEqual:@"0"]&&s.finished);checks++;}
 for(unsigned i=0;i<80;i++){
  if(i==32||i==33||i==34)continue; /* arbitrary nonnegative callback result */
  s=make(dir);NSMutableData*d=raw(s,3);((uint8_t*)d.mutableBytes)[i]^=128;
  stop(^{update(s,d);});assert(((FakeModulePeer*)s.peer).actions.count==0);checks++;
 }
 s=make(dir);s.phase=5;s.confirmed=800;stop(^{update(s,raw(s,1));});
 s=make(dir);s.receiptPath=[dir stringByAppendingPathComponent:@"missing/receipt"];stop(^{update(s,raw(s,1));});assert(((FakeModulePeer*)s.peer).actions.count==0);checks++;
 s=make(dir);CBCharacteristic*wrong=character(0x23,raw(s,1));stop(^{[s peripheral:s.peer didUpdateValueForCharacteristic:wrong error:nil];});
 s=make(dir);stop(^{[s peripheral:s.peer didWriteValueForCharacteristic:s.data error:nil];});
 s=make(dir);stop(^{[s centralManager:(CBCentralManager*)[NSObject new] didDisconnectPeripheral:s.peer error:nil];});
 s=make(dir);NSMutableData*prior=raw(s,3);((uint8_t*)prior.mutableBytes)[40]^=1;s.previous=prior;update(s,prior);assert(s.phase==2&&[(NSData*)((FakeModulePeer*)s.peer).actions.lastObject length]==45);checks++;
 s=make(dir);NSMutableData*foreign=raw(s,3);((uint8_t*)foreign.mutableBytes)[40]^=1;stop(^{update(s,foreign);});
 s=make(dir);NSMutableData*old=raw(s,1);((uint8_t*)old.mutableBytes)[40]^=1;s.previous=old;stop(^{update(s,old);});
 printf("PASS %u actual host callback checks; real Bluetooth manager=0 writes=0 secrets=0\n",checks);return 0;
}}
