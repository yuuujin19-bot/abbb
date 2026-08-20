import asyncio
from bleak import BleakScanner, BleakClient

DEVICE_NAME = "SX765B"
WRITE_CHAR = "0000ae01-0000-1000-8000-00805f9b34fb"

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
        print("Connected! Vibrate test...")
        await client.write_gatt_char(WRITE_CHAR, bytes([0x55, 0x03, 0x00, 0x00, 0x01, 0x03, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(WRITE_CHAR, bytes([0x55, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("Stopped. Suction test...")
        await asyncio.sleep(1)
        await client.write_gatt_char(WRITE_CHAR, bytes([0x55, 0x09, 0x00, 0x00, 0x02, 0x00, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(WRITE_CHAR, bytes([0x55, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("Done!")

asyncio.run(main())
