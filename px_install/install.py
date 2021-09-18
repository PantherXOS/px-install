'''Installation'''

import subprocess
from .classes import SystemConfiguration
from .system_config import write_system_config
from .system_channels import write_system_channels


def get_CMD_FORMAT_BIOS(disk: str):
    '''Expect /dev/sda or similiar'''
    part1 = "{}1".format(disk)
    part2 = "{}2".format(disk)

    CMD_FORMAT_BIOS = [
        ['parted', '-s', disk,
         '-- mklabel', 'msdos', 'mkpart', 'primary', 'fat32', '0%', '200M', 'mkpart', 'primary', '200M', '100%'],
        ['sgdisk', '-t', '1:ef02', disk],
        ['sgdisk', '-t', '2:8300', disk],
        ['parted', disk, 'set', '1', 'boot', 'on'],
        ['mkfs.ext4', '-L', 'my-root', part2]
    ]
    return CMD_FORMAT_BIOS


def get_CMD_FORMAT_EFI(disk: str):
    '''Expect /dev/sda or similiar'''
    part1 = "{}1".format(disk)
    part2 = "{}2".format(disk)
    CMD_FORMAT_EFI = [
        ['parted', '-s', disk,
         '-- mklabel', 'gpt', 'mkpart', 'primary', 'fat32', '0%', '200M', 'mkpart', 'primary', '200M', '100%'],
        ['sgdisk', '-t 1:ef00', disk],
        ['sgdisk', '-t 2:8300', disk],
        ['parted', disk, 'set', '1', 'esp', 'on'],
        ['mkfs.fat', '-F32', part1],
        ['mkfs.ext4', '-L my-root', part2]
    ]
    return CMD_FORMAT_EFI


CMD_PREP_INSTALL = [
    ['mount', 'LABEL=my-root', '/mnt'],
    ['herd', 'start cow-store', '/mnt'],
    ['mkdir', '/mnt/etc']
]

CMD_CREATE_SWAP = [
    ['dd', 'if=/dev/zero', 'of=/mnt/swapfile', 'bs=1MiB', 'count=4096'],
    ['chmod', '600', '/mnt/swapfile'],
    ['mkswap', '/mnt/swapfile'],
    ['swapon', '/mnt/swapfile']
]

CMD_INSTALL = [
    ['guix', 'pull', '--channels=/mnt/etc/channels.scm', '--disable-authentication'],
    ['hash', 'guix'],
    ['guix', 'system', 'init', '/mnt/etc/system.scm', '/mnt']
]


def run_commands(input: list):
    for command in input:
        subprocess.run(command)


def installation(config: 'SystemConfiguration'):
    firmware = config.firmware

    if firmware == 'bios':
        run_commands(get_CMD_FORMAT_BIOS(config.disk))
    if firmware == 'efi':
        run_commands(get_CMD_FORMAT_EFI(config.disk))

    run_commands(CMD_PREP_INSTALL)
    run_commands(CMD_CREATE_SWAP)

    write_system_config(config)
    write_system_channels()

    run_commands(CMD_INSTALL)

    print('You should set a root password and renew your user password after installation.')
