# guix shell python python-py-cpuinfo python-qrcode python-tqdm -- python3 -m unittest tests/test_system_config.py

import os
import unittest

from px_install.classes import BlockDevice, SystemConfiguration
from px_install.system_config import write_system_config, operating_system_config

config_dir = '/tmp/px_install_test_system_config'
config_path = '{}/system.scm'.format(config_dir)

class TestSystemConfig(unittest.TestCase):
    def test_get_template_bios(self):
        type = 'MINIMAL'
        variant = 'DEFAULT'
        firmware = 'bios'
        hostname = 'px-base'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'panther'
        password = 'pantherx'
        public_key = 'NONE'
        disk = BlockDevice(type='disk', name='vda', size=100000)
        
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

        self.maxDiff = None
        self.assertEqual(res, ''';; PantherX OS Configuration

(use-modules (gnu)
             (gnu system)
             (px system panther))

(operating-system
 (inherit %panther-os)
 (host-name "px-base")
 (timezone "Europe/Berlin")
 (locale "en_US.utf8")

  ;; Boot in "legacy" BIOS mode, assuming <DISK> is the
  ;; target hard disk, and "my-root" is the label of the target
  ;; root file system.
  (bootloader (bootloader-configuration
               (bootloader grub-bootloader)
               (targets '("/dev/vda"))))

  (file-systems (cons (file-system
                       (device (file-system-label "my-root"))
                       (mount-point "/")
                       (type "ext4"))
                      %base-file-systems))

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
             %panther-base-packages))

  ;; Services
  (services (cons*
             %panther-base-services))
)''')

    def test_get_template_efi(self):
        type = 'MINIMAL'
        variant = 'DEFAULT'
        firmware = 'efi'
        hostname = 'px-base'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'panther'
        password = 'pantherx'
        public_key = 'NONE'
        disk = BlockDevice(type='disk', name='vda', size=100000)
        
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

        self.maxDiff = None
        self.assertEqual(res, ''';; PantherX OS Configuration

(use-modules (gnu)
             (gnu system)
             (px system panther))

(operating-system
 (inherit %panther-os)
 (host-name "px-base")
 (timezone "Europe/Berlin")
 (locale "en_US.utf8")

  ;; Boot in EFI mode, assuming <DISK> is the
  ;; target hard disk, and "my-root" is the label of the target
  ;; root file system.
  (bootloader (bootloader-configuration
               (bootloader grub-efi-bootloader)
               (targets '("/boot/efi"))))

  (file-systems (cons (file-system
                       (device (file-system-label "my-root"))
                       (mount-point "/")
                       (type "ext4"))
                      %base-file-systems))

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
             %panther-base-packages))

  ;; Services
  (services (cons*
             %panther-base-services))
)''')

    # TODO: DEVICE UUID's are NONE
    def test_get_template_efi_encryption(self):
        type = 'MINIMAL'
        variant = 'DEFAULT'
        firmware = 'efi'
        hostname = 'px-base'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'panther'
        password = 'pantherx'
        public_key = 'NONE'
        disk = BlockDevice(type='disk', name='vda', size=100000)
        
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

        res = operating_system_config(config)

        self.maxDiff = None
        self.assertEqual(res, ''';; PantherX OS Configuration

(use-modules (gnu)
             (gnu system)
             (px system panther))

(operating-system
 (inherit %panther-os)
 (host-name "px-base")
 (timezone "Europe/Berlin")
 (locale "en_US.utf8")

  ;; Boot in EFI mode, assuming <DISK> is the
  ;; target hard disk, and "my-root" is the label of the target
  ;; root file system.
  (bootloader (bootloader-configuration
               (bootloader grub-efi-bootloader)
               (targets '("/boot/efi"))))

  (mapped-devices
   (list (mapped-device
          (source
           (uuid "None"))
          (target "cryptroot")
          (type luks-device-mapping))))

  (file-systems (append
                 (list (file-system
                        (device "/dev/mapper/cryptroot")
                        (mount-point "/")
                        (type "ext4")
                        (dependencies mapped-devices))
                       (file-system
                        (device (uuid "None" 'fat32))
                        (mount-point "/boot/efi")
                        (type "vfat")))
                 %base-file-systems))

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
             %panther-base-packages))

  ;; Services
  (services (cons*
             %panther-base-services))
)''')

    def test_get_template_efi_public_key(self):
        type = 'MINIMAL'
        variant = 'DEFAULT'
        firmware = 'efi'
        hostname = 'px-base'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'panther'
        password = 'pantherx'
        public_key = 'ssh-ed25519 AAAAC name'
        disk = BlockDevice(type='disk', name='vda', size=100000)
        
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

        self.maxDiff = None
        self.assertEqual(res, ''';; PantherX OS Configuration

(use-modules (gnu)
             (gnu system)
             (px system panther))

(use-service-modules ssh)

(define %ssh-public-key
  "ssh-ed25519 AAAAC name")

(operating-system
 (inherit %panther-os)
 (host-name "px-base")
 (timezone "Europe/Berlin")
 (locale "en_US.utf8")

  ;; Boot in EFI mode, assuming <DISK> is the
  ;; target hard disk, and "my-root" is the label of the target
  ;; root file system.
  (bootloader (bootloader-configuration
               (bootloader grub-efi-bootloader)
               (targets '("/boot/efi"))))

  (file-systems (cons (file-system
                       (device (file-system-label "my-root"))
                       (mount-point "/")
                       (type "ext4"))
                      %base-file-systems))

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
             %panther-base-packages))

  ;; Services
  (services (cons*
             (service openssh-service-type
                      (openssh-configuration
                       (permit-root-login 'prohibit-password)
                       (authorized-keys
                        `(("root" ,(plain-file "panther.pub" %ssh-public-key))))))
             %panther-base-services))
)''')

    def test_get_template_desktop_efi(self):
        type = 'DESKTOP'
        variant = 'DEFAULT'
        firmware = 'efi'
        hostname = 'px-base'
        timezone = 'Europe/Berlin'
        locale = 'en_US.utf8'
        username = 'panther'
        password = 'pantherx'
        public_key = 'NONE'
        disk = BlockDevice(type='disk', name='vda', size=100000)
        
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

        self.maxDiff = None
        self.assertEqual(res, ''';; PantherX OS Configuration

(use-modules (gnu)
             (gnu system)
             (gnu services desktop)
             (px system panther))

(operating-system
 (inherit %panther-desktop-os)
 (host-name "px-base")
 (timezone "Europe/Berlin")
 (locale "en_US.utf8")

  ;; Boot in EFI mode, assuming <DISK> is the
  ;; target hard disk, and "my-root" is the label of the target
  ;; root file system.
  (bootloader (bootloader-configuration
               (bootloader grub-efi-bootloader)
               (targets '("/boot/efi"))))

  (file-systems (cons (file-system
                       (device (file-system-label "my-root"))
                       (mount-point "/")
                       (type "ext4"))
                      %base-file-systems))

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
             %panther-desktop-packages))

  ;; Services
  (services (cons*
              ;; Desktop environment
              (service lxqt-desktop-service-type)
             %panther-desktop-services))
)''')

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
