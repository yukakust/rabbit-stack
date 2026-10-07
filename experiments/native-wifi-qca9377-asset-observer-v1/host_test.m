/* HOST callback harness; fake peer only, NO CBCentralManager or native IO. */
#define main fixture_sender_main
#include "sender.m"
#undef main
#include <assert.h>
@interface FakePeer:NSObject
@property NSUUID*identifier;
@property NSMutableArray<NSString*>*calls;
@property unsigned writes;
@end
@implementation FakePeer
- (NSUInteger)maximumWriteValueLengthForType:(CBCharacteristicWriteType)t{(void)t;return 512;}
- (void)readValueForCharacteristic:(CBCharacteristic*)c{[self.calls addObject:[@"read:" stringByAppendingString:c.UUID.UUIDString]];}
- (void)writeValue:(NSData*)v forCharacteristic:(CBCharacteristic*)c type:(CBCharacteristicWriteType)t{(void)v;(void)t;self.writes++;[self.calls addObject:[@"write:" stringByAppendingString:c.UUID.UUIDString]];}
@end
@interface FakeCentral:NSObject
@end
@implementation FakeCentral
- (void)cancelPeripheralConnection:(CBPeripheral*)p{(void)p;}
@end
@interface TestSender:Sender
@property NSMutableArray<NSString*>*trace;
@property unsigned nextCount;
- (uint32_t)floor;
- (QfsExpected)fixtureExpected;
@end
@implementation TestSender
- (void)fail:(NSString*)reason{ao_stop(&sequence);@throw [NSException exceptionWithName:@"Stopped" reason:reason userInfo:nil];}
- (void)save{[super save];[self.trace addObject:@"saved-real-QFS-floor"];}
- (uint32_t)floor{return progress.floor;}
- (QfsExpected)fixtureExpected{return expected;}
- (void)diagnostic:(NSString*)stage error:(NSError*)e raw:(NSData*)raw{[super diagnostic:stage error:e raw:raw];[self.trace addObject:@"diagnostic-durable"];}
- (void)nextActionAfterDiagnostic{self.nextCount++;[self.trace addObject:@"next-action"];[super nextActionAfterDiagnostic];}
@end
static unsigned checks;
static CBMutableCharacteristic*character(NSString*u,NSData*v,BOOL writing){return [[CBMutableCharacteristic alloc]initWithType:[CBUUID UUIDWithString:u] properties:writing?CBCharacteristicPropertyWrite:CBCharacteristicPropertyRead value:v permissions:writing?CBAttributePermissionsWriteable:CBAttributePermissionsReadable];}
static TestSender*sender(NSString*directory,BOOL sending){
 NSMutableData*packet=[NSMutableData dataWithLength:736];uint8_t*b=packet.mutableBytes;memcpy(b,"RABFW001",8);put(b+104,512);put(b+108,0);put(b+112,512);put(b+116,65536);put(b+120,59);
 NSString*path=[directory stringByAppendingPathComponent:@"dummy-layout-packet.bin"];assert([packet writeToFile:path atomically:YES]);
 TestSender*s=[TestSender new];s.trace=[NSMutableArray array];s.prefixLog=[directory stringByAppendingPathComponent:@"diagnostic.jsonl"];
 assert([s configure:path checkpoint:[directory stringByAppendingPathComponent:@"checkpoint.json"] sending:sending]);
 FakePeer*p=[FakePeer new];p.identifier=[[NSUUID alloc]initWithUUIDString:@"F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF"];p.calls=[NSMutableArray array];s.peer=(CBPeripheral*)p;s.central=(CBCentralManager*)[FakeCentral new];
 s.control=character(controlUUID,nil,YES);s.data=character(dataUUID,nil,YES);
 QfsExpected e=[s fixtureExpected];uint8_t raw[64]={0};memcpy(raw,"RFCS0001",8);put(raw+8,1);put(raw+16,e.length);put(raw+20,128);memcpy(raw+24,e.digest,32);
 s.status=character(statusUUID,[NSData dataWithBytes:raw length:64],NO);
 uint8_t prefix[240]={0};memcpy(prefix,"QPFX0001",8);put(prefix+8,59);
 s.prefix=character(@"52414242-4954-4649-8000-000000000041",[NSData dataWithBytes:prefix length:240],NO);return s;
}
static void receipt(TestSender*s){[s read:s.status stage:@"asset-read"];[s peripheral:s.peer didUpdateValueForCharacteristic:s.status error:nil];}
static void waitqueue(void){[[NSRunLoop mainRunLoop]runUntilDate:[NSDate dateWithTimeIntervalSinceNow:.08]];}
static void stopped(void(^action)(void)){
 @try{action();assert(!"must stop");}@catch(NSException*e){assert([e.name isEqual:@"Stopped"]);checks++;}
}
int main(int argc,const char**argv){@autoreleasepool{
 assert(argc==2);NSString*base=[NSString stringWithUTF8String:argv[1]];[[NSFileManager defaultManager]createDirectoryAtPath:base withIntermediateDirectories:YES attributes:nil error:nil];
 for(unsigned mode=0;mode<11;mode++){
  NSString*d=[base stringByAppendingPathComponent:[NSString stringWithFormat:@"case%u",mode]];[[NSFileManager defaultManager]createDirectoryAtPath:d withIntermediateDirectories:YES attributes:nil error:nil];TestSender*s=sender(d,mode!=1);FakePeer*p=(FakePeer*)s.peer;
  receipt(s);assert([s floor]==128&&s.nextCount==0&&p.writes==0&&s.expectedRead==s.prefix);checks++;
  if(mode<2){
   [s peripheral:s.peer didUpdateValueForCharacteristic:s.prefix error:nil];assert([s floor]==128&&s.nextCount==1);assert([s.trace indexOfObject:@"diagnostic-durable"]<[s.trace indexOfObject:@"next-action"]);waitqueue();assert(p.writes==(mode==1?0u:1u));checks++;
   if(mode==0){uint32_t floor=[s floor];stopped(^{[s peripheral:s.peer didWriteValueForCharacteristic:s.control error:nil];});assert([s floor]==floor);}
  }else if(mode==2){NSError*error=[NSError errorWithDomain:@"CBATTErrorDomain" code:1 userInfo:nil];stopped(^{[s peripheral:s.peer didUpdateValueForCharacteristic:s.prefix error:error];});}
  else if(mode==3){NSMutableData*v=[s.prefix.value mutableCopy];((uint8_t*)v.mutableBytes)[0]^=1;s.prefix=character(@"52414242-4954-4649-8000-000000000041",v,NO);s.expectedRead=s.prefix;stopped(^{[s peripheral:s.peer didUpdateValueForCharacteristic:s.prefix error:nil];});}
  else if(mode==4){stopped(^{[s peripheral:s.peer didUpdateValueForCharacteristic:s.status error:nil];});}
  else if(mode==5){NSMutableData*v=[s.prefix.value mutableCopy];[v setLength:239];s.prefix=character(@"52414242-4954-4649-8000-000000000041",v,NO);s.expectedRead=s.prefix;stopped(^{[s peripheral:s.peer didUpdateValueForCharacteristic:s.prefix error:nil];});}
  else if(mode==6){stopped(^{[s write:[NSData data] characteristic:s.control];});}
  else if(mode==7){NSMutableData*v=[s.prefix.value mutableCopy];put((uint8_t*)v.mutableBytes+8,57);s.prefix=character(@"52414242-4954-4649-8000-000000000041",v,NO);s.expectedRead=s.prefix;stopped(^{[s peripheral:s.peer didUpdateValueForCharacteristic:s.prefix error:nil];});}
  else if(mode==8){NSError*e=[NSError errorWithDomain:@"CBErrorDomain" code:7 userInfo:nil];stopped(^{[s centralManager:s.central didDisconnectPeripheral:s.peer error:e];});}
  else if(mode==9){NSError*e=[NSError errorWithDomain:@"CBErrorDomain" code:6 userInfo:nil];stopped(^{[s centralManager:s.central didFailToConnectPeripheral:s.peer error:e];});}
  else{stopped(^{[s boundedTimeout];});}
  if(mode>=2){waitqueue();assert([s floor]==128&&s.nextCount==0&&p.writes==0);checks++;}
  if(mode>=8){NSString*log=[NSString stringWithContentsOfFile:s.prefixLog encoding:NSUTF8StringEncoding error:nil];assert([log containsString:(mode==10?@"RabbitAssetObserver":@"CBErrorDomain")]&&[log containsString:@"raw_bytes\":0"]&&[log containsString:(mode==8?@"disconnected":mode==9?@"connection-failed":@"bounded-timeout")]);assert([s.trace.lastObject isEqual:@"diagnostic-durable"]);checks++;}
  if(mode==2){NSString*log=[NSString stringWithContentsOfFile:s.prefixLog encoding:NSUTF8StringEncoding error:nil];assert([log containsString:@"CBATTErrorDomain"]&&[log containsString:@"raw_bytes\":240"]);checks++;}
 }
 for(unsigned kind=0;kind<5;kind++){AoSequence q={0};assert(!ao_prefix(&q,1,123));assert(!ao_ack(&q));assert(!ao_write(&q,0));assert(ao_read(&q,AO_ASSET_READ));assert(!ao_read(&q,kind));assert(ao_receipt(&q,QFS_DATA,37));assert(ao_read(&q,AO_PREFIX_READ));assert(!ao_write(&q,1));assert(!ao_prefix(&q,1,38)&&q.pending==AO_STOP);checks++;}
 printf("PASS %u HOST OBJC sender callback/sequence cases; NO BLUETOOTH MANAGER/KEY/NATIVE IO\n",checks);return 0;
}}
