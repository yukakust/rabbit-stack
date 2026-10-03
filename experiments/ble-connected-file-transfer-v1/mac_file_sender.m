/* Mac central: acknowledged GATT writes, final application receipt required.
 * Physical world delivery observed; interruption/resume still under test. No pairing.
 * UUID match is discovery, NOT authentication or confidential transport. */
#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#import <CommonCrypto/CommonDigest.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "sender_status.h"
static NSString *const Service=@"52414242-4954-4649-8000-000000000001";
static void put32(uint8_t*p,uint32_t n){for(int i=0;i<4;i++)p[i]=n>>(8*i);}
@interface Sender:NSObject<CBCentralManagerDelegate,CBPeripheralDelegate>
@property(nonatomic,strong) CBCentralManager *central;
@property(nonatomic,strong) CBPeripheral *peer;
@property(nonatomic,strong) CBCharacteristic *control,*data,*status;
@property(nonatomic,strong) NSData *stream,*nonce,*expectedDigest;
@property NSUInteger offset,pending;
@property NSUInteger confirmed,pauseAfter,minimumReceived;
@property NSUInteger chunkBytes,dataDelayMs;
@property NSUInteger connectionGeneration;
@property NSTimeInterval startedAt;
@property uint32_t counter;
@property int phase;
@property unsigned kind,reconnects;
@property BOOL finished;
@property BOOL queryOnly;
@property BOOL abortOnly;
@property(nonatomic,strong) NSUUID *queryPeripheral;
- (void)fail:(NSString*)why;
- (void)next;
- (void)scheduleNext;
@end
@implementation Sender
- (void)fail:(NSString*)why {fprintf(stderr,"FAIL: %s; application outcome may be unknown; staging retained if Dell remains powered\n",why.UTF8String);[self.central stopScan];if(self.peer)[self.central cancelPeripheralConnection:self.peer];exit(1);}
- (void)centralManagerDidUpdateState:(CBCentralManager*)central {
 if(central.state==CBManagerStatePoweredOn){
  if(self.queryPeripheral){
   NSArray<CBPeripheral*>*known=[central retrievePeripheralsWithIdentifiers:@[self.queryPeripheral]];
   if(known.count!=1){[self fail:@"cached query peripheral unavailable"];return;}
   self.peer=known[0];self.peer.delegate=self;
   printf("READ-ONLY CACHED CONNECT: %s (not identity authentication)\n",self.peer.identifier.UUIDString.UTF8String);
   [central connectPeripheral:self.peer options:nil];return;
  }
  puts("SCANNING FOR RABBIT FILE SERVICE (not identity authentication)");[central scanForPeripheralsWithServices:@[[CBUUID UUIDWithString:Service]] options:nil];}
 else if(central.state==CBManagerStatePoweredOff||central.state==CBManagerStateUnauthorized||central.state==CBManagerStateUnsupported)[self fail:@"Bluetooth unavailable"];
}
- (void)centralManager:(CBCentralManager*)c didDiscoverPeripheral:(CBPeripheral*)p advertisementData:(NSDictionary*)ad RSSI:(NSNumber*)rssi {
 if(self.peer)return;
 printf("DISCOVERED: %s RSSI=%ld; connecting\n",p.identifier.UUIDString.UTF8String,(long)rssi.integerValue);
 (void)ad;self.peer=p;p.delegate=self;[c stopScan];[c connectPeripheral:p options:nil];
}
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p {(void)c;self.connectionGeneration++;puts("CONNECTED: discovering file service");[p discoverServices:@[[CBUUID UUIDWithString:Service]]];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e {(void)c;(void)p;[self fail:e.localizedDescription?:@"connect failed"];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e {
 if(self.finished||p!=self.peer)return;
 self.connectionGeneration++;
 if(self.queryPeripheral){[self fail:@"cached query disconnected; no packet sent"];return;}
 fprintf(stderr,"DISCONNECTED: phase=%d offset=%lu/%lu domain=%s code=%ld reason=%s\n",self.phase,(unsigned long)self.offset,(unsigned long)self.stream.length,e?e.domain.UTF8String:"none",e?(long)e.code:0,e?e.localizedDescription.UTF8String:"none");
 if(++self.reconnects>3){[self fail:@"bounded reconnect limit; rerun SAME saved session to query outcome"];return;}
 puts("RECONNECT: delivery unknown; querying retained session, not assuming application");
 self.peer=nil;self.control=nil;self.data=nil;self.status=nil;self.phase=0;
 [c scanForPeripheralsWithServices:@[[CBUUID UUIDWithString:Service]] options:nil];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e {
 if(p!=self.peer)return;
 printf("SERVICE DISCOVERY: count=%lu error=%s\n",(unsigned long)p.services.count,e?e.localizedDescription.UTF8String:"none");
 if(e||p.services.count!=1){[self fail:@"service discovery failed"];return;}
 [p discoverCharacteristics:nil forService:p.services[0]];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)service error:(NSError*)e {
 if(p!=self.peer)return;
 if(e){[self fail:e.localizedDescription];return;}
 printf("CHARACTERISTIC DISCOVERY: count=%lu\n",(unsigned long)service.characteristics.count);
 for(CBCharacteristic*c in service.characteristics){NSString*u=c.UUID.UUIDString;
  if([u isEqualToString:@"52414242-4954-4649-8000-000000000002"])self.control=c;
  if([u isEqualToString:@"52414242-4954-4649-8000-000000000003"])self.data=c;
  if([u isEqualToString:@"52414242-4954-4649-8000-000000000004"])self.status=c;
 }
 if(!self.control||!self.data||!self.status||!(self.control.properties&CBCharacteristicPropertyWrite)||!(self.data.properties&CBCharacteristicPropertyWrite)||!(self.status.properties&CBCharacteristicPropertyRead)){[self fail:@"incompatible file service"];return;}
 if(self.queryOnly||self.abortOnly){puts("READ-ONLY QUERY: no BEGIN, DATA, COMMIT or ABORT");self.phase=5;if(self.queryOnly)[p readRSSI];else [p readValueForCharacteristic:self.status];return;}
 uint8_t begin[16]={1,1,(uint8_t)self.kind,0};memcpy(begin+4,self.nonce.bytes,8);put32(begin+12,(uint32_t)self.stream.length);
 printf("BEGIN: acknowledged write; maximum value bytes=%lu\n",(unsigned long)[p maximumWriteValueLengthForType:CBCharacteristicWriteWithResponse]);
 self.phase=1;[p writeValue:[NSData dataWithBytes:begin length:16] forCharacteristic:self.control type:CBCharacteristicWriteWithResponse];
}
- (void)scheduleNext {
 if(!self.dataDelayMs){[self next];return;}
 if(!self.pauseAfter||self.queryOnly||self.abortOnly){[self fail:@"diagnostic pacing requires staging-only transfer"];return;}
 CBPeripheral*peer=self.peer;CBCharacteristic*data=self.data;
 NSUInteger generation=self.connectionGeneration,offset=self.offset;
 self.phase=8;
 [NSTimer scheduledTimerWithTimeInterval:self.dataDelayMs/1000.0 repeats:NO block:^(NSTimer*t){
  (void)t;if(!self.finished&&self.phase==8&&self.connectionGeneration==generation&&self.peer==peer&&self.data==data&&self.offset==offset)[self next];
 }];
}
- (void)next {
 if(self.queryOnly||self.abortOnly){[self fail:@"data/commit forbidden in query/abort mode"];return;}
 if(self.offset==self.stream.length){uint8_t commit[9]={2};memcpy(commit+1,self.nonce.bytes,8);self.phase=3;[self.peer writeValue:[NSData dataWithBytes:commit length:9] forCharacteristic:self.control type:CBCharacteristicWriteWithResponse];return;}
 NSUInteger limit=MIN((NSUInteger)244,[self.peer maximumWriteValueLengthForType:CBCharacteristicWriteWithResponse]);
 if(limit<=4){[self fail:@"write MTU too small"];return;}
 self.pending=MIN(MIN(limit-4,self.chunkBytes),self.stream.length-self.offset);
 NSMutableData*value=[NSMutableData dataWithLength:4+self.pending];put32(value.mutableBytes,(uint32_t)self.offset);memcpy((uint8_t*)value.mutableBytes+4,(const uint8_t*)self.stream.bytes+self.offset,self.pending);
 self.phase=2;[self.peer writeValue:value forCharacteristic:self.data type:CBCharacteristicWriteWithResponse];
}
- (void)peripheral:(CBPeripheral*)p didReadRSSI:(NSNumber*)rssi error:(NSError*)e {
 if(p!=self.peer||!self.queryOnly||self.phase!=5)return;
 printf("CONNECTED RSSI=%s error=%s (local radio measurement, not attestation)\n",rssi?rssi.stringValue.UTF8String:"unavailable",e?e.localizedDescription.UTF8String:"none");
 [p readValueForCharacteristic:self.status];
}
- (void)peripheral:(CBPeripheral*)p didWriteValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e {
 if(p!=self.peer)return;
 if(self.abortOnly){
  if(self.phase!=6||c!=self.control||e){[self fail:@"ABORT response failed or unexpected"];return;}
  self.phase=7;[p readValueForCharacteristic:self.status];return;
 }
 if((self.phase==2&&c!=self.data)||((self.phase==1||self.phase==3)&&c!=self.control)){
  [self fail:@"write callback characteristic/phase mismatch"];return;
 }
 if(e){[self fail:e.localizedDescription];return;}
 if(self.phase==1||self.phase==3){printf("CONTROL ACK: phase=%d; reading application status\n",self.phase);[p readValueForCharacteristic:self.status];return;}
 if(self.phase!=2){[self fail:@"unexpected write response"];return;}
 self.offset+=self.pending;
 if(self.offset-self.confirmed>=4096||(self.pauseAfter&&self.offset>=self.pauseAfter)){
  self.phase=4;[p readValueForCharacteristic:self.status];return;
 }
 [self scheduleNext];
}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e {
 if(p!=self.peer)return;
 if(e||c!=self.status||c.value.length!=60){[self fail:@"invalid application status"];return;}
 if(self.queryOnly||self.abortOnly){
  const uint8_t*raw=c.value.bytes;
  if(memcmp(raw,"RFS\1",4)||raw[20]>4||raw[22]||raw[23]||rs_u32(raw+12)>rs_u32(raw+16)||rs_u32(raw+16)>262176){[self fail:@"invalid read-only status envelope"];return;}
  printf("RFS STATUS HEX=");for(unsigned i=0;i<60;i++)printf("%02x",raw[i]);puts("");
  printf("READ-ONLY STATUS (NOT ATTESTATION): state=%u error=%u received=%u length=%u receipt_counter=%u saved_session_matches=%s\n",raw[20],raw[21],rs_u32(raw+12),rs_u32(raw+16),rs_u32(raw+24),memcmp(raw+4,self.nonce.bytes,8)?"no":"yes");
  if(self.abortOnly){
   if(memcmp(raw+4,self.nonce.bytes,8)){[self fail:@"ABORT requires exact saved session"];return;}
   if(self.phase==5){
    if(raw[20]!=1||rs_u32(raw+16)!=self.stream.length){[self fail:@"ABORT allowed only for exact staging session"];return;}
    uint8_t abort[9]={3};memcpy(abort+1,self.nonce.bytes,8);self.phase=6;
    puts("ABORT: exact saved STAGING session only; no DATA or COMMIT");
    [p writeValue:[NSData dataWithBytes:abort length:9] forCharacteristic:self.control type:CBCharacteristicWriteWithResponse];return;
   }
   if(self.phase!=7||raw[20]!=0||rs_u32(raw+12)||rs_u32(raw+16)){[self fail:@"ABORT idle state not confirmed"];return;}
   puts("ABORT CONFIRMED (NOT ATTESTATION): exact session idle, length=0 received=0");
  }
  self.finished=YES;[self.central cancelPeripheralConnection:self.peer];exit(0);
 }
 uint32_t received=0;int outcome=rs_status(c.value.bytes,c.value.length,self.nonce.bytes,
  self.expectedDigest.bytes,self.counter,(uint32_t)self.stream.length,&received);
 if(outcome==RS_INVALID){[self fail:@"receipt session/length/state/identity mismatch"];return;}
 if(outcome==RS_REJECTED){
  self.finished=YES;puts("FILE REJECTED RECEIPT (NOT ATTESTATION): exact SHA256/session/counter matched; error=2; NOT APPLIED");
  printf("TRANSFER ELAPSED=%.3f seconds (including reconnects)\n",NSProcessInfo.processInfo.systemUptime-self.startedAt);
  [self.central cancelPeripheralConnection:self.peer];exit(2);
 }
 if(outcome==RS_APPLIED){
  self.finished=YES;puts("FILE APPLIED RECEIPT (NOT ATTESTATION): exact SHA256/session/counter matched");
  printf("TRANSFER ELAPSED=%.3f seconds (including reconnects)\n",NSProcessInfo.processInfo.systemUptime-self.startedAt);
  [self.central cancelPeripheralConnection:self.peer];exit(0);
 }
 if(outcome==RS_PENDING){
  CBPeripheral*waitingPeer=self.peer;CBCharacteristic*waitingStatus=self.status;
  self.phase=3;[NSTimer scheduledTimerWithTimeInterval:0.2 repeats:NO block:^(NSTimer*t){
   (void)t;if(self.phase==3&&self.peer==waitingPeer&&self.status==waitingStatus)
    [waitingPeer readValueForCharacteristic:waitingStatus];}];return;
 }
 if(self.phase!=1&&self.phase!=4){[self fail:@"final receipt absent or unexpected status phase"];return;}
 if(!rs_resume_allowed(received,(uint32_t)self.confirmed,(uint32_t)self.minimumReceived)){
  printf("RECEIVER STAGING REGRESSED: previously confirmed=%lu now=%u; receiver reset/loss possible, NOT same-boot resume\n",(unsigned long)MAX(self.confirmed,self.minimumReceived),received);
  [self fail:@"receiver staging regressed; inspect Dell state before resuming SAME session"];return;
 }
 self.offset=self.confirmed=received;
 printf(self.phase==4?"STAGING CHECKPOINT=%lu/%lu (not applied)\n":"RESUME OFFSET=%lu/%lu\n",(unsigned long)self.offset,(unsigned long)self.stream.length);
 if(self.pauseAfter&&received>=self.pauseAfter){
  self.finished=YES;puts("STAGED-NOT-APPLIED: deliberate stop; keep Dell powered and rerun SAME saved session without --stage-only-bytes");
  [self.central cancelPeripheralConnection:self.peer];exit(0);
 }
 [self scheduleNext];
}
@end
int main(int argc,char**argv){@autoreleasepool{
 setvbuf(stdout,NULL,_IONBF,0);
 if(argc<2||argc>11)return 2;
 NSData*raw=[NSData dataWithContentsOfFile:[NSString stringWithUTF8String:argv[1]]];
 NSDictionary*b=raw?[NSJSONSerialization JSONObjectWithData:raw options:0 error:nil]:nil;
 if(![b isKindOfClass:NSDictionary.class]||![b[@"stream_base64"] isKindOfClass:NSString.class]||![b[@"session_base64"] isKindOfClass:NSString.class]||![b[@"counter"] isKindOfClass:NSNumber.class])return 2;
 if([b[@"counter"] unsignedLongLongValue]>0xffffffffull)return 2;
 id kind=b[@"kind"];if(kind&&![kind isKindOfClass:NSNumber.class])return 2;
 Sender*s=[Sender new];s.stream=[[NSData alloc]initWithBase64EncodedString:b[@"stream_base64"] options:0];s.nonce=[[NSData alloc]initWithBase64EncodedString:b[@"session_base64"] options:0];s.counter=[b[@"counter"] unsignedIntValue];s.kind=kind?[kind unsignedIntValue]:1;
 if((s.kind!=1&&s.kind!=2)||s.stream.length<=32||s.stream.length>(s.kind==1?65567u:262176u)||s.nonce.length!=8||!s.counter)return 2;
 s.chunkBytes=240;BOOL chunkSpecified=NO,delaySpecified=NO,minimumSpecified=NO;
 for(int i=2;i<argc;i++){
  if(!strcmp(argv[i],"--query-only")){if(s.queryOnly)return 2;s.queryOnly=YES;}
  else if(!strcmp(argv[i],"--abort-only")){if(s.abortOnly)return 2;s.abortOnly=YES;}
  else if(!strcmp(argv[i],"--peripheral")){
   if(++i>=argc||s.queryPeripheral)return 2;s.queryPeripheral=[[NSUUID alloc]initWithUUIDString:[NSString stringWithUTF8String:argv[i]]];if(!s.queryPeripheral)return 2;
  }else if(!strcmp(argv[i],"--chunk-bytes")){
   if(++i>=argc||chunkSpecified)return 2;char*end=0;unsigned long value=strtoul(argv[i],&end,10);
   if(!argv[i][0]||*end||!value||value>240)return 2;s.chunkBytes=value;chunkSpecified=YES;
  }else if(!strcmp(argv[i],"--minimum-received")){
   if(++i>=argc||minimumSpecified)return 2;char*end=0;unsigned long value=strtoul(argv[i],&end,10);
   if(!argv[i][0]||*end||value>s.stream.length)return 2;s.minimumReceived=value;minimumSpecified=YES;
  }else if(!strcmp(argv[i],"--data-delay-ms")){
   if(++i>=argc||delaySpecified)return 2;char*end=0;unsigned long value=strtoul(argv[i],&end,10);
   if(!argv[i][0]||*end||!value||value>100)return 2;s.dataDelayMs=value;delaySpecified=YES;
  }else{
   char*end=0;unsigned long value=strtoul(argv[i],&end,10);
   if(!argv[i][0]||*end||!value||value>=s.stream.length||s.pauseAfter)return 2;s.pauseAfter=value;
  }
 }
 if((s.queryOnly&&s.abortOnly)||(s.queryPeripheral&&!s.queryOnly)||((s.queryOnly||s.abortOnly)&&(s.pauseAfter||chunkSpecified||minimumSpecified)))return 2;
 if(delaySpecified&&(!s.pauseAfter||s.queryOnly||s.abortOnly))return 2;
 if(delaySpecified)printf("STAGING DIAGNOSTIC DATA DELAY=%lu ms; NO COMMIT\n",(unsigned long)s.dataDelayMs);
 if(!s.queryOnly&&!s.abortOnly)printf("DATA CHUNK LIMIT=%lu bytes (excluding offset)\n",(unsigned long)s.chunkBytes);
 unsigned char hash[32];CC_SHA256((const uint8_t*)s.stream.bytes+32,(CC_LONG)s.stream.length-32,hash);
 if(memcmp(hash,s.stream.bytes,32))return 2;s.expectedDigest=[NSData dataWithBytes:hash length:32];
 s.startedAt=NSProcessInfo.processInfo.systemUptime;
 s.central=[[CBCentralManager alloc]initWithDelegate:s queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:s.queryOnly?60:300 repeats:NO block:^(NSTimer*t){(void)t;[s fail:s.queryOnly?@"60-second read-only query timeout":@"300-second bounded timeout"];}];
 [[NSRunLoop currentRunLoop]run];
 }return 1;}
