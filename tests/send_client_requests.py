import time
import serial
import struct
import sys

# Example Modbus RTU function codes
READ_COILS = 0x01
READ_HOLDING_REGISTERS = 0x03

# CRC16 Modbus implementation
def crc16(data: bytes) -> bytes:
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 0x0001) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return struct.pack("<H", crc)

# Compose a fake Modbus RTU response
def make_response(slave_addr: int, function_code: int, data: bytes) -> bytes:
    packet = struct.pack("B", slave_addr) + struct.pack("B", function_code) + data
    return packet + crc16(packet)

def main(port='/dev/ttyUSB0', baud=9600):
    # Replace with your test port or use a loopback USB adapter (e.g., ttyUSB0 connected to ttyUSB1)

    with serial.Serial(port, baud, timeout=1) as ser:
        print(f"Sending fake Modbus RTU responses on {port}...")

        # Send a few fake responses
        for i in range(10):
            # Simulate a response to READ_COILS: 1 byte of data (e.g., 0b00001101)
            data_bytes = struct.pack("B", 1) + struct.pack("B", 0b00001101)
            frame = make_response(slave_addr=1, function_code=READ_COILS, data=data_bytes)

            ser.write(frame)
            print(f"Sent [{i}]: {frame.hex(' ')}")

            time.sleep(0.5)

if __name__ == "__main__":
    main(*sys.argv[1:])
