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

        print("=== Testing suction commands on handle 8 ===\n")

        # Format 1: v6 constrict [0x55, 0x09, 0x00, 0x00, level, 0x00, 0x00]
        print("Test 1: v6 constrict format [55 09 00 00 03 00 00]")
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x09, 0x00, 0x00, 0x03, 0x00, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("  stopped\n")
        await asyncio.sleep(1)

        # Format 2: SL278H style [0x55, 0x04, 0x00, 0x00, 0x01, intensity, 0xAA]
        print("Test 2: SL278H format [55 04 00 00 01 50 AA]")
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x04, 0x00, 0x00, 0x01, 0x50, 0xAA]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x04, 0x00, 0x00, 0x00, 0x00, 0xAA]), response=False)
        print("  stopped\n")
        await asyncio.sleep(1)

        # Format 3: v6 constrict with higher level
        print("Test 3: v6 constrict higher [55 09 00 00 05 00 00]")
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x09, 0x00, 0x00, 0x05, 0x00, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("  stopped\n")
        await asyncio.sleep(1)

        # Format 4: CMD 0x06 (some SVAKOM models use this for suction)
        print("Test 4: CMD 06 [55 06 00 00 01 03 00]")
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x06, 0x00, 0x00, 0x01, 0x03, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("  stopped\n")
        await asyncio.sleep(1)

        # Format 5: CMD 0x04 without tail
        print("Test 5: CMD 04 no tail [55 04 00 00 01 03 00]")
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x04, 0x00, 0x00, 0x01, 0x03, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("  stopped\n")
        await asyncio.sleep(1)

        # Format 6: vibrate channel 2 [0x55, 0x03, 0x02, 0x00, 0x01, 0x05, 0x00]
        print("Test 6: vibrate ch2 [55 03 02 00 01 05 00]")
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x03, 0x02, 0x00, 0x01, 0x05, 0x00]), response=False)
        await asyncio.sleep(3)
        await client.write_gatt_char(WRITE_HANDLE, bytes([0x55, 0x03, 0x02, 0x00, 0x00, 0x00, 0x00]), response=False)
        print("  stopped\n")
        await asyncio.sleep(1)

        print("=== Now trying other handles with suction ===\n")
        suck_cmd = bytes([0x55, 0x09, 0x00, 0x00, 0x03, 0x00, 0x00])
        stop_cmd = bytes([0x55, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00])
        for service in client.services:
            for char in service.characteristics:
                if "write-without-response" in char.properties and char.handle != 8:
                    print(f"Suction on handle {char.handle}...")
                    try:
                        await client.write_gatt_char(char.handle, suck_cmd, response=False)
                        await asyncio.sleep(3)
                        await client.write_gatt_char(char.handle, stop_cmd, response=False)
                        print("  stopped")
                    except Exception as e:
                        print(f"  Error: {e}")
                    await asyncio.sleep(1)

        print("\nDone! Which test made suction work?")

asyncio.run(main())
