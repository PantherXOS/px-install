'''Installation'''

import time
from .classes import BlockDevice, SystemConfiguration
from .remote_config import (move_enterprice_channels,
                            move_enterprise_system_config)
from .system_channels import write_system_channels
from .system_config import write_system_config
from .util import pre_install_environment_check, run_commands


def get_CMD_FORMAT_BIOS(disk: BlockDevice):
    '''Expect /dev/sda or similiar'''
    part2 = disk.get_partition_dev_name(2)

    cmd_format_bios = [
        [
            'parted', '-s', disk.dev_name, '--',
            'mklabel', 'gpt',
            'mkpart', 'primary', 'fat32', '0%', '10M',
            'mkpart', 'primary', '10M', '99%'
        ],
        # ['sgdisk', '-t', '1:ef02', disk.dev_name],
        # ['sgdisk', '-t', '2:8300', disk.dev_name],
        # ['parted', disk.dev_name, 'set', '1', 'boot', 'on'],
        ['parted', disk.dev_name, 'set', '1', 'bios_grub', 'on'],
        ['mkfs.ext4', '-q', '-L', 'my-root', part2]
    ]
    return cmd_format_bios


def get_CMD_FORMAT_EFI(disk: BlockDevice):
    '''Expect /dev/sda or similiar'''
    part1 = disk.get_partition_dev_name(1)
    part2 = disk.get_partition_dev_name(2)

    cmd_format_efi = [
        [
            'parted', '-s', disk.dev_name, '--',
            'mklabel', 'gpt',
            'mkpart', 'primary', 'fat32', '0%', '200M',
            'mkpart', 'primary', '200M', '100%'
        ],
        ['sgdisk', '-t', '1:ef00', disk.dev_name],
        ['sgdisk', '-t', '2:8300', disk.dev_name],
        ['parted', disk.dev_name, 'set', '1', 'esp', 'on'],
        ['mkfs.fat', '-I', '-F32', part1],
        ['mkfs.ext4', '-q', '-L', 'my-root', part2],
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


def installation(config: SystemConfiguration, is_enterprise_config: bool = False):
    firmware = config.firmware

    print('=> (1) Formatting hard disk {} ...'.format(config.disk.dev_name))
    if firmware == 'bios':
        run_commands(get_CMD_FORMAT_BIOS(config.disk), show_progress=False)
    if firmware == 'efi':
        run_commands(get_CMD_FORMAT_EFI(config.disk), show_progress=False)

    # Testing ...
    time.sleep(1)

    print('=> (2) Mounting partitions ...')
    run_commands(CMD_PREP_INSTALL)

    # Testing ...
    time.sleep(1)

    print('=> (3) Creating SWAP file ...')
    run_commands(CMD_CREATE_SWAP, show_progress=False)

    # Testing ...
    time.sleep(1)

    if is_enterprise_config:
        move_enterprise_system_config()
        move_enterprice_channels()
    else:
        print('=> (4) Writing system configuration ...')
        write_system_config(config)
        write_system_channels()

    # Testing ...
    time.sleep(1)

    pre_install_environment_check(config)

    print('=> (5) Starting installation ...')
    print('Depending on your internet connection speed and system performance, this operation will take 10 to 90 minutes.')
    run_commands(CMD_INSTALL)

    print()
    print("PantherX OS has been installed successfully.")
    print("")
    print("You should change your user and root password after reboot.")
    print("Reboot with 'reboot'")
