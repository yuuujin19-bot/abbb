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
        print("Connected!\n")
        print("=== Brute-force CMD bytes on handle 8 ===")
        print("Looking for suction. Press Ctrl+C if something dangerous happens.\n")

        # Skip 0x03 (known vibrate)
        # Try CMD 0x04 to 0x14, two formats each
        for cmd in [0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x14]:
            # Format A: [55, cmd, 00, 00, level, 00, 00]
            data_a = bytes([0x55, cmd, 0x00, 0x00, 0x03, 0x00, 0x00])
            print(f"CMD 0x{cmd:02X} format A: {data_a.hex(' ')}")
            await client.write_gatt_char(WRITE_HANDLE, data_a, response=False)
            await asyncio.sleep(2)
            # stop attempt
            await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, cmd, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
            await asyncio.sleep(0.5)

            # Format B: [55, cmd, 00, 00, 01, level, 00]
            data_b = bytes([0x55, cmd, 0x00, 0x00, 0x01, 0x03, 0x00])
            print(f"CMD 0x{cmd:02X} format B: {data_b.hex(' ')}")
            await client.write_gatt_char(WRITE_HANDLE, data_b, response=False)
            await asyncio.sleep(2)
            # stop attempt
            await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, cmd, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
            await asyncio.sleep(0.5)

        print("\nDone! Which CMD and format triggered suction?")
        print("Tell me the hex line that was printed right before suction started.")

asyncio.run(main())
