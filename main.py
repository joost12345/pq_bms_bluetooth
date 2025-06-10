import sys
import asyncio
import logging
import argparse
from battery import BatteryInfo


def commands():
    """
    Command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "DEVICE_MAC",
        help="Bluetooth device MAC address in format 12:34:56:78:AA:CC",
        type=str,
    )

    parser.add_argument("--bms", help="Get battery BMS info", action="store_true")
    parser.add_argument(
        "-t",
        "--timeout",
        help="Bluetooth response timeout in seconds (default: 10)",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--pair", help="Pair with device before interacting", action="store_true"
    )
    parser.add_argument(
        "-s",
        "--services",
        help="List device GATT services and characteristics",
        action="store_true",
    )
    parser.add_argument("--verbose", help="Verbose logs", action="store_true")

    args = parser.parse_args()
    return args


async def async_main():
    args = commands()
    logger = None
    if args.verbose:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s [%(funcName)s] %(message)s")
        handler.setFormatter(formatter)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    battery = BatteryInfo(args.DEVICE_MAC, args.pair, args.timeout, logger)

    if args.services:
        request = battery.get_request()
        await request.print_services()
        sys.exit(0)

    if args.bms:
        await battery.read_bms()  # Nu wachten we op de async functie
        print(battery.get_json())
        sys.exit(battery.error_code)

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
