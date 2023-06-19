# This is a imperfect replication of the python version for easy testing.

read -p "Type: 'desktop' or 'server' [desktop]: " TYPE 
TYPE=${TYPE:-'desktop'}
echo $TYPE

read -p "Hostname [panther_computer]: " HOSTNAME 
HOSTNAME=${HOSTNAME:-'panther_computer'}
echo $HOSTNAME

read -p "Timezone [Europe/Berlin]: " TIMEZONE 
TIMEZONE=${TIMEZONE:-'Europe/Berlin'}
echo $TIMEZONE

read -p "Locale [en_US.utf8]: " LOCALE 
LOCALE=${LOCALE:-'en_US.utf8'}
echo $LOCALE

read -p "User 1: Username [panther]: " USERNAME 
USERNAME=${USERNAME:-'panther'}
echo $USERNAME

read -p "User 1: Comment [panther's account]: " USER_COMMENT 
USER_COMMENT=${USER_COMMENT:-"panther's account"}
echo $USER_COMMENT

read -p "User 1: Password [pantherx]: " USER_PASSWORD 
USER_PASSWORD=${USER_PASSWORD:-'pantherx'}
echo $USER_PASSWORD

PUBLIC_KEY=''

if [ $TYPE == 'server' ]
then
	read -p "root: Public key [ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP7gcLZzs2JiEx2kWCc8lTHOC0Gqpgcudv0QVJ4QydPg franz]: " PUBLIC_KEY 
	PUBLIC_KEY=${PUBLIC_KEY:-'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP7gcLZzs2JiEx2kWCc8lTHOC0Gqpgcudv0QVJ4QydPg franz'}
	echo $PUBLIC_KEY
fi

echo
echo "### Disks ###"
lsblk
echo

read -p "Disk [/dev/sda]: " disk 
disk=${disk:-'/dev/sda'}
echo $disk

CRYPT='$6$abc'

CONFIG='/mnt/etc/system.scm'
CHANNELS='/mnt/etc/guix/channels.scm'

# TODO: Subtitute disk into config

function write_desktop_system_config_efi() {
	rm $CONFIG
cat >> $CONFIG <<EOL
;; PantherX OS Desktop Configuration r2
;; boot in EFI mode
;; /etc/system.scm

(use-modules (gnu)
             (gnu system)
             (px system config)
             (gnu packages))

(px-desktop-os
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
   %px-desktop-packages))

  ;; Globally-activated services.
  (services (cons*
   %px-desktop-services))))
EOL
}

function write_server_system_config_efi() {
	rm $CONFIG
cat >> $CONFIG <<EOL
;; PantherX OS Server Configuration r2
;; boot in EFI mode
;; /etc/system.scm

(use-modules (gnu)
             (gnu system)
             (px system config)
             (gnu packages))

(define %ssh-public-key
  "${PUBLIC_KEY}")

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
                ;; makes it a sudoer.
                (supplementary-groups '("wheel"))
                (home-directory "/home/${USERNAME}"))
               %base-user-accounts))

  ;; Globally-installed packages.
  (packages (cons*
   %px-server-packages))

  ;; Globally-activated services.
  (services (cons*
   %px-server-services)))

 #:open-ports '(("tcp" "ssh"))
 #:authorized-keys <ACCENT>(("root" ,(plain-file "panther.pub" %ssh-public-key))))
EOL
}

function write_desktop_system_config_bios() {
	rm $CONFIG
cat >> $CONFIG <<EOL
;; PantherX OS Desktop Configuration r2
;; boot in "legacy" BIOS mode
;; /etc/system.scm

(use-modules (gnu)
             (gnu system)
             (px system)
             (px system config)
			 (gnu packages))

(px-desktop-os
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
   %px-desktop-packages))

  ;; Globally-activated services.
  (services (cons*
   %px-desktop-services))))
EOL
}

function write_server_system_config_bios() {
	rm $CONFIG
cat >> $CONFIG <<EOL
;; PantherX OS Server Configuration r2
;; boot in "legacy" BIOS mode
;; /etc/system.scm

(use-modules (gnu)
             (gnu system)
             (px system config)
			 (gnu packages))

(define %ssh-public-key
  "${PUBLIC_KEY}")

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
                ;; makes it a sudoer.
                (supplementary-groups '("wheel"))
                (home-directory "/home/${USERNAME}"))
               %base-user-accounts))

  ;; Globally-installed packages.
  (packages (cons*
   %px-server-packages))

  ;; Globally-activated services.
  (services (cons*
   %px-server-services)))

 #:open-ports '(("tcp" "ssh"))
 #:authorized-keys <ACCENT>(("root" ,(plain-file "panther.pub" %ssh-public-key))))
EOL
}

function write_system_channels() {
	rm $CHANNELS
cat >> $CHANNELS <<EOL
;; PantherX Default Channels

(list (channel
        (name 'guix)
        (url "https://channels.pantherx.org/git/pantherx.git")
        (branch "rolling"))
      (channel
        (name 'nongnu)
        (url "https://channels.pantherx.org/git/nongnu.git")
        (branch "rolling"))
      (channel
        (name 'pantherx)
        (url "https://channels.pantherx.org/git/pantherx-extra.git")
        (branch "rolling")))
EOL
}

function get_CMD_FORMAT_BIOS() {
	part1="${disk}1"
	part2="${disk}2"
	parted -s $disk --  mklabel gpt mkpart primary fat32 0% 10M mkpart primary 10M 99%
    # sgdisk -t 1:ef02 $disk
    # sgdisk -t 2:8300 $disk
    # parted $disk set 1 boot on
	parted $disk set 1 bios_grub on
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
	mkdir /mnt/etc/guix
}

function CMD_CREATE_SWAP() {
	dd if=/dev/zero of=/mnt/swapfile bs=1MiB count=4096
    chmod 600 /mnt/swapfile
    mkswap /mnt/swapfile
    swapon /mnt/swapfile
}

function CMD_INSTALL() {
	guix pull --channels=$CHANNELS --disable-authentication
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
	if [ ! -d "/sys/firmware/efi" ]
	then
		if [ $TYPE == 'server' ]
		then
			write_server_system_config_bios
		else
			write_desktop_system_config_bios
		fi
	else
		if [ $TYPE == 'server' ]
		then
			write_server_system_config_efi
		else
			write_desktop_system_config_efi
		fi
	fi
	sed -i "s/<ACCENT>/\`/" $CONFIG
	write_system_channels
	CMD_INSTALL
}

echo "FINAL SETTINGS ===="
echo
echo "Type: $TYPE"
echo "Hostname: $HOSTNAME"
echo "Timezome: $TIMEZONE"
echo "Locale: $LOCALE"
echo "Username: $USERNAME"
echo "User comment: $USER_COMMENT"
echo "User password: $USER_PASSWORD"
if [ $TYPE == 'server' ]
then
	echo "root public key: $PUBLIC_KEY"
fi
echo
echo "... installing to $disk"
echo
echo "===================="
echo
read -p "Are you sure? (Continue with 'y' or 'Y')" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
	installation
fi
