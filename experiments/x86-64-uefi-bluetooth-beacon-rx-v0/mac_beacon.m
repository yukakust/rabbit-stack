#import <CoreBluetooth/CoreBluetooth.h>
#import <Foundation/Foundation.h>

#include <stdio.h>
#include <stdlib.h>

static NSString *const RabbitUUID = @"52414242-4954-4C45-8000-000000000001";

@interface RabbitBeacon : NSObject <CBPeripheralManagerDelegate>
@property(nonatomic, strong) CBPeripheralManager *manager;
@end

@implementation RabbitBeacon

- (instancetype)init {
    self = [super init];
    if (self != nil) {
        self.manager = [[CBPeripheralManager alloc]
            initWithDelegate:self
                       queue:dispatch_get_main_queue()
                     options:@{CBPeripheralManagerOptionShowPowerAlertKey : @YES}];
    }
    return self;
}

- (void)peripheralManagerDidUpdateState:(CBPeripheralManager *)peripheral {
    switch (peripheral.state) {
    case CBManagerStatePoweredOn:
        [peripheral startAdvertising:@{
            CBAdvertisementDataServiceUUIDsKey : @[[CBUUID UUIDWithString:RabbitUUID]]
        }];
        break;
    case CBManagerStateUnauthorized:
        fprintf(stderr,
                "FAIL: Bluetooth permission was not granted to this terminal application\n");
        exit(2);
    case CBManagerStateUnsupported:
        fprintf(stderr, "FAIL: this Mac does not support Bluetooth LE peripheral mode\n");
        exit(2);
    case CBManagerStatePoweredOff:
        fprintf(stdout, "WAIT: turn Bluetooth on\n");
        fflush(stdout);
        break;
    default:
        fprintf(stdout, "WAIT: CoreBluetooth state %ld\n", (long)peripheral.state);
        fflush(stdout);
        break;
    }
}

- (void)peripheralManagerDidStartAdvertising:(CBPeripheralManager *)peripheral
                                       error:(NSError *)error {
    (void)peripheral;
    if (error != nil) {
        fprintf(stderr, "FAIL: could not advertise Rabbit UUID: %s\n",
                error.localizedDescription.UTF8String);
        exit(2);
    }
    fprintf(stdout, "RABBIT BEACON ADVERTISING\n");
    fprintf(stdout, "UUID=52414242-4954-4C45-8000-000000000001\n");
    fprintf(stdout,
            "Keep this process running while the Dell performs its 20-second passive scan.\n");
    fflush(stdout);
}

@end


int main(void) {
    @autoreleasepool {
        RabbitBeacon *beacon = [[RabbitBeacon alloc] init];
        (void)beacon;
        [[NSRunLoop currentRunLoop] run];
    }
    return 0;
}
