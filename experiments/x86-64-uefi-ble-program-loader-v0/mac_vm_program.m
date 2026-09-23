#import <CoreBluetooth/CoreBluetooth.h>
#import <Foundation/Foundation.h>

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

static uint32_t RabbitFNV1a(const uint8_t *bytes, NSUInteger count) {
    uint32_t value = 0x811C9DC5u;
    for (NSUInteger index = 0; index < count; ++index) {
        value ^= bytes[index]; value *= 0x01000193u;
    }
    return value;
}

@interface RabbitProgramSender : NSObject <CBPeripheralManagerDelegate, CBCentralManagerDelegate>
@property(nonatomic, strong) CBPeripheralManager *peripheral;
@property(nonatomic, strong) CBCentralManager *central;
@property(nonatomic, strong) NSArray<NSString *> *uuids;
@property(nonatomic) NSUInteger index;
@property(nonatomic, strong) NSTimer *timer;
@property(nonatomic) uint8_t expectedTransfer;
@property(nonatomic) uint32_t expectedHash;
@end

@implementation RabbitProgramSender
- (instancetype)initWithUUIDs:(NSArray<NSString *> *)uuids
              expectedTransfer:(uint8_t)transfer
                  expectedHash:(uint32_t)programHash {
    self = [super init];
    if (self != nil) {
        self.uuids = uuids; self.index = 0;
        self.expectedTransfer = transfer; self.expectedHash = programHash;
        self.peripheral = [[CBPeripheralManager alloc]
            initWithDelegate:self queue:dispatch_get_main_queue()
            options:@{CBPeripheralManagerOptionShowPowerAlertKey : @YES}];
        self.central = [[CBCentralManager alloc]
            initWithDelegate:self queue:dispatch_get_main_queue()
            options:@{CBCentralManagerOptionShowPowerAlertKey : @YES}];
    }
    return self;
}

- (void)advertiseCurrent {
    [self.peripheral stopAdvertising];
    NSString *uuid = self.uuids[self.index];
    [self.peripheral startAdvertising:@{
        CBAdvertisementDataServiceUUIDsKey : @[[CBUUID UUIDWithString:uuid]]
    }];
    fprintf(stdout, "FRAME %lu/%lu UUID=%s\n", (unsigned long)(self.index + 1),
            (unsigned long)self.uuids.count, uuid.UTF8String); fflush(stdout);
    self.index = (self.index + 1) % self.uuids.count;
}

- (void)centralManagerDidUpdateState:(CBCentralManager *)central {
    if (central.state == CBManagerStatePoweredOn) {
        [central scanForPeripheralsWithServices:nil
            options:@{CBCentralManagerScanOptionAllowDuplicatesKey : @YES}];
    } else if (central.state == CBManagerStateUnauthorized) {
        fprintf(stderr, "FAIL: Bluetooth scan permission was not granted\n"); exit(2);
    } else if (central.state == CBManagerStateUnsupported) {
        fprintf(stderr, "FAIL: Bluetooth LE central mode is unsupported\n"); exit(2);
    }
}

- (void)centralManager:(CBCentralManager *)central
 didDiscoverPeripheral:(CBPeripheral *)peripheral
     advertisementData:(NSDictionary<NSString *, id> *)advertisementData
                  RSSI:(NSNumber *)RSSI {
    (void)peripheral; (void)RSSI;
    NSArray<CBUUID *> *services = advertisementData[CBAdvertisementDataServiceUUIDsKey];
    for (CBUUID *service in services) {
        NSString *compact = [[[service UUIDString]
            stringByReplacingOccurrencesOfString:@"-" withString:@""] uppercaseString];
        if (compact.length != 32) continue;
        uint8_t bytes[16]; BOOL valid = YES;
        for (NSUInteger index = 0; index < 16; ++index) {
            NSString *pair = [compact substringWithRange:NSMakeRange(index * 2, 2)];
            char *end = NULL; unsigned long value = strtoul(pair.UTF8String, &end, 16);
            if (end == pair.UTF8String || *end != '\0' || value > 255) { valid = NO; break; }
            bytes[index] = (uint8_t)value;
        }
        if (!valid || bytes[0] != 'R' || bytes[1] != 'A' || bytes[2] != 0x11) continue;
        uint32_t programHash = ((uint32_t)bytes[4] << 24) | ((uint32_t)bytes[5] << 16)
            | ((uint32_t)bytes[6] << 8) | bytes[7];
        uint32_t counter = ((uint32_t)bytes[8] << 24) | ((uint32_t)bytes[9] << 16)
            | ((uint32_t)bytes[10] << 8) | bytes[11];
        uint32_t checksum = ((uint32_t)bytes[12] << 24) | ((uint32_t)bytes[13] << 16)
            | ((uint32_t)bytes[14] << 8) | bytes[15];
        if (bytes[3] != self.expectedTransfer || programHash != self.expectedHash
                || checksum != RabbitFNV1a(bytes, 12)) continue;
        fprintf(stdout, "ACK RECEIVED: TRANSFER=%02X HASH=%08X APPLIED_COUNTER=%u\n",
            bytes[3], programHash, counter); fflush(stdout);
        [self.timer invalidate]; [self.peripheral stopAdvertising]; [central stopScan];
        exit(0);
    }
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
    if (argc < 4) { fprintf(stderr, "usage: rabbit-vm-program TRANSFER HASH UUID...\n"); return 2; }
    @autoreleasepool {
        char *transferEnd = NULL; char *hashEnd = NULL;
        unsigned long transfer = strtoul(argv[1], &transferEnd, 16);
        unsigned long programHash = strtoul(argv[2], &hashEnd, 16);
        if (*argv[1] == '\0' || *transferEnd != '\0' || transfer > 255 || *argv[2] == '\0'
                || *hashEnd != '\0' || programHash > UINT32_MAX) {
            fprintf(stderr, "FAIL: invalid expected acknowledgement identity\n"); return 2;
        }
        NSMutableArray<NSString *> *values = [NSMutableArray array];
        for (int i = 3; i < argc; ++i) [values addObject:[NSString stringWithUTF8String:argv[i]]];
        RabbitProgramSender *sender = [[RabbitProgramSender alloc] initWithUUIDs:values
            expectedTransfer:(uint8_t)transfer expectedHash:(uint32_t)programHash];
        (void)sender;
        fprintf(stdout, "RABBIT VM PROGRAM TRANSFER STARTED; waiting for exact Dell ACK\n"); fflush(stdout);
        [[NSRunLoop currentRunLoop] run];
    }
    return 0;
}
