from px_install.registration import write_registration_files
import os
import unittest
from px_install.classes import RemoteConfig

file_dir = '/tmp/px_install_test_registration'
file_path = '{}/register_config.sh'.format(file_dir)
file_path_2 = '{}/register_config.json'.format(file_dir)

class TestRegistration(unittest.TestCase):
    def test_write_registration_files(self):
        type = 'DESKTOP'
        title = 'Test'
        location = 'Moon'
        role = 'DESKTOP'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        key_security = ''
        key_type = ''
        domain = ''
        host = ''
        
        config = RemoteConfig(
            type, timezone, locale, title, location, role, key_security, key_type, domain, host
        )

        os.makedirs(file_dir)
        write_registration_files(config, file_dir)

        # VERIFY

        file_content = open(file_path, 'r')
        file_content_lines = file_content.readlines()
        file_content.close()
        found = False
        for line in file_content_lines:
            if str('export DEVICE_ROLE={}'.format(role)) in line:
                found = True
                
        self.assertTrue(found)

        os.remove(file_path)
        os.remove(file_path_2)
        os.removedirs(file_dir)
