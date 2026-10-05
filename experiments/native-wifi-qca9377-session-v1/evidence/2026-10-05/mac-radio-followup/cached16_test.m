#define main actual_sender_main
#include "cached16_sender.m"
#undef main
#include <assert.h>
@interface FakeStatus:NSObject
@property NSData*value;
@end
@implementation FakeStatus
@end
@interface FakePeer:NSObject
@property NSString*checkpoint;
@property NSData*packet;
@property unsigned writes;
@property unsigned offset;
@end
@implementation FakePeer
- (NSUUID*)identifier{return [[NSUUID alloc]initWithUUIDString:@"00000000-0000-0000-0000-000000000001"];}
- (NSUInteger)maximumWriteValueLengthForType:(CBCharacteristicWriteType)t{assert(t==CBCharacteristicWriteWithResponse);return 512;}
- (void)writeValue:(NSData*)value forCharacteristic:(CBCharacteristic*)c type:(CBCharacteristicWriteType)t{
 (void)c;assert(t==CBCharacteristicWriteWithResponse);
 NSDictionary*d=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:self.checkpoint] options:0 error:nil];
 assert([d[@"attempted"]intValue]==1);assert(value.length>=5&&value.length<=20);
 const uint8_t*b=value.bytes;unsigned at=u32(b);assert(at==self.offset);
 assert(!memcmp(b+4,(const uint8_t*)self.packet.bytes+at,value.length-4));self.offset+=(unsigned)value.length-4;self.writes++;
}
@end
@interface CountSender:Sender
@property unsigned saves;
@end
@implementation CountSender
- (void)save{self.saves++;[super save];}
@end
@interface FailSender:Sender
@end
@implementation FailSender
- (void)save{@throw [NSException exceptionWithName:@"expected-persist-failure" reason:@"fixture" userInfo:nil];}
@end
static NSDictionary*record(NSString*p){return [NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:p] options:0 error:nil];}
int main(int argc,const char**argv){@autoreleasepool{
 assert(argc==3);NSString*packet=[NSString stringWithUTF8String:argv[1]],*checkpoint=[NSString stringWithUTF8String:argv[2]];
 [[NSFileManager defaultManager]removeItemAtPath:checkpoint error:nil];
 FakePeer*peer=[FakePeer new];peer.checkpoint=checkpoint;peer.packet=[NSData dataWithContentsOfFile:packet];assert(peer.packet);
 CountSender*s=[CountSender new];assert([s configure:packet checkpoint:checkpoint sending:YES]);s.peer=(CBPeripheral*)peer;s.data=(CBCharacteristic*)[NSObject new];
 for(unsigned i=0;i<32;i++){s.writing=NO;[s writeData];}
 assert(peer.writes==32&&peer.offset==512&&s.saves==1&&[record(checkpoint)[@"floor"]intValue]==0);
 uint8_t raw[64]={0},digest[32];memcpy(raw,"RFCS0001",8);put(raw+8,1);put(raw+16,(uint32_t)peer.packet.length);put(raw+20,512);rabbit_sha256(digest,peer.packet.bytes,peer.packet.length);memcpy(raw+24,digest,32);
 FakeStatus*status=[FakeStatus new];status.value=[NSData dataWithBytes:raw length:64];s.status=(CBCharacteristic*)status;s.writing=NO;s.sending=NO;
 [s peripheral:(CBPeripheral*)peer didUpdateValueForCharacteristic:(CBCharacteristic*)status error:nil];
 assert(s.saves==2&&[record(checkpoint)[@"floor"]intValue]==512);
 s.sending=YES;s.finished=NO;[s writeData];assert(peer.writes==33&&s.saves==2&&[record(checkpoint)[@"floor"]intValue]==512);
 [[NSFileManager defaultManager]removeItemAtPath:checkpoint error:nil];
 FailSender*f=[FailSender new];assert([f configure:packet checkpoint:checkpoint sending:YES]);f.peer=(CBPeripheral*)peer;f.data=(CBCharacteristic*)[NSObject new];unsigned before=peer.writes;BOOL failed=NO;
 @try{[f writeData];}@catch(NSException*e){assert([e.name isEqualToString:@"expected-persist-failure"]);failed=YES;}
 assert(failed&&peer.writes==before&&![[NSFileManager defaultManager]fileExistsAtPath:checkpoint]);
 puts("DURABILITY BEFORE FIRST WRITE; ACK DOES NOT PROMOTE FLOOR; RECEIPT PERSISTS FLOOR; SAVE FAILURE BLOCKS RADIO PASS; NO BLUETOOTH MANAGER");return 0;
}}
