;; PantherX OS Desktop Configuration v2
;; boot in EFI mode
;; /etc/system.scm

(use-modules (gnu)
             (gnu system)
             (px system install)
             (px system))

(px-desktop-os
 (operating-system
  (host-name "<HOSTNAME>")
  (timezone "<TIMEZONE>")
  (locale "<LOCALE>")
  
  ;; Boot in EFI mode, assuming <DISK> is the
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
			(device "<PARTITION_ONE>")
			(mount-point "/boot/efi")
			(type "vfat")))
		 %base-file-systems))
  
  (users (cons (user-account
                (name "<USERNAME>")
                (comment "<USER_COMMENT>")
                (group "users")
                ;; Set the default password to 'pantherx'
                ;; Important: Change with 'passwd panther' after first login
		(password (crypt "<USER_PASSWORD>" "$6$abc"))
		
                ;; Adding the account to the "wheel" group
                ;; makes it a sudoer.  Adding it to "audio"
                ;; and "video" allows the user to play sound
                ;; and access the webcam.
                (supplementary-groups '("wheel"
                                        "audio" "video"))
                (home-directory "/home/<USER_HOME>"))
               %base-user-accounts))
  
  ;; Globally-installed packages.
  (packages (cons*
	     %px-desktop-packages))
  
  ;; Services
  (services (cons*
	     %px-desktop-services))))
