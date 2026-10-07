/* One previously owner-signed chunk, exact RAM receipt, no signing/activation. */
#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include "firmware_sender_core.h"
#include "sha256.h"
#include "sequence.h"
static NSString*const advertised=@"52414242-4954-4649-8000-000000000001";
static NSString*const assetService=@"52414242-4954-4649-8000-000000000007";
static NSString*const controlUUID=@"52414242-4954-4649-8000-000000000008";
static NSString*const dataUUID=@"52414242-4954-4649-8000-000000000009";
static NSString*const statusUUID=@"52414242-4954-4649-8000-00000000000A";
static uint32_t u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static NSString*hex(const uint8_t*p,size_t n){NSMutableString*s=[NSMutableString string];for(size_t i=0;i<n;i++)[s appendFormat:@"%02x",p[i]];return s;}
@interface Sender:NSObject<CBCentralManagerDelegate,CBPeripheralDelegate>{QfsExpected expected;QfsProgress progress;AoSequence sequence;}
@property CBCentralManager*central;
@property NSUUID*wanted;
@property CBPeripheral*peer;
@property CBCharacteristic*control;
@property CBCharacteristic*data;
@property CBCharacteristic*status;
@property CBCharacteristic*prefix;
@property CBCharacteristic*expectedRead;
@property CBCharacteristic*expectedWrite;
@property NSString*prefixLog;
@property NSString*packetPath;
@property NSString*readStage;
@property NSString*receiptHex;
@property unsigned discoveries;
@property uint32_t prefixGeneration;
@property int nextAction;
@property NSData*packet;
@property NSString*checkpoint;
@property BOOL sending;
@property BOOL writing;
@property NSUInteger cursor;
@property NSUInteger sinceStatus;
@property BOOL finished;
- (void)writeData;
- (void)boundedTimeout;
- (void)nextActionAfterDiagnostic;
- (void)read:(CBCharacteristic*)c stage:(NSString*)stage;
- (void)diagnostic:(NSString*)stage error:(NSError*)error raw:(NSData*)raw;
- (BOOL)configure:(NSString*)path checkpoint:(NSString*)checkpoint sending:(BOOL)sending;
@end
@implementation Sender
- (void)fail:(NSString*)reason{ao_stop(&sequence);fprintf(stderr,"FIRMWARE CHUNK STOPPED: %s; preserve packet/checkpoint, no activation inferred\n",reason.UTF8String);exit(1);}
- (void)boundedTimeout{[self diagnostic:@"bounded-timeout" error:[NSError errorWithDomain:@"RabbitAssetObserver" code:1 userInfo:@{NSLocalizedDescriptionKey:@"existing bounded timeout expired"}] raw:nil];[self fail:@"bounded timeout; exact saved session retained"];}
- (void)diagnostic:(NSString*)stage error:(NSError*)error raw:(NSData*)raw{
 if(!self.prefixLog)return;
 NSDictionary*v=@{@"timestamp_unix":@([NSDate date].timeIntervalSince1970),@"host_uptime_seconds":@([NSProcessInfo processInfo].systemUptime),@"stage":stage,@"peripheral":self.peer.identifier.UUIDString?:@"",@"NSError_domain":error.domain?:@"",@"NSError_code":@(error.code),@"NSError_description":error.localizedDescription?:@"",@"cached_value_possible":@(error!=nil),@"raw_bytes":@(raw.length),@"raw_hex":hex(raw.bytes,raw.length),@"asset_receipt_hex":self.receiptHex?:@"",@"confirmed_floor":@(progress.floor),@"attempted":@(progress.attempted),@"next_action":@(self.nextAction),@"expected_prefix_generation":@(self.prefixGeneration),@"writes_are_transport_only":@YES,@"device_attestation":@NO};
 NSData*j=[NSJSONSerialization dataWithJSONObject:v options:NSJSONWritingSortedKeys error:nil];
 int fd=open(self.prefixLog.fileSystemRepresentation,O_WRONLY|O_CREAT|O_APPEND|O_NOFOLLOW,0600);
 struct stat logInfo,packetInfo,checkpointInfo;
 if(fd>=0&&(fstat(fd,&logInfo)||!S_ISREG(logInfo.st_mode)||(stat(self.packetPath.fileSystemRepresentation,&packetInfo)==0&&logInfo.st_dev==packetInfo.st_dev&&logInfo.st_ino==packetInfo.st_ino)||(stat(self.checkpoint.fileSystemRepresentation,&checkpointInfo)==0&&logInfo.st_dev==checkpointInfo.st_dev&&logInfo.st_ino==checkpointInfo.st_ino))){close(fd);[self fail:@"diagnostic file aliases immutable packet/checkpoint or is not regular; no next action"];return;}
 if(fd<0){[self fail:@"diagnostic open failed; no next action"];return;}
 const uint8_t*p=j.bytes;size_t left=j.length;
 while(left){ssize_t n=write(fd,p,left);if(n<=0){close(fd);[self fail:@"diagnostic append failed; no next action"];return;}p+=n;left-=(size_t)n;}
 if(write(fd,"\n",1)!=1||fsync(fd)){close(fd);[self fail:@"diagnostic durable save failed; no next action"];return;}close(fd);
 fd=open(self.prefixLog.stringByDeletingLastPathComponent.fileSystemRepresentation,O_RDONLY);
 if(fd<0||fsync(fd)){if(fd>=0)close(fd);[self fail:@"diagnostic directory sync failed; no next action"];return;}close(fd);
}
- (void)read:(CBCharacteristic*)c stage:(NSString*)stage{
 unsigned kind=c==self.prefix?AO_PREFIX_READ:AO_ASSET_READ;
 if(self.writing||self.expectedRead||!c||!ao_read(&sequence,kind)){[self fail:@"overlapping/unexpected read"];return;}
 self.expectedRead=c;self.readStage=stage;[self.peer readValueForCharacteristic:c];
}
- (BOOL)configure:(NSString*)path checkpoint:(NSString*)checkpoint sending:(BOOL)sending{
 if(self.prefixLog){NSString*log=self.prefixLog.stringByStandardizingPath.stringByResolvingSymlinksInPath;
  if([log isEqual:path.stringByStandardizingPath.stringByResolvingSymlinksInPath]||[log isEqual:checkpoint.stringByStandardizingPath.stringByResolvingSymlinksInPath])return NO;}
 self.packetPath=path;self.packet=[NSData dataWithContentsOfFile:path];self.checkpoint=checkpoint;self.sending=sending;
 if(self.packet.length<=224||self.packet.length>65760)return NO;
 const uint8_t*p=self.packet.bytes;uint32_t total=u32(p+104),offset=u32(p+108),length=u32(p+112);
 if(memcmp(p,"RABFW001",8)||!total||total>2097152||offset>=total||offset%65536||u32(p+116)!=65536
  ||length!=self.packet.length-224||length!=(total-offset>65536?65536:total-offset))return NO;
 uint64_t generation=(uint64_t)u32(p+120)|((uint64_t)u32(p+124)<<32);if(self.prefixLog&&(!generation||generation>UINT32_MAX))return NO;self.prefixGeneration=(uint32_t)generation;
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
  if(self.prefixLog){[self diagnostic:@"known-peer-not-cached" error:nil raw:nil];[self fail:@"known peer missing; no alternate connection/controller"];return;}
  [c scanForPeripheralsWithServices:@[[CBUUID UUIDWithString:advertised]] options:nil];
 }
 else if(c.state==CBManagerStateUnauthorized||c.state==CBManagerStateUnsupported||c.state==CBManagerStatePoweredOff)[self fail:@"Bluetooth unavailable"];
}
- (void)centralManager:(CBCentralManager*)c didDiscoverPeripheral:(CBPeripheral*)p advertisementData:(NSDictionary*)a RSSI:(NSNumber*)r{
 (void)a;(void)r;if(self.peer||(self.wanted&&![p.identifier isEqual:self.wanted]))return;self.peer=p;p.delegate=self;[c stopScan];[c connectPeripheral:p options:nil];
}
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p{(void)c;[p discoverServices:self.prefixLog?@[[CBUUID UUIDWithString:assetService],[CBUUID UUIDWithString:@"52414242-4954-4649-8000-000000000040"]]:@[[CBUUID UUIDWithString:assetService]]];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;[self diagnostic:@"connection-failed" error:e raw:nil];[self fail:e.localizedDescription?:@"connection failed"];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;if(!self.finished){[self diagnostic:@"disconnected" error:e raw:nil];[self fail:e.localizedDescription?:@"disconnected; retain exact saved packet without automatic replay"]; }exit(0);}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e{
 if(p!=self.peer||e){[self diagnostic:@"service-discovery-error" error:e raw:nil];[self fail:e.localizedDescription?:@"wrong peer"];return;}
 unsigned found=0;
 for(CBService*s in p.services){
  if([s.UUID isEqual:[CBUUID UUIDWithString:assetService]]){found++;[p discoverCharacteristics:@[[CBUUID UUIDWithString:controlUUID],[CBUUID UUIDWithString:dataUUID],[CBUUID UUIDWithString:statusUUID]] forService:s];}
  else if(self.prefixLog&&[s.UUID isEqual:[CBUUID UUIDWithString:@"52414242-4954-4649-8000-000000000040"]]){found++;[p discoverCharacteristics:@[[CBUUID UUIDWithString:@"52414242-4954-4649-8000-000000000041"]] forService:s];}
 }
 if(found!=(self.prefixLog?2u:1u)){[self diagnostic:@"required-service-missing" error:nil raw:nil];[self fail:@"required asset/prefix service absent; no writes"];}
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)s error:(NSError*)e{
 if(p!=self.peer||e){[self diagnostic:@"characteristic-discovery-error" error:e raw:nil];[self fail:e.localizedDescription?:@"wrong peer"];return;}
 for(CBCharacteristic*c in s.characteristics){
  if([c.UUID isEqual:[CBUUID UUIDWithString:controlUUID]]&&(c.properties&CBCharacteristicPropertyWrite)){if(self.control)[self fail:@"duplicate control"];self.control=c;}
  if([c.UUID isEqual:[CBUUID UUIDWithString:dataUUID]]&&(c.properties&CBCharacteristicPropertyWrite)){if(self.data)[self fail:@"duplicate data"];self.data=c;}
  if([c.UUID isEqual:[CBUUID UUIDWithString:statusUUID]]&&(c.properties&CBCharacteristicPropertyRead)){if(self.status)[self fail:@"duplicate status"];self.status=c;}
  if(self.prefixLog&&[c.UUID isEqual:[CBUUID UUIDWithString:@"52414242-4954-4649-8000-000000000041"]]&&(c.properties&CBCharacteristicPropertyRead)){if(self.prefix)[self fail:@"duplicate prefix"];self.prefix=c;}
 }
 if(++self.discoveries<(self.prefixLog?2u:1u))return;
 if(!self.control||!self.data||!self.status||(self.prefixLog&&!self.prefix)){[self diagnostic:@"required-characteristic-missing" error:nil raw:nil];[self fail:@"required characteristics absent"];return;}
 if([p maximumWriteValueLengthForType:CBCharacteristicWriteWithResponse]<44){[self fail:@"negotiated write budget too small"];return;}
 [self read:self.status stage:@"asset-read"];
}
- (void)write:(NSData*)value characteristic:(CBCharacteristic*)c{
 if(self.writing||self.expectedRead||!ao_write(&sequence,self.sending)){[self fail:@"invalid sender write phase"];return;}
 progress.attempted=1;[self save];self.writing=YES;self.expectedWrite=c;
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
 if(e){[self diagnostic:@"write-error" error:e raw:nil];[self fail:e.localizedDescription];return;}
 if(p!=self.peer||!self.writing||c!=self.expectedWrite||!ao_ack(&sequence)){[self fail:@"unexpected write ACK"];return;}
 self.writing=NO;self.expectedWrite=nil;
 if(c==self.data&&self.cursor<expected.length&&self.sinceStatus<4096){
  dispatch_after(dispatch_time(DISPATCH_TIME_NOW,50*NSEC_PER_MSEC),dispatch_get_main_queue(),^{if(!self.finished)[self writeData];});return;
 }
 [self read:self.status stage:@"asset-checkpoint-read"]; /* ACK never advances confirmed floor. */
}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e{
 if(p!=self.peer||!self.expectedRead||c!=self.expectedRead||self.writing){[self diagnostic:@"cross-characteristic-callback" error:e raw:c.value];[self fail:@"unexpected peer/characteristic/read phase"];return;}
 self.expectedRead=nil;
 if(c==self.prefix){
  /* Persist full public bytes/NSError BEFORE inspecting or scheduling anything. */
  [self diagnostic:@"prefix-read" error:e raw:c.value];
  const uint8_t*b=c.value.bytes;BOOL valid=!e&&c.value.length==240&&!memcmp(b,"QPFX0001",8)&&u32(b+8)==self.prefixGeneration;
  if(!ao_prefix(&sequence,valid,progress.floor)){[self fail:@"prefix diagnostic error/bounds/magic/generation; preserve checkpoint; no next action"];return;}
  [self nextActionAfterDiagnostic];return;
 }
 if(e){[self diagnostic:self.readStage error:e raw:c.value];[self fail:e.localizedDescription];return;}
 QfsStatus status;if(c!=self.status||self.writing||qfs_parse(&status,c.value.bytes,c.value.length)){[self fail:@"invalid exact64byte receipt"];return;}
 int action=qfs_next(&status,&expected,&progress);if(!ao_receipt(&sequence,action,progress.floor)){[self fail:@"asset receipt sequencing"];return;}[self save];self.receiptHex=hex(c.value.bytes,c.value.length);self.nextAction=action;
 NSDictionary*v=@{@"peripheral":p.identifier.UUIDString,@"state":@(status.state),@"error":@(status.error),@"length":@(status.length),@"received":@(status.received),@"packet_sha256":hex(status.digest,32),@"bitmap":@(status.bitmap),@"ready":@(status.ready),@"action":@(action),@"confirmed_floor":@(progress.floor),@"device_attestation":@NO,@"firmware_started":@NO};
 NSData*json=[NSJSONSerialization dataWithJSONObject:v options:NSJSONWritingSortedKeys error:nil];fwrite(json.bytes,1,json.length,stdout);puts("");fflush(stdout);
 if(self.prefixLog){[self read:self.prefix stage:@"prefix-read"];return;}
 [self nextActionAfterDiagnostic];
}
- (void)nextActionAfterDiagnostic{
 int action=self.nextAction;CBPeripheral*p=self.peer;
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
 if((argc!=4&&argc!=6)||(strcmp(argv[3],"--send")&&strcmp(argv[3],"--query-only")&&strcmp(argv[3],"--preflight"))){fprintf(stderr,"usage: sender signed-packet checkpoint --send|--query-only|--preflight [--prefix-log PATH]\n");return 2;}
 Sender*s=[Sender new];if(argc==6){if(strcmp(argv[4],"--prefix-log"))return 2;s.prefixLog=[NSString stringWithUTF8String:argv[5]];}if(![s configure:[NSString stringWithUTF8String:argv[1]] checkpoint:[NSString stringWithUTF8String:argv[2]] sending:!strcmp(argv[3],"--send")]){fprintf(stderr,"invalid immutable packet/checkpoint\n");return 2;}
 if(!strcmp(argv[3],"--preflight")){[s save];puts("OFFLINE PACKET/CHECKPOINT PASS; NO BLUETOOTH MANAGER");return 0;}
 NSString*wanted=[NSProcessInfo processInfo].environment[@"RABBIT_ASSET_PEER"];
 if(wanted){s.wanted=[[NSUUID alloc]initWithUUIDString:wanted];if(!s.wanted){fprintf(stderr,"invalid known peer; no manager started\n");return 2;}}
 if(s.prefixLog&&!s.wanted){fprintf(stderr,"observer requires explicit known RABBIT_ASSET_PEER; no manager started\n");return 2;}
 s.central=[[CBCentralManager alloc]initWithDelegate:s queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:s.sending?240:60 repeats:NO block:^(NSTimer*t){(void)t;[s boundedTimeout];}];
 [[NSRunLoop mainRunLoop]run];return 1;
}}
