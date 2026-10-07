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
@property NSString *journal;
@property NSData *initialStatus;
@property BOOL connecting;
@property NSMutableArray *callbacks;
@property BOOL finished;
@property NSTimeInterval progressAt;
@end
@implementation ScanReader
- (void)persist:(NSString*)format error:(NSString*)error{
 NSMutableDictionary*o=[@{@"format":format,@"peripheral":peerID,@"writes":@0,@"device_attestation":@NO,@"status_hex":self.statuses?:@[],@"pages_hex":self.passes?:@[],@"callbacks":self.callbacks?:@[]} mutableCopy];
 if(error)o[@"error"]=error;
 NSError*e=nil;NSData*j=[NSJSONSerialization dataWithJSONObject:o options:NSJSONWritingSortedKeys error:&e];
 if(!j||![j writeToFile:self.journal options:NSDataWritingAtomic error:&e]){fprintf(stderr,"RAW JOURNAL FAILED\n");exit(1);}
}
- (void)fail:(NSString*)s{
 [self persist:@"QPFX1-QPHCI1-PARTIAL" error:s];
 fprintf(stderr,"PREFIX READ FAILED: %s\n",s.UTF8String);exit(1);
}
- (void)request{
 self.progressAt=[NSProcessInfo processInfo].systemUptime;
 unsigned id=(self.stage==1||self.stage==3)?0x50+self.page:0x41;
 self.expected=uid(id);CBCharacteristic*c=self.chars[self.expected];
 if(!c||!(c.properties&CBCharacteristicPropertyRead)){[self fail:@"exact read characteristic missing"];return;}
 [self.peer readValueForCharacteristic:c];
}
- (void)centralManagerDidUpdateState:(CBCentralManager*)c{
 if(c.state==CBManagerStatePoweredOn&&!self.connecting){
  self.connecting=YES;
  NSArray<CBPeripheral*>*list=[c retrievePeripheralsWithIdentifiers:@[[[NSUUID alloc]initWithUUIDString:peerID]]];
  if(list.count!=1){[self fail:@"known Dell peer is not cached; no broad discovery performed"];return;}
  self.peer=list[0];self.peer.delegate=self;[c connectPeripheral:self.peer options:nil];
 }else if(c.state==CBManagerStateUnauthorized||c.state==CBManagerStateUnsupported||c.state==CBManagerStatePoweredOff)[self fail:@"Bluetooth unavailable"];
}
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p{(void)c;if(p!=self.peer||![p.identifier.UUIDString isEqual:peerID]){[self fail:@"unexpected connected peer"];return;}[p discoverServices:@[[CBUUID UUIDWithString:uid(0x40)]]];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;[self fail:e.localizedDescription?:@"connect failed"];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;if(!self.finished)[self fail:e.localizedDescription?:@"disconnected"];exit(0);}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e{
 if(p!=self.peer||e){[self fail:e.localizedDescription?:@"unexpected service callback"];return;}
 unsigned found=0;
 for(CBService*s in p.services)if([s.UUID isEqual:[CBUUID UUIDWithString:uid(0x40)]]){
  found++;NSMutableArray*ids=[NSMutableArray arrayWithObject:[CBUUID UUIDWithString:uid(0x41)]];
  for(unsigned i=0;i<10;i++)[ids addObject:[CBUUID UUIDWithString:uid(0x50+i)]];
  [p discoverCharacteristics:ids forService:s];
 }
 if(found!=1)[self fail:@"exact one prefix service required"];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)s error:(NSError*)e{
 if(p!=self.peer||![s.UUID isEqual:[CBUUID UUIDWithString:uid(0x40)]]||self.discoveries){[self fail:@"unexpected discovery callback"];return;}if(e){[self fail:e.localizedDescription];return;}
 for(CBCharacteristic*c in s.characteristics){NSString*k=c.UUID.UUIDString.uppercaseString;if(self.chars[k]){[self fail:@"duplicate characteristic"];return;}self.chars[k]=c;}
 if(++self.discoveries==1){if(self.chars.count!=11){[self fail:@"all11 exact characteristics required"];return;}[self request];}
}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e{
 NSData*received=c.value?:[NSData data];
 if(self.callbacks.count>=24)[self fail:@"bounded callback count exceeded"];
 [self.callbacks addObject:@{@"uuid":c.UUID.UUIDString,@"bytes":@(received.length),@"hex":hex([received subdataWithRange:NSMakeRange(0,MIN(received.length,512))]),@"truncated":@(received.length>512),@"error":e.localizedDescription?:@""}];
 [self persist:@"QPFX1-QPHCI1-PARTIAL" error:nil];
 if(p!=self.peer||e||![c.UUID.UUIDString.uppercaseString isEqual:self.expected]){[self fail:e.localizedDescription?:@"unexpected read callback"];return;}
 NSData*d=c.value;
 if(self.stage==0||self.stage==2||self.stage==4){
  [self.statuses addObject:hex(d)];[self persist:@"QPFX1-QPHCI1-PARTIAL" error:nil];
  const uint8_t*b=d.bytes;
  if(d.length!=240||memcmp(b,"QPFX0001",8)||word(b+8)!=57||word(b+12)!=3||word(b+24)!=1||word(b+88)!=12||word(b+92)!=14){[self fail:@"actual57 all14 release required before raw reads"];return;}
  for(unsigned i=22;i<=32;i++)if(word(b+8+4*i)){[self fail:@"owner still held"];return;}
  if(!self.initialStatus)self.initialStatus=[d copy];
  const uint8_t*first=self.initialStatus.bytes;
  for(unsigned i=0;i<58;i++)if((i<=32||i==48||i==49||i>=54)&&word(first+8+4*i)!=word(b+8+4*i)){[self fail:@"frozen status invariant changed"];return;}
  if(self.stage==4){
   if(![self.passes[0] isEqual:self.passes[1]]){[self fail:@"raw pages changed"];return;}
   [self persist:@"QPFX1-QPHCI1" error:nil];
   self.finished=YES;[self.central cancelPeripheralConnection:p];return;
  }
  self.stage++;self.page=0;
 }else{
  unsigned bytes=self.page==9?64:512;
  [self.passes[self.stage==1?0:1] addObject:hex(d)];[self persist:@"QPFX1-QPHCI1-PARTIAL" error:nil];
  if(d.length!=bytes){[self fail:@"exact512/64-byte page required"];return;}
  if(++self.page==10){self.stage++;self.page=0;}
 }
 [self request];
}
@end
int main(int argc,const char**argv){@autoreleasepool{
 if(argc==2&&!strcmp(argv[1],"--preflight")){puts("PREFIX57 OBSERVER COMPILED; ZERO RADIO OPERATIONS; NO BLUETOOTH MANAGER/SECRET LOAD");return 0;}
 if(argc!=3||strcmp(argv[1],"--read")||argv[2][0]!='/')return 2;
 ScanReader*r=[ScanReader new];r.callbacks=[NSMutableArray array];r.chars=[NSMutableDictionary dictionary];r.statuses=[NSMutableArray array];r.passes=[NSMutableArray arrayWithObjects:[NSMutableArray array],[NSMutableArray array],nil];
 r.journal=[NSString stringWithUTF8String:argv[2]];[r persist:@"QPFX1-QPHCI1-PARTIAL" error:nil];
 r.progressAt=[NSProcessInfo processInfo].systemUptime;
 [NSTimer scheduledTimerWithTimeInterval:5 repeats:YES block:^(NSTimer*t){(void)t;if([NSProcessInfo processInfo].systemUptime<r.progressAt||[NSProcessInfo processInfo].systemUptime-r.progressAt>90)[r fail:@"bounded90-second stalled progress"]; }];
 r.central=[[CBCentralManager alloc]initWithDelegate:r queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:600 repeats:NO block:^(NSTimer*t){(void)t;[r fail:@"bounded600-second snapshot timeout"];}];
 [[NSRunLoop mainRunLoop]run];return 1;
}}
