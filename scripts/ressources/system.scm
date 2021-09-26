(use-modules (gnu)
             (gnu system)
             (px system))

(px-desktop-os
 (operating-system
  (host-name "<HOSTNAME>")
  (timezone "<TIMEZONE>")
  (locale "<LOCALE>")

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
		        (password (crypt "<USER_PASSWORD>" "$6$abc"))

                (supplementary-groups '("wheel"
                                        "audio" "video"))
                (home-directory "/home/<USER_HOME>"))
               %base-user-accounts))

  (packages (cons*
   %px-desktop-packages))

  (services (cons*
   %px-desktop-services))
  ))