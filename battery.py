import json
import asyncio
import logging
from request import Request

class BatteryInfo:
    '''
    Class parse BMS information from PowerQueen LiFePO4 battery over bluetooth

    Attributes:
        logger (str): Instance of python logger.
    '''
    BMS_CHARACTERISTIC_ID = '0000FFE1-0000-1000-8000-00805F9B34FB' ## Bluetooth characteristic for BMS data
    SN_CHARACTERISTIC_ID = "0000FFE2-0000-1000-8000-00805F9B34FB" ## characteristic for reading serial number (seems not implemented)

    pq_commands = {
        'GET_VERSION'      : '00 00 04 01 16 55 AA 1A',
        'GET_BATTERY_INFO' : '00 00 04 01 13 55 AA 17',
        ## Application does not read internal serial number.
        ## On version 1.1.4 used SN from QR code, during adding battery
        'SERIAL_NUMBER'    : '00 00 04 01 10 55 AA 14'
    }

    def __init__(self, bluetooth_device_mac: str, logger=None):
        self.packVoltage = None
        self.voltage = None
        self.batteryPack: dict = {}
        self.current = None
        self.remianAh = None
        self.factoryAh = None
        self.cellTemperature = None
        self.mosfetTemperature = None
        self.heat = None
        self.protectState = None
        self.failureState = None
        self.equilibriumState = None
        self.batteryState = None
        self.SOC = None
        self.SOH = None
        self.dischargesCount = None
        self.dischargesAHCount = None

        self.firmwareVersion = None
        self.manfuctureDate = None
        self.hardwareVersion = None

        if logger:
            self._logger = logger
        else:
            self._logger = logging.getLogger(__name__)

        self._request = Request(bluetooth_device_mac, logger=self._logger)

    def get_request(self):
        '''
          Return Blutooth request instance
        '''
        return self._request

    def read_bms(self):
        '''
          Function read BMS info via bluetooth using bleak client
        '''
        asyncio.run(self._request.bulk_send(
            characteristic_id = self.BMS_CHARACTERISTIC_ID,
            commandsParsers = {
                self.pq_commands["GET_VERSION"]: self.parse_version,
                self.pq_commands["GET_BATTERY_INFO"]: self.parse_battery_info,
                ## Internal SN not used or not implemented
                ## self.pq_commands["SERIAL_NUMBER"]: self.parse_serial_number
            }
        ))

    def get_json(self):
        '''
          Function return complete JSON string of parsed BMS information
        '''
        state = self.__dict__
        del state['_logger']
        del state['_request']

        return json.dumps(
            state,
            default=lambda o: o.__dict__,
            sort_keys=False,
            indent=4)

    def parse_battery_info(self, data):
        '''
          Parse battery info from bytearray
        '''
        self.packVoltage = int.from_bytes(data[8:12][::-1], byteorder='big')
        self.voltage = int.from_bytes(data[12:16][::-1], byteorder='big')

        cell = 0
        batPack = data[16:48]
        for key, dt in enumerate(batPack):
            if not dt or key % 2:
                continue

            cellVoltage = int.from_bytes([batPack[key + 1], dt], byteorder='big')
            self.batteryPack[cell] = cellVoltage/1000
            cell += 1

        ## Load \ Unload current A
        self.current = int.from_bytes(data[48:52][::-1], byteorder='big')

        ## Remain Ah
        remianAh = int.from_bytes(data[62:64][::-1], byteorder='big')
        self.remianAh = round(remianAh/100, 2)

        ## Factory Ah
        fccAh = int.from_bytes(data[64:66][::-1], byteorder='big')
        self.factoryAh = round(fccAh/100, 2)

        ## Temperature
        s = pow(2, 16)
        self.cellTemperature = int.from_bytes(data[52:54][::-1], byteorder='big')
        self.mosfetTemperature = int.from_bytes(data[54:56][::-1], byteorder='big')

        self.heat = int.from_bytes(data[68:72][::-1], byteorder='big')

        self.protectState = int.from_bytes(data[76:80][::-1], byteorder='big')
        self.failureState = int.from_bytes(data[80:84][::-1], byteorder='big')
        self.equilibriumState = int.from_bytes(data[84:88][::-1], byteorder='big')
        self.batteryState = int.from_bytes(data[88:90][::-1], byteorder='big')

        ## Charge level
        self.SOC = f"{int.from_bytes(data[90:92][::-1], byteorder='big')}%"

        ## Battery Status ??
        self.SOH = f"{int.from_bytes(data[92:96][::-1], byteorder='big')}%"

        self.dischargesCount = int.from_bytes(data[96:100][::-1], byteorder='big')

        ## Discharge AH times
        self.dischargesAHCount = int.from_bytes(data[100:104][::-1], byteorder='big')


    def parse_version(self, data):
        '''
          Parse firmvware version from bytearray
        '''
        start = data[8:]
        self.firmwareVersion = f"{int.from_bytes(start[0:2][::-1], byteorder='big')}.{int.from_bytes(start[2:4][::-1], byteorder='big')}.{int.from_bytes(start[4:6][::-1], byteorder='big')}"
        self.manfuctureDate = f"{int.from_bytes(start[6:8][::-1], byteorder='big')}-{int(start[8])}-{int(start[9])}"

        vers = ""
        #rawV = data[0:8]
        for ver in start[0::2]:
            if ver >= 32 and ver <= 126:
                vers += chr(ver)

        self.hardwareVersion = vers

    def parse_serial_number(self, data):
        '''
          Parse battery serial number from bytearray
          Seems logic not implemented in BMS
        '''
        print(f"Serial number: ${data}")
