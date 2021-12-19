from px_install.block_devices import get_block_device_by_name, get_block_devices, get_largest_valid_block_device
from px_install.classes import BlockDevice
import unittest
from px_install.util import convert_size_string, is_valid_hostname, is_valid_timezone, list_of_commands_to_string

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

    def test_convert_size_string(self):
        value = '953.3G'
        result = convert_size_string(value)
        self.assertEqual(result, 953300.0)

    def test_convert_size_string_megabyte(self):
        value = '549M'
        result = convert_size_string(value)
        self.assertEqual(result, 549)

    def test_get_block_devices(self):
        process_result = '''{\n   "blockdevices": [\n      {"name":"sda", "maj:min":"8:0", "rm":false, "size":"1.8T", "ro":false, "type":"disk", "mountpoint":null},\n      {"name":"nvme0n1", "maj:min":"259:0", "rm":false, "size":"953.9G", "ro":false, "type":"disk", "mountpoint":null,\n         "children": [\n            {"name":"nvme0n1p1", "maj:min":"259:1", "rm":false, "size":"549M", "ro":false, "type":"part", "mountpoint":"/boot/efi"},\n            {"name":"nvme0n1p2", "maj:min":"259:2", "rm":false, "size":"953.3G", "ro":false, "type":"part", "mountpoint":null,\n               "children": [\n                  {"name":"cryptroot", "maj:min":"253:0", "rm":false, "size":"953.3G", "ro":false, "type":"crypt", "mountpoint":"/"}\n               ]\n            }\n         ]\n      }\n   ]\n}\n'''
        expected = [
            BlockDevice(type='disk', name='sda', size=1800000.0),
            BlockDevice(type='disk', name='nvme0n1', size=953900.0)
        ]
        result = get_block_devices(process_result)
        self.assertEqual(result, expected)

    def test_get_largest_valid_block_device(self):
        devices = [
            BlockDevice(type='disk', name='sda', size=1800000.0),
            BlockDevice(type='disk', name='nvme0n1', size=953900.0)
        ]
        expected = BlockDevice(type='disk', name='sda', size=1800000.0)
        result = get_largest_valid_block_device(devices)
        self.assertEqual(result, expected)

    def test_get_block_device_by_name(self):
        process_result = '''{\n   "blockdevices": [\n      {"name":"sda", "maj:min":"8:0", "rm":false, "size":"1.8T", "ro":false, "type":"disk", "mountpoint":null},\n      {"name":"nvme0n1", "maj:min":"259:0", "rm":false, "size":"953.9G", "ro":false, "type":"disk", "mountpoint":null,\n         "children": [\n            {"name":"nvme0n1p1", "maj:min":"259:1", "rm":false, "size":"549M", "ro":false, "type":"part", "mountpoint":"/boot/efi"},\n            {"name":"nvme0n1p2", "maj:min":"259:2", "rm":false, "size":"953.3G", "ro":false, "type":"part", "mountpoint":null,\n               "children": [\n                  {"name":"cryptroot", "maj:min":"253:0", "rm":false, "size":"953.3G", "ro":false, "type":"crypt", "mountpoint":"/"}\n               ]\n            }\n         ]\n      }\n   ]\n}\n'''
        expected = BlockDevice(type='disk', name='sda', size=1800000.0)
        result = get_block_device_by_name('/dev/sda', process_result)
        self.assertEqual(result, expected)

    def test_blockdevice_get_partition(self):
        device1 = BlockDevice(type='disk', name='sda', size=1800000.0)
        self.assertEqual(device1.get_partition_dev_name(1), '/dev/sda1')
        self.assertEqual(device1.get_partition_dev_name(2), '/dev/sda2')
        device2 = BlockDevice(type='disk', name='nvme0n1', size=953900.0)
        self.assertEqual(device2.get_partition_dev_name(1), '/dev/nvme0n1p1')
        self.assertEqual(device2.get_partition_dev_name(2), '/dev/nvme0n1p2')
