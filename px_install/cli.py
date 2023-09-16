'''Command line interface'''

import argparse
import logging
import sys
import time

from .defaults import DEFAULT_VARIANT
from .block_devices import (get_block_device_by_name, get_block_devices,
                            get_largest_valid_block_device,
                            print_block_devices)
from .classes import SystemConfiguration
from .remote_config import get_enterprise_config
from .system_config import (exit_if_system_config_exists,
                            basic_config_check)
from .util import (check_efi_or_bios, is_online, is_valid_hostname,
                   is_valid_timezone, online_check, print_debug_qr_code,
                   random_hostname)
from .wifi import (dhclient_get_ip, has_valid_wifi_interface,
                   list_network_interfaces, prompt_for_wifi_config,
                   rfkill_unblock_wifi, wpa_supplicant_activate,
                   write_wifi_config)

log = logging.getLogger(__name__)


def get_cl_arguments():
    hostname_generated = random_hostname('pantherx', 6)
    block_devices = get_block_devices()
    largest_block_device = get_largest_valid_block_device(block_devices)
    if largest_block_device is None:
        raise ValueError('No valid disk found for installation.')
    default_disk_name = largest_block_device.dev_name

    disk_input = ''

	# TODO: Replace with: default_system_configuration()
    type = ''
    variant = DEFAULT_VARIANT
    firmware = check_efi_or_bios()
    hostname = ''
    timezone = ''
    locale = ''
    username = ''
    password = ''
    public_key = 'NONE'
    disk = ''
    use_disk_encryption = False

    is_enterprise_config = False
    enterprise_config_id = None
    enterprise_config = None

    '''First, a couple of helpers to aid setup'''
    if len(sys.argv) == 2 and sys.argv[1] == 'help' or len(sys.argv) == 2 and sys.argv[1] == '--help':
        '''
        Help
        '''
        print()
        print("- 'px-install' to install with defaults")
        print("- 'px-install run' to customize defaults via prompts")
        print("- 'px-install --param ...' to customize defaults via params")
        print("- 'px-install wifi-setup' to get help with WiFi setup")
        print("- 'px-install network-check' to check what network adapters are configured and if you are online")
        print()
        online = is_online()
        if online:
            print('You appear to be online.')
            print("Run 'px-install run' to continue with the setup.")
        else:
            print('You do not appear to be online.')
        sys.exit(0)
    elif len(sys.argv) == 2 and sys.argv[1] == 'wifi-setup':
        '''
        Wi-Fi Setup
        '''
        valid_interface = has_valid_wifi_interface()
        if not valid_interface:
            sys.exit(1)
        wifi_config = prompt_for_wifi_config()
        # Write config
        write_wifi_config(wifi_config)
        # Rfkill to be safe
        rfkill_unblock_wifi()
        time.sleep(5)
        # Read and activate config
        wpa_supplicant_activate()
        time.sleep(5)
        # Try to get IP
        dhclient_get_ip()
        # print_wifi_help()
        sys.exit(0)
    elif len(sys.argv) == 2 and sys.argv[1] == 'network-check':
        interfaces = list_network_interfaces()
        print()
        print('######## RESULT ########')
        print('Found {} suitable network adapters'.format(len(interfaces)))
        print()
        count = 1
        for item in interfaces:
            ip_info = "UNKNOWN"
            if len(item.addr_info) > 0:
                ip_info = ""
                for addr in item.addr_info:
                    ip_info += '| IP: {}  Broadcast: {} '.format(addr.local, addr.broadcast)
            print('''{}. Adapter
Name: {}
State: {}
Address: {}
'''.format(count, item.name, item.operstate, ip_info))
            count += 1
        online = is_online()
        if online:
            print('You appear to be online.')
            print("Run 'px-install run' to continue with the setup.")
        else:
            print('You do not appear to be online.')
            print("Run 'px-install wifi-setup' to get some assistance with Wi-Fi setup, otherwise refer to our installation guide.")
        sys.exit(0)
    elif len(sys.argv) == 2 and sys.argv[1] == 'run':
        '''
        Run setup with prompts
        '''
        online_check()
        exit_if_system_config_exists()

        print()
        print("You will be prompted for a couple of important details. To accept the default, press ENTER.")
        print()
        type = input("Type of setup: 'MINIMAL', 'DESKTOP', 'SERVER', 'ENTERPRISE'. ['DESKTOP']: ") or 'DESKTOP'
        print("-> Selected {}".format(type))
        print()
        if type == 'DESKTOP':
            print()
            variant = input(f"Type of desktop: 'DEFAULT', 'MATE', 'XFCE', 'GNOME'. ['{DEFAULT_VARIANT}']: ") or DEFAULT_VARIANT
            print("-> Selected {}".format(variant))
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
        print_block_devices(block_devices)
        print()
        disk_input = input("Specify a the disk to use (Format: '/dev/<DISK>') ['{}']: ".format(default_disk_name)) or default_disk_name
        print("-> Selected {}".format(disk_input))
        print()
        disk_encryption = input("Enable full disk encryption? ('yes', 'no') ['{}']: ".format('no')) or 'no'
        print("-> Selected {}".format(disk_encryption.lower()))
        if disk_encryption.lower() == 'yes':
            print()
            print('Note: You have selected to encrypt your hard disk. You will be prompted for a disk encryption password moments after the installation starts.')
            print()
            use_disk_encryption = True
    else:
        '''
        Run setup with params
        '''
        online_check()
        exit_if_system_config_exists()

        parser = argparse.ArgumentParser()
        parser.add_argument("-t", "--type", type=str, default="DESKTOP",
                            choices=['MINIMAL', 'DESKTOP', 'SERVER', 'ENTERPRISE'],
                            help="Installation type."
                            )
        parser.add_argument("-v", "--variant", type=str, default=DEFAULT_VARIANT,
                            choices=['DEFAULT', 'MATE', 'XFCE', 'GNOME'],
                            help="Desktop variant."
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
        parser.add_argument("-de", "--disk_encryption", type=bool, default=False,
                            help="Use full disk encryption. Defaults to False"
                            )
        parser.add_argument("-depw", "--disk_encryption_password", type=str,
                            help="Use full disk encryption. Defaults to False"
                            )
        parser.add_argument("-c", "--config", type=str,
                            help="Specify a enterprise config ID. This will overwrite all other settings."
                            )
        parser.add_argument("-curl", "--config_url", type=str, default="https://temp.pantherx.org/install",
                            )
        args = parser.parse_args()

        type = args.type
        variant = args.variant
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
        disk_encryption = args.disk_encryption
        if disk_encryption is True or disk_encryption == 'True':
            print()
            print('Note: You have selected to encrypt your hard disk. You will be prompted for a disk encryption password moments after the installation starts.')
            print()
            use_disk_encryption = True

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

    config = None

    if enterprise_config:
        config = SystemConfiguration(
            type=enterprise_config.type,
            variant=DEFAULT_VARIANT,
            firmware=firmware.lower(),
            hostname=hostname,
            timezone=enterprise_config.timezone,
            locale=enterprise_config.locale,
            username=username,
            password=password,
            public_key=public_key,
            disk=disk,
            use_disk_encryption=use_disk_encryption
        )

        print()
        print('######## SUMMARY ########')
        print()
        print("Type: {}".format(config.type))
        print("Firmware: {}".format(config.firmware))
        print("Hostname: {}".format(config.hostname))
        print("Locale: {}".format(config.locale))
        print("Time Zone: {}".format(config.timezone))
        # print("Username: {}".format(config.username))
        # print("Password: {}".format(config.password))
        # print("Public key: {}".format(config.public_key))
        print("Disk: {} ({} Gigabyte)".format(config.disk.dev_name, disk.size_in_gb()))
        print()

    else:
        config = SystemConfiguration(
            type=type,
            variant=variant,
            firmware=firmware.lower(),
            hostname=hostname,
            timezone=timezone,
            locale=locale,
            username=username,
            password=password,
            public_key=public_key,
            disk=disk,
            use_disk_encryption=use_disk_encryption
        )
        basic_config_check(config)

        print()
        print('######## SUMMARY ########')
        print()
        print("Type: {}".format(config.type))
        if config.type == 'DESKTOP':
            print("Variant: {}".format(variant))
        print("Firmware: {}".format(config.firmware))
        print("Hostname: {}".format(config.hostname))
        print("Locale: {}".format(config.locale))
        print("Time Zone: {}".format(config.timezone))
        print("Username: {}".format(config.username))
        print("Password: {}".format(config.password))
        print("Public key: {}".format(config.public_key))
        if use_disk_encryption:
            print("Disk: {} ({} Gigabyte) - Encrypted".format(config.disk.dev_name, disk.size_in_gb()))
        else:
            print("Disk: {} ({} Gigabyte)".format(config.disk.dev_name, disk.size_in_gb()))
        print()

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
