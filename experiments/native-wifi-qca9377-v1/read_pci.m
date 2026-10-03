/* Read-only Bluetooth central. Never issues a characteristic write. */
#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#include <stdio.h>
#include <stdlib.h>
static NSString*const service=@"52414242-4954-4649-8000-000000000001";
static NSString*const diagnosticService=@"52414242-4954-4649-8000-000000000005";
static NSString*const diagnostic=@"52414242-4954-4649-8000-000000000006";
@interface Reader:NSObject<CBCentralManagerDelegate,CBPeripheralDelegate>
@property CBCentralManager*central;
@property CBPeripheral*peer;
@property BOOL finished;
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
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p{(void)c;[p discoverServices:@[[CBUUID UUIDWithString:diagnosticService]]];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;[self fail:e.localizedDescription?:@"connection failed"];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;if(!self.finished)[self fail:e.localizedDescription?:@"disconnected"];
 exit(0);
}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e{
 if(e){[self fail:@"service discovery failed"];return;}
 for(CBService*s in p.services)if([s.UUID isEqual:[CBUUID UUIDWithString:diagnosticService]]){[p discoverCharacteristics:nil forService:s];return;}
 [self fail:@"diagnostic service absent"];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)s error:(NSError*)e{
 if(e){[self fail:e.localizedDescription];return;}
 fprintf(stderr,"PCI CHARACTERISTICS=%lu\n",(unsigned long)s.characteristics.count);
 for(CBCharacteristic*c in s.characteristics)if([c.UUID isEqual:[CBUUID UUIDWithString:diagnostic]]&&(c.properties&CBCharacteristicPropertyRead)){
  [p readValueForCharacteristic:c];return;
 }
 [self fail:@"read-only PCI profile absent"];
}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e{
 const uint8_t*b=c.value.bytes;
 if(e||![c.UUID isEqual:[CBUUID UUIDWithString:diagnostic]]||
  !((c.value.length==128&&!memcmp(b,"QPD\1",4))||(c.value.length==160&&!memcmp(b,"QPD\2",4))||(c.value.length==144&&!memcmp(b,"QPD\3",4))||(c.value.length==196&&!memcmp(b,"QPD\4",4))||(c.value.length==240&&!memcmp(b,"QPD\5",4)))){
  [self fail:@"invalid PCI diagnostic envelope"];return;
 }
 NSMutableString*hex=[NSMutableString string];for(NSUInteger i=0;i<c.value.length;i++)[hex appendFormat:@"%02x",b[i]];
 NSDictionary*result=@{@"format":b[3]==1?@"QPD1":b[3]==2?@"QPD2":b[3]==3?@"QPD3":b[3]==4?@"QPD4":@"QPD5",@"raw_hex":hex,@"peripheral":p.identifier.UUIDString,
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
