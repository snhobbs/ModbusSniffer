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
log = logging.getLogger("modbus_sniffer")

kByteLength_8N1 = 10  # 8N1 is 10 bits/byte over the wire

class SerialSnooper:
    """
    Modbus RTU serial snooper that listens for and decodes Modbus messages.

    Attributes:
        kMaxReadSize (int): Maximum number of bytes to read in one call.
    """
    kMaxReadSize = 128

    def __init__(self, port, baud=9600, timeout=None, byte_length=kByteLength_8N1):
        """
        Args:
            port (str): Serial port path (e.g., /dev/ttyUSB0 or COM3).
            baud (int): Baud rate of the serial communication.
            timeout (float or None): Timeout in seconds. If None, it is computed based on baud rate.
            byte_length (int): Clocks per byte, default is 10 for standard 8N1
        """
        self.port = port
        self.baud = baud
        if timeout is None:
            timeout = float(9 * byte_length) / baud
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
@click.option("--port", "-p", default="/dev/ttyUSB0", help="Serial device path (e.g., /dev/ttyUSB0 or COM1)")
@click.option("--baud", "-b", type=int, default=9600, help="Baud rate for serial communication")
@click.option("--debug", is_flag=True, help="Enable debug-level logging")
@click.option("--timeout", type=float, help="Set a custom Modbus timeout in seconds")
@click.option("--logfile", type=click.Path(), help="Optional log file path")
def main(port, baud, debug, timeout, logfile):
    log_level = logging.DEBUG if debug else logging.INFO

    # Configure root logger
    logging.getLogger().handlers.clear()  # Remove existing handlers
    handlers = [logging.StreamHandler()]
    if logfile:
        handlers.append(logging.FileHandler(logfile))

    logging.basicConfig(
        level=log_level,
        format=FORMAT,
        #handlers=handlers
    )

    log.info(f"Starting ModbusSniffer on {port} @ {baud} baud")

    with SerialSnooper(port, baud, timeout) as ss:
        while True:
            data = ss.read_raw()
            if len(data):
                pass
            _ = ss.process(data)


if __name__ == "__main__":
    main()
