import os
import unittest

from px_install.classes import BlockDevice, SystemConfiguration
from px_install.system_config import get_template_filename, write_system_config

config_dir = '/tmp/px_install_test_system_config'
config_path = '{}/system.scm'.format(config_dir)

class TestSystemConfig(unittest.TestCase):
    def test_get_template_bios(self):
        type = 'DESKTOP'
        firmware = 'bios'
        hostname = 'hostname'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'pantherx'
        password = 'pantherx'
        public_key = 'NONE'
        disk = BlockDevice(type='disk', name='/dev/sda', size=100000)
        
        config = SystemConfiguration(
            type, firmware, hostname, timezone, locale, username, password, public_key, disk
        )

        res = get_template_filename(config)

        self.assertEqual(res, 'base-desktop-bios.scm')

    def test_get_template_bios_ssh(self):
        type = 'DESKTOP'
        firmware = 'bios'
        hostname = 'hostname'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'pantherx'
        password = 'pantherx'
        public_key = 'ssh-ed25519 AAAAC'
        disk = BlockDevice(type='disk', name='/dev/sda', size=100000)
        
        config = SystemConfiguration(
            type, firmware, hostname, timezone, locale, username, password, public_key, disk
        )

        res = get_template_filename(config)

        self.assertEqual(res, 'base-desktop-bios-ssh.scm')

    def test_get_template_efi(self):
        type = 'DESKTOP'
        firmware = 'efi'
        hostname = 'hostname'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'pantherx'
        password = 'pantherx'
        public_key = 'NONE'
        disk = BlockDevice(type='disk', name='/dev/sda', size=100000)
        
        config = SystemConfiguration(
            type, firmware, hostname, timezone, locale, username, password, public_key, disk
        )

        res = get_template_filename(config)

        self.assertEqual(res, 'base-desktop-efi.scm')

    def test_get_template_efi_ssh(self):
        type = 'DESKTOP'
        firmware = 'efi'
        hostname = 'hostname'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'pantherx'
        password = 'pantherx'
        public_key = 'ssh-ed25519 AAAAC'
        disk = BlockDevice(type='disk', name='/dev/sda', size=100000)
        
        config = SystemConfiguration(
            type, firmware, hostname, timezone, locale, username, password, public_key, disk
        )

        res = get_template_filename(config)

        self.assertEqual(res, 'base-desktop-efi-ssh.scm')

    def test_write_system_config_efi(self):
        type = 'DESKTOP'
        firmware = 'efi'
        hostname = 'hostname'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'pantherx'
        password = 'pantherx'
        public_key = 'NONE'
        disk = BlockDevice(type='disk', name='/dev/sda', size=100000)
        
        config = SystemConfiguration(
            type, firmware, hostname, timezone, locale, username, password, public_key, disk
        )

        os.makedirs(config_dir)

        write_system_config(config, config_path)

        # VERIFY

        system_config_file = open(config_path, 'r')
        config_list = system_config_file.readlines()
        system_config_file.close()
        found = False
        for line in config_list:
            if str('(host-name "{}")'.format(hostname)) in line:
                found = True
                
        self.assertTrue(found)

        os.remove(config_path)
        os.removedirs(config_dir)
