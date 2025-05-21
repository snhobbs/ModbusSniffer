import logging
import click

FORMAT = (
    "%(asctime)-15s %(threadName)-15s"
    " %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
)

from . modbus_sniffer import SerialSnooper

_log = logging.getLogger("modbus-sniffer")
@click.command()
@click.option("--port", "-p", default="/dev/ttyUSB0", help="Serial device")
@click.option("--baud", "-b", type=int, default=9600)
@click.option("--debug", is_flag=True, help="Debug level verbosity")
@click.option("--timeout", type=float, help="Modbus timeout")
def main(port, baud, debug, timeout):
    if debug:
        _log.setLevel(logging.DEBUG)
    else:
        _log.setLevel(logging.INFO)

    with SerialSnooper(port, baud, timeout) as ss:
        while True:
            data = ss.read_raw()
            if len(data):
                pass
            _ = ss.process(data)


if __name__ == "__main__":
    logging.basicConfig(format=FORMAT)
    _log.setLevel(logging.DEBUG)
    main()
