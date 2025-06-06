'''Misc'''

import json
import os
import random
import re
import string
import subprocess
import sys
import threading
import time
from subprocess import Popen, PIPE

import cpuinfo
import qrcode
import urllib3
from pytz import all_timezones


def check_efi_or_bios():
    '''Check if EFI is supported'''
    firmware = ''
    if os.path.exists('/sys/firmware/efi'):
        firmware = 'efi'
    else:
        firmware = 'bios'
    return firmware


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
    '''
    Check whether the given timezone is valid.
    For ex. 'Europe/Berlin'
    '''
    if timezone in all_timezones:
        return True
    else:
        return False


def list_of_commands_to_string(command: list):
    '''
    Combine a list of comma-seperated commands to string
    For ex. ['ls', '-a'] -> 'ls -a'
    '''
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


def decode_return_value(value: bytes):
    try:
        result = value.decode()
        if value != "":
            return result
    except:
        if value != "":
            return value

    return None


def _run_command_process(command_string: str, silent=False, support_user_input=False, print_stats=False):
    if support_user_input:
        result = subprocess.run(command_string, shell=True,)
        if result.returncode != 0:
            return {'result': None, 'error': result.stderr}
        else:
            return {'result': result.stdout, 'error': None}
    else:
        with Popen(command_string, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True) as process:
            # Use threading instead of multiprocessing to avoid Manager().Queue() issues

            stdout_lines = []
            stderr_lines = []

            def read_stdout():
                for line in iter(process.stdout.readline, ""):
                    if not silent:
                        print(line, end="")
                    stdout_lines.append(line)
                process.stdout.close()

            def read_stderr():
                for line in iter(process.stderr.readline, ""):
                    if not silent:
                        print(line, end="")
                    stderr_lines.append(line)
                process.stderr.close()

            stdout_thread = threading.Thread(target=read_stdout)
            stderr_thread = threading.Thread(target=read_stderr)

            stdout_thread.start()
            stderr_thread.start()

            stdout_thread.join()
            stderr_thread.join()

            process.wait()

            output = "".join(stdout_lines)
            error = "".join(stderr_lines)
            error_message = f'Command exited with error code: {process.returncode}.'

            if process.returncode != 0:
                if error:
                    return {'result': None, 'error': error}
                else:
                    return {'result': None, 'error': error_message}

            if output:
                return {'result': output, 'error': None}
            else:
                return {'result': None, 'error': None}


def run_commands(commands: list, allow_retry: bool = False, silent: bool = True, support_user_input: bool = False, print_stats: bool = False):
    '''
    Execute an array of commands
    
    params:
        commands: a list of commands: [['ls', '-a'], ['ls']]
        allow_retry: if True, retry on known error patterns
        silent: if True, don't print output
        support_user_input: if True, allow user input (will use subprocess.run instead of Popen)
        print_stats: print CPU and Memory usage
    '''

    RETRY_MESSAGES = ["invalid option -- 'C'", "error: TLS error in procedure", "guix-command substitute' died unexpectedly", "HTTP download failed"]

    for command in commands:
        retries = 0
        while True:
            command_string = list_of_commands_to_string(command)
            result = _run_command_process(command_string, silent=silent, support_user_input=support_user_input, print_stats=print_stats)

            if result['error']:
                if allow_retry and any(message in result['error'] for message in RETRY_MESSAGES) and retries < 3:
                    print(f'''
Something went wrong ...

#########

{result['error']}

########

Automatic retrying due to known error pattern.
                    ''')
                    retries += 1
                    if retries == 2:
                        for i in range(1, 6):
                            print(f"Retrying in {6-i} minutes...")
                            time.sleep(60)
                    elif retries == 3:
                        for i in range(1, 2):
                            print(f"Retrying in {2-i} minutes...")
                            time.sleep(60)
                elif allow_retry:
                    print(f'''
Something went wrong ...

#########

{result['error']}

########

Would you like to retry the last operation? 
This usually helps in case of network hiccups.
                    ''')
                    retry = input("Retry last operation? 'yes' to retry; 'no' to cancel [yes/no]: ")
                    user_input = retry.lower()
                    if user_input != 'yes' and user_input != 'retry':
                        raise Exception(result['error'])
                else:
                    raise Exception(result['error'])
            else:
                break


def convert_size_string(value: str):
    '''
    Extract the numeric size from lsblk disk size output
    '''
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
    elif 'K' in value:
        clean = value[:-1]
        size = float(clean) / 1000
    elif 'B' in value:
        clean = value[:-1]
        size = float(clean) / 1000000
    else:
        raise ValueError('Could not convert {} to a number.'.format(value))
    return size


def pre_install_environment_check(config):
    '''
    Runs a bunch of checks to ensure the environment is ready
    1. Partition exists
    2. Swapfile is ready
    3. Config found

    Raises an EnvironmentError in case any check fails
    '''

    # TODO: Disk check is disabled due to many errors reloading disk partitions info
    # Could not reload block device /dev/nvme0n1
    # disk = config.disk
    # disk.reload()

    errors = []

    # data_partition = disk.get_partition_dev_name(2)
    # data_partition_valid = disk.is_valid_partition(data_partition)
    # if disk.size_in_gb() < 19:
    #     errors.append('The selected disk {} is not large enough to comfortably run this operating system.')

    # if not data_partition_valid:
    #     errors.append('Partition {} does not exist')

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
    '''
    Generate a QR code from the given string and print to terminal
    '''
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(debug)
    qr.print_ascii(invert=True)


def generate_and_print_debug_info(config, version, error=''):
    '''
    Collect some debugging info to include in the QR code
    '''
    error_truncate = (error[:200] + '..') if len(error) > 200 else error

    cpu = ''

    cpu_info_result = cpuinfo.get_cpu_info()
    if 'brand_raw' in cpu_info_result:
        cpu = cpu_info_result['brand_raw']
    elif 'vendor_id_raw' in cpu_info_result:
        cpu = cpu_info_result['vendor_id_raw']
    else:
        cpu = 'Unknown'

    debug_output = {
        'v': version,
        'c': cpu,
        'f': config.firmware,
        # 'l': config.locale,
        'd': config.disk.name,
        'e': error_truncate,
    }
    print_debug_qr_code(json.dumps(debug_output))


def is_online():
    '''
    Checks that the user is online
    '''
    try:
        http = urllib3.PoolManager()
        http.request('GET', 'https://channels.pantherx.org', timeout=1)
        return True
    except:
        return False


def online_check():
    '''
    Inline online check based on is_online
    -> Will exit if not online
    '''
    online = is_online()
    if not online:
        print()
        print('######## ERROR ########')
        print('Your system does not appear to have an active internet connection.')
        print()
        print_debug_qr_code('https://wiki.pantherx.org/Installation-guide/#connect-to-the-internet')
        print('Scan to open: https://wiki.pantherx.org/Installation-guide/#connect-to-the-internet')
        sys.exit(1)
