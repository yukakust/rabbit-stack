/* Public signed executable chunk transport. UUID/receipt is NOT identity
 * authentication or confidential provisioning. No signer or secret API. */
#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#import <CommonCrypto/CommonDigest.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint32_t r32(const uint8_t*p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static uint64_t r64(const uint8_t*p){return r32(p)|(uint64_t)r32(p+4)<<32;}
static void w32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=v>>(i*8);}
static NSString*const svc=@"52414242-4954-4649-8000-000000000021";
@interface ModuleSender:NSObject<CBCentralManagerDelegate,CBPeripheralDelegate>
@property(nonatomic,strong)CBCentralManager*central;
@property(nonatomic,strong)CBPeripheral*peer;
@property(nonatomic,strong)CBCharacteristic*control,*data,*status;
@property(nonatomic,strong)NSData*chunk,*session,*digest,*previous;
@property(nonatomic,strong)NSUUID*peripheral;
@property(nonatomic,strong)NSString*receiptPath;
@property uint64_t epoch;
@property NSUInteger offset,pending,confirmed,generation;
@property int phase;
@property BOOL finished;
@property NSTimeInterval started;
- (void)fail:(NSString*)why;
- (void)next;
- (void)begin;
@end
@implementation ModuleSender
- (void)begin{uint8_t b[45]={1};memcpy(b+1,self.session.bytes,8);w32(b+9,(uint32_t)self.chunk.length);memcpy(b+13,self.digest.bytes,32);self.phase=2;[self.peer writeValue:[NSData dataWithBytes:b length:45] forCharacteristic:self.control type:CBCharacteristicWriteWithResponse];}
- (void)fail:(NSString*)why{fprintf(stderr,"MODULE FAILURE: %s; retained exact saved session required, no automatic resign/overwrite\n",why.UTF8String);[self.central stopScan];if(self.peer)[self.central cancelPeripheralConnection:self.peer];exit(1);}
- (void)centralManagerDidUpdateState:(CBCentralManager*)c{
 if(c.state==CBManagerStatePoweredOn){NSArray<CBPeripheral*>*ps=[c retrievePeripheralsWithIdentifiers:@[self.peripheral]];if(ps.count!=1){[self fail:@"exact cached peripheral unavailable"];return;}self.peer=ps[0];self.peer.delegate=self;[c connectPeripheral:self.peer options:nil];}
 else if(c.state==CBManagerStatePoweredOff||c.state==CBManagerStateUnauthorized||c.state==CBManagerStateUnsupported)[self fail:@"Bluetooth unavailable"];
}
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p{(void)c;if(p!=self.peer)return;self.generation++;[p discoverServices:@[[CBUUID UUIDWithString:svc]]];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;[self fail:e.localizedDescription?:@"connect failed"];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;if(p!=self.peer||self.finished)return;self.generation++;[self fail:e.localizedDescription?:@"disconnected; resume same session after fresh status"];}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e{
 if(p!=self.peer)return;if(e||p.services.count!=1||![p.services[0].UUID isEqual:[CBUUID UUIDWithString:svc]]){[self fail:@"exact module service missing"];return;}[p discoverCharacteristics:nil forService:p.services[0]];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)s error:(NSError*)e{
 if(p!=self.peer)return;if(e||![s.UUID isEqual:[CBUUID UUIDWithString:svc]]){[self fail:@"characteristic discovery"];return;}
 for(CBCharacteristic*c in s.characteristics){NSString*u=c.UUID.UUIDString;if([u isEqualToString:@"52414242-4954-4649-8000-000000000022"])self.control=c;if([u isEqualToString:@"52414242-4954-4649-8000-000000000023"])self.data=c;if([u isEqualToString:@"52414242-4954-4649-8000-000000000024"])self.status=c;}
 if(!self.control||!self.data||!self.status||!(self.control.properties&CBCharacteristicPropertyWrite)||!(self.data.properties&CBCharacteristicPropertyWrite)||!(self.status.properties&CBCharacteristicPropertyRead)||[p maximumWriteValueLengthForType:CBCharacteristicWriteWithResponse]<45){[self fail:@"bounded module characteristics/MTU unavailable"];return;}
 self.phase=1;[p readValueForCharacteristic:self.status]; /* read BEFORE BEGIN */
}
- (void)next{
 if(self.offset>=self.chunk.length){uint8_t b[9]={3};memcpy(b+1,self.session.bytes,8);self.phase=4;[self.peer writeValue:[NSData dataWithBytes:b length:9] forCharacteristic:self.control type:CBCharacteristicWriteWithResponse];return;}
 NSUInteger max=MIN((NSUInteger)244,[self.peer maximumWriteValueLengthForType:CBCharacteristicWriteWithResponse]);if(max<14){[self fail:@"data MTU"];return;}self.pending=MIN(max-13,self.chunk.length-self.offset);
 NSMutableData*b=[NSMutableData dataWithLength:13+self.pending];uint8_t*p=b.mutableBytes;p[0]=2;memcpy(p+1,self.session.bytes,8);w32(p+9,(uint32_t)self.offset);memcpy(p+13,(const uint8_t*)self.chunk.bytes+self.offset,self.pending);self.phase=3;[self.peer writeValue:b forCharacteristic:self.data type:CBCharacteristicWriteWithResponse];
}
- (void)peripheral:(CBPeripheral*)p didWriteValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e{
 if(p!=self.peer)return;if(e||!((self.phase==3&&c==self.data)||((self.phase==2||self.phase==4)&&c==self.control))){[self fail:@"write error/phase mismatch"];return;}
 if(self.phase==3){self.offset+=self.pending;if(self.offset-self.confirmed<2048&&self.offset<self.chunk.length){[self next];return;}}
 self.phase=5;[p readValueForCharacteristic:self.status];
}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e{
 if(p!=self.peer)return;if(e||c!=self.status||c.value.length!=80||(self.phase!=1&&self.phase!=5&&self.phase!=6)){[self fail:@"invalid status callback"];return;}
 const uint8_t*r=c.value.bytes;uint32_t state=r32(r+16),error=r32(r+20),length=r32(r+24),received=r32(r+28);int32_t result=(int32_t)r32(r+32);
 if(memcmp(r,"QMT00001",8)||r64(r+8)!=self.epoch||state>5||r32(r+36)||length>65824||received>length){[self fail:@"status envelope/epoch mismatch"];return;}
 if(!state){unsigned n=0;for(unsigned i=16;i<80;i++)n|=r[i];if(n||self.phase!=1){[self fail:@"noncanonical or unexpected IDLE"];return;}[self begin];return;}
 if(self.phase==1&&state==3&&self.previous.length==80&&[self.previous isEqualToData:c.value]&&!error&&result>=0&&received==length&&length>=289&&memcmp(r+40,self.session.bytes,8)){[self begin];return;}
 if(memcmp(r+40,self.session.bytes,8)||memcmp(r+48,self.digest.bytes,32)||length!=self.chunk.length){[self fail:@"different retained session; manual inspected transition required"];return;}
 if((state<=3&&error)||(state==3&&result<0)||((state==1||state==2)&&result)||((state==2||state==3)&&received!=length)){[self fail:@"contradictory acceptance"];return;}
 if(state>=4){[self fail:@"retained rejected/closed state"];return;}
 if(self.phase!=1&&received<self.confirmed){[self fail:@"confirmed progress regressed"];return;}
 NSError*save=nil;if(![c.value writeToFile:self.receiptPath options:NSDataWritingAtomic error:&save]){[self fail:save.localizedDescription?:@"durable receipt save failed"];return;}
 self.confirmed=received;printf("MODULE STATUS state=%u received=%u/%u result=%d; NOT device attestation\n",state,received,length,result);fflush(stdout);
 if(state==3){self.finished=YES;puts("EXACT CHUNK ACCEPTED; complete module/entropy/WIFI not inferred");[self.central cancelPeripheralConnection:p];exit(0);}
 if(state==2){self.phase=6;NSUInteger g=self.generation;[NSTimer scheduledTimerWithTimeInterval:0.02 repeats:NO block:^(NSTimer*t){(void)t;if(!self.finished&&self.phase==6&&g==self.generation&&p==self.peer)[p readValueForCharacteristic:self.status];}];return;}
 self.offset=received;[self next];
}
@end
int main(int argc,const char**argv){@autoreleasepool{
 if(argc==2&&!strcmp(argv[1],"--preflight")){puts("PUBLIC-MODULE-MAC-PREFLIGHT; manager=0 writes=0 keys=0");return 0;}
 if(argc!=8){fprintf(stderr,"saved chunk session8 epoch peripheral receipt previous-or-dash required\n");return 2;}
 ModuleSender*s=[ModuleSender new];s.chunk=[NSData dataWithContentsOfFile:@(argv[1])];s.session=[NSData dataWithContentsOfFile:@(argv[2])];s.peripheral=[[NSUUID alloc]initWithUUIDString:@(argv[4])];s.receiptPath=@(argv[5]);char*end=NULL;s.epoch=strtoull(argv[3],&end,10);
 if(strcmp(argv[6],"-"))s.previous=[NSData dataWithContentsOfFile:@(argv[6])];
 if(strcmp(argv[7],"--public-signed-module-only")||(!s.previous&&strcmp(argv[6],"-"))||(s.previous&&s.previous.length!=80)||!s.chunk||s.chunk.length<289||s.chunk.length>65824||s.session.length!=8||!s.peripheral||!s.epoch||!end||*end){fprintf(stderr,"invalid saved public session\n");return 2;}
 const uint8_t*b=s.chunk.bytes;uint32_t role=r32(b+196);unsigned nz=0;for(unsigned i=0;i<8;i++)nz|=((const uint8_t*)s.session.bytes)[i];if(!nz||r32(b+200)!=1||!((role==1&&!memcmp(b,"RABMOD01",8))||(role==2&&!memcmp(b,"RABRSN01",8))))return 2;
 uint8_t hash[32];CC_SHA256(s.chunk.bytes,(CC_LONG)s.chunk.length,hash);s.digest=[NSData dataWithBytes:hash length:32];s.started=NSProcessInfo.processInfo.systemUptime;
 s.central=[[CBCentralManager alloc]initWithDelegate:s queue:dispatch_get_main_queue() options:nil];
 [NSTimer scheduledTimerWithTimeInterval:1 repeats:YES block:^(NSTimer*t){(void)t;if(!s.finished&&NSProcessInfo.processInfo.systemUptime-s.started>=600)[s fail:@"600s host bound; retained session only"]; }];
 [[NSRunLoop mainRunLoop]run];return 1;
}}
