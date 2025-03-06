'''Write system config with substituted values'''

# TODO: Probably easier to create the config from scratch than this ...

import os
import sys

from .classes import SystemConfiguration


def basic_config_check(config: SystemConfiguration):
    '''Check if the config is valid'''
    if config.type not in ['MINIMAL', 'DESKTOP', 'SERVER', 'ENTERPRISE']:
        raise ValueError('Unknown type: {}'.format(config.type))

def exit_if_system_config_exists():
    '''Rundimentary check to see this is not a installed system'''
    if os.path.isfile('/etc/system.scm'):
        print('You should not run this on a installed system.')
        sys.exit()


def _modules(config: SystemConfiguration):
    content = '''(use-modules (gnu)
             (gnu system)'''
    
    if config.type == 'DESKTOP':
            content += '''
             (gnu services desktop)'''

    content += '''
             (px system panther))'''
    
    if config.public_key != 'NONE':
        content += f'''

(use-service-modules ssh)

(define %ssh-public-key
  "{config.public_key}")'''
    
    return content


def _type(type):
    if type == 'MINIMAL':
        return '%panther-os'
    elif type == 'DESKTOP':
        return '%panther-desktop-os'
    elif type == 'SERVER':
        return '%panther-os'
    else:
        raise ValueError('Unknown type: {}'.format(type))


def _bootloader(firmware: str, disk: str):
    if firmware == 'bios':
        return f'''
  ;; Boot in "legacy" BIOS mode, assuming <DISK> is the
  ;; target hard disk, and "my-root" is the label of the target
  ;; root file system.
  (bootloader (bootloader-configuration
               (bootloader grub-bootloader)
               (targets '("{disk}"))))'''
    elif firmware == 'efi':
        return  f'''
  ;; Boot in EFI mode, assuming <DISK> is the
  ;; target hard disk, and "my-root" is the label of the target
  ;; root file system.
  (bootloader (bootloader-configuration
               (bootloader grub-efi-bootloader)
               (targets '("/boot/efi"))))'''
    else:
        raise ValueError('Unknown firmware: {}'.format(firmware))


def _mapped_devices(config: SystemConfiguration):
    if config.use_disk_encryption:
        return f'''
  (mapped-devices
   (list (mapped-device
          (source
           (uuid "{config.disk.get_partition_uuid(2)}"))
          (target "cryptroot")
          (type luks-device-mapping))))'''


def _file_systems(config: SystemConfiguration):
    if config.use_disk_encryption:
        return f'''{_mapped_devices(config)}

  (file-systems (append
                 (list (file-system
                        (device "/dev/mapper/cryptroot")
                        (mount-point "/")
                        (type "ext4")
                        (dependencies mapped-devices))
                       (file-system
                        (device (uuid "{config.disk.get_partition_uuid(1)}" 'fat32))
                        (mount-point "/boot/efi")
                        (type "vfat")))
                 %base-file-systems))'''
    else:
        return f'''
  (file-systems (cons (file-system
                       (device (file-system-label "my-root"))
                       (mount-point "/")
                       (type "ext4"))
                      %base-file-systems))'''


def _users(config: SystemConfiguration):
    comment = "{}'s account".format(config.username)
    return f'''
  (users (cons (user-account
                (name "{config.username}")
                (comment "{comment}")
                (group "users")
                ;; Important: Change with 'passwd {config.username}' after first login
                (password (crypt "{config.password}" "$6$abc"))

                ;; Adding the account to the "wheel" group
                ;; makes it a sudoer.  Adding it to "audio"
                ;; and "video" allows the user to play sound
                ;; and access the webcam.
                (supplementary-groups '("wheel"
                                        "audio" "video"))
                (home-directory "/home/{config.username}"))
               %base-user-accounts))'''


def _packages(config: SystemConfiguration):
    identifier = '%panther-base-packages'
    if config.type == 'DESKTOP':
        identifier = '%panther-desktop-packages'
        if config.variant == 'XFCE' or config.variant == 'MATE':
            identifier = '%panther-desktop-packages'
    elif config.type == 'SERVER':
        identifier = '%panther-base-packages'
    elif config.type == 'MINIMAL':
        identifier = '%panther-base-packages'
    else:
        raise ValueError('Unknown type: {}'.format(config.type))
    return f'''
  ;; Globally-installed packages
  (packages (cons*
             {identifier}))'''


def _services(config: SystemConfiguration):
    identifier = '%panther-base-services'
    if config.type == 'DESKTOP':
        identifier = '%panther-desktop-services'
    elif config.type == 'SERVER':
        identifier = '%panther-base-services'
    elif config.type == 'MINIMAL':
        identifier = '%panther-base-services'
    else:
        raise ValueError('Unknown type: {}'.format(config.type))
    
    content ='''
  ;; Services
  (services (cons*'''
    
    if config.type == 'DESKTOP':
        service = '(service lxqt-desktop-service-type)'
        if config.variant == 'XFCE':
            service = '(service xfce-desktop-service-type)'
        elif config.variant == 'MATE':
            service = '(service mate-desktop-service-type)'
        elif config.variant == 'GNOME':
            service = '(service gnome-desktop-service-type)'

        content += f'''
              ;; Desktop environment
              {service}'''
              
    if config.public_key != 'NONE':
        
        content += f'''
             (service openssh-service-type
                      (openssh-configuration
                       (permit-root-login 'prohibit-password)
                       (authorized-keys
                        `(("root" ,(plain-file "{config.username}.pub" %ssh-public-key))))))'''

    content += f'''
             {identifier}))'''
    
    return content


def operating_system_config(config: SystemConfiguration):
    return f''';; PantherX OS Configuration

{_modules(config)}

(operating-system
 (inherit {_type(config.type)})
 (host-name "{config.hostname}")
 (timezone "{config.timezone}")
 (locale "{config.locale}")
{_bootloader(config.firmware, config.disk.dev_name)}
{_file_systems(config)}
{_users(config)}
{_packages(config)}
{_services(config)}
)'''


def write_system_config(config: SystemConfiguration, path: str = '/mnt/etc/system.scm'):
    with open(path, 'w') as f:
        f.write(operating_system_config(config))
