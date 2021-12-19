'''Misc'''

import json
import os
import random
import re
import string
import subprocess

import cpuinfo
import qrcode
import urllib3
from pytz import all_timezones
from tqdm import tqdm


def check_efi_or_bios():
    '''Check if EFI is supported'''
    firmware = ''
    if os.path.exists('/sys/firmware/efi'):
        firmware = 'efi'
    else:
        firmware = 'bios'
    return firmware


def print_disks():
    '''List all block devices'''
    subprocess.run(['lsblk'], check=True)


def random_hostname(name: str, length: int = 6):
    '''Generate a random hostname from name'''
    return name + '-' + ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(length))


def is_valid_hostname(hostname) -> bool:
    '''Validate a given string as hostname'''
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    if len(hostname) > 253:
        return False

    labels = hostname.split(".")

    # the TLD must be not all-numeric
    if re.match(r"[0-9]+$", labels[-1]):
        return False

    allowed = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(label) for label in labels)


def is_valid_timezone(timezone: str) -> bool:
    if timezone in all_timezones:
        return True
    else:
        return False


def list_of_commands_to_string(command: list):
    final = ''
    total = len(command)
    count = 1
    for item in command:
        if count == total:
            final += item
        else:
            final += "{} ".format(item)
        count += 1
    return final


def run_commands(commands: list, show_progress: bool = True):
    '''Execute an array of commands'''
    if show_progress:
        for command in tqdm(commands):
            command_string = list_of_commands_to_string(command)
            res = subprocess.run(command_string, shell=True, stdout=subprocess.DEVNULL)
            if res.stderr:
                print(res.stderr)
                raise Exception(res.stderr)
    else:
        for command in commands:
            command_string = list_of_commands_to_string(command)
            res = subprocess.run(command_string, shell=True, stdout=subprocess.DEVNULL)
            if res.stderr:
                print(res.stderr)
                raise Exception(res.stderr)


def convert_size_string(value: str):
    size = 0
    if 'T' in value:
        clean = value[:-1]
        size = float(clean) * 1000000
    elif 'G' in value:
        clean = value[:-1]
        size = float(clean) * 1000
    elif 'M' in value:
        clean = value[:-1]
        size = float(clean)
    else:
        raise ValueError('Could not convert {} to a number.'.format(value))
    return size


def pre_install_environment_check(config):
    disk = config.disk
    disk.reload()

    errors = []

    data_partition = disk.get_partition_dev_name(2)
    data_partition_valid = disk.is_valid_partition(data_partition)
    if not data_partition_valid:
        errors.append('Partition {} does not exist')

    swap_file_found = os.path.isfile('/mnt/swapfile')
    if not swap_file_found:
        errors.append('Swap file /mnt/swapfile does not exist.')

    system_config_found = os.path.isfile('/mnt/etc/system.scm')
    if not system_config_found:
        errors.append('System config /mnt/etc/system.scm does not exist.')

    if len(errors) > 0:
        for error in errors:
            print(error)
        raise EnvironmentError('Installation pre-requirement(s) check failed.')


def print_debug_qr_code(debug: str):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(debug)
    qr.print_ascii(invert=True)


def generate_and_print_debug_info(config, version, error=''):
    error_truncate = (error[:50] + '..') if len(error) > 50 else error
    debug_output = {
        'v': version,
        'c': cpuinfo.get_cpu_info()['brand_raw'],
        'f': config.firmware,
        # 'l': config.locale,
        'd': config.disk.name,
        'e': error_truncate,
    }
    print_debug_qr_code(json.dumps(debug_output))


def is_online():
    try:
        http = urllib3.PoolManager()
        http.request('GET', 'http://138.201.123.174', timeout=1)
        return True
    except:
        return False
