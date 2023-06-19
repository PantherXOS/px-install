'''Write channels config (repositories)'''

import shutil
import pkg_resources
from .util import run_commands


def write_system_substitutes_key(path: str = '/tmp/packages.pantherx.org.pub'):
    '''
    Writes substitute key temporary location

    This is for authorization during installation;
    After the installation, the key is available automatically trough the OS configuration.
    '''
    system_channels = pkg_resources.resource_filename(
        __name__, 'keys/packages.pantherx.org.pub'
    )
    shutil.copy(system_channels, path)


def authorize_substitute_server(key_path: str = '/tmp/packages.pantherx.org.pub'):
    '''
    Authorize system to use substitute server
    '''
    run_commands([[f"guix archive --authorize < {key_path}"]])