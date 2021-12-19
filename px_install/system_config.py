'''Write system config with substituted values'''

import os
import sys

import pkg_resources

from .classes import SystemConfiguration

available = [
    'base-desktop-bios-ssh.scm',
    'base-desktop-bios.scm',
    'base-desktop-efi-ssh.scm',
    'base-desktop-efi.scm'
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
        updated = updated.replace('<PARTITION_ONE>', config.disk.get_partition_dev_name(1))

        if config.public_key != 'NONE':
            updated = updated.replace('<PUBLIC_KEY>', config.public_key)

        f_out.write(updated)

    f_in.close()
    f_out.close()
