'''Write system config with substituted values'''

import os
import sys
import pkg_resources
from .classes import SystemConfiguration


def exit_if_system_config_exists():
    '''Rundimentary check to see this is not a installed system'''
    if os.path.isdir('/etc/'):
        print('You should not run this on a installed system.')
        sys.exit()


def write_system_config(config: 'SystemConfiguration', path: str = '/mnt/etc/system.scm'):
    '''Writes system config to /mnt/etc/system.scm'''
    template = "templates/base-{}-{}.scm".format(config.type, config.firmware)
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

        f_out.write(updated)
