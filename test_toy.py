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

        # Find AE01 with write-without-response under AE30 service
        write_handle = None
        for service in client.services:
            if "ae30" in service.uuid.lower():
                for char in service.characteristics:
                    if "ae01" in char.uuid.lower() and "write-without-response" in char.properties:
                        write_handle = char.handle
                        print(f"Found write char: handle={write_handle}")
                        break
                break

        if write_handle is None:
            print("Could not find write characteristic. Listing all:")
            for service in client.services:
                print(f"  Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"    {char.uuid} props={char.properties} handle={char.handle}")
            return

        print("Vibrate test (low)...")
        await client.write_gatt_char(write_handle, bytes([0x55, 0x03, 0x00, 0x00, 0x01, 0x03, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(write_handle, bytes([0x55, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("Vibrate stopped. Suction test (low)...")
        await asyncio.sleep(1)
        await client.write_gatt_char(write_handle, bytes([0x55, 0x09, 0x00, 0x00, 0x02, 0x00, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(write_handle, bytes([0x55, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("All done!")

asyncio.run(main())
