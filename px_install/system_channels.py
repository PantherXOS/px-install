'''Write channels config (repositories)'''

import shutil

import pkg_resources


def write_system_channels(path: str = '/mnt/etc/channels.scm'):
    '''Writes channels file to /mnt/etc/channels.scm'''
    system_channels = pkg_resources.resource_filename(
        __name__, 'templates/channels.scm'
    )
    shutil.copy(system_channels, path)
