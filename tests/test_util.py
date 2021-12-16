import unittest
from px_install.util import is_valid_hostname, is_valid_timezone, list_of_commands_to_string

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

    def test_list_of_commands_to_string_1(self):
        command = ['guix', 'package', '-s', 'px-install']
        command_string = list_of_commands_to_string(command)
        self.assertEqual(command_string, 'guix package -s px-install')

    def test_list_of_commands_to_string_2(self):
        command = ['guix']
        command_string = list_of_commands_to_string(command)
        self.assertEqual(command_string, 'guix')

    def test_is_valid_timezone(self):
        timezone = 'Asia/Tehran'
        valid = is_valid_timezone(timezone)
        self.assertTrue(valid)

    def test_is_invalid_timezone(self):
        timezone = 'Europe/France'
        valid = is_valid_timezone(timezone)
        self.assertFalse(valid)
