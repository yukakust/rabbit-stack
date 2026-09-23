#import <CoreBluetooth/CoreBluetooth.h>
#import <Foundation/Foundation.h>

#include <stdio.h>
#include <stdlib.h>

@interface RabbitProgramSender : NSObject <CBPeripheralManagerDelegate>
@property(nonatomic, strong) CBPeripheralManager *manager;
@property(nonatomic, strong) NSArray<NSString *> *uuids;
@property(nonatomic) NSUInteger index;
@property(nonatomic, strong) NSTimer *timer;
@end

@implementation RabbitProgramSender
- (instancetype)initWithUUIDs:(NSArray<NSString *> *)uuids {
    self = [super init];
    if (self != nil) {
        self.uuids = uuids; self.index = 0;
        self.manager = [[CBPeripheralManager alloc]
            initWithDelegate:self queue:dispatch_get_main_queue()
            options:@{CBPeripheralManagerOptionShowPowerAlertKey : @YES}];
    }
    return self;
}

- (void)advertiseCurrent {
    [self.manager stopAdvertising];
    NSString *uuid = self.uuids[self.index];
    [self.manager startAdvertising:@{
        CBAdvertisementDataServiceUUIDsKey : @[[CBUUID UUIDWithString:uuid]]
    }];
    fprintf(stdout, "FRAME %lu/%lu UUID=%s\n", (unsigned long)(self.index + 1),
            (unsigned long)self.uuids.count, uuid.UTF8String); fflush(stdout);
    self.index = (self.index + 1) % self.uuids.count;
}

- (void)advance:(NSTimer *)timer { (void)timer; [self advertiseCurrent]; }

- (void)peripheralManagerDidUpdateState:(CBPeripheralManager *)peripheral {
    if (peripheral.state == CBManagerStatePoweredOn) {
        [self advertiseCurrent];
        self.timer = [NSTimer scheduledTimerWithTimeInterval:0.45 target:self
            selector:@selector(advance:) userInfo:nil repeats:YES];
    } else if (peripheral.state == CBManagerStateUnauthorized) {
        fprintf(stderr, "FAIL: Bluetooth permission was not granted\n"); exit(2);
    } else if (peripheral.state == CBManagerStateUnsupported) {
        fprintf(stderr, "FAIL: Bluetooth LE peripheral mode is unsupported\n"); exit(2);
    }
}

- (void)peripheralManagerDidStartAdvertising:(CBPeripheralManager *)peripheral
                                       error:(NSError *)error {
    (void)peripheral;
    if (error != nil) {
        fprintf(stderr, "FAIL: could not advertise Rabbit VM frame: %s\n",
                error.localizedDescription.UTF8String); exit(2);
    }
}
@end

int main(int argc, const char *argv[]) {
    if (argc < 2) { fprintf(stderr, "usage: rabbit-vm-program UUID...\n"); return 2; }
    @autoreleasepool {
        NSMutableArray<NSString *> *values = [NSMutableArray array];
        for (int i = 1; i < argc; ++i) [values addObject:[NSString stringWithUTF8String:argv[i]]];
        RabbitProgramSender *sender = [[RabbitProgramSender alloc] initWithUUIDs:values];
        (void)sender;
        fprintf(stdout, "RABBIT VM PROGRAM TRANSFER STARTED; repeating until Ctrl-C\n"); fflush(stdout);
        [[NSRunLoop currentRunLoop] run];
    }
    return 0;
}
