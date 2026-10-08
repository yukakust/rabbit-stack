/* HOST read-only: one known peer, one connection, sequential service discovery. */
#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static NSString*const peerID=@"F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF";
static CBUUID*uuid(unsigned n){return [CBUUID UUIDWithString:[NSString stringWithFormat:@"52414242-4954-4649-8000-%012x",n]];}
static unsigned services[3]={0x22,0x2e,0x2a},values[3]={0x23,0x2f,0x2b},sizes[3]={160,448,416};
static const char*magic[3]={"QWBT0001","QF630001","QSCN0001"};
static uint32_t le32(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static NSString*hex(NSData*d){const uint8_t*p=d.bytes;NSMutableString*s=[NSMutableString string];for(NSUInteger i=0;i<d.length;i++)[s appendFormat:@"%02x",p[i]];return s;}
@interface Collector:NSObject<CBCentralManagerDelegate,CBPeripheralDelegate>
@property CBCentralManager*central;
@property CBPeripheral*peer;
@property CBService*expectedService;
@property CBCharacteristic*expectedValue;
@property NSString*logPath;
@property unsigned index,phase;
@property BOOL monitor,finished,waiting,scanProfile;
@property double began,operationBegan,scanBegan;
@property NSMutableArray*reports;
@property NSString*terminalResult;
- (void)fail:(NSString*)message;
- (void)record:(NSString*)stage error:(NSError*)e raw:(NSData*)raw;
- (void)discover;
- (void)readProgress;
- (void)clockTick;
@end
@implementation Collector
- (void)fail:(NSString*)m{self.finished=YES;self.phase=5;fprintf(stderr,"COLLECTOR STOP: %s; no reconnect/write/readiness inferred\n",m.UTF8String);exit(1);}
- (void)record:(NSString*)stage error:(NSError*)e raw:(NSData*)raw{
 NSDictionary*v=@{@"timestamp_unix":@([NSDate date].timeIntervalSince1970),@"uptime_seconds":@([NSProcessInfo processInfo].systemUptime),@"stage":stage,@"index":@(self.index),@"peripheral":self.peer.identifier.UUIDString?:peerID,@"NSError_domain":e.domain?:@"",@"NSError_code":@(e.code),@"NSError_description":e.localizedDescription?:@"",@"raw_bytes":@(raw.length),@"raw_hex":hex(raw),@"cached_value_possible":@(e!=nil),@"writes":@0,@"device_attestation":@NO};
 NSData*j=[NSJSONSerialization dataWithJSONObject:v options:NSJSONWritingSortedKeys error:nil];
 int fd=open(self.logPath.fileSystemRepresentation,O_WRONLY|O_CREAT|O_APPEND|O_NOFOLLOW,0600);struct stat st;
 if(fd<0||fstat(fd,&st)||!S_ISREG(st.st_mode)){if(fd>=0)close(fd);[self fail:@"diagnostic open/regular file failure"];return;}
 const uint8_t*p=j.bytes;size_t left=j.length;while(left){ssize_t n=write(fd,p,left);if(n<=0){close(fd);[self fail:@"diagnostic append failed"];return;}p+=n;left-=(size_t)n;}
 if(write(fd,"\n",1)!=1||fsync(fd)){close(fd);[self fail:@"diagnostic fsync failure"];return;}close(fd);
 fd=open(self.logPath.stringByDeletingLastPathComponent.fileSystemRepresentation,O_RDONLY);if(fd<0||fsync(fd)){if(fd>=0)close(fd);[self fail:@"diagnostic directory fsync failure"];return;}close(fd);
}
- (void)stop:(NSString*)stage error:(NSError*)e raw:(NSData*)raw{[self record:stage error:e raw:raw];[self fail:stage];}
- (void)discover{if(self.finished||self.index>=(self.scanProfile?3u:2u)){[self fail:@"unexpected next service"];return;}self.phase=1;self.waiting=YES;self.operationBegan=[NSProcessInfo processInfo].systemUptime;[self.peer discoverServices:@[uuid(services[self.index])]];}
- (void)readProgress{if(self.finished||self.phase!=4){[self fail:@"unexpected monitor read"];return;}self.phase=3;self.waiting=YES;self.operationBegan=[NSProcessInfo processInfo].systemUptime;[self.peer readValueForCharacteristic:self.expectedValue];}
- (void)clockTick{if(self.finished)return;double now=[NSProcessInfo processInfo].systemUptime;if(now<self.began||now-self.began>=5520||(self.index>0&&(now<self.scanBegan||now-self.scanBegan>=90))||(self.waiting&&(now<self.operationBegan||now-self.operationBegan>=60))){[self stop:@"bounded-timeout" error:[NSError errorWithDomain:@"RabbitScan61Progress" code:1 userInfo:nil] raw:nil];}}
- (void)centralManagerDidUpdateState:(CBCentralManager*)c{
 if(c.state==CBManagerStatePoweredOn){if(self.peer){[self stop:@"duplicate manager power callback" error:nil raw:nil];return;}NSArray*known=[c retrievePeripheralsWithIdentifiers:@[[[NSUUID alloc]initWithUUIDString:peerID]]];if(known.count!=1){[self stop:@"known-peer-not-cached" error:nil raw:nil];return;}self.peer=known[0];self.peer.delegate=self;self.waiting=YES;self.operationBegan=[NSProcessInfo processInfo].systemUptime;[c connectPeripheral:self.peer options:nil];}
 else if(c.state==CBManagerStateUnauthorized||c.state==CBManagerStateUnsupported||c.state==CBManagerStatePoweredOff)[self stop:@"Bluetooth-unavailable" error:nil raw:nil];
}
- (void)centralManager:(CBCentralManager*)c didConnectPeripheral:(CBPeripheral*)p{(void)c;if(p!=self.peer||![p.identifier.UUIDString isEqual:peerID]){[self stop:@"wrong-connected-peer" error:nil raw:nil];return;}[self discover];}
- (void)centralManager:(CBCentralManager*)c didFailToConnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;[self stop:@"connect-failed" error:e raw:nil];}
- (void)centralManager:(CBCentralManager*)c didDisconnectPeripheral:(CBPeripheral*)p error:(NSError*)e{(void)c;(void)p;if(!self.finished)[self stop:@"disconnected" error:e raw:nil];exit(0);}
- (void)peripheral:(CBPeripheral*)p didDiscoverServices:(NSError*)e{
 [self record:@"service-discovery" error:e raw:nil];if(e||p!=self.peer||self.phase!=1){[self fail:@"unexpected service callback"];return;}
 CBService*found=nil;for(CBService*s in p.services)if([s.UUID isEqual:uuid(services[self.index])]){if(found){[self fail:@"duplicate requested service"];return;}found=s;}
 if(!found){[self fail:@"requested exact service absent"];return;}self.expectedService=found;self.phase=2;[p discoverCharacteristics:@[uuid(values[self.index])] forService:found];
}
- (void)peripheral:(CBPeripheral*)p didDiscoverCharacteristicsForService:(CBService*)s error:(NSError*)e{
 [self record:@"characteristic-discovery" error:e raw:nil];if(e||p!=self.peer||s!=self.expectedService||self.phase!=2){[self fail:@"unexpected characteristic discovery"];return;}
 CBCharacteristic*found=nil;for(CBCharacteristic*c in s.characteristics)if([c.UUID isEqual:uuid(values[self.index])]&&(c.properties&CBCharacteristicPropertyRead)){if(found){[self fail:@"duplicate requested characteristic"];return;}found=c;}
 if(!found){[self fail:@"requested exact value absent"];return;}self.expectedValue=found;self.phase=3;[p readValueForCharacteristic:found];
}
- (void)peripheral:(CBPeripheral*)p didUpdateValueForCharacteristic:(CBCharacteristic*)c error:(NSError*)e{
 [self record:@"value-read" error:e raw:c.value];NSData*raw=c.value;const uint8_t*b=raw.bytes;
 if(e||p!=self.peer||c!=self.expectedValue||self.phase!=3||self.index>=(self.scanProfile?3u:2u)||![c.UUID isEqual:uuid(values[self.index])]||raw.length!=sizes[self.index]||memcmp(b,magic[self.index],8)||(self.index==1&&le32(b+8+59*4)!=63)||(self.index==2&&(le32(b+8+60*4)!=63||le32(b+8+61*4)!=13))){[self fail:@"wrong/error/size/magic/generation read; saved raw first"];return;}
 self.waiting=NO;
 // QWBT has no generation. Its bytes are progress only; Root must bind the
 // exact current62 APPLIED session externally before starting this executable.
 if(self.index==0 && (le32(b+12)!=0 || le32(b+20)!=0)){[self fail:@"bootstrap error; raw saved"];return;}
 BOOL pending=self.index==0 ? le32(b+8)!=5 : le32(b+8+(self.index==1?44:4)*4)!=1;
 if(self.index==0 && le32(b+8)>5){[self fail:@"unknown bootstrap phase"];return;}
 if(self.index==1&&!pending){
  unsigned phase=le32(b+8);if(phase!=4&&phase!=5){[self fail:@"released pipeline has unknown/nonterminal phase"];return;}
  BOOL fault=phase==5;unsigned errs[7]={1,4,27,39,58,61,63};for(unsigned i=0;i<7;i++)if(le32(b+8+errs[i]*4))fault=YES;
  self.terminalResult=fault?@"RELEASED_DIAGNOSTIC_FAILURE":@"RELEASED_PARTIAL_PIPELINE";
 }
 if(self.index==2&&!pending&&(le32(b+8+1*4)||le32(b+8+6*4)||le32(b+8+10*4)||le32(b+8+35*4)||le32(b+8+56*4)||le32(b+8+57*4)))self.terminalResult=@"RELEASED_DIAGNOSTIC_FAILURE";
 if(self.index>0 && !pending){
  if((self.index==1&&(le32(b+8+55*4)!=12||le32(b+8+56*4)!=14||le32(b+8+57*4)!=4))||(self.index==2&&(le32(b+8+53*4)!=12||le32(b+8+54*4)!=14||le32(b+8+55*4)!=4))){[self fail:@"incomplete all14 release"];return;}
  for(unsigned n=self.index==1?45:44;n<=(self.index==1?54:52);n++)if(le32(b+8+n*4)){[self fail:@"release contradicts held owner"];return;}
 }
 if(pending){self.phase=4;unsigned delay=self.index==0?30:2;dispatch_after(dispatch_time(DISPATCH_TIME_NOW,delay*NSEC_PER_SEC),dispatch_get_main_queue(),^{if(!self.finished)[self readProgress];});return;}
 [self.reports addObject:@{@"format":[NSString stringWithUTF8String:magic[self.index]],@"raw_hex":hex(raw),@"writes":@0,@"device_attestation":@NO}];self.index++;
 if(self.index<(self.scanProfile?3u:2u)){self.scanBegan=[NSProcessInfo processInfo].systemUptime;[self discover];return;}
 NSData*j=[NSJSONSerialization dataWithJSONObject:@{@"generation":@62,@"peripheral":peerID,@"reports":self.reports,@"terminal_result":self.terminalResult?:@"UNCONFIRMED",@"raw_read_safe":@YES,@"partial_startup":@YES,@"writes":@0,@"device_attestation":@NO,@"readiness_verdict":@"GEN63 all14 quiescent only; Root validates exact current62 binding; no SSID/auth/IP verdict"} options:NSJSONWritingSortedKeys error:nil];fwrite(j.bytes,1,j.length,stdout);puts("");fflush(stdout);self.finished=YES;self.phase=5;[self.central cancelPeripheralConnection:self.peer];
}
@end
int main(int argc,const char**argv){@autoreleasepool{
 if(argc!=3&&argc!=4&&argc!=5)return 2;BOOL monitor=!strcmp(argv[1],"--monitor"),preflight=!strcmp(argv[1],"--preflight");if(!monitor&&!preflight)return 2;
 NSString*path=[NSString stringWithUTF8String:argv[2]];if(!path.isAbsolutePath||![[NSFileManager defaultManager]fileExistsAtPath:path.stringByDeletingLastPathComponent])return 2;
 if(preflight){puts("HOST COLLECTOR PREFLIGHT ONLY; NO MANAGER");return 0;}
 if(argc<4||strcmp(argv[3],"--root-authorized-read")||(argc==5&&strcmp(argv[4],"--scan-profile"))){fprintf(stderr,"Root sole-controller admission required\n");return 2;}
 Collector*r=[Collector new];r.logPath=path;r.monitor=monitor;r.scanProfile=argc==5;r.reports=[NSMutableArray array];r.began=r.operationBegan=[NSProcessInfo processInfo].systemUptime;r.waiting=YES;r.central=[[CBCentralManager alloc]initWithDelegate:r queue:nil];
 [NSTimer scheduledTimerWithTimeInterval:1 repeats:YES block:^(NSTimer*t){(void)t;[r clockTick];}];[[NSRunLoop mainRunLoop]run];return 1;
}}
