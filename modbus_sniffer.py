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
        self.connection = serial.Serial(port, baud, timeout=float(128*10)/baud)
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

    def server_packet_callback(self, *args, **kwargs):
        arg = 0
        for msg in args:
            func_name = str(type(msg)).split('.')[-1].strip("'><").replace("Request", "")
            print("Master-> ID: {}, Function: {}: {}".format(msg.unit_id, func_name, msg.function_code), end=" ")
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
            arg += 1
            print('{}/{}\n'.format(arg, len(args)), end="")

    def client_packet_callback(self, *args, **kwargs):
        arg = 0
        for msg in args:
            func_name = str(type(msg)).split('.')[-1].strip("'><").replace("Request", "")
            print("Slave-> ID: {}, Function: {}: {}".format(msg.unit_id, func_name, msg.function_code), end=" ")
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
            arg += 1
            print('{}/{}\n'.format(arg, len(args)), end="")

    def read(self):
        b = self.connection.read(16)
        if len(b) == 0:
            return
        try:
            self.client_framer.processIncomingPacket(b, self.client_packet_callback, unit=None, single=True)
            #print("Check Client")
        except (IndexError, TypeError,KeyError) as e:
            #print(e)
            pass
        try:
            self.server_framer.processIncomingPacket(b, self.server_packet_callback, unit=None, single=True)
            #print("Check Server")
            pass
        except (IndexError, TypeError,KeyError) as e:
            #print(e)
            pass

if __name__ == "__main__":
    baud = 9600
    try:
        port = sys.argv[1]
    except IndexError:
        print("Usage: python3 {} device [baudrate, default={}]".format(sys.argv[0], baud))
        sys.exit(-1)
    try:
        baud = int(sys.argv[2])
    except (IndexError,ValueError):
        pass
    with SerialSnooper(port, baud) as ss:
        while True:
            response = ss.read()
            #sleep(float(1)/ss.baud)
    sys.exit(0)
