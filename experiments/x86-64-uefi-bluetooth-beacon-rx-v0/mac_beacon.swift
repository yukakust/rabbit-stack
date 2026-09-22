import CoreBluetooth
import Darwin
import Foundation

let rabbitServiceUUID = CBUUID(string: "52414242-4954-4C45-8000-000000000001")

final class RabbitBeacon: NSObject, CBPeripheralManagerDelegate {
    private var manager: CBPeripheralManager!

    override init() {
        super.init()
        manager = CBPeripheralManager(
            delegate: self,
            queue: nil,
            options: [CBPeripheralManagerOptionShowPowerAlertKey: true]
        )
    }

    func peripheralManagerDidUpdateState(_ peripheral: CBPeripheralManager) {
        switch peripheral.state {
        case .poweredOn:
            peripheral.startAdvertising([
                CBAdvertisementDataServiceUUIDsKey: [rabbitServiceUUID]
            ])
        case .unauthorized:
            print("FAIL: Bluetooth permission was not granted to this terminal application")
            exit(2)
        case .unsupported:
            print("FAIL: this Mac does not support Bluetooth LE peripheral mode")
            exit(2)
        case .poweredOff:
            print("WAIT: turn Bluetooth on")
        default:
            print("WAIT: CoreBluetooth state \(peripheral.state.rawValue)")
        }
    }

    func peripheralManagerDidStartAdvertising(
        _ peripheral: CBPeripheralManager,
        error: Error?
    ) {
        if let error {
            print("FAIL: could not advertise Rabbit UUID: \(error)")
            exit(2)
        }
        print("RABBIT BEACON ADVERTISING")
        print("UUID=52414242-4954-4C45-8000-000000000001")
        print("Keep this process running while the Dell performs its 20-second passive scan.")
        fflush(stdout)
    }

}

let beacon = RabbitBeacon()
RunLoop.current.run()
