#!/bin/bash

# PantherX on DigitalOcean
# Script 2/2

# THIS IS OPTIONAL
# If you just want to deploy (guix deploy) to the target machine, you don't need to run this script.

###### MODIFY

TIMEZONE="Europe/Berlin"
LOCALE="en_US.utf8"
USERNAME="panther"
USER_COMMENT="panther's account"
USER_PASSWORD="6a4NQqrp84Y7mj56"

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

CONFIG_INSTALL=/etc/bootstrap-config.scm
CONFIG=/etc/system.scm
CRYPT='$6$abc'

guix package -i curl

HOSTNAME=$(curl -s http://169.254.169.254/metadata/v1/hostname)
PUBLIC_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
NETMASK=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/netmask)
GATEWAY=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/gateway)

function write_server_config() {
cat >> $CONFIG <<EOL
;; PantherX OS Server Configuration r2 modified
;; boot on DigitalOcean
;; /etc/system.scm

(use-modules (gnu)
	     (gnu system)
	     (gnu packages networking)
	     (px system config)
	     (srfi srfi-1)
	     (gnu packages))

(use-service-modules networking ssh)

(define %custom-nftables-ruleset
  (plain-file "nftables.conf"
	      "
flush ruleset

table inet filter {
chain input {
type filter hook input priority 0; policy drop;

# early drop of invalid connections
ct state invalid drop

# allow established/related connections
ct state { established, related } accept

# allow from loopback
iifname lo accept

# allow icmp
ip protocol icmp accept
ip6 nexthdr icmpv6 accept

# allow ssh, http, https
tcp dport { ssh, http, https } accept

# reject everything else
reject with icmpx type port-unreachable
}
chain forward {
type filter hook forward priority 0; policy drop;
}
chain output {
type filter hook output priority 0; policy accept;
}
}
"))

(define %ssh-public-key
  "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP7gcLZzs2JiEx2kWCc8lTHOC0Gqpgcudv0QVJ4QydPg franz")

(remove! (lambda (service)
	   (eq? (service-kind service) 
		dhcp-client-service-type)) 
	 %px-server-services)

(define %custom-server-services
  (modify-services %px-server-services
		   (openssh-service-type
		    config =>
		    (openssh-configuration
		     (inherit config)
		     (authorized-keys
		      <ACCENT>(("root" ,(plain-file "panther.pub"
					     %ssh-public-key))))))
		   (nftables-service-type
		    config =>
		    (nftables-configuration
		     (inherit config)
		     (ruleset %custom-nftables-ruleset)))))

(px-server-os
 (operating-system
  (host-name "guix-testing")
  (timezone "Europe/Berlin")
  (locale "en_US.utf8")
  
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
  (packages (cons* %px-server-packages))
  
  (services (cons* (static-networking-service "eth0" "${PUBLIC_IPV4}"
					      #:netmask "${NETMASK}"
					      #:gateway "${GATEWAY}"
					      #:name-servers '("84.200.69.80" "84.200.70.40"))
		   %custom-server-services))))
EOL
}

write_server_config
sed -i "s/<ACCENT>/\`/" $CONFIG

guix pull --channels=/etc/guix/channels.scm

hash guix
guix system reconfigure $CONFIG

# Cleanup
rm /etc/bootstrap-config.scm
rm -rf /old-etc

reboot