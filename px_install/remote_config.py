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

    with open(path, 'w') as writer:
        writer.write(config_json)

def read_json_config(path: str = '/root/config/config.json'):
    '''Read config from extracted archive'''
    content_dict = None
    with open(path, 'r') as reader:
        file_content = reader.read()
        content_dict = json.loads(file_content)

    '''May not be defined // TODO: remove this when all configs are updated'''
    key_type = 'key_type' in content_dict and content_dict['key_type'] or 'RSA:2048'

    config = RemoteConfig(
        type=content_dict['type'],
        timezone=content_dict['timezone'],
        locale=content_dict['locale'],
        title=content_dict['title'],
        location=content_dict['location'],
        role=content_dict['role'],
        key_security=content_dict['key_security'],
        key_type=key_type,
        domain=content_dict['domain'],
        host=content_dict['host']
    )

    return config


def get_enterprise_config(config_id: str, url: str = 'https://temp.pantherx.org/install', path: str = '/root'):
    '''Download the config archive from the given url'''
    config_archive = '{}/config.tar.gz'.format(path)
    config_dir = '{}/config'.format(path)
    download_url = '{}/{}.tar.gz'.format(url, config_id)
    print('=> Downloading enterprise config from {} to {}.'.format(download_url, config_archive))
    with get(download_url) as download:
        download.raise_for_status()
        with open(config_archive, 'wb') as file:
            file.write(download.content)

    os.makedirs(config_dir)
    print('=> Extracting enterprise config from {} to {}'.format(config_archive, config_dir))
    subprocess.run(['tar', '-xvzf', config_archive, '-C', config_dir], check=True)

    config_path = '{}/config/config.json'.format(path)
    config = read_json_config(config_path)
    return config


def copy_enterprise_system_config(src: str = '/root/config/system.scm', dest_path: str = '/mnt/etc', dest_file: str = 'system.scm'):
    '''copy the system config from the extracted archive to the final location'''
    if not os.path.isdir(dest_path):
        os.makedirs(dest_path)
    dest = "{}/{}".format(dest_path, dest_file)
    print('=> Copying system config to {}.'.format(dest))
    shutil.copy(src, dest)


def copy_enterprise_channels(src: str = '/root/config/channels.scm', dest_path: str = '/mnt/etc/guix', dest_file: str = 'channels.scm'):
    '''copy the channels config from the extracted archive to the final location (create if necessary)'''
    if not os.path.isdir(dest_path):
        os.makedirs(dest_path)
    dest = "{}/{}".format(dest_path, dest_file)
    print('=> Copying channels to {}.'.format(dest))
    shutil.copy(src, dest)


def copy_enterprise_json_config(src_path: str = '/root/config', dest_path: str = '/mnt/etc'):
    '''copy the json config from the extracted archive to the final location (create if necessary)'''
    if not os.path.isdir(dest_path):
        os.makedirs(dest_path)
    src = "{}/{}".format(src_path, 'config.json')
    if os.path.isfile(src):
        dest = "{}/{}".format(dest_path, 'config.json')
        print('=> Copying json config to {}.'.format(dest))
        shutil.copy(src, dest)


def cleanup_enterprise_config(dir: str = '/root'):
    '''cleanup enterprise config archive and extracted folder'''
    config_archive = '{}/config.tar.gz'.format(dir)
    config_path = '{}/config'.format(dir)
    print('=> Cleaning up enterprise config files')
    try:
        os.remove(config_archive)
        shutil.rmtree(config_path)
    except:
        print('Could not remove all enterprise config files.')
