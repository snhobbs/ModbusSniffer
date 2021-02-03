import serial
from pymodbus.factory import ClientDecoder
from pymodbus.factory import ServerDecoder
from pymodbus.transaction import ModbusRtuFramer
#import pymodbus
#from pymodbus.transaction import ModbusRtuFramer
#from pymodbus.utilities import hexlify_packets
#from binascii import b2a_hex
from time import sleep
import sys

class SerialSnooper:
    def __init__(self, port, baud=9600):
        self.port = port
        self.baud = baud
        self.connection = serial.Serial(port, baud)
        self.client_framer = ModbusRtuFramer(decoder=ClientDecoder())
        self.server_framer = ModbusRtuFramer(decoder=ServerDecoder())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        self.connection.open()

    def close(self):
        self.connection.close()

    def packet_callback(self, *args, **kwargs):
        for msg in args:
            func_name = str(type(msg)).split('.')[-1].strip("'><").replace("Request", "")
            print("ID: {}, Function: {}: {}".format(msg.unit_id, func_name, msg.function_code), end=" ")
            try:
                print("Address: {}".format(msg.address), end=" ")
            except AttributeError:
                pass
            try:
                print("Count: {}".format(msg.count), end=" ")
            except AttributeError:
                pass
            try:
                print("Data: {}".format(msg.values), end=" ")
            except AttributeError:
                pass
        print('\n', end="")

    def read(self):
        b = self.connection.read_all()
        if len(b) == 0:
            return
        try:
            self.client_framer.processIncomingPacket(b, self.packet_callback, unit=None, single=True)
        except TypeError as e:
            print(e)
        try:
            self.server_framer.processIncomingPacket(b, self.packet_callback, unit=None, single=True)
        except TypeError as e:
            print(e)

if __name__ == "__main__":
    baud = 9600
    try:
        port = sys.argv[1]
    except IndexError:
        print("Usage: python3 modbus_snooper.py device [baudrate={}]".format(baud))
        sys.exit(-1)
    try:
        baud = int(sys.argv[2])
    except (IndexError,ValueError):
        pass
    with SerialSnooper(port, baud) as ss:
        while True:
            response = ss.read()
            sleep(float(4)/ss.baud)
    sys.exit(0)
