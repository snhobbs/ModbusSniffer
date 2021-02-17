import sys
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
#log.setLevel(logging.WARNING)
#log.setLevel(logging.INFO)
from modbus_sniffer import SerialSnooper
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
