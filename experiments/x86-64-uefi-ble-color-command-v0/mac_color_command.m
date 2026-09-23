#import <CoreBluetooth/CoreBluetooth.h>
#import <Foundation/Foundation.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

@interface RabbitColorCommand : NSObject <CBPeripheralManagerDelegate>
@property(nonatomic, strong) CBPeripheralManager *manager;
@property(nonatomic, copy) NSString *command;
@property(nonatomic, copy) NSString *uuid;
@end

@implementation RabbitColorCommand
- (instancetype)initWithCommand:(NSString *)command uuid:(NSString *)uuid {
    self = [super init];
    if (self != nil) {
        self.command = command;
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
    } else {
        fprintf(stdout, "WAIT: CoreBluetooth state %ld\n", (long)peripheral.state);
        fflush(stdout);
    }
}

- (void)peripheralManagerDidStartAdvertising:(CBPeripheralManager *)peripheral
                                       error:(NSError *)error {
    (void)peripheral;
    if (error != nil) {
        fprintf(stderr, "FAIL: could not advertise command: %s\n",
                error.localizedDescription.UTF8String); exit(2);
    }
    fprintf(stdout, "RABBIT COLOR COMMAND ADVERTISING\nCOMMAND=%s\nUUID=%s\n",
            self.command.UTF8String, self.uuid.UTF8String);
    fprintf(stdout, "Leave this running until Dell reports the command; then press Ctrl-C.\n");
    fflush(stdout);
}
@end

int main(int argc, const char *argv[]) {
    if (argc != 2 || (strcmp(argv[1], "blue") != 0 && strcmp(argv[1], "yellow") != 0)) {
        fprintf(stderr, "usage: rabbit-color-command blue|yellow\n"); return 2;
    }
    @autoreleasepool {
        NSString *command = [NSString stringWithUTF8String:argv[1]];
        NSString *uuid = [command isEqualToString:@"blue"]
            ? @"52414242-4954-4C45-8000-000000000002"
            : @"52414242-4954-4C45-8000-000000000003";
        RabbitColorCommand *sender = [[RabbitColorCommand alloc] initWithCommand:command uuid:uuid];
        (void)sender;
        [[NSRunLoop currentRunLoop] run];
    }
    return 0;
}
