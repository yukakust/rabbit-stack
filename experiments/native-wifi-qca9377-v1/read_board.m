/* Read-only known-Dell board observer. No writeValue invocation exists. */
#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#include <stdio.h>
static NSString*const known=@"F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF";
static NSString*const service=@"52414242-4954-4649-8000-000000000020";
static NSString*const characteristic=@"52414242-4954-4649-8000-000000000021";
@interface BoardReader:NSObject<CBCentralManagerDelegate,CBPeripheralDelegate>
@property CBCentralManager*central;
@property CBPeripheral*peer;
@property BOOL finished;
@end
@implementation BoardReader
- (void)fail:(NSString*)message{fprintf(stderr,"BOARD READ FAILED: %s\n",message.UTF8String);exit(1);}
- (void)centralManagerDidUpdateState:(CBCentralManager*)c{
 if(c.state==CBManagerStatePoweredOn){
  NSArray<CBPeripheral*>*list=[c retrievePeripheralsWithIdentifiers:@[[[NSUUID alloc]initWithUUIDString:known]]];
  if(list.count==1){self.peer=list[0];self.peer.delegate=self;[c connectPeripheral:self.peer options:nil];}
  else [c scanForPeripheralsWithServices:@[[CBUUID UUIDWithString:@"52414242-4954-4649-8000-000000000001"]] options:nil];
 }else if(c.state==CBManagerStateUnauthorized||c.state==CBManagerStateUnsupported||c.state==CBManagerStatePoweredOff)[self fail:@"Bluetooth unavailable"];
}
- (void)centralManager:(CBCentralManager*)c didDiscoverPeripheral:(CBPeripheral*)p advertisementData:(NSDictionary*)a RSSI:(NSNumber*)r{
 (void)a;(void)r;if(self.peer||![p.identifier.UUIDString isEqualToString:known])return;
 self.peer=p;p.delegate=self;[c stopScan];[c connectPeripheral:p options:nil];
}
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p{(void)c;[p discoverServices:@[[CBUUID UUIDWithString:service]]];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;[self fail:e.localizedDescription?:@"connection failed"];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;if(!self.finished)[self fail:e.localizedDescription?:@"disconnected"];exit(0);}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e{
 if(e){[self fail:e.localizedDescription];return;}
 for(CBService*s in p.services)if([s.UUID isEqual:[CBUUID UUIDWithString:service]]){[p discoverCharacteristics:@[[CBUUID UUIDWithString:characteristic]] forService:s];return;}
 [self fail:@"board service absent"];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)s error:(NSError*)e{
 if(e){[self fail:e.localizedDescription];return;}
 for(CBCharacteristic*c in s.characteristics)if([c.UUID isEqual:[CBUUID UUIDWithString:characteristic]]&&(c.properties&CBCharacteristicPropertyRead)){[p readValueForCharacteristic:c];return;}
 [self fail:@"board read characteristic absent"];
}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e{
 NSData*data=c.value;const uint8_t*b=data.bytes;
 if(e||![c.UUID isEqual:[CBUUID UUIDWithString:characteristic]]||data.length!=160||memcmp(b,"QBDI0001",8)){[self fail:e.localizedDescription?:@"board envelope invalid"];return;}
 NSMutableString*hex=[NSMutableString string];for(NSUInteger i=0;i<data.length;i++)[hex appendFormat:@"%02x",b[i]];
 NSDictionary*result=@{@"format":@"QBDI1",@"raw_hex":hex,@"peripheral":p.identifier.UUIDString,@"writes":@0,@"device_attestation":@NO};
 NSData*json=[NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingSortedKeys error:nil];fwrite(json.bytes,1,json.length,stdout);puts("");fflush(stdout);
 self.finished=YES;[self.central cancelPeripheralConnection:p];
}
@end
int main(int argc,const char**argv){@autoreleasepool{
 if(argc==2&&!strcmp(argv[1],"--preflight")){puts("BOARD OBSERVER COMPILED; NO BLUETOOTH MANAGER OR PRIVATE KEY");return 0;}
 if(argc!=2||strcmp(argv[1],"--read"))return 2;
 BoardReader*r=[BoardReader new];r.central=[[CBCentralManager alloc]initWithDelegate:r queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:60 repeats:NO block:^(NSTimer*t){(void)t;[r fail:@"bounded 60 second timeout"];}];
 [[NSRunLoop mainRunLoop]run];return 1;
}}
