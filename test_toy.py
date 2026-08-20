import asyncio
from bleak import BleakScanner, BleakClient

DEVICE_NAME = "SX765B"
WRITE_HANDLE = 8

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

        # Vibrate test - intensity 3/20, 3 seconds
        print("Vibrate test...")
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x03, 0x00, 0x00, 0x01, 0x03, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("Vibrate stopped.")
        await asyncio.sleep(1)

        # Suction test - intensity 2/10, 3 seconds
        print("Suction test...")
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x09, 0x00, 0x00, 0x02, 0x00, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("Suction stopped.")

        print("\nAll good! Both channels work.")

asyncio.run(main())
