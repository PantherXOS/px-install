import os
import unittest
from px_install.classes import RemoteConfig
from px_install.remote_config import write_json_config, read_json_config, get_enterprise_config, cleanup_enterprise_config

file_dir = '/tmp/px_install_test_remote_config'
file_path = '{}/config.json'.format(file_dir)

class TestRemoteConfig(unittest.TestCase):
    def test_read_and_write_json_config(self):
        type = 'DESKTOP'
        title = 'Test'
        location = 'Moon'
        role = 'DESKTOP'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        key_security = ''
        key_type = ''
        domain = ''
        host = 'https://domain.com'
        
        config = RemoteConfig(
            type, timezone, locale, title, location, role, key_security, key_type, domain, host
        )

        os.makedirs(file_dir)
        write_json_config(config, file_path)

        # VERIFY

        config_from_file = read_json_config(file_path)

        self.assertEqual(config_from_file.host, host)

        os.remove(file_path)
        os.removedirs(file_dir)

    def test_get_enterprise_config(self):
        os.makedirs(file_dir)
        config_id = '7c9a9bd559'

        config = get_enterprise_config(config_id, 'https://temp.pantherx.org/install', file_dir)

        self.assertEqual(config.host, 'https://identity.pantherx.org')
        cleanup_enterprise_config(file_dir)

        os.removedirs(file_dir)
