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
static NSData*raw(unsigned index,uint32_t phase,uint32_t released){NSMutableData*d=[NSMutableData dataWithLength:sizes[index]];uint8_t*p=d.mutableBytes;memcpy(p,magic[index],index?4:8);if(!index){p[8]=1;p[12]=0x9c;p[13]=3;p[16]=65;}(void)phase;(void)released;return d;}
static CBMutableCharacteristic*character(unsigned id,NSData*d){return [[CBMutableCharacteristic alloc]initWithType:uuid(id) properties:CBCharacteristicPropertyRead value:d permissions:CBAttributePermissionsReadable];}
static void discovery(TestCollector*r,NSData*data){CBMutableService*s=[[CBMutableService alloc]initWithType:uuid(services[r.index]) primary:YES];CBMutableCharacteristic*c=character(values[r.index],data);s.characteristics=@[c];((FakePeer*)r.peer).services=@[s];[r peripheral:r.peer didDiscoverServices:nil];[r peripheral:r.peer didDiscoverCharacteristicsForService:s error:nil];assert(r.phase==3&&r.expectedValue==c);checks++;}
static void stop(void(^f)(void)){@try{f();assert(!"must stop");}@catch(NSException*e){assert([e.name isEqual:@"Stopped"]);checks++;}}
int main(int argc,const char**argv){@autoreleasepool{
 assert(argc==2);NSString*base=[NSString stringWithUTF8String:argv[1]];[[NSFileManager defaultManager]createDirectoryAtPath:base withIntermediateDirectories:YES attributes:nil error:nil];
 for(unsigned mode=0;mode<11;mode++){
  NSString*d=[base stringByAppendingPathComponent:[NSString stringWithFormat:@"case%u",mode]];[[NSFileManager defaultManager]createDirectoryAtPath:d withIntermediateDirectories:YES attributes:nil error:nil];TestCollector*r=make(d,NO);[r discover];discovery(r,raw(0,3,1));NSUInteger before=((FakePeer*)r.peer).actions.count;
  if(mode==0){for(unsigned i=0;i<2;i++){if(i)discovery(r,raw(i,3,1));[r peripheral:r.peer didUpdateValueForCharacteristic:r.expectedValue error:nil];}assert(r.finished&&r.reports.count==2&&((FakeCentral*)r.central).cancelled==1);checks++;continue;}
  NSError*e=nil;CBCharacteristic*c=r.expectedValue;
  if(mode==1)c=character(0x23,c.value);
  if(mode==2)e=[NSError errorWithDomain:@"CBATTErrorDomain" code:9 userInfo:nil];
  if(mode==3)c=character(0x06,[NSMutableData dataWithLength:239]);
  if(mode==4){NSMutableData*b=[c.value mutableCopy];((uint8_t*)b.mutableBytes)[16]=64;c=character(0x06,b);}
  if(mode==5){NSMutableData*b=[c.value mutableCopy];((uint8_t*)b.mutableBytes)[0]^=1;c=character(0x06,b);}
  if(mode>=3&&mode<=5)r.expectedValue=c;
  if(mode==6)r.logPath=[d stringByAppendingPathComponent:@"missing-dir/read.jsonl"];
  if(mode==7){r.phase=2;}
  if(mode==8){r.index=1;}
  if(mode==9){c=character(0x07,raw(1,0,0));}
  if(mode==10){r.operationBegan-=61;r.waiting=YES;stop(^{[r clockTick];});}else stop(^{[r peripheral:r.peer didUpdateValueForCharacteristic:c error:e];});
  assert(r.finished&&r.index==(mode==8?1u:0u)&&r.reports.count==0&&((FakePeer*)r.peer).actions.count==before);checks++;
  if(mode==2){NSString*log=[NSString stringWithContentsOfFile:r.logPath encoding:NSUTF8StringEncoding error:nil];assert([log containsString:@"CBATTErrorDomain"]&&[log containsString:@"raw_bytes\":512"]);checks++;}
 }
 for(unsigned mode=0;mode<5;mode++){
  NSString*d=[base stringByAppendingPathComponent:[NSString stringWithFormat:@"discovery%u",mode]];[[NSFileManager defaultManager]createDirectoryAtPath:d withIntermediateDirectories:YES attributes:nil error:nil];TestCollector*r=make(d,NO);[r discover];
  if(mode==0){((FakePeer*)r.peer).services=@[];stop(^{[r peripheral:r.peer didDiscoverServices:nil];});}
  else if(mode==1){CBMutableService*s=[[CBMutableService alloc]initWithType:uuid(0x22) primary:YES];r.expectedService=s;r.phase=2;stop(^{[r peripheral:r.peer didDiscoverCharacteristicsForService:s error:nil];});}
  else if(mode==2){NSError*e=[NSError errorWithDomain:@"CBErrorDomain" code:7 userInfo:nil];stop(^{[r centralManager:r.central didDisconnectPeripheral:r.peer error:e];});NSString*log=[NSString stringWithContentsOfFile:r.logPath encoding:NSUTF8StringEncoding error:nil];assert([log containsString:@"CBErrorDomain"]);checks++;}
  else if(mode==3){r.operationBegan=[NSProcessInfo processInfo].systemUptime;r.began-=61;stop(^{[r clockTick];});}
  else{CBMutableService*s=[[CBMutableService alloc]initWithType:uuid(0x40) primary:YES];r.expectedService=s;r.phase=2;CBMutableService*wrong=[[CBMutableService alloc]initWithType:uuid(0x40) primary:YES];stop(^{[r peripheral:r.peer didDiscoverCharacteristicsForService:wrong error:nil];});}
  assert(r.index==0&&r.finished&&r.reports.count==0&&((FakePeer*)r.peer).actions.count==1);checks++;
 }
 printf("PASS %u HOST collector cases; NO REAL MANAGER/WRITE\n",checks);return 0;
}}
