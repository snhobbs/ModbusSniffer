import serial
from pymodbus.factory import ClientDecoder
from pymodbus.factory import ServerDecoder
from pymodbus.transaction import ModbusRtuFramer
import click
import logging

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
        arg = 0
        for msg in args:
            func_name = (
                str(type(msg)).split(".")[-1].strip("'><").replace("Request", "")
            )
            print(
                "Master-> ID: {}, Function: {}: {}".format(
                    msg.unit_id, func_name, msg.function_code
                ),
                end=" ",
            )
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
            print("{}/{}\n".format(arg, len(args)), end="")

    def client_packet_callback(self, *args, **kwargs):
        arg = 0
        for msg in args:
            func_name = (
                str(type(msg)).split(".")[-1].strip("'><").replace("Request", "")
            )
            print(
                "Slave-> ID: {}, Function: {}: {}".format(
                    msg.unit_id, func_name, msg.function_code
                ),
                end=" ",
            )
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
            print("{}/{}\n".format(arg, len(args)), end="")

    def read_raw(self, n=16):
        return self.connection.read(n)

    def process(self, data):
        if len(data) <= 0:
            return
        try:
            print("Check Client")
            self.client_framer.processIncomingPacket(
                data, self.client_packet_callback, unit=None, single=True
            )
        except (IndexError, TypeError, KeyError):
            # print(e)
            pass
        try:
            print("Check Server")
            self.server_framer.processIncomingPacket(
                data, self.server_packet_callback, unit=None, single=True
            )
            pass
        except (IndexError, TypeError, KeyError):
            # print(e)
            pass

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
                print(data)
            _ = ss.process(data)


if __name__ == "__main__":
    main()
