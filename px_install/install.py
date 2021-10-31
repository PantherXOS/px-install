'''Installation'''

from px_install.util import list_of_commands_to_string
import subprocess
from .classes import SystemConfiguration
from .system_config import write_system_config
from .system_channels import write_system_channels
from .remote_config import move_enterprice_channels, move_enterprise_system_config


def get_CMD_FORMAT_BIOS(disk: str):
    '''Expect /dev/sda or similiar'''
    part1 = "{}1".format(disk)
    part2 = "{}2".format(disk)

    cmd_format_bios = [
        [
            'parted', '-s', disk, '--',
            'mklabel', 'msdos',
            'mkpart', 'primary', 'fat32', '0%', '10M',
            'mkpart', 'primary', '10M', '100%'
        ],
        ['sgdisk', '-t', '1:ef02', disk],
        ['sgdisk', '-t', '2:8300', disk],
        ['parted', disk, 'set', '1', 'boot', 'on'],
        ['mkfs.ext4', '-L', 'my-root', part2]
    ]
    return cmd_format_bios


def get_CMD_FORMAT_EFI(disk: str):
    '''Expect /dev/sda or similiar'''
    part1 = "{}1".format(disk)
    part2 = "{}2".format(disk)
    cmd_format_efi = [
        [
            'parted', '-s', disk, '--',
            'mklabel', 'gpt',
            'mkpart', 'primary', 'fat32', '0%', '200M',
            'mkpart', 'primary', '200M', '100%'
        ],
        ['sgdisk', '-t', '1:ef00', disk],
        ['sgdisk', '-t', '2:8300', disk],
        ['parted', disk, 'set', '1', 'esp', 'on'],
        ['mkfs.fat', '-F32', part1],
        ['mkfs.ext4', '-L', 'my-root', part2],
        ['mkdir', '/boot/efi'],
        ['mount', part1, '/boot/efi']
    ]
    return cmd_format_efi


CMD_PREP_INSTALL = [
    ['mount', 'LABEL=my-root', '/mnt'],
    ['herd', 'start', 'cow-store', '/mnt'],
    ['mkdir', '/mnt/etc'],
    ['mkdir', '/mnt/etc/guix']
]

CMD_CREATE_SWAP = [
    ['dd', 'if=/dev/zero', 'of=/mnt/swapfile', 'bs=1MiB', 'count=4096'],
    ['chmod', '600', '/mnt/swapfile'],
    ['mkswap', '/mnt/swapfile'],
    ['swapon', '/mnt/swapfile']
]

CMD_INSTALL = [
    ['guix', 'pull', '--channels=/mnt/etc/guix/channels.scm', '--disable-authentication'],
    ['hash', 'guix'],
    ['guix', 'system', 'init', '/mnt/etc/system.scm', '/mnt']
]


def run_commands(commands: list):
    '''Execute an array of commands'''
    for command in commands:
        command_string = list_of_commands_to_string(command)
        subprocess.run(command_string, check=True, shell=True)


def installation(config: SystemConfiguration, is_enterprise_config: bool = False):
    firmware = config.firmware

    if firmware == 'bios':
        run_commands(get_CMD_FORMAT_BIOS(config.disk))
    if firmware == 'efi':
        run_commands(get_CMD_FORMAT_EFI(config.disk))

    run_commands(CMD_PREP_INSTALL)
    run_commands(CMD_CREATE_SWAP)

    if is_enterprise_config:
        move_enterprise_system_config()
        move_enterprice_channels()
    else:
        write_system_config(config)
        write_system_channels()

    run_commands(CMD_INSTALL)

    print('You should set a root password and change your user password after installation.')
