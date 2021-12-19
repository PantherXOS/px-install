''' Get enterprise device config from S3 by ID '''

import json
import os
import shutil
import subprocess

from requests import get

from .classes import EnhancedJSONEncoder, RemoteConfig


def write_json_config(config: RemoteConfig, path: str = '/root/config/config.json'):
    '''Write config (mostly for testing)'''
    config_json = json.dumps(config, cls=EnhancedJSONEncoder)

    with open(path, 'w') as file:
        file.write(config_json)

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


def get_enterprise_config(config_id: str, url: str = 'https://temp.pantherx.org/install', path: str = '/root'):
    '''Download the config archive from the given url'''
    config_archive = '{}/config.tar.gz'.format(path)
    config_dir = '{}/config'.format(path)
    download_url = '{}/{}.tar.gz'.format(url, config_id)
    with get(download_url) as download:
        download.raise_for_status()
        with open(config_archive, 'wb') as file:
            file.write(download.content)

    os.makedirs(config_dir)
    subprocess.run(['tar', '-xvzf', config_archive, '-C', config_dir], check=True)

    config_path = '{}/config/config.json'.format(path)
    config = read_json_config(config_path)
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


def cleanup_enterprise_config(dir: str = '/root'):
    '''cleanup enterprise config archive and extracted folder'''
    config_archive = '{}/config.tar.gz'.format(dir)
    config_path = '{}/config'.format(dir)
    os.remove(config_archive)
    # os.rmdir(config_path)
    shutil.rmtree(config_path)
