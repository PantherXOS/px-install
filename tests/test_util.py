from px_install.registration import write_registration_files
import os
import unittest
from px_install.classes import RemoteConfig
from px_install.util import is_valid_hostname

file_dir = '/tmp/px_install_test_registration'
file_path = '{}/register_config.sh'.format(file_dir)

class TestUtil(unittest.TestCase):
    def test_is_valid_hostname_valid_1(self):
        hostname = 'domain.com'
        valid = is_valid_hostname(hostname)
        self.assertTrue(valid)

    def test_is_valid_hostname_valid_2(self):
        hostname = 'domain'
        valid = is_valid_hostname(hostname)
        self.assertTrue(valid)

    def test_is_valid_hostname_valid_3(self):
        hostname = 'domain.de.gov'
        valid = is_valid_hostname(hostname)
        self.assertTrue(valid)

    def test_is_valid_hostname_invalid_1(self):
        hostname = 'domain_com'
        valid = is_valid_hostname(hostname)
        self.assertFalse(valid)

    def test_is_valid_hostname_invalid_2(self):
        hostname = 'domain.com/some'
        valid = is_valid_hostname(hostname)
        self.assertFalse(valid)

    def test_is_valid_hostname_invalid_3(self):
        hostname = 'domain/some'
        valid = is_valid_hostname(hostname)
        self.assertFalse(valid)