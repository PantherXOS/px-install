import os
import unittest

from px_install.classes import BlockDevice, SystemConfiguration
from px_install.system_config import write_system_config, operating_system_config

config_dir = '/tmp/px_install_test_system_config'
config_path = '{}/system.scm'.format(config_dir)

class TestSystemConfig(unittest.TestCase):
    def test_get_template_bios(self):
        type = 'DESKTOP'
        variant = 'XFCE'
        firmware = 'bios'
        hostname = 'px-desktop'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'panther'
        password = 'pantherx'
        public_key = 'NONE'
        disk = BlockDevice(type='disk', name='sda', size=100000)
        
        use_disk_encryption = False
        config = SystemConfiguration(
            type,
            variant,
            firmware,
            hostname,
            timezone,
            locale,
            username,
            password,
            public_key,
            disk,
            use_disk_encryption
        )

        res = operating_system_config(config)

        self.assertEqual(res, ''';; PantherX OS Configuration
;;
;; Update: px update apply
;; Apply changes: guix system reconfigure /etc/system.scm

(use-modules (gnu)
             (gnu system)
             (gnu services desktop)
             (px system config))

(px-desktop-os
 (operating-system
  (host-name "px-desktop")
  (timezone "Europe/Berlin")
  (locale "en_US.utf8")
  
  ;; Boot in "legacy" BIOS mode, assuming <DISK> is the
  ;; target hard disk, and "my-root" is the label of the target
  ;; root file system.
  (bootloader (bootloader-configuration
               (bootloader grub-bootloader)
               (targets '("/dev/sda"))))

  (file-systems (cons (file-system
                       (device (file-system-label "my-root"))
                       (mount-point "/")
                       (type "ext4"))
                      %base-file-systems))

  (swap-devices '("/swapfile"))
  
  (users (cons (user-account
                (name "panther")
                (comment "panther's account")
                (group "users")
                ;; Important: Change with 'passwd panther' after first login
                (password (crypt "pantherx" "$6$abc"))

                ;; Adding the account to the "wheel" group
                ;; makes it a sudoer.  Adding it to "audio"
                ;; and "video" allows the user to play sound
                ;; and access the webcam.
                (supplementary-groups '("wheel"
                                        "audio" "video"))
                (home-directory "/home/panther"))
               %base-user-accounts))
  
  ;; Globally-installed packages
  (packages (cons*
             %px-desktop-packages-gtk))
  
  ;; Services
  (services (cons*
              ;; Desktop environment
              ;; Use one or more at the same time
              ;; (service lxqt-desktop-service-type)
              ;; (service xfce-desktop-service-type)
              ;; (service mate-desktop-service-type)
              ;; (service gnome-desktop-service-type)
              (service xfce-desktop-service-type)
             %px-desktop-services))
 )
)''')

    # def test_get_template_bios_ssh(self):
    #     type = 'DESKTOP'
    #     firmware = 'bios'
    #     hostname = 'hostname'
    #     timezone = 'Europe/Berlin'
    #     locale = 'en_US.utf8'
    #     username = 'pantherx'
    #     password = 'pantherx'
    #     public_key = 'ssh-ed25519 AAAAC'
    #     disk = BlockDevice(type='disk', name='sda', size=100000)
        
    #     use_disk_encryption = False
    #     config = SystemConfiguration(
    #         type, firmware, hostname, timezone, locale, username, password, public_key, disk, use_disk_encryption
    #     )

    #     res = get_template_filename(config)

    #     self.assertEqual(res, 'base-desktop-bios-ssh.scm')

    # def test_get_template_efi(self):
    #     type = 'DESKTOP'
    #     firmware = 'efi'
    #     hostname = 'hostname'
    #     timezone = 'Europe/Berlin'
    #     locale = 'en_US.utf8'
    #     username = 'pantherx'
    #     password = 'pantherx'
    #     public_key = 'NONE'
    #     disk = BlockDevice(type='disk', name='sda', size=100000)
        
    #     use_disk_encryption = False
    #     config = SystemConfiguration(
    #         type, firmware, hostname, timezone, locale, username, password, public_key, disk, use_disk_encryption
    #     )

    #     res = get_template_filename(config)

    #     self.assertEqual(res, 'base-desktop-efi.scm')

    # def test_get_template_efi_ssh(self):
    #     type = 'DESKTOP'
    #     firmware = 'efi'
    #     hostname = 'hostname'
    #     timezone = 'Europe/Berlin'
    #     locale = 'en_US.utf8'
    #     username = 'pantherx'
    #     password = 'pantherx'
    #     public_key = 'ssh-ed25519 AAAAC'
    #     disk = BlockDevice(type='disk', name='sda', size=100000)
        
    #     use_disk_encryption = False
    #     config = SystemConfiguration(
    #         type, firmware, hostname, timezone, locale, username, password, public_key, disk, use_disk_encryption
    #     )

    #     res = get_template_filename(config)

    #     self.assertEqual(res, 'base-desktop-efi-ssh.scm')

    def test_write_system_config_efi(self):
        type = 'DESKTOP'
        variant = 'XFCE'
        firmware = 'efi'
        hostname = 'hostname'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'pantherx'
        password = 'pantherx'
        public_key = 'NONE'
        disk = BlockDevice(type='disk', name='sda', size=100000)
        
        use_disk_encryption = False
        config = SystemConfiguration(
            type,
            variant,
            firmware,
            hostname,
            timezone,
            locale,
            username,
            password,
            public_key,
            disk,
            use_disk_encryption
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

    def test_write_system_config_efi_encrypted(self):
        type = 'DESKTOP'
        variant = 'XFCE'
        firmware = 'efi'
        hostname = 'hostname'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'pantherx'
        password = 'pantherx'
        public_key = 'NONE'
        disk = BlockDevice(type='disk', name='nvme0n1', size=100000)
        
        use_disk_encryption = True
        config = SystemConfiguration(
            type,
            variant,
            firmware,
            hostname,
            timezone,
            locale,
            username,
            password,
            public_key,
            disk,
            use_disk_encryption
        )

        os.makedirs(config_dir)
        print(config_path)
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
