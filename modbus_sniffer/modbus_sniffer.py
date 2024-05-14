import contextlib
import logging

import click
import serial
from pymodbus.factory import ClientDecoder
from pymodbus.factory import ServerDecoder
from pymodbus.transaction import ModbusRtuFramer

FORMAT = (
    "%(asctime)-15s %(threadName)-15s"
    " %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
)
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
# log.setLevel(logging.WARNING)
# log.setLevel(logging.INFO)


class SerialSnooper:
    kMaxReadSize = 128
    kByteLength = 10

    def __init__(self, port, baud=9600, timeout=None):
        self.port = port
        self.baud = baud
        if timeout is None:
            timeout = float(9 * self.kByteLength) / baud
        self.timeout = timeout
        self.connection = serial.Serial(port, baud, timeout=timeout)
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
        for msg in args:
            (str(type(msg)).split(".")[-1].strip("'><").replace("Request", ""))
            with contextlib.suppress(AttributeError):
                pass
            with contextlib.suppress(AttributeError):
                pass
            with contextlib.suppress(AttributeError):
                pass

    def client_packet_callback(self, *args, **kwargs):
        for msg in args:
            (str(type(msg)).split(".")[-1].strip("'><").replace("Request", ""))
            with contextlib.suppress(AttributeError):
                pass
            with contextlib.suppress(AttributeError):
                pass
            with contextlib.suppress(AttributeError):
                pass

    def read_raw(self, n=16):
        return self.connection.read(n)

    def process(self, data):
        if len(data) <= 0:
            return
        with contextlib.suppress(IndexError, TypeError, KeyError):
            self.client_framer.processIncomingPacket(
                data, self.client_packet_callback, unit=None, single=True
            )
        with contextlib.suppress(IndexError, TypeError, KeyError):
            self.server_framer.processIncomingPacket(
                data, self.server_packet_callback, unit=None, single=True
            )

    def read(self):
        self.process(self.read_raw())


@click.command()
@click.option("--port", "-p", default="/dev/ttyUSB0", help="Serial device")
@click.option("--baud", "-b", type=int, default=9600)
@click.option("--debug", is_flag=True, help="Debug level verbosity")
@click.option("--timeout", type=float, help="Modbus timeout")
def main(port, baud, debug, timeout):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    with SerialSnooper(port, baud, timeout) as ss:
        while True:
            data = ss.read_raw()
            if len(data):
                pass
            _ = ss.process(data)


if __name__ == "__main__":
    main()
