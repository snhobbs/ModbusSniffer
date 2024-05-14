import copy
import serial
from multiprocessing import Process, Queue
from queue import Empty

# import pymodbus
# from pymodbus.transaction import ModbusRtuFramer
# from pymodbus.utilities import hexlify_packets
# from binascii import b2a_hex
import sys
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer

# from custom_message import CustomModbusRequest
# import socat_test as socat
import logging
from pymodbus.server.sync import StartSerialServer
from modbus_sniffer import SerialSnooper

# asynchronous import StartSerialServer
FORMAT = (
    "%(asctime)-15s %(threadName)-15s"
    " %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
)
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
# log.setLevel(logging.DEBUG)
# log.setLevel(logging.WARNING)
log.setLevel(logging.INFO)


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
        print(
            "Usage: python3 {} device [baudrate, default={}]".format(sys.argv[0], baud)
        )
        sys.exit(-1)
    try:
        baud = int(sys.argv[2])
    except (IndexError, ValueError):
        pass

    server = Process(target=run_server, args=("/tmp/ttyp0", baud))
    # run_server(device=port, baud=baud)
    server.start()
    try:
        master_sniffer = SerialSnooper(port, baud)
        slave_sniffer = SerialSnooper("/tmp/ptyp0", baud)
        mq = Queue()
        sq = Queue()
        master_thread = Process(
            target=read_to_queue, args=(master_sniffer.connection, mq)
        )
        slave_thread = Process(
            target=read_to_queue, args=(slave_sniffer.connection, sq)
        )
        master_thread.start()
        slave_thread.start()

        while True:
            master_data = bytes()
            slave_data = bytes()
            try:
                master_data = mq.get()  # read data from usb
                slave_sniffer.connection.write(master_data)  # connect data to slave
            except Empty:
                break

            try:
                slave_data = sq.get()  # read response from slave server
            except Empty:
                break
            master_sniffer.connection.write(slave_data)  # send slave response to master
            slave_sniffer.process(slave_data)  # read slave packet
            master_sniffer.process(master_data)  # read master packet
    finally:
        master_sniffer.close()
        slave_sniffer.close()
