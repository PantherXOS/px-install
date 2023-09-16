from px_install.system_channels import write_system_channels
import os
import unittest

channels_dir = '/tmp/px_install_test_system_channels'
channels_path = '{}/channels.scm'.format(channels_dir)

def cleanup():
    if os.path.isfile(channels_path):
        os.remove(channels_path)
    if os.path.isdir(channels_dir):
        os.removedirs(channels_dir)

class TestSystemChannels(unittest.TestCase):
    def test_write_system_channels(self):
        cleanup()
    
        os.makedirs(channels_dir)
        write_system_channels(channels_path)

        # VERIFY

        channels_file = open(channels_path, 'r')
        channels_file_list = channels_file.readlines()
        channels_file.close()
        found = False
        for line in channels_file_list:
            if str('(url "https://channels.pantherx.org/git/panther.git")') in line:
                found = True
                
        self.assertTrue(found)

        cleanup()