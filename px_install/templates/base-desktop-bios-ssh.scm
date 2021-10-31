;; PantherX OS Desktop Configuration v2
;; boot in "legacy" BIOS mode
;; /etc/system.scm

(use-modules (gnu)
             (gnu system)
             (px system install)
             (px system))

(use-service-modules ssh)

(define %ssh-public-key
  "${PUBLIC_KEY}")

(px-desktop-os
 (operating-system
  (host-name "<HOSTNAME>")
  (timezone "<TIMEZONE>")
  (locale "<LOCALE>")
  
  ;; Boot in "legacy" BIOS mode, assuming <DISK> is the
  ;; target hard disk, and "my-root" is the label of the target
  ;; root file system.
  (bootloader (bootloader-configuration
               (bootloader grub-bootloader)
               (target "<DISK>")))
  
  (file-systems (cons (file-system
                       (device (file-system-label "my-root"))
                       (mount-point "/")
                       (type "ext4"))
                      %base-file-systems))

  (swap-devices '("/swapfile"))
  
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
	     %px-desktop-services)))
 
 #:open-ports '(("tcp" "ssh"))
 #:authorized-keys <ACCENT>(("root" ,(plain-file "panther.pub" %ssh-public-key)))
