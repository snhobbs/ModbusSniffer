import contextlib
import copy

# from custom_message import CustomModbusRequest
# import socat_test as socat
import logging

# import pymodbus
# from pymodbus.transaction import ModbusRtuFramer
# from pymodbus.utilities import hexlify_packets
# from binascii import b2a_hex
import sys
from multiprocessing import Process

import serial
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusServerContext
from pymodbus.datastore import ModbusSlaveContext
from pymodbus.server.sync import StartSerialServer
from pymodbus.transaction import ModbusRtuFramer

from modbus_sniffer import SerialSnooper

# asynchronous import StartSerialServer
FORMAT = (
    "%(asctime)-15s %(threadName)-15s"
    " %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
)
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
# log.setLevel(logging.INFO)
# log.setLevel(logging.WARNING)


def run_server(device, baud=9600):
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [17] * 100),
        co=ModbusSequentialDataBlock(0, [17] * 100),
        hr=ModbusSequentialDataBlock(0, [25185] * 1024),
        ir=ModbusSequentialDataBlock(0, [25185] * 1024),
    )
    slaves = {
        1: copy.deepcopy(store),
        2: copy.deepcopy(store),
        3: copy.deepcopy(store),
        4: copy.deepcopy(store),
        5: copy.deepcopy(store),
        6: copy.deepcopy(store),
        246: copy.deepcopy(store),
    }
    context = ModbusServerContext(
        slaves=slaves,
        single=False,
    )

    # RTU Server
    StartSerialServer(
        context,
        identity=None,
        port=device,
        framer=ModbusRtuFramer,
        stopbits=1,
        timeout=3.5 * 10 / baud,
        bytesize=8,
        parity=serial.PARITY_NONE,
        baudrate=baud,
    )


def read_to_queue(s, q):
    while True:
        q.put(s.read(1))


if __name__ == "__main__":
    baud = 9600
    try:
        port = sys.argv[1]
    except IndexError:
        sys.exit(-1)
    with contextlib.suppress(IndexError, ValueError):
        baud = int(sys.argv[2])

    server = Process(target=run_server, args=("/tmp/ttyp0", baud))
    server.start()
    try:
        master_sniffer = SerialSnooper(port, baud)
        slave_sniffer = SerialSnooper("/tmp/ptyp0", baud)
        while True:
            master_data = b""
            slave_data = b""

            slave_data += slave_sniffer.connection.read(
                slave_sniffer.connection.in_waiting
            )  # read response from slave server
            master_sniffer.connection.write(slave_data)  # send slave response to master

            master_data += master_sniffer.connection.read(
                master_sniffer.connection.in_waiting
            )  # read data from usb
            slave_sniffer.connection.write(master_data)  # connect data to slave

            slave_sniffer.process(slave_data)  # read slave packet
            master_sniffer.process(master_data)  # read master packet
    finally:
        master_sniffer.close()
        slave_sniffer.close()
