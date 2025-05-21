# ModbusSniffer
Modbus RTU packet sniffer

**ModbusSniffer** is a simple Modbus RTU packet sniffer for serial buses.

It wraps `pymodbus` to decode and print all packets observed on the wire,
from either the master or slave perspective. This is especially useful
for debugging communication between Modbus devices, verifying protocol behavior,
or reverse-engineering device interactions.

## Features
- Pure Python, built on [pymodbus](https://github.com/pymodbus-dev/pymodbus)
- Captures and decodes Modbus RTU packets from both master and slave devices
- Great for protocol debugging, development, and test benches
-️ Simple command-line interface with readable log output
- Easily extensible for custom logging or automation

## Installation
```bash
git clone https://github.com/snhobbs/ModbusSniffer
cd ModbusSniffer
pip install .
```

## Usage
**Terminal output only**
```bash
python modbus_sniffer.py --port /dev/ttyUSB0 --baud 9600
```

**With logfile output**
```bash
python modbus_sniffer.py --port /dev/ttyUSB0 --baud 19200 --logfile modbus.log
```

| Option       | Description                                   |
| ------------ | --------------------------------------------- |
| `--port, -p` | Serial port to open (default: `/dev/ttyUSB0`) |
| `--baud, -b` | Baud rate (default: `9600`)                   |
| `--timeout`  | Set Modbus read timeout manually              |
| `--debug`    | Enable verbose debug logging                  |


## Testing with socat
1. Setup a simulated serial link

```bash
socat -d -d pty,raw,echo=0,link=/tmp/ttyS0 pty,raw,echo=0,link=/tmp/ttyS1
```

2. Start modbus_sniffer
```bash
python modbus_sniffer.py --port /tmp/ttyS0 --baud 9600
```

3. Run test script
```bash
python tests/send_client_requests.py /tmp/ttyS1 --baud 9600
```
