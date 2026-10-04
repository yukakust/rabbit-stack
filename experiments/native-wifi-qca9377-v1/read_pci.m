/* Read-only Bluetooth central. Never issues a characteristic write. */
#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#include <stdio.h>
#include <CommonCrypto/CommonDigest.h>
#include <stdlib.h>
static NSString*const service=@"52414242-4954-4649-8000-000000000001";
static NSString*const initService=@"52414242-4954-4649-8000-000000000009";
static NSString*const splitService=@"52414242-4954-4649-8000-000000000008";
static NSString*const extensionUUID=@"52414242-4954-4649-8000-000000000007";
static NSString*const diagnosticService=@"52414242-4954-4649-8000-000000000005";
static NSString*const diagnostic=@"52414242-4954-4649-8000-000000000006";
@interface Reader:NSObject<CBCentralManagerDelegate,CBPeripheralDelegate>
@property CBCentralManager*central;
@property CBPeripheral*peer;
@property BOOL finished;
@property NSData*prefix;
@property CBCharacteristic*extension;
@end
@implementation Reader
- (void)fail:(NSString*)message{fprintf(stderr,"PCI QUERY FAILED: %s\n",message.UTF8String);exit(1);}
- (void)centralManagerDidUpdateState:(CBCentralManager*)c{
 if(c.state==CBManagerStatePoweredOn)[c scanForPeripheralsWithServices:@[[CBUUID UUIDWithString:service]] options:nil];
 else if(c.state==CBManagerStateUnauthorized||c.state==CBManagerStateUnsupported||c.state==CBManagerStatePoweredOff)[self fail:@"Bluetooth unavailable"];
}
- (void)centralManager:(CBCentralManager*)c didDiscoverPeripheral:(CBPeripheral*)p advertisementData:(NSDictionary*)a RSSI:(NSNumber*)r{
 (void)a;(void)r;if(self.peer)return;self.peer=p;p.delegate=self;[c stopScan];[c connectPeripheral:p options:nil];
}
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p{(void)c;[p discoverServices:@[[CBUUID UUIDWithString:initService],[CBUUID UUIDWithString:splitService],[CBUUID UUIDWithString:diagnosticService]]];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;[self fail:e.localizedDescription?:@"connection failed"];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;if(!self.finished)[self fail:e.localizedDescription?:@"disconnected"];
 exit(0);
}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e{
 if(e){[self fail:@"service discovery failed"];return;}
 for(NSString*uuid in @[initService,splitService,diagnosticService])for(CBService*s in p.services)if([s.UUID isEqual:[CBUUID UUIDWithString:uuid]]&&([s.UUID isEqual:[CBUUID UUIDWithString:splitService]]||[s.UUID isEqual:[CBUUID UUIDWithString:diagnosticService]]||[s.UUID isEqual:[CBUUID UUIDWithString:initService]])){[p discoverCharacteristics:nil forService:s];return;}
 [self fail:@"diagnostic service absent"];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)s error:(NSError*)e{
 if(e){[self fail:e.localizedDescription];return;}
 fprintf(stderr,"PCI CHARACTERISTICS=%lu\n",(unsigned long)s.characteristics.count);
 for(CBCharacteristic*c in s.characteristics)if([c.UUID isEqual:[CBUUID UUIDWithString:extensionUUID]]&&(c.properties&CBCharacteristicPropertyRead))self.extension=c;
 for(CBCharacteristic*c in s.characteristics)if([c.UUID isEqual:[CBUUID UUIDWithString:diagnostic]]&&(c.properties&CBCharacteristicPropertyRead)){
  [p readValueForCharacteristic:c];return;
 }
 [self fail:@"read-only PCI profile absent"];
}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e{
 NSData*report=c.value;const uint8_t*b=report.bytes;
 if([c.UUID isEqual:[CBUUID UUIDWithString:extensionUUID]]){
  NSUInteger tail=self.prefix&&((const uint8_t*)self.prefix.bytes)[3]==14?148:84;
  if(e||!self.prefix||report.length!=36+tail||memcmp(b,"QIC\1",4)){[self fail:@"invalid diagnostic extension"];return;}
  uint8_t hash[32];CC_SHA256(self.prefix.bytes,(CC_LONG)self.prefix.length,hash);
  if(memcmp(hash,b+4,32)){[self fail:@"diagnostic prefix/extension hash mismatch"];return;}
  NSMutableData*joined=[self.prefix mutableCopy];[joined appendBytes:b+36 length:tail];report=joined;b=report.bytes;
 }else if(!e&&report.length==716&&(!memcmp(b,"QPD\15",4)||!memcmp(b,"QPD\16",4))){
  if(!self.extension){[self fail:@"diagnostic extension absent"];return;}
  uint32_t stage=(uint32_t)b[128]|((uint32_t)b[129]<<8)|((uint32_t)b[130]<<16)|((uint32_t)b[131]<<24);
  if(stage!=5&&stage!=6&&stage!=7&&!(b[3]==14&&stage==20)){[self fail:@"probe still active; retry read-only after cleanup"];return;}
  self.prefix=report;[p readValueForCharacteristic:self.extension];return;
 }
 if(e||!([c.UUID isEqual:[CBUUID UUIDWithString:diagnostic]]||[c.UUID isEqual:[CBUUID UUIDWithString:extensionUUID]])||
  !((report.length==128&&!memcmp(b,"QPD\1",4))||(report.length==160&&!memcmp(b,"QPD\2",4))||(report.length==144&&!memcmp(b,"QPD\3",4))||(report.length==196&&!memcmp(b,"QPD\4",4))||(report.length==240&&!memcmp(b,"QPD\5",4))||(report.length==246&&!memcmp(b,"QPD\6",4))||(report.length==280&&!memcmp(b,"QPD\7",4))||(report.length==356&&!memcmp(b,"QPD\10",4))||(report.length==620&&!memcmp(b,"QPD\11",4))||(report.length==700&&!memcmp(b,"QPD\12",4))||(report.length==716&&!memcmp(b,"QPD\13",4))||(report.length==800&&!memcmp(b,"QPD\14",4))||(report.length==800&&!memcmp(b,"QPD\15",4))||(report.length==864&&!memcmp(b,"QPD\16",4)))){
  [self fail:@"invalid PCI diagnostic envelope"];return;
 }
 NSMutableString*hex=[NSMutableString string];for(NSUInteger i=0;i<report.length;i++)[hex appendFormat:@"%02x",b[i]];
 NSDictionary*result=@{@"format":b[3]==1?@"QPD1":b[3]==2?@"QPD2":b[3]==3?@"QPD3":b[3]==4?@"QPD4":b[3]==5?@"QPD5":b[3]==6?@"QPD6":b[3]==7?@"QPD7":b[3]==8?@"QPD8":b[3]==9?@"QPD9":b[3]==10?@"QPD10":b[3]==11?@"QPD11":b[3]==12?@"QPD12":b[3]==13?@"QPD13":@"QPD14",@"raw_hex":hex,@"peripheral":p.identifier.UUIDString,
   @"device_attestation":@NO,@"writes":@0};
 NSData*json=[NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingSortedKeys error:nil];
 fwrite(json.bytes,1,json.length,stdout);puts("");fflush(stdout);
 self.finished=YES;[self.central cancelPeripheralConnection:p];
}
@end
int main(void){@autoreleasepool{
 Reader*r=[Reader new];r.central=[[CBCentralManager alloc]initWithDelegate:r queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:45 repeats:NO block:^(NSTimer*t){(void)t;[r fail:@"bounded 45 second timeout"];}];
 [[NSRunLoop mainRunLoop]run];return 1;
}}
