'''Misc'''

import os
import random
import re
import string
import subprocess

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
    else:
        for command in commands:
            command_string = list_of_commands_to_string(command)
            res = subprocess.run(command_string, shell=True, stdout=subprocess.DEVNULL)
            if res.stderr:
                print(res.stderr)
