'''Write channels config (repositories)'''

import shutil
import pkg_resources
from .util import run_commands
from typing import List


def write_system_substitutes_key(paths: str = ['/tmp/packages.pantherx.org.pub', '/tmp/substitutes.nonguix.org.pub']):
    '''
    Writes substitute key temporary location

    This is for authorization during installation;
    After the installation, the key is available automatically trough the OS configuration.

    Important: The filename (/your_path/FILENAME) must match a available pkg_resources resource in keys/... .
    '''

    for path in paths:
        # Get filename from path
        filename = path.split('/')[-1]
        key = pkg_resources.resource_filename(
            __name__, f"keys/{filename}"
        )
        shutil.copy(key, path)


def authorize_substitute_server(key_paths: List[str] = ['/tmp/packages.pantherx.org.pub', '/tmp/substitutes.nonguix.org.pub']):
    '''
    Authorize system to use substitute server
    '''
    for key_path in key_paths:
        run_commands([[f"guix archive --authorize < {key_path}"]])