/* One previously owner-signed chunk, exact RAM receipt, no signing/activation. */
#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include "firmware_sender_core.h"
#include "sha256.h"
static NSString*const advertised=@"52414242-4954-4649-8000-000000000001";
static NSString*const assetService=@"52414242-4954-4649-8000-000000000007";
static NSString*const controlUUID=@"52414242-4954-4649-8000-000000000008";
static NSString*const dataUUID=@"52414242-4954-4649-8000-000000000009";
static NSString*const statusUUID=@"52414242-4954-4649-8000-00000000000A";
static uint32_t u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static NSString*hex(const uint8_t*p,size_t n){NSMutableString*s=[NSMutableString string];for(size_t i=0;i<n;i++)[s appendFormat:@"%02x",p[i]];return s;}
@interface Sender:NSObject<CBCentralManagerDelegate,CBPeripheralDelegate>{QfsExpected expected;QfsProgress progress;}
@property CBCentralManager*central;
@property NSUUID*wanted;
@property CBPeripheral*peer;
@property CBCharacteristic*control;
@property CBCharacteristic*data;
@property CBCharacteristic*status;
@property NSData*packet;
@property NSString*checkpoint;
@property BOOL sending;
@property BOOL writing;
@property NSUInteger cursor;
@property NSUInteger sinceStatus;
@property BOOL finished;
- (void)writeData;
- (BOOL)configure:(NSString*)path checkpoint:(NSString*)checkpoint sending:(BOOL)sending;
@end
@implementation Sender
- (void)fail:(NSString*)reason{fprintf(stderr,"FIRMWARE CHUNK STOPPED: %s; preserve packet/checkpoint, no activation inferred\n",reason.UTF8String);exit(1);}
- (BOOL)configure:(NSString*)path checkpoint:(NSString*)checkpoint sending:(BOOL)sending{
 self.packet=[NSData dataWithContentsOfFile:path];self.checkpoint=checkpoint;self.sending=sending;
 if(self.packet.length<=224||self.packet.length>65760)return NO;
 const uint8_t*p=self.packet.bytes;uint32_t total=u32(p+104),offset=u32(p+108),length=u32(p+112);
 if(memcmp(p,"RABFW001",8)||!total||total>2097152||offset>=total||offset%65536||u32(p+116)!=65536
  ||length!=self.packet.length-224||length!=(total-offset>65536?65536:total-offset))return NO;
 expected.length=(uint32_t)self.packet.length;expected.bit=1u<<(offset/65536);unsigned count=(total+65535)/65536;expected.all=count==32?UINT32_MAX:(1u<<count)-1;
 rabbit_sha256(expected.digest,self.packet.bytes,self.packet.length);
 if([[NSFileManager defaultManager]fileExistsAtPath:checkpoint]){
  NSData*saved=[NSData dataWithContentsOfFile:checkpoint];NSError*error=nil;
  if(saved.length>1024)return NO;
  NSDictionary*v=[NSJSONSerialization JSONObjectWithData:saved options:0 error:&error];
  if(error||![v isKindOfClass:[NSDictionary class]]||v.count!=3||![v[@"packet_sha256"]isEqual:hex(expected.digest,32)]
   ||![v[@"floor"]isKindOfClass:[NSNumber class]]||![v[@"attempted"]isKindOfClass:[NSNumber class]])return NO;
  long long floor=[v[@"floor"]longLongValue],attempted=[v[@"attempted"]longLongValue];
  if(floor<0||floor>expected.length||attempted<0||attempted>1||[v[@"floor"]doubleValue]!=floor||[v[@"attempted"]doubleValue]!=attempted)return NO;
  progress.floor=(uint32_t)floor;progress.attempted=(uint8_t)attempted;
 }
 return YES;
}
- (void)save{
 NSDictionary*v=@{@"packet_sha256":hex(expected.digest,32),@"floor":@(progress.floor),@"attempted":@(progress.attempted)};
 NSData*json=[NSJSONSerialization dataWithJSONObject:v options:NSJSONWritingSortedKeys error:nil];NSError*error=nil;
 if(![json writeToFile:self.checkpoint options:NSDataWritingAtomic error:&error])[self fail:@"checkpoint write failed before radio write"];
 int fd=open(self.checkpoint.fileSystemRepresentation,O_RDONLY);if(fd<0||fsync(fd)){if(fd>=0)close(fd);[self fail:@"checkpoint fsync failed"];}close(fd);
 fd=open(self.checkpoint.stringByDeletingLastPathComponent.fileSystemRepresentation,O_RDONLY);if(fd<0||fsync(fd)){if(fd>=0)close(fd);[self fail:@"checkpoint directory fsync failed"];}close(fd);
}
- (void)centralManagerDidUpdateState:(CBCentralManager*)c{
 if(c.state==CBManagerStatePoweredOn){
  if(self.wanted){NSArray<CBPeripheral*>*known=[c retrievePeripheralsWithIdentifiers:@[self.wanted]];if(known.count==1){self.peer=known[0];self.peer.delegate=self;[c connectPeripheral:self.peer options:nil];return;}}
  [c scanForPeripheralsWithServices:@[[CBUUID UUIDWithString:advertised]] options:nil];
 }
 else if(c.state==CBManagerStateUnauthorized||c.state==CBManagerStateUnsupported||c.state==CBManagerStatePoweredOff)[self fail:@"Bluetooth unavailable"];
}
- (void)centralManager:(CBCentralManager*)c didDiscoverPeripheral:(CBPeripheral*)p advertisementData:(NSDictionary*)a RSSI:(NSNumber*)r{
 (void)a;(void)r;if(self.peer||(self.wanted&&![p.identifier isEqual:self.wanted]))return;self.peer=p;p.delegate=self;[c stopScan];[c connectPeripheral:p options:nil];
}
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p{(void)c;[p discoverServices:@[[CBUUID UUIDWithString:assetService]]];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;[self fail:e.localizedDescription?:@"connection failed"];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;if(!self.finished)[self fail:e.localizedDescription?:@"disconnected; reconnect the same saved packet"];exit(0);}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e{
 if(e){[self fail:e.localizedDescription];return;}
 for(CBService*s in p.services)if([s.UUID isEqual:[CBUUID UUIDWithString:assetService]]){[p discoverCharacteristics:nil forService:s];return;}
 [self fail:@"RAM asset service absent; no writes"];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)s error:(NSError*)e{
 if(e){[self fail:e.localizedDescription];return;}
 for(CBCharacteristic*c in s.characteristics){
  if([c.UUID isEqual:[CBUUID UUIDWithString:controlUUID]]&&(c.properties&CBCharacteristicPropertyWrite)){if(self.control)[self fail:@"duplicate control"];self.control=c;}
  if([c.UUID isEqual:[CBUUID UUIDWithString:dataUUID]]&&(c.properties&CBCharacteristicPropertyWrite)){if(self.data)[self fail:@"duplicate data"];self.data=c;}
  if([c.UUID isEqual:[CBUUID UUIDWithString:statusUUID]]&&(c.properties&CBCharacteristicPropertyRead)){if(self.status)[self fail:@"duplicate status"];self.status=c;}
 }
 if(!self.control||!self.data||!self.status){[self fail:@"required asset characteristics absent"];return;}
 if([p maximumWriteValueLengthForType:CBCharacteristicWriteWithResponse]<44){[self fail:@"negotiated write budget too small"];return;}
 [p readValueForCharacteristic:self.status];
}
- (void)write:(NSData*)value characteristic:(CBCharacteristic*)c{
 if(self.writing||!self.sending){[self fail:@"invalid sender write phase"];return;}
 progress.attempted=1;[self save];self.writing=YES;
 [self.peer writeValue:value forCharacteristic:c type:CBCharacteristicWriteWithResponse];
}
- (void)writeData{
 NSUInteger maximum=[self.peer maximumWriteValueLengthForType:CBCharacteristicWriteWithResponse];
 if(self.cursor>=expected.length||maximum<44){[self fail:@"invalid data cursor/budget"];return;}
 NSUInteger count=expected.length-self.cursor;if(count>240)count=240;if(count>maximum-4)count=maximum-4;
 uint8_t bytes[244];put(bytes,(uint32_t)self.cursor);memcpy(bytes+4,(const uint8_t*)self.packet.bytes+self.cursor,count);
 NSData*value=[NSData dataWithBytes:bytes length:count+4];self.cursor+=count;self.sinceStatus+=count;
 /* Cursor is volatile scheduling only. Saved floor advances ONLY on RFCS. */
 [self write:value characteristic:self.data];
}
- (void)peripheral:(CBPeripheral*)p didWriteValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e{
 if(e){[self fail:e.localizedDescription];return;}
 if(!self.writing||(c!=self.control&&c!=self.data)){[self fail:@"unexpected write ACK"];return;}
 self.writing=NO;
 if(c==self.data&&self.cursor<expected.length&&self.sinceStatus<4096){
  dispatch_after(dispatch_time(DISPATCH_TIME_NOW,50*NSEC_PER_MSEC),dispatch_get_main_queue(),^{if(!self.finished)[self writeData];});return;
 }
 [p readValueForCharacteristic:self.status]; /* ACK never advances confirmed floor. */
}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e{
 if(e){[self fail:e.localizedDescription];return;}
 QfsStatus status;if(c!=self.status||self.writing||qfs_parse(&status,c.value.bytes,c.value.length)){[self fail:@"invalid exact64byte receipt"];return;}
 int action=qfs_next(&status,&expected,&progress);[self save];
 NSDictionary*v=@{@"peripheral":p.identifier.UUIDString,@"state":@(status.state),@"error":@(status.error),@"length":@(status.length),@"received":@(status.received),@"packet_sha256":hex(status.digest,32),@"bitmap":@(status.bitmap),@"ready":@(status.ready),@"action":@(action),@"confirmed_floor":@(progress.floor),@"device_attestation":@NO,@"firmware_started":@NO};
 NSData*json=[NSJSONSerialization dataWithJSONObject:v options:NSJSONWritingSortedKeys error:nil];fwrite(json.bytes,1,json.length,stdout);puts("");fflush(stdout);
 if(!self.sending||action==QFS_DONE){self.finished=YES;[self.central cancelPeripheralConnection:p];return;}
 if(action==QFS_REJECTED||action==QFS_LOSS||action==QFS_BUSY||action==QFS_INVALID){[self fail:@"rejected, receiver loss, busy or invalid state; no replay/abort"];return;}
 NSData*value;CBCharacteristic*destination;
 if(action==QFS_BEGIN||action==QFS_COMMIT){uint8_t command[44]={0};memcpy(command,"RFC1",4);command[4]=action==QFS_BEGIN?1:2;put(command+8,expected.length);memcpy(command+12,expected.digest,32);value=[NSData dataWithBytes:command length:44];destination=self.control;}
 else if(action==QFS_DATA){
  self.cursor=progress.floor;self.sinceStatus=0;
  dispatch_after(dispatch_time(DISPATCH_TIME_NOW,50*NSEC_PER_MSEC),dispatch_get_main_queue(),^{if(!self.finished)[self writeData];});return;
 }else{[self fail:@"unknown action"];return;}
 dispatch_after(dispatch_time(DISPATCH_TIME_NOW,50*NSEC_PER_MSEC),dispatch_get_main_queue(),^{if(!self.finished)[self write:value characteristic:destination];});
}
@end
int main(int argc,const char**argv){@autoreleasepool{
 if(argc!=4||(strcmp(argv[3],"--send")&&strcmp(argv[3],"--query-only")&&strcmp(argv[3],"--preflight"))){fprintf(stderr,"usage: sender signed-packet checkpoint --send|--query-only|--preflight\n");return 2;}
 Sender*s=[Sender new];if(![s configure:[NSString stringWithUTF8String:argv[1]] checkpoint:[NSString stringWithUTF8String:argv[2]] sending:!strcmp(argv[3],"--send")]){fprintf(stderr,"invalid immutable packet/checkpoint\n");return 2;}
 if(!strcmp(argv[3],"--preflight")){[s save];puts("OFFLINE PACKET/CHECKPOINT PASS; NO BLUETOOTH MANAGER");return 0;}
 NSString*wanted=[NSProcessInfo processInfo].environment[@"RABBIT_ASSET_PEER"];
 if(wanted){s.wanted=[[NSUUID alloc]initWithUUIDString:wanted];if(!s.wanted){fprintf(stderr,"invalid known peer; no manager started\n");return 2;}}
 s.central=[[CBCentralManager alloc]initWithDelegate:s queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:s.sending?240:60 repeats:NO block:^(NSTimer*t){(void)t;[s fail:@"bounded timeout; exact saved session retained"];}];
 [[NSRunLoop mainRunLoop]run];return 1;
}}
