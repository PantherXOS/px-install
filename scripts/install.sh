# This is a imperfect replication of the python version for easy testing.

read -p "Hostname [panther_computer]: " HOSTNAME 
HOSTNAME=${HOSTNAME:-panther_computer}
echo $HOSTNAME

read -p "Timezone [Europe/Berlin]: " TIMEZONE 
TIMEZONE=${TIMEZONE:-'Europe/Berlin'}
echo $TIMEZONE

read -p "Locale [en_US.utf8]: " LOCALE 
LOCALE=${LOCALE:-'en_US.utf8'}
echo $LOCALE

read -p "User 1: Username [panther]: " USERNAME 
USERNAME=${USERNAME:-panther}
echo $USERNAME

read -p "User 1: Comment [panther's account]: " USER_COMMENT 
USER_COMMENT=${USER_COMMENT:-"panther's account"}
echo $USER_COMMENT

read -p "User 1: Password [pantherx]: " USER_PASSWORD 
USER_PASSWORD=${USER_PASSWORD:-panther_computer}
echo $USER_PASSWORD

read -p "root: Public key [ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP7gcLZzs2JiEx2kWCc8lTHOC0Gqpgcudv0QVJ4QydPg franz]: " PUBLIC_KEY 
PUBLIC_KEY=${PUBLIC_KEY:-'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP7gcLZzs2JiEx2kWCc8lTHOC0Gqpgcudv0QVJ4QydPg franz'}
echo $PUBLIC_KEY

echo
echo "### Disks ###"
lsblk
echo

read -p "Disk [/dev/sda]: " disk 
disk=${disk:-'/dev/sda'}
echo $disk

CRYPT='$6$abc'

CONFIG='/mnt/etc/system.scm'

function write_system_config_efi() {
	rm $CONFIG
cat >> $CONFIG <<EOL
(use-modules (gnu)
             (gnu system)
             (px system)
			 (gnu packages))

(use-service-modules ssh)

(define %ssh-public-key
  "${PUBLIC_KEY}")

(define %custom-server-services
  (modify-services %px-server-services
                   (openssh-service-type
                     config =>
                     (openssh-configuration
                      (inherit config)
                      (authorized-keys
                       <ACCENT>(("root" ,(plain-file "authorized_keys"
                                              %ssh-public-key))))))))

(px-server-os
 (operating-system
  (host-name "${HOSTNAME}")
  (timezone "${TIMEZONE}")
  (locale "${LOCALE}")

  (initrd-modules (append (list "virtio_scsi")
                                %base-initrd-modules))

  ;; Boot in EFI mode, assuming /dev/sda is the
  ;; target hard disk, and "my-root" is the label of the target
  ;; root file system.
  (bootloader (bootloader-configuration
               (bootloader grub-efi-bootloader)
               (target "/boot/efi")))
       
  (file-systems (append
        (list (file-system
                (device (file-system-label "my-root"))
                (mount-point "/")
                (type "ext4"))
              (file-system
                (device "/dev/sda1")
                (mount-point "/boot/efi")
                (type "vfat")))
              %base-file-systems))

  (users (cons (user-account
                (name "${USERNAME}")
                (comment "${USER_COMMENT}")
                (group "users")
		        (password (crypt "${USER_PASSWORD}" "${CRYPT}"))

                ;; Adding the account to the "wheel" group
                ;; makes it a sudoer.  Adding it to "audio"
                ;; and "video" allows the user to play sound
                ;; and access the webcam.
                (supplementary-groups '("wheel"
                                        "audio" "video"))
                (home-directory "/home/${USERNAME}"))
               %base-user-accounts))

  ;; Globally-installed packages.
  (packages (cons*
   %px-server-packages))

  ;; Services
  (services (cons*
    %custom-server-services))
  ))
EOL
}

function write_system_config_bios() {
	rm $CONFIG
cat >> $CONFIG <<EOL
(use-modules (gnu)
             (gnu system)
             (px system)
			 (gnu packages))

(use-service-modules ssh)

(define %ssh-public-key
  "${PUBLIC_KEY}")

(define %custom-server-services
  (modify-services %px-server-services
                   (openssh-service-type
                     config =>
                     (openssh-configuration
                      (inherit config)
                      (authorized-keys
                       <ACCENT>(("root" ,(plain-file "authorized_keys"
                                              %ssh-public-key))))))))

(px-server-os
 (operating-system
  (host-name "${HOSTNAME}")
  (timezone "${TIMEZONE}")
  (locale "${LOCALE}")

  (initrd-modules (append (list "virtio_scsi")
                                %base-initrd-modules))

  ;; Boot in "legacy" BIOS mode, assuming /dev/sda is the
  ;; target hard disk, and "my-root" is the label of the target
  ;; root file system.
  (bootloader (bootloader-configuration
               (bootloader grub-bootloader)
               (target "/dev/sda")))
       
  (file-systems (cons (file-system
                       (device (file-system-label "my-root"))
                       (mount-point "/")
                       (type "ext4"))
                      %base-file-systems))

  (users (cons (user-account
                (name "${USERNAME}")
                (comment "${USER_COMMENT}")
                (group "users")
		        (password (crypt "${USER_PASSWORD}" "${CRYPT}"))

                ;; Adding the account to the "wheel" group
                ;; makes it a sudoer.  Adding it to "audio"
                ;; and "video" allows the user to play sound
                ;; and access the webcam.
                (supplementary-groups '("wheel"
                                        "audio" "video"))
                (home-directory "/home/${USERNAME}"))
               %base-user-accounts))

  ;; Globally-installed packages.
  (packages (cons*
   %px-server-packages))

  ;; Services
  (services (cons*
    %custom-server-services))
  ))
EOL
}

function write_system_channels() {
	rm /mnt/etc/channels.scm
cat >> /mnt/etc/channels.scm <<EOL
;; PantherX Default Channels

(list (channel
        (name 'guix)
        (url "https://channels.pantherx.org/git/pantherx.git")
        (branch "rolling-nonlibre"))
      (channel
        (name 'nongnu)
        (url "https://channels.pantherx.org/git/nongnu.git")
        (branch "rolling"))
      (channel
        (name 'pantherx)
        (url "https://channels.pantherx.org/git/pantherx-extra.git")
        (branch "master")))
EOL
}

function get_CMD_FORMAT_BIOS() {
	part1="${disk}1"
	part2="${disk}2"
	parted -s $disk -- mklabel msdos mkpart primary fat32 0% 10M mkpart primary 10M 100%
    sgdisk -t 1:ef02 $disk
    sgdisk -t 2:8300 $disk
    parted $disk set 1 boot on
    mkfs.ext4 -L my-root $part2
}

function get_CMD_FORMAT_EFI() {
	part1="${disk}1"
	part2="${disk}2"
	parted -s $disk -- mklabel gpt mkpart primary fat32 0% 200M mkpart primary 200M 100%
    sgdisk -t 1:ef00 $disk
    sgdisk -t 2:8300 $disk
    parted $disk set 1 esp on
    mkfs.fat -F32 $part1
    mkfs.ext4 -L my-root $part2
	mkdir /boot/efi
	mount $part1 /boot/efi
}

function CMD_PREP_INSTALL() {
	mount LABEL=my-root /mnt
    herd start cow-store /mnt
    mkdir /mnt/etc
}

function CMD_CREATE_SWAP() {
	dd if=/dev/zero of=/mnt/swapfile bs=1MiB count=4096
    chmod 600 /mnt/swapfile
    mkswap /mnt/swapfile
    swapon /mnt/swapfile
}

function CMD_INSTALL() {
	guix pull --channels=/mnt/etc/channels.scm --disable-authentication
    hash guix
    guix system init $CONFIG /mnt
}

function installation() {
	if [ ! -d "/sys/firmware/efi" ]; then
		get_CMD_FORMAT_BIOS
	else
		get_CMD_FORMAT_EFI
	fi
	CMD_PREP_INSTALL
	CMD_CREATE_SWAP
	if [ ! -d "/sys/firmware/efi" ]; then
		write_system_config_bios
	else
		write_system_config_efi
	fi
	sed -i "s/<ACCENT>/\`/" $CONFIG
	write_system_channels
	CMD_INSTALL
}

echo "FINAL SETTINGS ===="
echo
echo "Hostname: $HOSTNAME"
echo "Timezome: $TIMEZONE"
echo "Locale: $LOCALE"
echo "Username: $USERNAME"
echo "User comment: $USER_COMMENT"
echo "User password: $USER_PASSWORD"
echo "root public key: $PUBLIC_KEY"
echo
echo "... installing to $disk"
echo
echo "===================="
echo
read -p "Are you sure? (Continue with 'y' or 'Y')" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
	installation
fi
