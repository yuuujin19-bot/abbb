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
        print("Connected!")

        # Find the correct AE01 characteristic under AE30 service
        write_char = None
        for service in client.services:
            if "ae30" in service.uuid:
                for char in service.characteristics:
                    if "ae01" in char.uuid:
                        write_char = char
                        break
        if not write_char:
            print("ERROR: AE01 characteristic not found!")
            print("Listing all services:")
            for service in client.services:
                print(f"  Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"    Char: {char.uuid} | Props: {char.properties} | Handle: {char.handle}")
            return

        print(f"Using characteristic: {write_char.uuid} handle={write_char.handle}")

        print("Vibrate test (low)...")
        await client.write_gatt_char(write_char, bytes([0x55, 0x03, 0x00, 0x00, 0x01, 0x03, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(write_char, bytes([0x55, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("Stopped. Suction test (low)...")
        await asyncio.sleep(1)
        await client.write_gatt_char(write_char, bytes([0x55, 0x09, 0x00, 0x00, 0x02, 0x00, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(write_char, bytes([0x55, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("Done!")

asyncio.run(main())
