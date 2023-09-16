'''Installation'''

import time
from typing import List

from .block_devices import get_block_devices, get_largest_valid_block_device
from .defaults import DEFAULT_LOCALE, DEFAULT_VARIANT
from .system_substitutes import authorize_substitute_server, write_system_substitutes_key
from .classes import BlockDevice, SystemConfiguration
from .remote_config import (copy_enterprise_channels, copy_enterprise_json_config,
                            copy_enterprise_system_config)
from .system_channels import write_system_channels
from .system_config import write_system_config
from .util import check_efi_or_bios, pre_install_environment_check, random_hostname, run_commands


def get_format_system_partition_CMD(part2: str, use_disk_encryption: bool):
    if use_disk_encryption:
        return [
            ['cryptsetup', 'luksFormat', part2],
            ['cryptsetup', 'open', '--type', 'luks', part2, 'cryptroot'],
            ['mkfs.ext4', '-q', '-L', 'my-root', '/dev/mapper/cryptroot']
        ]
    else:
        return [
            ['mkfs.ext4', '-q', '-L', 'my-root', part2]
        ]



def get_CMD_FORMAT_BIOS(disk: BlockDevice, use_disk_encryption: bool):
    '''Expect /dev/sda or similiar'''
    part2 = disk.get_partition_dev_name(2)

    cmd_format_partition = get_format_system_partition_CMD(part2, use_disk_encryption)
    cmd_format_bios = [
        [
            'parted', '-s', disk.dev_name, '--',
            'mklabel', 'gpt',
            'mkpart', 'primary', 'fat32', '0%', '10M',
            'mkpart', 'primary', '10M', '99%'
        ],
        ['parted', disk.dev_name, 'set', '1', 'bios_grub', 'on'],
        *cmd_format_partition
    ]
    return cmd_format_bios


def get_CMD_FORMAT_EFI(disk: BlockDevice, use_disk_encryption: bool):
    '''Expect /dev/sda or similiar'''
    part1 = disk.get_partition_dev_name(1)
    part2 = disk.get_partition_dev_name(2)

    cmd_format_partition = get_format_system_partition_CMD(part2, use_disk_encryption)
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
        *cmd_format_partition,
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

CMD_INSTALL_PULL = [
    ['guix', 'pull', '--channels=/mnt/etc/guix/channels.scm'],
]

CMD_INSTALL_PULL_HASH = [
    ['hash', 'guix'],
    ['GUIX_PROFILE="$HOME/.config/guix/current"', '&&', '. "$GUIX_PROFILE/etc/profile"'],
]

CMD_INSTALL = [
    [
        'GUIX_PROFILE="$HOME/.config/guix/current"', '&&', '. "$GUIX_PROFILE/etc/profile"', '&&', 'hash', 'guix', '&&'
        'guix', 'system', 'init', '/mnt/etc/system.scm', '/mnt', "--substitute-urls='https://bordeaux.guix.gnu.org https://ci.guix.gnu.org https://packages.pantherx.org https://substitutes.nonguix.org'"
    ]
]


def installation(config: SystemConfiguration, is_enterprise_config: bool = False):
    firmware = config.firmware

    print('=> (1) Formatting hard disk {} ...'.format(config.disk.dev_name))

    support_user_input = False
    if config.use_disk_encryption:
        # This is necessary for the password prompt to show, during disk encryption.
        support_user_input = True

    if firmware == 'bios':
        run_commands(get_CMD_FORMAT_BIOS(config.disk, config.use_disk_encryption), support_user_input=support_user_input)
    if firmware == 'efi':
        run_commands(get_CMD_FORMAT_EFI(config.disk, config.use_disk_encryption), support_user_input=support_user_input)

    # Testing ...
    time.sleep(2)

    print('=> (2) Mounting partitions ...')
    run_commands(CMD_PREP_INSTALL)

    # Testing ...
    time.sleep(2)

    print('=> (3) Creating SWAP file ...')
    run_commands(CMD_CREATE_SWAP)

    # Testing ...
    time.sleep(2)

    if is_enterprise_config:
        print('=> (4) Authorize substitutes from packages.pantherx.org ...')
        write_system_substitutes_key()
        time.sleep(1)
        authorize_substitute_server()
        print('=> (5) Writing enterprise system configuration ...')
        copy_enterprise_system_config()
        copy_enterprise_json_config()
        copy_enterprise_channels()
    else:
        print('=> (4) Authorize substitutes from packages.pantherx.org ...')
        write_system_substitutes_key()
        time.sleep(1)
        authorize_substitute_server()
        print('=> (5) Writing system configuration ...')
        write_system_config(config)
        write_system_channels()

    # Testing ...
    time.sleep(2)

    pre_install_environment_check(config)

    print('=> (6) Starting installation ...')
    print('Depending on your internet connection speed and system performance, this operation will take 10 to 90 minutes.')
    print('')
    print('=> (6.1) Downloading the latest changes ...')
    run_commands(CMD_INSTALL_PULL, allow_retry=True, print_stats=True)
    run_commands(CMD_INSTALL_PULL_HASH)
    print('\nFinished downloading the latest changes.\n')
    print('=> (6.2) Installing ...')
    run_commands(CMD_INSTALL, allow_retry=True, print_stats=True)

    print('')
    print("PantherX OS has been installed successfully.")
    print("")
    print("You should change your user and root password after reboot.")
    print("Reboot with 'reboot'")


def default_system_configuration() -> SystemConfiguration:
    '''
    SystemConfiguration with defaults set.:
    - type (default: DESKTOP)
    - variant (default: DEFAULT)
    - firmware (default: auto: bios/efi)
    - hostname (default: pantherx-....)
    - timezone (default: Europe/Berlin)
    - locale (default: en_US.utf8)
    - username (default: panther)
    - password (default: pantherx)
    - public_key (default: NONE)
    - use_disk_encryption (default: False)

    Will throw a ValueError when no block device has been found.
    '''

    block_devices = get_block_devices()
    largest_block_device = get_largest_valid_block_device(block_devices)
    if largest_block_device is None:
        raise ValueError('No valid block device found.')
    return SystemConfiguration(
        type="DESKTOP",
        variant=DEFAULT_VARIANT,
        firmware=check_efi_or_bios(),
        hostname=random_hostname('pantherx', 6),
        timezone="Europe/Berlin",
        locale=DEFAULT_LOCALE,
        username="panther",
        password="pantherx",
        public_key="NONE",
        disk=largest_block_device,
        use_disk_encryption=False
    )

class SystemInstallation():
    config: SystemConfiguration
    is_enterprise_config: bool
    
    step: int = 0
    errors: List

    def __init__(self, config: SystemConfiguration, is_enterprise_config = False):
        self.config = config
        self.is_enterprise_config = is_enterprise_config

    def format(self):
        '''First step: formatting'''
        if self.config.firmware == 'bios':
            run_commands(get_CMD_FORMAT_BIOS(self.config.disk, self.config.use_disk_encryption))
        if self.config.firmware == 'efi':
            run_commands(get_CMD_FORMAT_EFI(self.config.disk, self.config.use_disk_encryption))
        self.step = 1

    def mount_partitions(self):
        '''Second step: mount partitions'''
        run_commands(CMD_PREP_INSTALL)
        self.step = 2

    def create_swap(self):
        '''Third step: create a swap file'''
        run_commands(CMD_CREATE_SWAP)
        self.step = 3

    def generate_config(self):
        '''Forth step: generate system config'''

        if self.is_enterprise_config:
            print('=> (4) Writing enterprise system configuration ...')
            copy_enterprise_system_config()
            copy_enterprise_json_config()
            copy_enterprise_channels()
        else:
            print('=> (4) Writing system configuration ...')
            write_system_config(self.config)
            write_system_channels()
        self.step = 4

    def pull(self):
        '''Fifth step: pull channel data'''
        # TODO: Remove 'capture_output=False'
        run_commands(CMD_INSTALL_PULL, allow_retry=True, print_stats=True)
        run_commands(CMD_INSTALL_PULL_HASH)
        self.step = 5

    def install(self):
        '''Sixth step: install system'''
        # TODO: Remove 'capture_output=False'
        run_commands(CMD_INSTALL, allow_retry=True, print_stats=True)
        self.step = 6