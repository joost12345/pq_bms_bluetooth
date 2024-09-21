# pq_bms_bluetooth
Python library for PowerQueen LiFePO4 batteries with BMS Bluetooth connection.

The code does not make any changes or change any settings in BMS of battery. Only reading information.

## Installation

Create python virtual environment

```
python -m venv venv
source venv/bin/activate
```

Install requirements

```
pip install -r requirements.txt
```

## Usage

Find Bluetooth MAC address of your battery.
On linux it possible to do with `bluez` tool.

Start bluetooth tool `bluetoothctl` and scan for avaliable bluetooth devices `scan on`.
<br>Once it find some devices and shows the list, stop scanning with command `scan off`

<span style="color:blue">[bluetooth]</span># scan on
<br>Discovery started
<br>[<span style="color:yellow">CHG</span>] Controller 12:34:56:78:AA:CC Discovering: yes
<br>[<span style="color:green">NEW</span>] Device 12:34:56:78:CC:12 Some Sound Device etc.
<br>[<span style="color:green">NEW</span>] Device 12:34:56:78:29:CF P-12100BXXX77-A00123
<br>[<span style="color:green">NEW</span>] Device 12:34:56:78:F8:7C 7E-C1-31-61-F8-7C
<br>[<span style="color:green">NEW</span>] Device 12:34:56:78:D4:3D 5B-10-AC-7A-D4-3D
<br><span style="color:blue">[bluetooth]</span># scan off


Run
```
python main.py DEVICE_MAC --bms
```


## Tested on

Software:
- Python 3.10, 3.11
- Linux Ubuntu 22.04
- Raspberry Pi OS Debian 12 (bookworm) (kernel 6.6+)

Hardware:
- Power Queen LiFePO4 12V 100A
