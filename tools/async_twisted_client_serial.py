#!/usr/bin/env python
"""
Pymodbus Asynchronous Client Examples
--------------------------------------------------------------------------

The following is an example of how to use the asynchronous serial modbus
client implementation from pymodbus with twisted.
"""

from twisted.internet import reactor
from pymodbus.client.asynchronous import schedulers
from pymodbus.client.asynchronous.serial import AsyncModbusSerialClient
from pymodbus.client.asynchronous.twisted import ModbusClientProtocol

import logging
import sys

logging.basicConfig()
log = logging.getLogger("pymodbus")
log.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------#
# state a few constants
# ---------------------------------------------------------------------------#

STATUS_REGS = (1, 2)
STATUS_COILS = (1, 3)
CLIENT_DELAY = 1
UNIT = 0x03


class ExampleProtocol(ModbusClientProtocol):
    def __init__(self, framer):
        """Initializes our custom protocol

        :param framer: The decoder to use to process messages
        :param endpoint: The endpoint to send results to
        """
        ModbusClientProtocol.__init__(self, framer)
        log.debug("Beginning the processing loop")
        reactor.callLater(CLIENT_DELAY, self.fetch_holding_registers)

    def fetch_holding_registers(self):
        """Defer fetching holding registers"""
        log.debug("Starting the next cycle")
        d = self.read_holding_registers(*STATUS_REGS, unit=UNIT)
        d.addCallbacks(self.send_holding_registers, self.error_handler)

    def send_holding_registers(self, response):
        """Write values of holding registers, defer fetching coils

        :param response: The response to process
        """
        log.info(response.getRegister(0))
        log.info(response.getRegister(1))
        d = self.read_coils(*STATUS_COILS, unit=UNIT)
        d.addCallbacks(self.start_next_cycle, self.error_handler)

    def start_next_cycle(self, response):
        """Write values of coils, trigger next cycle

        :param response: The response to process
        """
        print(response)
        log.info(response.getBit(0))
        log.info(response.getBit(1))
        log.info(response.getBit(2))
        reactor.callLater(CLIENT_DELAY, self.fetch_holding_registers)

    def error_handler(self, failure):
        """Handle any twisted errors

        :param failure: The error to handle
        """
        log.error(failure)


if __name__ == "__main__":
    proto, client = AsyncModbusSerialClient(
        schedulers.REACTOR,
        method="rtu",
        baudrate=sys.argv[2],
        port=sys.argv[1],
        timeout=2,
        proto_cls=ExampleProtocol,
    )
    proto.start()
    # proto.stop()
