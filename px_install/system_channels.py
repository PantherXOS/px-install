'''Write channels config (repositories)'''

import pkg_resources


def write_system_channels(path: str = '/mnt/etc/channels.scm'):
    '''Writes channels file to /mnt/etc/channels.scm'''
    system_channels = pkg_resources.resource_filename(
        __name__, 'templates/channels.scm'
    )
    out = path

    f_in = open(system_channels, "r")
    f_out = open(out, "w")

    for line in f_in:
        f_out.write(line)
