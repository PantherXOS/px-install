#!/bin/bash

# PantherX on AWS EC2 - t3.* instance-type

# Test on:
# - Ubuntu 21.04
# - Debian 11
# - Debian 9 (see comments ~ line 48)
#
# 1. Create a new EC2 (t3.*) VM with Debian 11
# 2. Login with SSH and switch to root
# 3. Paste this script into a setup.sh and run it*
# 4. Wait ~10 minutes on a 25 Euro Cloud Server
#
# If you just want to deploy to the target machine, from your PantherX installation, this is all you need to do.
#
# Modify below values to suit your needs. Change the password!

###### MODIFY

TIMEZONE="Europe/Berlin"
LOCALE="en_US.utf8"
USERNAME="panther"
USER_COMMENT="panther's account"
USER_PASSWORD="6a4NQqrp84Y7mj56"

HOSTNAME='pantherx'

###### MODIFY END

if [ "$USER_PASSWORD" == "6a4NQqrp84Y7mj56" ]; then
	echo "######### IMPORTANT #########"
	echo "You did not modify the default user password. Overwriting ..."
	USER_PASSWORD=$(openssl rand -base64 24)
	echo
	echo "#########"
	echo $USER_PASSWORD
	echo "#########"
	echo
fi

CONFIG=/etc/bootstrap-config.scm
CHANNELS=/etc/channels.scm
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
cat <<EOT >> ~root/.config/guix/current/share/guix/bordeaux.guix.gnu.pub
(public-key
 (ecc
  (curve Ed25519)
  (q #7D602902D3A2DBB83F8A0FB98602A754C5493B0B778C8D1DD4E0F41DE14DE34F#)
  )
 )
EOT
guix archive --authorize < ~root/.config/guix/current/share/guix/ci.guix.gnu.org.pub
guix archive --authorize < ~root/.config/guix/current/share/guix/bordeaux.guix.gnu.pub
# guix pull
guix package -i glibc-utf8-locales --substitute-urls='https://bordeaux.guix.gnu.org https://ci.guix.gnu.org'
export GUIX_LOCPATH="$HOME/.guix-profile/lib/locale"
guix package -i openssl --substitute-urls='https://bordeaux.guix.gnu.org https://ci.guix.gnu.org'

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
               (target "/dev/nvme0n1")))
       
  (file-systems (append
        (list (file-system
                (device "/dev/nvme0n1p1")
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

  (services (cons* 
  (service dhcp-client-service-type)
  (service openssh-service-type
  		  (openssh-configuration
		  (permit-root-login 'without-password)))
  %base-services)))
EOL
}

function write_system_channels() {
cat >> $CHANNELS <<EOL
;; PantherX Default Channels

(list (channel
        (name 'guix)
        (url "https://channels.pantherx.org/git/pantherx.git")
        (branch "production"))
      (channel
        (name 'nongnu)
        (url "https://channels.pantherx.org/git/nongnu.git")
        (branch "production"))
      (channel
        (name 'pantherx)
        (url "https://channels.pantherx.org/git/pantherx-extra.git")
        (branch "production")))
EOL
}

write_server_config
write_system_channels
#write_signing_key
# guix archive --authorize < /etc/packages.pantherx.org.pub
# guix pull --disable-authentication --channels=/etc/channels.scm
# hash guix

guix system build /etc/bootstrap-config.scm --substitute-urls='https://bordeaux.guix.gnu.org https://ci.guix.gnu.org'
# these appear to be the necessary on Ubuntu 21.04
mv /etc/ssl /etc/bk_ssl
mv /etc/pam.d /etc/bk_pam.d
mv /etc/skel /etc/bk_skel

guix system reconfigure /etc/bootstrap-config.scm --substitute-urls='https://bordeaux.guix.gnu.org https://ci.guix.gnu.org'
mv /etc /old-etc
mkdir /etc
cp -r /old-etc/{passwd,group,shadow,gshadow,mtab,guix,bootstrap-config.scm} /etc/
cp /old-etc/channels.scm /etc/guix/channels.scm
guix system reconfigure /etc/bootstrap-config.scm --substitute-urls='https://bordeaux.guix.gnu.org https://ci.guix.gnu.org'

echo "We are done here."
echo $HOSTNAME
echo
echo "In case you missed it, here's the password again:"
echo $USER_PASSWORD

# reboot