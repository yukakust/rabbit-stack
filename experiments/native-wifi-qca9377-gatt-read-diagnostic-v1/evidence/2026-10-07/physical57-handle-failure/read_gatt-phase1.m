#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#include <stdio.h>
/* Host-only, known peer, discovery and one read. No write/notify/sign APIs. */
@interface Reader : NSObject<CBCentralManagerDelegate, CBPeripheralDelegate>
@property CBCentralManager *central;
@property CBPeripheral *peer;
@property NSString *serviceID;
@property NSString *valueID;
@end
@implementation Reader
- (void)event:(NSString *)stage error:(NSError *)error {
 NSDictionary *v=@{@"stage":stage,@"domain":error.domain?:@"",@"code":@(error?error.code:0),@"message":error.localizedDescription?:@""};
 NSData *d=[NSJSONSerialization dataWithJSONObject:v options:NSJSONWritingSortedKeys error:nil];
 fwrite(d.bytes,1,d.length,stdout);puts("");fflush(stdout);
 if(error)exit(1);
}
- (void)centralManagerDidUpdateState:(CBCentralManager *)c {
 [self event:[NSString stringWithFormat:@"manager:%ld",(long)c.state] error:nil];
 if(c.state!=CBManagerStatePoweredOn)return;
 NSArray *p=[c retrievePeripheralsWithIdentifiers:@[[[NSUUID alloc]initWithUUIDString:@"F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF"]]];
 if(p.count!=1)exit(2);
 self.peer=p[0];self.peer.delegate=self;[c connectPeripheral:self.peer options:nil];
}
- (void)centralManager:(CBCentralManager *)c didConnectPeripheral:(CBPeripheral *)p {
 (void)c;[self event:@"connected; discover all services" error:nil];[p discoverServices:nil];
}
- (void)centralManager:(CBCentralManager *)c didFailToConnectPeripheral:(CBPeripheral *)p error:(NSError *)e {
 (void)c;(void)p;[self event:@"connect failed" error:e];exit(1);
}
- (void)centralManager:(CBCentralManager *)c didDisconnectPeripheral:(CBPeripheral *)p error:(NSError *)e {
 (void)c;(void)p;[self event:@"disconnected" error:e];exit(1);
}
- (void)peripheral:(CBPeripheral *)p didDiscoverServices:(NSError *)e {
 [self event:@"discover services callback" error:e];
 for(CBService *s in p.services){[self event:[@"service:" stringByAppendingString:s.UUID.UUIDString] error:nil];}
 for(CBService *s in p.services)if([s.UUID isEqual:[CBUUID UUIDWithString:self.serviceID]]){[p discoverCharacteristics:nil forService:s];return;}
 [self event:@"requested service absent; no read" error:nil];exit(3);
}
- (void)peripheral:(CBPeripheral *)p didDiscoverCharacteristicsForService:(CBService *)s error:(NSError *)e {
 [self event:[@"discover characteristics:" stringByAppendingString:s.UUID.UUIDString] error:e];
 for(CBCharacteristic *v in s.characteristics)[self event:[NSString stringWithFormat:@"characteristic:%@ properties:%lu",v.UUID.UUIDString,(unsigned long)v.properties] error:nil];
 for(CBCharacteristic *v in s.characteristics)if([v.UUID isEqual:[CBUUID UUIDWithString:self.valueID]]&&(v.properties&CBCharacteristicPropertyRead)){[self event:[@"read request:" stringByAppendingString:v.UUID.UUIDString] error:nil];[p readValueForCharacteristic:v];return;}
 [self event:@"requested readable value absent" error:nil];exit(3);
}
- (void)peripheral:(CBPeripheral *)p didUpdateValueForCharacteristic:(CBCharacteristic *)v error:(NSError *)e {
 (void)p;[self event:[@"read callback:" stringByAppendingString:v.UUID.UUIDString] error:e];
 NSMutableString *hex=[NSMutableString new];const unsigned char *b=v.value.bytes;
 for(NSUInteger i=0;i<v.value.length;i++)[hex appendFormat:@"%02x",b[i]];
 [self event:[NSString stringWithFormat:@"value bytes:%lu hex:%@",(unsigned long)v.value.length,hex] error:nil];exit(0);
}
@end
int main(int argc,const char **argv){@autoreleasepool{
 if(argc!=2||(strcmp(argv[1],"asset")&&strcmp(argv[1],"prefix")))return 2;
 Reader *r=[Reader new];BOOL asset=!strcmp(argv[1],"asset");
 r.serviceID=asset?@"52414242-4954-4649-8000-000000000007":@"52414242-4954-4649-8000-000000000040";
 r.valueID=asset?@"52414242-4954-4649-8000-00000000000A":@"52414242-4954-4649-8000-000000000041";
 r.central=[[CBCentralManager alloc]initWithDelegate:r queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:60 repeats:NO block:^(NSTimer *t){(void)t;[r event:@"bounded timeout" error:nil];exit(4);}];
 [[NSRunLoop mainRunLoop]run];return 4;
}}
