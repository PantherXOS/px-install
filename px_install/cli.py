'''Command line interface'''

import argparse
import logging
import sys
from datetime import time

from px_install.block_devices import (get_block_device_by_name,
                                      get_block_devices,
                                      get_largest_valid_block_device,
                                      list_block_devices)

from .classes import SystemConfiguration
from .remote_config import get_enterprise_config
from .system_config import matching_template_is_available
from .util import (check_efi_or_bios, is_valid_hostname, is_valid_timezone,
                   random_hostname)

log = logging.getLogger(__name__)


def get_cl_arguments():

    hostname_generated = random_hostname('pantherx', 6)
    block_devices = get_block_devices()
    largest_block_device = get_largest_valid_block_device(block_devices)
    if largest_block_device is None:
        raise ValueError('No valid disk found for installation.')
    default_disk_name = "/dev/{}".format(largest_block_device.name)

    disk_input = ''

    type = ''
    firmware = check_efi_or_bios()
    hostname = ''
    timezone = ''
    locale = ''
    username = ''
    password = ''
    public_key = 'NONE'
    disk = ''

    is_enterprise_config = False
    enterprise_config_id = None
    enterprise_config = None

    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        print()
        print("You will be prompted for a couple of important details. To accept the default, press ENTER.")
        print()
        type = input("Type of setup: 'DESKTOP', 'SERVER', 'ENTERPRISE'. ['DESKTOP']: ") or 'DESKTOP'
        print("-> Selected {}".format(type))
        print()
        print("Your system appears to support {}. Overwrite?".format(firmware.upper()))
        firmware = input("Type of setup: 'BIOS', 'EFI'. ['{}']: ".format(firmware.upper())) or firmware
        print("-> Selected {}".format(firmware.upper()))
        print()
        hostname = input("Specify hostname. ['{}']: ".format(hostname_generated)) or hostname_generated
        if not is_valid_hostname(hostname):
            print('{} is not a valid hostname.'.format(hostname))
            print("Allowed: [0-9], [a-z], '-'. Example: my-pantherx")
            print()
            hostname = input("Specify hostname. ['{}']: ".format(hostname_generated)) or hostname_generated
            if not is_valid_hostname(hostname):
                print('{} is not a valid hostname.'.format(hostname))
                sys.exit(1)
        print("-> Selected {}".format(hostname))
        print()
        timezone = input("Specify a time zone. ['Europe/Berlin']: ") or 'Europe/Berlin'
        if not is_valid_timezone(timezone):
            print('{} is not a valid time zone.'.format(timezone))
            print("Valid examples include: 'Europe/Berlin', 'Asia/Kuala_Lumpur', 'US/Pacific', 'Etc/GMT+3'")
            print()
            timezone = input("Specify a time zone. ['Europe/Berlin']: ") or 'Europe/Berlin'
            if not is_valid_timezone(timezone):
                print('{} is not a valid time zone.'.format(timezone))
                sys.exit(1)
        print("-> Selected {}".format(timezone))
        print()
        locale = input("Specify a locale. ['en_US.utf8']: ") or 'en_US.utf8'
        print("-> Selected {}".format(locale))
        print()
        username = input("Specify your username. ['panther']: ") or 'panther'
        username = username.lower()
        print("-> Selected {}".format(username))
        print()
        password = input("Specify {} password. ['pantherx']: ".format(username)) or 'pantherx'
        print("-> Selected {}".format(password))
        print()
        public_key = input("Specify a public key to login via SSH or leave empty. ['NONE']: ") or 'NONE'
        print("-> Selected {}".format(public_key))
        print()
        list_block_devices(block_devices)
        print()
        disk_input = input("Specify a the disk to use (Format: '/dev/<DISK>') ['{}']: ".format(default_disk_name)) or default_disk_name
        print("-> Selected {}".format(disk_input))

    else:
        '''Command line arguments'''
        parser = argparse.ArgumentParser()
        parser.add_argument("-t", "--type", type=str, default="DESKTOP",
                            choices=['DESKTOP', 'SERVER', 'ENTERPRISE'],
                            help="Installation type."
                            )
        parser.add_argument("-fw", "--firmware", type=str,
                            choices=['EFI', 'BIOS'],
                            help="Overwrite automatic detection of EFI / BIOS install."
                            )
        parser.add_argument("-hn", "--hostname", type=str, default=hostname_generated,
                            help="Specify hostname. Defaults to '{}'.".format(hostname_generated)
                            )
        parser.add_argument("-tz", "--timezone", type=str, default="Europe/Berlin",
                            help="Specify a time zone. Defaults to 'Europe/Berlin'"
                            )
        parser.add_argument("-l", "--locale", type=str, default='en_US.utf8',
                            help="Specify a locale. Defaults to 'en_US.utf8'"
                            )
        parser.add_argument("-u", "--username", type=str, default='panther',
                            help="Specify a username. Defaults to 'panther'"
                            )
        parser.add_argument("-pw", "--password", type=str, default='pantherx',
                            help="Specify a user password. Defaults to 'pantherx'"
                            )
        parser.add_argument("-pk", "--key", type=str,
                            help="Specify a public key to login via SSH. Example: `ssh-ed25519 AA ... 4QydPg franz`"
                            )
        parser.add_argument("-d", "--disk", type=str, default=default_disk_name,
                            help="Specify the disk to use. Defaults to '{}'".format(default_disk_name)
                            )
        parser.add_argument("-c", "--config", type=str,
                            help="Specify a enterprise config ID. This will overwrite all other settings."
                            )
        parser.add_argument("-curl", "--config_url", type=str, default="https://temp.pantherx.org/install",
                            )
        args = parser.parse_args()

        type = args.type
        firmware = check_efi_or_bios()
        if args.firmware:
            firmware = args.firmware.lower()
        hostname = args.hostname
        if not is_valid_hostname(hostname):
            print('{} is not a valid hostname.'.format(hostname))
            print("Allowed: [0-9], [a-z], '-'. Example: my-pantherx")
            sys.exit()
        timezone = args.timezone
        if not is_valid_timezone(timezone):
            print('{} is not a valid time zone.'.format(timezone))
            print("Valid examples include: 'Europe/Berlin', 'Asia/Kuala_Lumpur', 'US/Pacific', 'Etc/GMT+3'")
        locale = args.locale
        username = args.username
        password = args.password
        public_key = args.key
        disk_input = args.disk

        if args.config:
            is_enterprise_config = True
            enterprise_config_id = args.config
            enterprise_config = get_enterprise_config(args.config, args.config_url)
            type = enterprise_config.type
            timezone = enterprise_config.timezone
            locale = enterprise_config.locale

        public_key = 'NONE'
        if args.key:
            public_key = args.key

        print()
        print("To customize defaults, run 'px-install run' instead.")

    disk = get_block_device_by_name(disk_input)
    if disk is None:
        raise EnvironmentError('Selected disk {} does not exist.'.format(disk_input))

    config = SystemConfiguration(
        type=type,
        firmware=firmware.lower(),
        hostname=hostname,
        timezone=timezone,
        locale=locale,
        username=username,
        password=password,
        public_key=public_key,
        disk=disk
    )

    print()
    print('######## SUMMARY ########')
    print()
    print("Type: {}".format(config.type))
    print("Firmware: {}".format(config.firmware))
    print("Hostname: {}".format(config.hostname))
    print("Locale: {}".format(config.locale))
    print("Username: {}".format(config.username))
    print("Password: {}".format(config.password))
    print("Public key: {}".format(config.public_key))
    print("Disk: {} ({} Gigabyte)".format(config.disk.dev_name, disk.size_in_gb()))
    print()

    matching_template_is_available(config)

    print('IMPORTANT: Your hard disk {} will be formatted and all data lost!'.format(config.disk.dev_name))
    print('Would you like to continue?')
    print()
    approved = input("Approve system configuration with 'yes'; cancel with 'no': ")
    if approved.lower() != 'yes':
        print('You did not approve. Exiting...')
        sys.exit()

    return {
        "config": config,
        "is_enterprise_config": is_enterprise_config,
        "enterprise_config_id": enterprise_config_id,
        "enterprise_config": enterprise_config
    }
