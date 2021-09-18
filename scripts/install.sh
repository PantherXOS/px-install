# This is a imperfect replication of the python version for easy testing.

HOSTNAME="panther_computer"
TIMEZONE="Europe/Berlin"
LOCALE="en_US.utf8"
USERNAME="panther"
USER_COMMENT="panther's account"
USER_PASSWORD="pantherx"

CRYPT='$6$abc'

disk="/dev/sda"

function write_system_config() {
	rm /mnt/etc/system.scm
cat >> /mnt/etc/system.scm <<EOL
(use-modules (gnu)
             (gnu system)
             (px system))

(px-desktop-os
 (operating-system
  (host-name "${HOSTNAME}")
  (timezone "${TIMEZONE}")
  (locale "${LOCALE}")

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

  ;; Services
  (services (cons*
   %px-desktop-services))
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

# EFI version

function get_CMD_FORMAT_EFI() {
	part1="${disk}1"
	part2="${disk}2"
	parted -s $disk --mklabel gpt mkpart primary 
	parted -s $disk -- mklabel gpt mkpart primary fat32 0% 200M mkpart primary 200M 100%
    sgdisk -t 1:ef00 $disk
    sgdisk -t 2:8300 $disk
    parted $disk, set 1 esp on
    mkfs.fat -F32 $part1
    mkfs.ext4 -L my-root $part2
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
    guix system init /mnt/etc/system.scm /mnt
}


get_CMD_FORMAT_EFI
CMD_PREP_INSTALL
CMD_CREATE_SWAP
write_system_config
write_system_channels
CMD_INSTALL