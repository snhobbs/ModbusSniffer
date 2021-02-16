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
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
#log.setLevel(logging.WARNING)
#log.setLevel(logging.INFO)

class SerialSnooper:
    kMaxReadSize = 128
    kByteLength = 10
    def __init__(self, port, baud=9600):
        self.port = port
        self.baud = baud
        self.connection = serial.Serial(port, baud, timeout=float(self.kByteLength*self.kMaxReadSize)/baud)
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

    def read_raw(self, n=16):
        return self.connection.read(n)

    def process(self, data):
        if len(data) <= 0:
            return
        try:
            print("Check Client")
            self.client_framer.processIncomingPacket(data, self.client_packet_callback, unit=None, single=True)
        except (IndexError, TypeError,KeyError) as e:
            #print(e)
            pass
        try:
            print("Check Server")
            self.server_framer.processIncomingPacket(data, self.server_packet_callback, unit=None, single=True)
            pass
        except (IndexError, TypeError,KeyError) as e:
            #print(e)
            pass

    def read(self):
        self.process(self.read_raw())

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
            data = ss.read_raw()
            if len(data):
                print(data)
            response = ss.process(data)
            #sleep(float(1)/ss.baud)
    sys.exit(0)
