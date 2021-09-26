''' Get enterprise device config from S3 by ID '''

import json
import subprocess
import shutil
import os

from requests import get

from .classes import RemoteConfig


def read_json_config(path: str = '/root/config/config.json'):
    '''Read config from extracted archive'''
    type = None
    timezone = None
    locale = None
    title = None
    location = None
    role = None
    key_security = None
    key_type = None
    domain = None
    host = None

    with open(path, 'r') as file:
        json_content = file.read()
        content = json.loads(json_content)
        type = content['type']
        timezone = content['timezone']
        locale = content['locale']
        title = content['title']
        location = content['location']
        role = content['role']
        key_security = content['key_security']
        key_type = 'RSA:2048'
        domain = content['domain']
        host = content['host']

    config = RemoteConfig(
        type,
        timezone,
        locale,
        title,
        location,
        role,
        key_security,
        key_type,
        domain,
        host
    )

    return config


def get_enterprise_config(config_id: str, url: str = 'https://temp.pantherx.org/install'):
    '''Download the config archive from the given url'''
    download_url = '{}/{}'.format(url, config_id)
    with get(download_url) as download:
        download.raise_for_status()
        with open('/root/config.tgz', 'wb') as file:
            file.write(download.content)

    subprocess.run(['tar', '-xvzf', '/root/config.tgz', '-C', '/root/config'], check=True)

    config = read_json_config()
    return config


def move_enterprise_system_config(src: str = '/root/config/system.scm', dest: str = '/mnt/etc/system.scm'):
    '''move the system config from the extracted archive to the final location'''
    shutil.copy(src, dest)


def move_enterprice_channels(src: str = '/root/config/channels/scm', dest_path: str = '/mnt/etc/guix', dest_file: str = 'channels.scm'):
    '''move the channels config from the extracted archive to the final location (create if necessary)'''
    if not os.path.isdir(dest_path):
        os.makedirs(dest_path)
    dest = "{}/{}".format(dest_path, dest_file)
    shutil.copy(src, dest)


def cleanup_enterprise_config(config_archive: str = '/root/config.tgz', config_path: str = '/root/config'):
    '''cleanup enterprise config archive and extracted folder'''
    os.remove(config_archive)
    os.rmdir(config_path)