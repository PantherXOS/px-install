#!/bin/bash

# Guix on DigitalOcean

# Test on:
# - Ubuntu 21.04
# - Debian 11
#
# 1. Create a new Droplet
# 2. Select Debian 11 and create the Droplet
# 3. Login with SSH
# 4. Paste this script into a setup.sh and run it
# 5. Wait ~10 minutes on a $5 Droplet and login with SSH panther@ip
#
# Modify below values to suit your needs. Change the password!

###### MODIFY

TIMEZONE="Europe/Berlin"
LOCALE="en_US.utf8"
USERNAME="panther"
USER_COMMENT="panther's account"
USER_PASSWORD="6a4NQqrp84Y7mj56"

###### MODIFY END

CONFIG=/etc/bootstrap-config.scm
CRYPT='$6$abc'

apt-get update -y
apt-get install curl xz-utils -y
# Uncomment this for Debian 9
# sed -i '/^mozilla\/DST_Root_CA_X3/s/^/!/' /etc/ca-certificates.conf && update-ca-certificates -f
wget https://ftp.gnu.org/gnu/guix/guix-binary-1.3.0.x86_64-linux.tar.xz
cd /tmp
tar --warning=no-timestamp -xf ~/guix-binary-1.3.0.x86_64-linux.tar.xz
mv var/guix /var/ && mv gnu /
mkdir -p ~root/.config/guix
ln -sf /var/guix/profiles/per-user/root/current-guix ~root/.config/guix/current
export GUIX_PROFILE="`echo ~root`/.config/guix/current" ;
source $GUIX_PROFILE/etc/profile
groupadd --system guixbuild
for i in `seq -w 1 10`;
do
   useradd -g guixbuild -G guixbuild         \
           -d /var/empty -s `which nologin`  \
           -c "Guix build user $i" --system  \
           guixbuilder$i;
done;

cp ~root/.config/guix/current/lib/systemd/system/guix-daemon.service /etc/systemd/system/
systemctl start guix-daemon && systemctl enable guix-daemon
mkdir -p /usr/local/bin
cd /usr/local/bin
ln -s /var/guix/profiles/per-user/root/current-guix/bin/guix
mkdir -p /usr/local/share/info
cd /usr/local/share/info
for i in /var/guix/profiles/per-user/root/current-guix/share/info/*; do
    ln -s $i; done
guix archive --authorize < ~root/.config/guix/current/share/guix/ci.guix.gnu.org.pub
# guix pull
guix package -i glibc-utf8-locales
export GUIX_LOCPATH="$HOME/.guix-profile/lib/locale"
guix package -i openssl

HOSTNAME=$(curl -s http://169.254.169.254/metadata/v1/hostname)
PUBLIC_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
NETMASK=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/netmask)
GATEWAY=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/gateway)

function write_server_config() {
cat >> $CONFIG <<EOL
;; Server Configuration (plain) v1
;; /etc/system.scm

(use-modules (gnu))
(use-service-modules networking ssh)
(use-package-modules screen ssh certs tls)

(operating-system
  (host-name "${HOSTNAME}")
  (timezone "${TIMEZONE}")
  (locale "${LOCALE}")

  (initrd-modules (append (list "virtio_scsi")
                                %base-initrd-modules))

  (bootloader (bootloader-configuration
               (bootloader grub-bootloader)
               (target "/dev/vda")))
       
  (file-systems (append
        (list (file-system
                (device "/dev/vda1")
                (mount-point "/")
                (type "ext4")))
              %base-file-systems))

  (users (cons (user-account
                (name "${USERNAME}")
                (comment "${USER_COMMENT}")
                (group "users")
		        (password (crypt "${USER_PASSWORD}" "${CRYPT}"))

                (supplementary-groups '("wheel"))
                (home-directory "/home/${USERNAME}"))
               %base-user-accounts))

  ;; Globally-installed packages.
  (packages (cons* screen openssh nss-certs gnutls %base-packages))

  (services (cons* (static-networking-service "eth0" "${PUBLIC_IPV4}"
  #:netmask "${NETMASK}"
  #:gateway "${GATEWAY}"
  #:name-servers '("84.200.69.80" "84.200.70.40"))
  (service openssh-service-type
  		  (openssh-configuration
		  (permit-root-login 'without-password)))
  %base-services)))
EOL
}

write_server_config

# guix pull
guix system build /etc/bootstrap-config.scm
# these appear to be the necessary on Ubuntu 21.04
mv /etc/ssl /etc/bk_ssl
mv /etc/pam.d /etc/bk_pam.d
mv /etc/skel /etc/bk_skel

guix system reconfigure /etc/bootstrap-config.scm
mv /etc /old-etc
mkdir /etc
cp -r /old-etc/{passwd,group,shadow,gshadow,mtab,guix,bootstrap-config.scm} /etc/
guix system reconfigure /etc/bootstrap-config.scm

reboot