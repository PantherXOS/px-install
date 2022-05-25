'''Write system config with substituted values'''

# TODO: Probably easier to create the config from scratch than this ...

import os
import sys

import pkg_resources

from .classes import SystemConfiguration

available = [
    'base-desktop-bios-ssh.scm',
    'base-desktop-bios.scm',
    'base-desktop-efi-ssh.scm',
    'base-desktop-efi.scm',
    'base-server-bios-ssh.scm',
    'base-server-bios.scm',
    'base-server-efi-ssh.scm',
    'base-server-efi.scm'
]


def get_template_filename(config: SystemConfiguration):
    base = ""
    if config.public_key == 'NONE':
        base = "base-{}-{}.scm".format(config.type.lower(), config.firmware)
    else:
        base = "base-{}-{}-ssh.scm".format(config.type.lower(), config.firmware)
    return base


def matching_template_is_available(config: SystemConfiguration):
    template = get_template_filename(config)
    if template not in available:
        print("Invalid combination: {}. No template is available.".format(template))
        sys.exit()


def exit_if_system_config_exists():
    '''Rundimentary check to see this is not a installed system'''
    if os.path.isfile('/etc/system.scm'):
        print('You should not run this on a installed system.')
        sys.exit()


def write_system_config(config: SystemConfiguration, path: str = '/mnt/etc/system.scm'):
    '''Writes system config to /mnt/etc/system.scm'''
    matching_template_is_available(config)

    template_filename = get_template_filename(config)
    template = "templates/{}".format(template_filename)
    system_config_efi = pkg_resources.resource_filename(
        __name__, template
    )
    out = path

    f_in = open(system_config_efi, "r")
    f_out = open(out, "w")

    for line in f_in:
        skip_line = False
        updated = line
        updated = updated.replace('<HOSTNAME>', config.hostname)
        updated = updated.replace('<TIMEZONE>', config.timezone)
        updated = updated.replace('<LOCALE>', config.locale)
        updated = updated.replace('<USERNAME>', config.username)
        updated = updated.replace('<USER_PASSWORD>', config.password)
        updated = updated.replace(
            '<USER_COMMENT>', "{}'s account".format(config.username)
        )
        updated = updated.replace('<USER_HOME>', config.username)
        updated = updated.replace('<DISK>', config.disk.dev_name)
        
        if config.use_disk_encryption:
            partitionUuid = '''(uuid "{}" 'fat32)'''.format(config.disk.get_partition_uuid(1))
            # TODO: Should be (device (uuid "14C5-1711" 'fat32))
            updated = updated.replace('"<PARTITION_ONE>"', partitionUuid)
        else:
            updated = updated.replace('<PARTITION_ONE>', config.disk.get_partition_dev_name(1))

        if config.public_key != 'NONE':
            updated = updated.replace('<PUBLIC_KEY>', config.public_key)

        if '<MAPPED_DEVICES_' in updated:
            if config.use_disk_encryption:
                if '<MAPPED_DEVICES_1>' in updated:
                    updated = updated.replace('<MAPPED_DEVICES_1>', '(mapped-devices')
                if '<MAPPED_DEVICES_2>' in updated:
                    updated = updated.replace('<MAPPED_DEVICES_2>', ' (list (mapped-device')
                if '<MAPPED_DEVICES_3>' in updated:
                    updated = updated.replace('<MAPPED_DEVICES_3>', '        (source')
                if '<MAPPED_DEVICES_4>' in updated:
                    partition_uuid = config.disk.get_partition_uuid(2)
                    updated = updated.replace('<MAPPED_DEVICES_4>', '         (uuid "{}"))'.format(partition_uuid))
                if '<MAPPED_DEVICES_5>' in updated:
                    updated = updated.replace('<MAPPED_DEVICES_5>', '        (target "cryptroot")')
                if '<MAPPED_DEVICES_6>' in updated:
                    updated = updated.replace('<MAPPED_DEVICES_6>', '        (type luks-device-mapping))))')
            else:
                skip_line = True

        if '<ROOT_FILE_SYSTEM_' in updated:
            if config.use_disk_encryption:
                if '<ROOT_FILE_SYSTEM_1>' in updated:
                    updated = updated.replace('<ROOT_FILE_SYSTEM_1>', '(file-system')
                if '<ROOT_FILE_SYSTEM_2>' in updated:
                    updated = updated.replace('<ROOT_FILE_SYSTEM_2>', ' (device "/dev/mapper/cryptroot")')
                if '<ROOT_FILE_SYSTEM_3>' in updated:
                    updated = updated.replace('<ROOT_FILE_SYSTEM_3>', ' (mount-point "/")')
                if '<ROOT_FILE_SYSTEM_4>' in updated:
                    updated = updated.replace('<ROOT_FILE_SYSTEM_4>', ' (type "ext4")')
                if '<ROOT_FILE_SYSTEM_5>' in updated:
                    updated = updated.replace('<ROOT_FILE_SYSTEM_5>', ' (dependencies mapped-devices))')

            else:
                if '<ROOT_FILE_SYSTEM_1>' in updated:
                    updated = updated.replace('<ROOT_FILE_SYSTEM_1>', '(file-system')
                if '<ROOT_FILE_SYSTEM_2>' in updated:
                    updated = updated.replace('<ROOT_FILE_SYSTEM_2>', ' (device (file-system-label "my-root"))')
                if '<ROOT_FILE_SYSTEM_3>' in updated:
                    updated = updated.replace('<ROOT_FILE_SYSTEM_3>', ' (mount-point "/")')
                if '<ROOT_FILE_SYSTEM_4>' in updated:
                    updated = updated.replace('<ROOT_FILE_SYSTEM_4>', ' (type "ext4"))')
                if '<ROOT_FILE_SYSTEM_5>' in updated:
                    skip_line = True

        
        if not skip_line:
            f_out.write(updated)

    f_in.close()
    f_out.close()
