#define main filter_program_main
#include "read_filter.m"
#undef main
#include <assert.h>
@interface FakePeer:NSObject
@property NSUUID*identifier;
@property NSArray*services;
@property NSMutableArray*actions;
@end
@implementation FakePeer
- (void)discoverServices:(NSArray*)ids{assert(ids.count==1);[self.actions addObject:@"service"] ;}
- (void)discoverCharacteristics:(NSArray*)ids forService:(CBService*)s{(void)s;[self.actions addObject:@(ids.count)];}
- (void)readValueForCharacteristic:(CBCharacteristic*)c{[self.actions addObject:c.UUID.UUIDString];}
@end
@interface FakeCentral:NSObject
@property unsigned cancelled;
@end
@implementation FakeCentral
- (void)cancelPeripheralConnection:(CBPeripheral*)p{(void)p;self.cancelled++;}
@end
@interface TestReader:FilterReader
@property NSMutableArray*trace;
@end
@implementation TestReader
- (void)fail:(NSString*)s{self.finished=YES;@throw [NSException exceptionWithName:@"Stopped" reason:s userInfo:nil];}
- (void)record:(NSString*)stage error:(NSError*)e raw:(NSData*)raw{[super record:stage error:e raw:raw];[self.trace addObject:@"DURABLE"];}
- (void)request{[self.trace addObject:@"NEXT"];[super request];}
@end
static unsigned checks;
static NSData*bytes(NSString*h){NSMutableData*d=[NSMutableData data];for(NSUInteger i=0;i<h.length;i+=2){unsigned n;NSScanner*s=[NSScanner scannerWithString:[h substringWithRange:NSMakeRange(i,2)]];assert([s scanHexInt:&n]);uint8_t b=(uint8_t)n;[d appendBytes:&b length:1];}return d;}
static CBMutableCharacteristic*character(unsigned id,NSData*v){return [[CBMutableCharacteristic alloc]initWithType:[CBUUID UUIDWithString:uid(id)] properties:CBCharacteristicPropertyRead value:v permissions:CBAttributePermissionsReadable];}
static TestReader*make(NSString*d){TestReader*r=[TestReader new];r.chars=[NSMutableDictionary dictionary];r.statuses=[NSMutableArray array];r.pipelines=[NSMutableArray array];r.passes=[NSMutableArray arrayWithObjects:[NSMutableArray array],[NSMutableArray array],nil];r.trace=[NSMutableArray array];r.logPath=[d stringByAppendingPathComponent:@"callbacks.jsonl"];FakePeer*p=[FakePeer new];p.identifier=[[NSUUID alloc]initWithUUIDString:peerID];p.actions=[NSMutableArray array];r.peer=(CBPeripheral*)p;r.central=(CBCentralManager*)[FakeCentral new];return r;}
static void discovery(TestReader*r){for(unsigned pass=0;pass<3;pass++){CBMutableService*s=[[CBMutableService alloc]initWithType:[CBUUID UUIDWithString:uid(pass==0?0x2e:pass==1?0x2a:0x2c)] primary:YES];NSMutableArray*cs=[NSMutableArray array];for(unsigned i=0;i<(pass==2?110u:1u);i++)[cs addObject:character(pass==2?0x80+i:pass==1?0x2b:0x2f,nil)];s.characteristics=cs;((FakePeer*)r.peer).services=@[s];[r peripheral:r.peer didDiscoverServices:nil];[r peripheral:r.peer didDiscoverCharacteristicsForService:s error:nil];assert(r.discoveries==pass+1);checks++;}assert(r.expected!=nil);checks++;}
static void stop(void(^f)(void)){@try{f();assert(!"must stop");}@catch(NSException*e){assert([e.name isEqual:@"Stopped"]);checks++;}}
static void callback(TestReader*r,NSData*d,NSError*e){unsigned id=(r.stage==1||r.stage==3)?0x80+r.page:(r.part?0x2b:0x2f);CBMutableCharacteristic*c=character(id,d);r.chars[uid(id)]=c;[r peripheral:r.peer didUpdateValueForCharacteristic:c error:e];}
int main(int argc,const char**argv){@autoreleasepool{
 assert(argc==3);NSString*base=[NSString stringWithUTF8String:argv[1]];NSDictionary*fixture=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:[NSString stringWithUTF8String:argv[2]]] options:0 error:nil];NSData*status=bytes(fixture[@"status_hex"][0]);NSData*pipeline=bytes(fixture[@"pipeline_hex"][0]);NSArray*pages=fixture[@"pages_hex"][0];
 for(unsigned mode=0;mode<10;mode++){
  NSString*d=[base stringByAppendingPathComponent:[NSString stringWithFormat:@"case%u",mode]];[[NSFileManager defaultManager]createDirectoryAtPath:d withIntermediateDirectories:YES attributes:nil error:nil];TestReader*r=make(d);discovery(r);NSUInteger before=((FakePeer*)r.peer).actions.count;
  if(mode==0){for(unsigned n=0;n<226;n++){NSData*v=(r.stage==1||r.stage==3)?bytes(pages[r.page]):r.part?status:pipeline;callback(r,v,nil);checks++;if(!r.finished){assert([r.trace indexOfObject:@"DURABLE"]<[r.trace indexOfObject:@"NEXT"]);checks++;}}assert(r.finished&&r.statuses.count==3&&[r.passes[0] isEqual:r.passes[1]]&&((FakeCentral*)r.central).cancelled==1);checks++;continue;}
  NSMutableData*bad=[pipeline mutableCopy];NSError*e=nil;
  if(mode==1)((uint8_t*)bad.mutableBytes)[244]=62;
  if(mode==2)((uint8_t*)bad.mutableBytes)[8+45*4]=1;
  if(mode==3)[bad setLength:543];
  if(mode==4)e=[NSError errorWithDomain:@"CBATTErrorDomain" code:1 userInfo:nil];
  if(mode==5)r.logPath=[d stringByAppendingPathComponent:@"absent/log.jsonl"];
  if(mode==6){CBCharacteristic*wrong=character(0x2f,bad);stop(^{[r peripheral:r.peer didUpdateValueForCharacteristic:wrong error:nil];});}
  else if(mode==7){callback(r,pipeline,nil);callback(r,status,nil);before=((FakePeer*)r.peer).actions.count;stop(^{callback(r,[NSMutableData dataWithLength:511],nil);});}
  else if(mode==8){callback(r,pipeline,nil);callback(r,status,nil);for(unsigned n=0;n<110;n++)callback(r,bytes(pages[n]),nil);before=((FakePeer*)r.peer).actions.count;((uint8_t*)bad.mutableBytes)[8+13*4]^=1;stop(^{callback(r,bad,nil);});}
  else if(mode==9){CBMutableService*s=[[CBMutableService alloc]initWithType:[CBUUID UUIDWithString:uid(0x2c)] primary:YES];stop(^{[r peripheral:r.peer didDiscoverCharacteristicsForService:s error:nil];});}
  else stop(^{callback(r,bad,e);});
  assert(r.finished&&((FakePeer*)r.peer).actions.count==before&&((FakeCentral*)r.central).cancelled==0);checks++;
  if(mode==4){NSString*log=[NSString stringWithContentsOfFile:r.logPath encoding:NSUTF8StringEncoding error:nil];assert([log containsString:@"CBATTErrorDomain"]&&[log containsString:@"raw_bytes\":544"]);checks++;}
 }
 printf("PASS %u HOST FILTER64 callback cases; NO MANAGER/WRITES\n",checks);return 0;
}}
