/* Known-peer read-only collector. Preflight creates no Bluetooth manager. */
#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#include <stdio.h>
#include <string.h>
static NSString *const peerID=@"F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF";
static NSString *uid(unsigned n){return [[NSString stringWithFormat:@"52414242-4954-4649-8000-%012x",n] uppercaseString];}
static NSString *hex(NSData *data){NSMutableString *s=[NSMutableString string];const uint8_t*b=data.bytes;for(NSUInteger i=0;i<data.length;i++)[s appendFormat:@"%02x",b[i]];return s;}
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
@interface ScanReader:NSObject<CBCentralManagerDelegate,CBPeripheralDelegate>
@property CBCentralManager *central;
@property CBPeripheral *peer;
@property NSMutableDictionary<NSString*,CBCharacteristic*> *chars;
@property NSMutableArray<NSString*> *statuses;
@property NSMutableArray<NSMutableArray<NSString*>*> *passes;
@property unsigned discoveries,stage,page;
@property NSString *expected;
@property BOOL finished;
@property NSTimeInterval progressAt;
@end
@implementation ScanReader
- (void)fail:(NSString*)s{
 NSDictionary*partial=@{@"format":@"QSCN1-QEXP1-PARTIAL",@"peripheral":peerID,@"writes":@0,@"device_attestation":@NO,@"status_hex":self.statuses?:@[],@"pages_hex":self.passes?:@[],@"error":s};
 NSData*j=[NSJSONSerialization dataWithJSONObject:partial options:NSJSONWritingSortedKeys error:nil];if(j){fwrite(j.bytes,1,j.length,stdout);puts("");fflush(stdout);}
 fprintf(stderr,"SCAN READ FAILED: %s\n",s.UTF8String);exit(1);
}
- (void)request{
 self.progressAt=[NSDate timeIntervalSinceReferenceDate];
 unsigned id=(self.stage==1||self.stage==3)?0x80+self.page:0x2b;
 self.expected=uid(id);CBCharacteristic*c=self.chars[self.expected];
 if(!c||!(c.properties&CBCharacteristicPropertyRead)){[self fail:@"exact read characteristic missing"];return;}
 [self.peer readValueForCharacteristic:c];
}
- (void)centralManagerDidUpdateState:(CBCentralManager*)c{
 if(c.state==CBManagerStatePoweredOn){
  NSArray<CBPeripheral*>*list=[c retrievePeripheralsWithIdentifiers:@[[[NSUUID alloc]initWithUUIDString:peerID]]];
  if(list.count!=1){[self fail:@"known Dell peer is not cached; no broad discovery performed"];return;}
  self.peer=list[0];self.peer.delegate=self;[c connectPeripheral:self.peer options:nil];
 }else if(c.state==CBManagerStateUnauthorized||c.state==CBManagerStateUnsupported||c.state==CBManagerStatePoweredOff)[self fail:@"Bluetooth unavailable"];
}
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p{(void)c;[p discoverServices:@[[CBUUID UUIDWithString:uid(0x2a)],[CBUUID UUIDWithString:uid(0x2c)]]];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;[self fail:e.localizedDescription?:@"connect failed"];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;if(!self.finished)[self fail:e.localizedDescription?:@"disconnected"];exit(0);}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e{
 if(e){[self fail:e.localizedDescription];return;}
 unsigned found=0;
 for(CBService*s in p.services){
  if([s.UUID isEqual:[CBUUID UUIDWithString:uid(0x2a)]]){found++;[p discoverCharacteristics:@[[CBUUID UUIDWithString:uid(0x2b)]] forService:s];}
  else if([s.UUID isEqual:[CBUUID UUIDWithString:uid(0x2c)]]){found++;NSMutableArray*ids=[NSMutableArray array];for(unsigned i=0;i<110;i++)[ids addObject:[CBUUID UUIDWithString:uid(0x80+i)]];[p discoverCharacteristics:ids forService:s];}
 }
 if(found!=2)[self fail:@"exact scan/status export services missing"];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)s error:(NSError*)e{
 (void)p;if(e){[self fail:e.localizedDescription];return;}
 for(CBCharacteristic*c in s.characteristics){NSString*k=c.UUID.UUIDString.uppercaseString;if(self.chars[k]){[self fail:@"duplicate characteristic"];return;}self.chars[k]=c;}
 if(++self.discoveries==2){if(self.chars.count!=111){[self fail:@"all111 exact characteristics required"];return;}[self request];}
}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e{
 if(e||![c.UUID.UUIDString.uppercaseString isEqual:self.expected]){[self fail:e.localizedDescription?:@"unexpected read callback"];return;}
 NSData*d=c.value;
 if(self.stage==0||self.stage==2||self.stage==4){
  const uint8_t*b=d.bytes;
  if(d.length!=416||memcmp(b,"QSCN0001",8)||word(b+8+4*4)!=1||word(b+8+53*4)!=12||word(b+8+54*4)!=14||word(b+8+60*4)!=55||word(b+8+61*4)!=13){[self fail:@"exact55 status/all-owner release required BEFORE exports"];return;}
  uint64_t sum=0;for(unsigned i=40;i<=43;i++){uint32_t v=word(b+8+4*i);if(v>65535){[self fail:@"credit bound"];return;}if(i<43)sum+=v;else if(sum!=v){[self fail:@"credit conservation"];return;}}
  NSArray<NSString*>*policy=@[@"a5ce1d3e2fdf8aefc2f862c77239cd2fbff1077371763c59c1b7a10d86ae3148",@"7e236caecd939c8ec98be4870bf30422f28ffef2565a38aaaa2d9ddabd0c2641",@"0789d74c4b8e2e788bf2e67296190b01673daf42274935a43f14335c47c96027"];
  for(unsigned i=0;i<3;i++)if(![hex([d subdataWithRange:NSMakeRange(264+32*i,32)]) isEqual:policy[i]]){[self fail:@"reviewed policy/ruleset/location digest mismatch"];return;}
  for(unsigned i=44;i<=52;i++)if(word(b+8+4*i)){[self fail:@"owner still held"];return;}
  NSString*v=hex(d);
  if(self.statuses.count&&![self.statuses[0] isEqual:v]){[self fail:@"status changed during capture"];return;}
  [self.statuses addObject:v];
  if(self.stage==4){
   if(![self.passes[0] isEqual:self.passes[1]]){[self fail:@"export pages changed"];return;}
   NSDictionary*result=@{@"format":@"QSCN1-QEXP1",@"peripheral":p.identifier.UUIDString,@"writes":@0,@"device_attestation":@NO,@"status_hex":self.statuses,@"pages_hex":self.passes};
   NSData*j=[NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingSortedKeys error:nil];fwrite(j.bytes,1,j.length,stdout);puts("");fflush(stdout);
   self.finished=YES;[self.central cancelPeripheralConnection:p];return;
  }
  self.stage++;self.page=0;
 }else{
  unsigned bytes=self.page%5==4?36:512;
  if(d.length!=bytes){[self fail:@"exact512/36-byte page required"];return;}
  [self.passes[self.stage==1?0:1] addObject:hex(d)];
  if(++self.page==110){self.stage++;self.page=0;}
 }
 [self request];
}
@end
int main(int argc,const char**argv){@autoreleasepool{
 if(argc==2&&!strcmp(argv[1],"--preflight")){puts("SCAN55 OBSERVER COMPILED; ZERO RADIO OPERATIONS; NO BLUETOOTH MANAGER/SECRET LOAD");return 0;}
 if(argc!=2||strcmp(argv[1],"--read"))return 2;
 ScanReader*r=[ScanReader new];r.chars=[NSMutableDictionary dictionary];r.statuses=[NSMutableArray array];r.passes=[NSMutableArray arrayWithObjects:[NSMutableArray array],[NSMutableArray array],nil];
 r.progressAt=[NSDate timeIntervalSinceReferenceDate];
 [NSTimer scheduledTimerWithTimeInterval:5 repeats:YES block:^(NSTimer*t){(void)t;if([NSDate timeIntervalSinceReferenceDate]-r.progressAt>90)[r fail:@"bounded90-second stalled progress"]; }];
 r.central=[[CBCentralManager alloc]initWithDelegate:r queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:600 repeats:NO block:^(NSTimer*t){(void)t;[r fail:@"bounded600-second snapshot timeout"];}];
 [[NSRunLoop mainRunLoop]run];return 1;
}}
