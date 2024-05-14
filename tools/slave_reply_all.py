import contextlib
import copy

# asynchronous import StartSerialServer
import logging

# import pymodbus
# from pymodbus.transaction import ModbusRtuFramer
# from pymodbus.utilities import hexlify_packets
# from binascii import b2a_hex
import sys

import serial
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusServerContext
from pymodbus.datastore import ModbusSlaveContext

# from custom_message import CustomModbusRequest
# import socat_test as socat
from pymodbus.server.sync import StartSerialServer
from pymodbus.transaction import ModbusRtuFramer

FORMAT = (
    "%(asctime)-15s %(threadName)-15s"
    " %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
)
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
# log.setLevel(logging.INFO)
# log.setLevel(logging.WARNING)


def write_to_reg(start, arr, string):
    i = 0
    while i <= len(string) // 2:
        try:
            reg = ord(string[2 * i]) << 8
            reg += ord(string[2 * i + 1])
        except IndexError:
            break
        finally:
            arr[start + i] = reg
            assert reg < (1 << 16)
        i += 1
    return arr


version = "MSDS Rev B."
fv = "2.0.1"
input_reg = [0] * 1024
input_reg = write_to_reg(33, input_reg, fv)
input_reg = write_to_reg(1, input_reg, version)


def run_server(device, baud=9600):
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [17] * 100),
        co=ModbusSequentialDataBlock(0, [17] * 100),
        hr=ModbusSequentialDataBlock(0, [25185] * 1024),
        ir=ModbusSequentialDataBlock(0, copy.deepcopy(input_reg)),
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
        timeout=3.5 * 10 / baud,
        framer=ModbusRtuFramer,
        stopbits=1,
        bytesize=8,
        parity=serial.PARITY_NONE,
        baudrate=baud,
    )


if __name__ == "__main__":
    baud = 9600
    try:
        port = sys.argv[1]
    except IndexError:
        sys.exit(-1)
    with contextlib.suppress(IndexError, ValueError):
        baud = int(sys.argv[2])

    run_server(device=port, baud=baud)
