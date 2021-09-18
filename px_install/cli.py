'''Command line interface'''

import argparse
import logging

from .classes import SystemConfiguration
from .util import check_efi_or_bios
from .remote_config import get_enterprise_config

log = logging.getLogger(__name__)


def get_cl_arguments():
    '''Command line arguments'''
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", type=str, default="DESKTOP",
                        choices=['DESKTOP', 'SERVER', 'ENTERPRISE'],
                        help="Installation type."
                        )
    parser.add_argument("-f", "--firmware", type=str,
                        choices=['EFI', 'BIOS'],
                        help="Overwrite automatic detection of EFI / BIOS install."
                        )
    parser.add_argument("-h", "--hostname", type=str, default="panther",
                        help="Specify hostname. Defaults to 'panther'"
                        )
    parser.add_argument("-t", "--timezone", type=str, default="Europe/Berlin",
                        help="Specify a time zone. Defaults to 'Europe/Berlin'"
                        )
    parser.add_argument("-l", "--locale", type=str, default='en_US.utf8',
                        help="Specify a locale. Defaults to 'en_US.utf8'"
                        )
    parser.add_argument("-u", "--username", type=str, default='panther',
                        help="Specify a username. Defaults to 'panther'"
                        )
    parser.add_argument("-p", "--password", type=str, default='pantherx',
                        help="Specify a user password. Defaults to 'pantherx'"
                        )
    parser.add_argument("-d", "--disk", type=str, default='/dev/sda',
                        help="Specify the disk to use. Defaults to '/dev/sda'"
                        )
    parser.add_argument("-c", "--config", type=str,
                        help="Specify a enterprise config ID. This will overwrite all other settings."
                        )
    args = parser.parse_args()

    type = args.type
    firmware = check_efi_or_bios()
    if args.firmware:
        firmware = args.firmware.lower()
    hostname = args.type
    timezone = args.timezone
    locale = args.locale

    e_config = None
    if args.config:
        e_config = get_enterprise_config(args.config)
        type = e_config.type
        timezone = e_config.timezone
        locale = e_config.locale

    config = SystemConfiguration(
        type=type,
        firmware=firmware,
        hostname=hostname,
        timezone=timezone,
        locale=locale,
        username=args.username,
        password=args.password,
        disk=args.disk
    )

    return {
        "config": config,
        "config_id": args.config,
        "config_remote": e_config
    }
