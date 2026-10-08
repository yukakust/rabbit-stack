#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#include <stdio.h>
#include <string.h>
static NSString*const peerID=@"F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF";
static NSString*hex(NSData*d){NSMutableString*s=[NSMutableString string];const uint8_t*p=d.bytes;for(NSUInteger i=0;i<d.length;i++)[s appendFormat:@"%02x",p[i]];return s;}
@interface Inventory:NSObject<CBCentralManagerDelegate,CBPeripheralDelegate>
@property CBCentralManager*central;
@property CBPeripheral*peer;
@property NSArray<CBService*>*services;
@property NSUInteger index;
@property BOOL finished;
@property CBCharacteristic*status;
@end
@implementation Inventory
- (void)record:(NSString*)stage error:(NSError*)e info:(NSDictionary*)info {
 NSDictionary*r=@{@"stage":stage,@"peripheral":self.peer.identifier.UUIDString?:peerID,@"writes":@0,@"timestamp":@([NSDate date].timeIntervalSince1970),@"NSError_domain":e.domain?:@"",@"NSError_code":@(e.code),@"info":info?:@{}};
 NSData*d=[NSJSONSerialization dataWithJSONObject:r options:NSJSONWritingSortedKeys error:nil];fwrite(d.bytes,1,d.length,stdout);puts("");fflush(stdout);
}
- (void)fail:(NSString*)s{self.finished=YES;fprintf(stderr,"INVENTORY STOP: %s; zero writes\n",s.UTF8String);exit(1);}
- (void)next {
 if(self.index<self.services.count){[self.peer discoverCharacteristics:nil forService:self.services[self.index]];return;}
 if(self.status){[self.peer readValueForCharacteristic:self.status];return;}
 [self record:@"inventory-complete-status-absent" error:nil info:@{}];self.finished=YES;[self.central cancelPeripheralConnection:self.peer];
}
- (void)centralManagerDidUpdateState:(CBCentralManager*)c {
 if(c.state==CBManagerStatePoweredOn){NSArray*a=[c retrievePeripheralsWithIdentifiers:@[[[NSUUID alloc]initWithUUIDString:peerID]]];if(a.count!=1)[self fail:@"exact known peer unavailable"];self.peer=a[0];self.peer.delegate=self;[c connectPeripheral:self.peer options:nil];}
 else if(c.state==CBManagerStatePoweredOff||c.state==CBManagerStateUnauthorized||c.state==CBManagerStateUnsupported)[self fail:@"Bluetooth unavailable"];
}
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p{(void)c;if(p!=self.peer)[self fail:@"wrong peer"];[p discoverServices:nil];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;[self record:@"connect-failed" error:e info:@{}];[self fail:@"connect failure"];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;if(!self.finished){[self record:@"disconnected" error:e info:@{}];[self fail:@"unexpected disconnect"]; }exit(0);}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e {
 NSMutableArray*a=[NSMutableArray array];for(CBService*s in p.services)[a addObject:s.UUID.UUIDString];[self record:@"all-services" error:e info:@{@"UUIDs":a}];
 if(e||p!=self.peer||p.services.count>32)[self fail:@"service error/bounds"];
 self.services=[p.services copy];self.index=0;[self next];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)s error:(NSError*)e {
 NSMutableArray*a=[NSMutableArray array];for(id item in s.characteristics){if(![item isKindOfClass:[CBCharacteristic class]]){NSString*u=[item isKindOfClass:[CBService class]]?((CBService*)item).UUID.UUIDString:@"unknown";[a addObject:@{@"unexpected_class":NSStringFromClass([item class]),@"UUID":u}];continue;}CBCharacteristic*c=(CBCharacteristic*)item;[a addObject:@{@"UUID":c.UUID.UUIDString,@"properties":@(c.properties)}];if([c.UUID.UUIDString.uppercaseString isEqual:@"52414242-4954-4649-8000-00000000002B"]&&(c.properties&CBCharacteristicPropertyRead))self.status=c;}
 [self record:@"all-characteristics" error:e info:@{@"service":s.UUID.UUIDString,@"characteristics":a}];
 if(e||p!=self.peer||self.index>=self.services.count||s!=self.services[self.index]||s.characteristics.count>256)[self fail:@"characteristic error/sequence/bounds"];
 self.index++;[self next];
}
- (void)peripheral:(CBPeripheral*)p didModifyServices:(NSArray<CBService*>*)s{(void)p;NSMutableArray*a=[NSMutableArray array];for(CBService*v in s)[a addObject:v.UUID.UUIDString];[self record:@"modified-services" error:nil info:@{@"UUIDs":a}];[self fail:@"service database changed during inventory"];}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e {
 [self record:@"diagnostic-status-read-untrusted-parent" error:e info:@{@"UUID":c.UUID.UUIDString,@"parent_service":c.service.UUID.UUIDString,@"scan_success_authority":@NO,@"bytes":@(c.value.length),@"hex":hex(c.value),@"cached_value_possible":@(e!=nil)}];
 if(e||p!=self.peer||c!=self.status)[self fail:@"status read error; raw retained"];
 self.finished=YES;[self.central cancelPeripheralConnection:p];
}
@end
int main(int argc,const char**argv){@autoreleasepool{
 if(argc==2&&!strcmp(argv[1],"--preflight")){puts("INVENTORY HOST PREFLIGHT; NO MANAGER/WRITES");return 0;}
 if(argc!=2||strcmp(argv[1],"--root-authorized-read"))return 2;
 Inventory*r=[Inventory new];r.central=[[CBCentralManager alloc]initWithDelegate:r queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:120 repeats:NO block:^(NSTimer*t){(void)t;[r fail:@"bounded inventory timeout"];}];[[NSRunLoop mainRunLoop]run];return 1;
}}
