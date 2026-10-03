/* Mac-only passive diagnostic. No connection or characteristic write. */
#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#include <stdio.h>
static NSString*const fileService=@"52414242-4954-4649-8000-000000000001";
static NSString*const pciService=@"52414242-4954-4649-8000-000000000005";
static NSString*const assetService=@"52414242-4954-4649-8000-000000000007";
@interface Probe:NSObject<CBCentralManagerDelegate>
@property CBCentralManager*central;
@property NSMutableArray*candidates;
@property NSUInteger adverts;
@property NSUInteger connected;
@property NSInteger cachedState;
@property BOOL scanned;
@end
@implementation Probe
- (void)centralManagerDidUpdateState:(CBCentralManager*)c{
 if(c.state!=CBManagerStatePoweredOn||self.scanned)return;
 self.scanned=YES;
 self.connected=[c retrieveConnectedPeripheralsWithServices:@[[CBUUID UUIDWithString:fileService]]].count;
 NSArray<CBPeripheral*>*cached=[c retrievePeripheralsWithIdentifiers:@[[[NSUUID alloc]initWithUUIDString:@"F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF"]]];
 self.cachedState=cached.count?cached[0].state:-1;
 /* Filter locally, exposing no unrelated device names/identifiers. */
 [c scanForPeripheralsWithServices:nil options:@{CBCentralManagerScanOptionAllowDuplicatesKey:@NO}];
}
- (void)centralManager:(CBCentralManager*)c didDiscoverPeripheral:(CBPeripheral*)p advertisementData:(NSDictionary*)a RSSI:(NSNumber*)r{
 (void)c;self.adverts++;
 NSMutableArray*services=[NSMutableArray array];NSArray*uuids=a[CBAdvertisementDataServiceUUIDsKey]?:@[];
 for(CBUUID*u in uuids)if([u isEqual:[CBUUID UUIDWithString:fileService]]||[u isEqual:[CBUUID UUIDWithString:pciService]]||[u isEqual:[CBUUID UUIDWithString:assetService]])[services addObject:u.UUIDString];
 if(services.count)[self.candidates addObject:@{@"peripheral":p.identifier.UUIDString,@"rabbit_services":services,@"rssi":r,@"state":@(p.state)}];
}
@end
int main(void){@autoreleasepool{
 Probe*p=[Probe new];p.candidates=[NSMutableArray array];p.cachedState=-1;p.central=[[CBCentralManager alloc]initWithDelegate:p queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:20 repeats:NO block:^(NSTimer*t){(void)t;
  [p.central stopScan];NSDictionary*v=@{@"controller_state":@(p.central.state),@"authorization":@(CBCentralManager.authorization),@"scan_started":@(p.scanned),@"advertisement_count":@(p.adverts),@"connected_rabbit_count":@(p.connected),@"known_dell_cached_state":@(p.cachedState),@"rabbit_candidates":p.candidates,@"connections_started":@0,@"writes":@0,@"physical_wifi_verified":@NO};
  NSData*json=[NSJSONSerialization dataWithJSONObject:v options:NSJSONWritingSortedKeys error:nil];fwrite(json.bytes,1,json.length,stdout);puts("");fflush(stdout);exit(0);
 }];[[NSRunLoop mainRunLoop]run];return 1;
}}
