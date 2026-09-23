#import <CoreBluetooth/CoreBluetooth.h>
#import <Foundation/Foundation.h>

#include <stdio.h>
#include <stdlib.h>

@interface RabbitProgramSender : NSObject <CBPeripheralManagerDelegate>
@property(nonatomic, strong) CBPeripheralManager *manager;
@property(nonatomic, copy) NSString *uuid;
@end

@implementation RabbitProgramSender
- (instancetype)initWithUUID:(NSString *)uuid {
    self = [super init];
    if (self != nil) {
        self.uuid = uuid;
        self.manager = [[CBPeripheralManager alloc]
            initWithDelegate:self queue:dispatch_get_main_queue()
            options:@{CBPeripheralManagerOptionShowPowerAlertKey : @YES}];
    }
    return self;
}

- (void)peripheralManagerDidUpdateState:(CBPeripheralManager *)peripheral {
    if (peripheral.state == CBManagerStatePoweredOn) {
        [peripheral startAdvertising:@{
            CBAdvertisementDataServiceUUIDsKey : @[[CBUUID UUIDWithString:self.uuid]]
        }];
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
        fprintf(stderr, "FAIL: could not advertise Rabbit VM program: %s\n",
                error.localizedDescription.UTF8String); exit(2);
    }
    fprintf(stdout, "RABBIT VM PROGRAM ADVERTISING\nUUID=%s\n",
            self.uuid.UTF8String);
    fprintf(stdout, "Leave this running until Dell reports PROGRAM APPLIED; then press Ctrl-C.\n");
    fflush(stdout);
}
@end

int main(int argc, const char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "usage: rabbit-vm-program UUID\n"); return 2;
    }
    @autoreleasepool {
        NSString *uuid = [NSString stringWithUTF8String:argv[1]];
        RabbitProgramSender *sender = [[RabbitProgramSender alloc] initWithUUID:uuid];
        (void)sender;
        [[NSRunLoop currentRunLoop] run];
    }
    return 0;
}

