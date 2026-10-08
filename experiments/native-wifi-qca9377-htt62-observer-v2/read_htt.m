/* Known-peer read-only collector. Preflight creates no Bluetooth manager. */
#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
static NSString *const peerID=@"F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF";
static NSString *uid(unsigned n){return [[NSString stringWithFormat:@"52414242-4954-4649-8000-%012x",n] uppercaseString];}
static NSString *hex(NSData *data){NSMutableString *s=[NSMutableString string];const uint8_t*b=data.bytes;for(NSUInteger i=0;i<data.length;i++)[s appendFormat:@"%02x",b[i]];return s;}
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
@interface HttReader:NSObject<CBCentralManagerDelegate,CBPeripheralDelegate>
@property CBCentralManager *central;
@property CBPeripheral *peer;
@property NSMutableDictionary<NSString*,CBCharacteristic*> *chars;
@property NSMutableArray<NSString*> *statuses;
@property NSMutableArray<NSMutableArray<NSString*>*> *passes;
@property unsigned discoveries,stage,page;
@property CBService*selectedService;
@property NSString*logPath;
- (void)record:(NSString*)stage error:(NSError*)e raw:(NSData*)raw;
@property NSString *expected;
@property BOOL finished;
@property NSTimeInterval progressAt;
@end
@implementation HttReader
- (void)record:(NSString*)stage error:(NSError*)e raw:(NSData*)raw{
 NSDictionary*v=@{@"timestamp_unix":@([NSDate date].timeIntervalSince1970),@"uptime":@([NSProcessInfo processInfo].systemUptime),@"stage":stage,@"capture_stage":@(self.stage),@"page":@(self.page),@"expected":self.expected?:@"",@"NSError_domain":e.domain?:@"",@"NSError_code":@(e.code),@"NSError_description":e.localizedDescription?:@"",@"raw_bytes":@(raw.length),@"raw_hex":hex(raw),@"cached_value_possible":@(e!=nil),@"peripheral":peerID,@"writes":@0,@"device_attestation":@NO};
 NSData*j=[NSJSONSerialization dataWithJSONObject:v options:NSJSONWritingSortedKeys error:nil];int fd=open(self.logPath.fileSystemRepresentation,O_WRONLY|O_CREAT|O_APPEND|O_NOFOLLOW,0600);struct stat st;
 if(fd<0||fstat(fd,&st)||!S_ISREG(st.st_mode)){if(fd>=0)close(fd);[self fail:@"diagnostic file open failed"];return;}
 const uint8_t*p=j.bytes;size_t left=j.length;while(left){ssize_t n=write(fd,p,left);if(n<=0){close(fd);[self fail:@"diagnostic append failed"];return;}p+=n;left-=(size_t)n;}
 if(write(fd,"\n",1)!=1||fsync(fd)){close(fd);[self fail:@"diagnostic fsync failed"];return;}close(fd);fd=open(self.logPath.stringByDeletingLastPathComponent.fileSystemRepresentation,O_RDONLY);if(fd<0||fsync(fd)){if(fd>=0)close(fd);[self fail:@"diagnostic dir fsync failed"];return;}close(fd);
}
- (void)fail:(NSString*)s{self.finished=YES;
 NSDictionary*partial=@{@"format":@"QHTT1-QHTX1-PARTIAL",@"peripheral":peerID,@"writes":@0,@"device_attestation":@NO,@"status_hex":self.statuses?:@[],@"pages_hex":self.passes?:@[],@"error":s};
 NSData*j=[NSJSONSerialization dataWithJSONObject:partial options:NSJSONWritingSortedKeys error:nil];if(j){fwrite(j.bytes,1,j.length,stdout);puts("");fflush(stdout);}
 fprintf(stderr,"HTT READ FAILED: %s\n",s.UTF8String);exit(1);
}
- (void)request{
 self.progressAt=[NSDate timeIntervalSinceReferenceDate];
 unsigned id=(self.stage==1||self.stage==3)?0x80+self.page:0x2f;
 self.expected=uid(id);CBCharacteristic*c=self.chars[self.expected];
 if(!c||!(c.properties&CBCharacteristicPropertyRead)){[self fail:@"exact read characteristic missing"];return;}
 [self.peer readValueForCharacteristic:c];
}
- (void)centralManagerDidUpdateState:(CBCentralManager*)c{
 if(c.state==CBManagerStatePoweredOn){
  if(self.peer){[self fail:@"duplicate manager callback; no reconnect"];return;}
  NSArray<CBPeripheral*>*list=[c retrievePeripheralsWithIdentifiers:@[[[NSUUID alloc]initWithUUIDString:peerID]]];
  if(list.count!=1){[self fail:@"known Dell peer is not cached; no broad discovery performed"];return;}
  self.peer=list[0];self.peer.delegate=self;[c connectPeripheral:self.peer options:nil];
 }else if(c.state==CBManagerStateUnauthorized||c.state==CBManagerStateUnsupported||c.state==CBManagerStatePoweredOff)[self fail:@"Bluetooth unavailable"];
}
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p{(void)c;if(p!=self.peer||![p.identifier.UUIDString.uppercaseString isEqual:peerID]){[self fail:@"wrong connected peer"];return;}[p discoverServices:@[[CBUUID UUIDWithString:uid(0x2e)]]];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;[self record:@"connect-failed" error:e raw:nil];[self fail:e.localizedDescription?:@"connect failed"];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;if(!self.finished){[self record:@"disconnected" error:e raw:nil];[self fail:e.localizedDescription?:@"disconnected"]; }exit(0);}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e{
 [self record:@"services" error:e raw:nil];if(e||p!=self.peer||self.discoveries>1){[self fail:@"service callback mismatch/error"];return;}
 unsigned service=self.discoveries?0x30:0x2e;CBService*found=nil;
 for(CBService*s in p.services)if([s.UUID isEqual:[CBUUID UUIDWithString:uid(service)]]){if(found){[self fail:@"duplicate exact service"];return;}found=s;}
 if(!found){[self fail:@"exact requested service missing"];return;}self.selectedService=found;NSMutableArray*ids=[NSMutableArray array];if(!self.discoveries)[ids addObject:[CBUUID UUIDWithString:uid(0x2f)]];else for(unsigned i=0;i<30;i++)[ids addObject:[CBUUID UUIDWithString:uid(0x80+i)]];
 [p discoverCharacteristics:ids forService:found];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)s error:(NSError*)e{
 [self record:@"characteristics" error:e raw:nil];if(e||p!=self.peer||s!=self.selectedService||self.discoveries>1){[self fail:@"characteristic callback mismatch/error"];return;}
 for(CBCharacteristic*c in s.characteristics){NSString*k=c.UUID.UUIDString.uppercaseString;unsigned n=self.discoveries?30:1;BOOL expected=NO;for(unsigned i=0;i<n;i++)if([k isEqual:uid(self.discoveries?0x80+i:0x2f)])expected=YES;
  if(!expected||self.chars[k]||!(c.properties&CBCharacteristicPropertyRead)){[self fail:@"unexpected/duplicate/non-read characteristic"];return;}self.chars[k]=c;}
 if(self.chars.count!=(self.discoveries?31u:1u)){[self fail:@"exact characteristic count"];return;}
 if(++self.discoveries==1){[p discoverServices:@[[CBUUID UUIDWithString:uid(0x30)]]];return;}[self request];
}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e{
 [self record:@"read" error:e raw:c.value];
 if(self.finished||e||p!=self.peer||c!=self.chars[self.expected]||![c.UUID.UUIDString.uppercaseString isEqual:self.expected]){[self fail:e.localizedDescription?:@"unexpected read callback"];return;}
 NSData*d=c.value;
 if(self.stage==0||self.stage==2||self.stage==4){
  const uint8_t*b=d.bytes;
  if(d.length!=320||memcmp(b,"QHTT0001",8)||word(b+8+4*4)!=1||word(b+8+44*4)!=12||word(b+8+45*4)!=14||word(b+8+46*4)!=4||word(b+8+54*4)!=62){[self fail:@"exact62 status/all-owner release required BEFORE exports"];return;}
  uint64_t sum=0;for(unsigned i=31;i<=34;i++){uint32_t v=word(b+8+4*i);if(v>65535){[self fail:@"credit bound"];return;}if(i<34)sum+=v;else if(sum!=v){[self fail:@"credit conservation"];return;}}
  for(unsigned i=35;i<=43;i++)if(word(b+8+4*i)){[self fail:@"owner still held"];return;}
  for(unsigned i=296;i<320;i++)if(b[i]){[self fail:@"status reserved padding"];return;}
  NSString*v=hex(d);
  if(self.statuses.count&&![self.statuses[0] isEqual:v]){[self fail:@"status changed during capture"];return;}
  [self.statuses addObject:v];
  if(self.stage==4){
   if(![self.passes[0] isEqual:self.passes[1]]){[self fail:@"export pages changed"];return;}
   NSDictionary*result=@{@"format":@"QHTT1-QHTX1",@"peripheral":p.identifier.UUIDString,@"writes":@0,@"device_attestation":@NO,@"status_hex":self.statuses,@"pages_hex":self.passes};
   NSData*j=[NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingSortedKeys error:nil];fwrite(j.bytes,1,j.length,stdout);puts("");fflush(stdout);
   self.finished=YES;[self.central cancelPeripheralConnection:p];return;
  }
  self.stage++;self.page=0;
 }else{
  unsigned bytes=self.page%5==4?56:512;
  if(d.length!=bytes){[self fail:@"exact512/56-byte page required"];return;}
  [self.passes[self.stage==1?0:1] addObject:hex(d)];
  if(++self.page==30){self.stage++;self.page=0;}
 }
 [self request];
}
@end
int main(int argc,const char**argv){@autoreleasepool{
 if(argc==2&&!strcmp(argv[1],"--preflight")){puts("HTT62 OBSERVER COMPILED; ZERO RADIO OPERATIONS; NO BLUETOOTH MANAGER/SECRET LOAD");return 0;}
 if(argc!=4||strcmp(argv[1],"--root-authorized-read")||strcmp(argv[2],"--log"))return 2;
 NSString*log=[NSString stringWithUTF8String:argv[3]];if(!log.isAbsolutePath)return 2;
 HttReader*r=[HttReader new];r.logPath=log;r.chars=[NSMutableDictionary dictionary];r.statuses=[NSMutableArray array];r.passes=[NSMutableArray arrayWithObjects:[NSMutableArray array],[NSMutableArray array],nil];
 r.progressAt=[NSDate timeIntervalSinceReferenceDate];
 [NSTimer scheduledTimerWithTimeInterval:5 repeats:YES block:^(NSTimer*t){(void)t;if([NSDate timeIntervalSinceReferenceDate]-r.progressAt>90){[r record:@"timeout" error:nil raw:nil];[r fail:@"bounded90-second stalled progress"]; } }];
 r.central=[[CBCentralManager alloc]initWithDelegate:r queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:600 repeats:NO block:^(NSTimer*t){(void)t;[r record:@"timeout" error:nil raw:nil];[r fail:@"bounded600-second snapshot timeout"];}];
 [[NSRunLoop mainRunLoop]run];return 1;
}}
