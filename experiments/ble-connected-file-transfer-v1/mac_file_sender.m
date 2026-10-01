/* Mac central: acknowledged GATT writes, final application receipt required.
 * Candidate only: Dell does not yet expose this service. No pairing is requested.
 * UUID match is discovery, NOT authentication or confidential transport. */
#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#import <CommonCrypto/CommonDigest.h>
#include <stdio.h>
#include <string.h>
static NSString *const Service=@"52414242-4954-4649-8000-000000000001";
static uint32_t le32(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put32(uint8_t*p,uint32_t n){for(int i=0;i<4;i++)p[i]=n>>(8*i);}
@interface Sender:NSObject<CBCentralManagerDelegate,CBPeripheralDelegate>
@property(nonatomic,strong) CBCentralManager *central;
@property(nonatomic,strong) CBPeripheral *peer;
@property(nonatomic,strong) CBCharacteristic *control,*data,*status;
@property(nonatomic,strong) NSData *stream,*nonce,*hash;
@property NSUInteger offset,pending;
@property uint32_t counter;
@property int phase;
@property BOOL finished;
- (void)fail:(NSString*)why;
- (void)next;
@end
@implementation Sender
- (void)fail:(NSString*)why {fprintf(stderr,"FAIL: %s; application outcome may be unknown; staging retained if Dell remains powered\n",why.UTF8String);[self.central stopScan];if(self.peer)[self.central cancelPeripheralConnection:self.peer];exit(1);}
- (void)centralManagerDidUpdateState:(CBCentralManager*)central {
 if(central.state==CBManagerStatePoweredOn){puts("SCANNING FOR RABBIT FILE SERVICE (not identity authentication)");[central scanForPeripheralsWithServices:@[[CBUUID UUIDWithString:Service]] options:nil];}
 else if(central.state==CBManagerStatePoweredOff||central.state==CBManagerStateUnauthorized||central.state==CBManagerStateUnsupported)[self fail:@"Bluetooth unavailable"];
}
- (void)centralManager:(CBCentralManager*)c didDiscoverPeripheral:(CBPeripheral*)p advertisementData:(NSDictionary*)ad RSSI:(NSNumber*)rssi {
 (void)ad;(void)rssi;if(self.peer)return;self.peer=p;p.delegate=self;[c stopScan];[c connectPeripheral:p options:nil];
}
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p {(void)c;[p discoverServices:@[[CBUUID UUIDWithString:Service]]];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e {(void)c;(void)p;[self fail:e.localizedDescription?:@"connect failed"];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e {(void)c;(void)p;if(!self.finished)[self fail:e.localizedDescription?:@"disconnected before final receipt"];}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e {
 if(e||p.services.count!=1){[self fail:@"service discovery failed"];return;}
 [p discoverCharacteristics:nil forService:p.services[0]];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)service error:(NSError*)e {
 if(e){[self fail:e.localizedDescription];return;}
 for(CBCharacteristic*c in service.characteristics){NSString*u=c.UUID.UUIDString;
  if([u isEqualToString:@"52414242-4954-4649-8000-000000000002"])self.control=c;
  if([u isEqualToString:@"52414242-4954-4649-8000-000000000003"])self.data=c;
  if([u isEqualToString:@"52414242-4954-4649-8000-000000000004"])self.status=c;
 }
 if(!self.control||!self.data||!self.status||!(self.control.properties&CBCharacteristicPropertyWrite)||!(self.data.properties&CBCharacteristicPropertyWrite)||!(self.status.properties&CBCharacteristicPropertyRead)){[self fail:@"incompatible file service"];return;}
 uint8_t begin[16]={1,1,1,0};memcpy(begin+4,self.nonce.bytes,8);put32(begin+12,(uint32_t)self.stream.length);
 self.phase=1;[p writeValue:[NSData dataWithBytes:begin length:16] forCharacteristic:self.control type:CBCharacteristicWriteWithResponse];
}
- (void)next {
 if(self.offset==self.stream.length){uint8_t commit[9]={2};memcpy(commit+1,self.nonce.bytes,8);self.phase=3;[self.peer writeValue:[NSData dataWithBytes:commit length:9] forCharacteristic:self.control type:CBCharacteristicWriteWithResponse];return;}
 NSUInteger limit=MIN((NSUInteger)244,[self.peer maximumWriteValueLengthForType:CBCharacteristicWriteWithResponse]);
 if(limit<=4){[self fail:@"write MTU too small"];return;}
 self.pending=MIN(limit-4,self.stream.length-self.offset);
 NSMutableData*value=[NSMutableData dataWithLength:4+self.pending];put32(value.mutableBytes,(uint32_t)self.offset);memcpy((uint8_t*)value.mutableBytes+4,(const uint8_t*)self.stream.bytes+self.offset,self.pending);
 self.phase=2;[self.peer writeValue:value forCharacteristic:self.data type:CBCharacteristicWriteWithResponse];
}
- (void)peripheral:(CBPeripheral*)p didWriteValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e {
 (void)c;if(e){[self fail:e.localizedDescription];return;}
 if(self.phase==1||self.phase==3){[p readValueForCharacteristic:self.status];return;}
 if(self.phase!=2){[self fail:@"unexpected write response"];return;}
 self.offset+=self.pending;[self next];
}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e {
 (void)p;if(e||c!=self.status||c.value.length!=60){[self fail:@"invalid application status"];return;}
 const uint8_t*b=c.value.bytes;
 if(memcmp(b,"RFS\1",4)||memcmp(b+4,self.nonce.bytes,8)||le32(b+16)!=self.stream.length||b[22]||b[23]){[self fail:@"receipt session/length mismatch"];return;}
 if(b[20]==2){
  if(le32(b+12)!=self.stream.length||le32(b+24)!=self.counter||memcmp(b+28,self.hash.bytes,32)){[self fail:@"applied receipt identity mismatch"];return;}
  self.finished=YES;puts("FILE APPLIED RECEIPT (NOT ATTESTATION): exact SHA256/session/counter matched");[self.central cancelPeripheralConnection:self.peer];exit(0);
 }
 if(self.phase==3||b[20]!=1||b[21]||le32(b+12)>self.stream.length){[self fail:@"world rejected or final receipt absent"];return;}
 self.offset=le32(b+12);printf("RESUME OFFSET=%lu/%lu\n",(unsigned long)self.offset,(unsigned long)self.stream.length);[self next];
}
@end
int main(int argc,char**argv){@autoreleasepool{
 if(argc!=2)return 2;
 NSData*raw=[NSData dataWithContentsOfFile:[NSString stringWithUTF8String:argv[1]]];
 NSDictionary*b=raw?[NSJSONSerialization JSONObjectWithData:raw options:0 error:nil]:nil;
 if(![b isKindOfClass:NSDictionary.class]||![b[@"stream_base64"] isKindOfClass:NSString.class]||![b[@"session_base64"] isKindOfClass:NSString.class]||![b[@"counter"] isKindOfClass:NSNumber.class])return 2;
 Sender*s=[Sender new];s.stream=[[NSData alloc]initWithBase64EncodedString:b[@"stream_base64"] options:0];s.nonce=[[NSData alloc]initWithBase64EncodedString:b[@"session_base64"] options:0];s.counter=[b[@"counter"] unsignedIntValue];
 if(s.stream.length<=32||s.stream.length>65567||s.nonce.length!=8||!s.counter)return 2;
 unsigned char hash[32];CC_SHA256((const uint8_t*)s.stream.bytes+32,(CC_LONG)s.stream.length-32,hash);
 if(memcmp(hash,s.stream.bytes,32))return 2;s.hash=[NSData dataWithBytes:hash length:32];
 s.central=[[CBCentralManager alloc]initWithDelegate:s queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:300 repeats:NO block:^(NSTimer*t){(void)t;[s fail:@"300-second bounded timeout"];}];
 [[NSRunLoop currentRunLoop]run];
 }return 1;}
