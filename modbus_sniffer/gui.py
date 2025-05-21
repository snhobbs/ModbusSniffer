from quick import gui_it
import logging
from . cli import main as cli_main

_log = logging.getLogger("modbus-sniffer")


def main():
    gui_it(cli_main)


if __name__ == "__main__":
    logging.basicConfig(format=FORMAT)
    _log.setLevel(logging.DEBUG)
    main()
