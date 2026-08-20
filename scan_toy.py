import asyncio
from bleak import BleakScanner, BleakClient

DEVICE_NAME = "SX765B"

async def main():
    print("Scanning...")
    device = None
    devices = await BleakScanner.discover(timeout=8.0)
    for d in devices:
        if d.name and DEVICE_NAME in d.name:
            device = d
            break
    if not device:
        print("Not found")
        return
    print("Found: " + str(device.name))
    async with BleakClient(device.address) as client:
        print("Connected!\n")
        print("=== ALL SERVICES ===\n")
        for service in client.services:
            print(f"Service: {service.uuid} (handle {service.handle})")
            for char in service.characteristics:
                print(f"  Char: {char.uuid}")
                print(f"        Handle: {char.handle} | Props: {char.properties}")
            print()

        print("=== TRYING ALL WRITABLE CHARS ===\n")
        vib_cmd = bytes([0x55, 0x03, 0x00, 0x00, 0x01, 0x05, 0x00])
        stop_cmd = bytes([0x55, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00])
        for service in client.services:
            for char in service.characteristics:
                if "write-without-response" in char.properties:
                    print(f"Writing to handle {char.handle} ({char.uuid})...")
                    try:
                        await client.write_gatt_char(char.handle, vib_cmd, response=False)
                        print(f"  -> Written OK. Waiting 3s - did toy move?")
                        await asyncio.sleep(3)
                        await client.write_gatt_char(char.handle, stop_cmd, response=False)
                        print(f"  -> Stopped")
                    except Exception as e:
                        print(f"  -> Error: {e}")
                    await asyncio.sleep(1)

        print("\nDone!")

asyncio.run(main())
