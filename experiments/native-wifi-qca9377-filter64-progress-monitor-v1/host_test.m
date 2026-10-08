#define main collector_program_main
#include "collector.m"
#undef main
#include <assert.h>
@interface FakePeer:NSObject
@property NSUUID*identifier;
@property NSArray*services;
@property NSMutableArray*actions;
@end
@implementation FakePeer
- (void)discoverServices:(NSArray*)a{assert(a.count==1);[self.actions addObject:@"service"];}
- (void)discoverCharacteristics:(NSArray*)a forService:(CBService*)s{(void)s;assert(a.count==1);[self.actions addObject:@"characteristic"];}
- (void)readValueForCharacteristic:(CBCharacteristic*)c{(void)c;[self.actions addObject:@"read"];}
@end
@interface FakeCentral:NSObject
@property unsigned cancelled;
@end
@implementation FakeCentral
- (void)cancelPeripheralConnection:(CBPeripheral*)p{(void)p;self.cancelled++;}
@end
@interface TestCollector:Collector
@property NSMutableArray*trace;
@end
@implementation TestCollector
- (void)fail:(NSString*)s{self.finished=YES;self.phase=5;@throw [NSException exceptionWithName:@"Stopped" reason:s userInfo:nil];}
- (void)record:(NSString*)stage error:(NSError*)e raw:(NSData*)raw{[super record:stage error:e raw:raw];[self.trace addObject:@"durable"];}
- (void)discover{[self.trace addObject:@"NEXT"];[super discover];}
@end
static unsigned checks;
static TestCollector*make(NSString*d,BOOL monitor){TestCollector*r=[TestCollector new];r.logPath=[d stringByAppendingPathComponent:@"read.jsonl"];r.monitor=monitor;r.reports=[NSMutableArray array];r.trace=[NSMutableArray array];r.began=r.operationBegan=[NSProcessInfo processInfo].systemUptime;FakePeer*p=[FakePeer new];p.identifier=[[NSUUID alloc]initWithUUIDString:peerID];p.actions=[NSMutableArray array];r.peer=(CBPeripheral*)p;r.central=(CBCentralManager*)[FakeCentral new];return r;}
static void word(uint8_t*p,unsigned n,uint32_t v){for(unsigned k=0;k<4;k++)p[8+n*4+k]=(uint8_t)(v>>(k*8));}
static NSData*raw(unsigned index,uint32_t phase,uint32_t released){NSMutableData*d=[NSMutableData dataWithLength:sizes[index]];uint8_t*p=d.mutableBytes;memcpy(p,magic[index],8);if(!index){word(p,0,phase);}else if(index==1){word(p,0,phase?phase:4);word(p,44,released);word(p,55,12);word(p,56,14);word(p,57,4);word(p,59,64);}else{word(p,4,released);word(p,53,12);word(p,54,14);word(p,55,4);word(p,60,64);word(p,61,13);}return d;}
static CBMutableCharacteristic*character(unsigned id,NSData*d){return [[CBMutableCharacteristic alloc]initWithType:uuid(id) properties:CBCharacteristicPropertyRead value:d permissions:CBAttributePermissionsReadable];}
static void discovery(TestCollector*r,NSData*data){CBMutableService*s=[[CBMutableService alloc]initWithType:uuid(services[r.index]) primary:YES];CBMutableCharacteristic*c=character(values[r.index],data);s.characteristics=@[c];((FakePeer*)r.peer).services=@[s];[r peripheral:r.peer didDiscoverServices:nil];[r peripheral:r.peer didDiscoverCharacteristicsForService:s error:nil];assert(r.phase==3&&r.expectedValue==c);checks++;}
static void stop(void(^f)(void)){@try{f();assert(!"must stop");}@catch(NSException*e){assert([e.name isEqual:@"Stopped"]);checks++;}}
int main(int argc,const char**argv){@autoreleasepool{
 assert(argc==2);NSString*base=[NSString stringWithUTF8String:argv[1]];[[NSFileManager defaultManager]createDirectoryAtPath:base withIntermediateDirectories:YES attributes:nil error:nil];
 for(unsigned mode=0;mode<14;mode++){
  NSString*d=[base stringByAppendingPathComponent:[NSString stringWithFormat:@"case%u",mode]];[[NSFileManager defaultManager]createDirectoryAtPath:d withIntermediateDirectories:YES attributes:nil error:nil];TestCollector*r=make(d,YES);[r discover];discovery(r,raw(0,5,1));NSUInteger before=((FakePeer*)r.peer).actions.count;
  if(mode==0){[r peripheral:r.peer didUpdateValueForCharacteristic:r.expectedValue error:nil];assert(r.index==1);discovery(r,raw(1,0,1));[r peripheral:r.peer didUpdateValueForCharacteristic:r.expectedValue error:nil];assert(r.finished&&r.reports.count==2&&((FakeCentral*)r.central).cancelled==1);checks++;continue;}
  if(mode==1){CBCharacteristic*c=character(values[0],raw(0,2,0));r.expectedValue=c;[r peripheral:r.peer didUpdateValueForCharacteristic:c error:nil];assert(!r.finished&&r.phase==4&&r.index==0&&r.reports.count==0&&((FakePeer*)r.peer).actions.count==before);checks++;continue;}
  if(mode>=7){[r peripheral:r.peer didUpdateValueForCharacteristic:r.expectedValue error:nil];discovery(r,raw(1,0,1));before=((FakePeer*)r.peer).actions.count;}
  NSError*e=nil;CBCharacteristic*c=r.expectedValue;
  if(mode==2)e=[NSError errorWithDomain:@"CBATTErrorDomain" code:9 userInfo:nil];
  if(mode==3)c=character(values[0],[NSMutableData dataWithLength:159]);
  if(mode==4){NSMutableData*b=[c.value mutableCopy];((uint8_t*)b.mutableBytes)[0]^=1;c=character(values[0],b);}
  if(mode==5){NSMutableData*b=[c.value mutableCopy];word(b.mutableBytes,1,1);c=character(values[0],b);}
  if(mode==6){r.operationBegan-=61;stop(^{[r clockTick];});checks++;continue;}
  if(mode==7){c=character(values[1],raw(1,0,0));r.expectedValue=c;[r peripheral:r.peer didUpdateValueForCharacteristic:c error:nil];assert(!r.finished&&r.phase==4&&r.index==1&&r.reports.count==1&&((FakePeer*)r.peer).actions.count==before);checks++;continue;}
  if(mode>=8&&mode<=11){NSMutableData*b=[c.value mutableCopy];word(b.mutableBytes,mode==8?59:mode==9?56:mode==10?45:57,mode==8?62:mode==9?13:mode==10?1:3);c=character(values[1],b);}
  if(mode==12){r.scanBegan-=91;r.operationBegan=[NSProcessInfo processInfo].systemUptime;stop(^{[r clockTick];});checks++;continue;}
  if(mode==13){r.began-=5521;r.operationBegan=[NSProcessInfo processInfo].systemUptime;stop(^{[r clockTick];});checks++;continue;}
  r.expectedValue=c;stop(^{[r peripheral:r.peer didUpdateValueForCharacteristic:c error:e];});assert(r.finished&&((FakePeer*)r.peer).actions.count==before);checks++;
  if(mode==2){NSString*log=[NSString stringWithContentsOfFile:r.logPath encoding:NSUTF8StringEncoding error:nil];assert([log containsString:@"CBATTErrorDomain"]&&[log containsString:@"raw_bytes\":160"]);checks++;}
 }
 for(unsigned n=45;n<=54;n++){
  NSString*d=[base stringByAppendingPathComponent:[NSString stringWithFormat:@"owner%u",n]];[[NSFileManager defaultManager]createDirectoryAtPath:d withIntermediateDirectories:YES attributes:nil error:nil];TestCollector*r=make(d,YES);r.index=1;r.scanBegan=r.began;[r discover];NSMutableData*b=[raw(1,0,1) mutableCopy];word(b.mutableBytes,n,1);discovery(r,b);stop(^{[r peripheral:r.peer didUpdateValueForCharacteristic:r.expectedValue error:nil];});assert(r.finished);checks++;
 }
 for(unsigned mode=0;mode<4;mode++){
  NSString*d=[base stringByAppendingPathComponent:[NSString stringWithFormat:@"profile%u",mode]];[[NSFileManager defaultManager]createDirectoryAtPath:d withIntermediateDirectories:YES attributes:nil error:nil];TestCollector*r=make(d,YES);r.scanProfile=YES;[r discover];discovery(r,raw(0,5,1));[r peripheral:r.peer didUpdateValueForCharacteristic:r.expectedValue error:nil];discovery(r,raw(1,0,1));[r peripheral:r.peer didUpdateValueForCharacteristic:r.expectedValue error:nil];assert(r.index==2&&!r.finished);NSMutableData*b=[raw(2,0,1) mutableCopy];if(mode==1)word(b.mutableBytes,60,62);if(mode==2)word(b.mutableBytes,44,1);if(mode==3)word(b.mutableBytes,54,13);discovery(r,b);
  if(mode)stop(^{[r peripheral:r.peer didUpdateValueForCharacteristic:r.expectedValue error:nil];});else{[r peripheral:r.peer didUpdateValueForCharacteristic:r.expectedValue error:nil];assert(r.finished&&r.reports.count==3);checks++;}
 }
 for(unsigned mode=0;mode<3;mode++){
  NSString*d=[base stringByAppendingPathComponent:[NSString stringWithFormat:@"terminal%u",mode]];[[NSFileManager defaultManager]createDirectoryAtPath:d withIntermediateDirectories:YES attributes:nil error:nil];TestCollector*r=make(d,YES);r.index=1;[r discover];NSMutableData*b=[raw(1,mode==1?5:4,1) mutableCopy];if(mode==1)word(b.mutableBytes,1,112);if(mode==2)word(b.mutableBytes,0,0);discovery(r,b);
  if(mode==2)stop(^{[r peripheral:r.peer didUpdateValueForCharacteristic:r.expectedValue error:nil];});else{[r peripheral:r.peer didUpdateValueForCharacteristic:r.expectedValue error:nil];assert(r.finished&&[r.terminalResult isEqual:mode==1?@"RELEASED_DIAGNOSTIC_FAILURE":@"RELEASED_PARTIAL_PIPELINE"]);checks++;}
 }
 printf("PASS %u HOST progress collector cases; NO REAL MANAGER/WRITE\n",checks);return 0;
}}
