;; TODO: Once the template is finalized, clear-out testing values

;; PantherX OS Server deployment template
;; for Digital Ocean
;;
;; Services: PostgreSQL, Redis, Nginx, Synapse
;; Firewall: 22, 80, 443

;; Init via script in repo: px-install/pantherx-on-digitalocean.sh

(use-modules (gnu)
	     (gnu system)
	     (srfi srfi-1)
	     (gnu packages tls)
	     (gnu packages base)
	     (gnu packages node)
	     (gnu packages python)
	     (gnu packages databases)
	     (gnu packages networking)
	     (gnu packages commencement)
	     (gnu packages version-control)
	     (px system config)
	     (px packages databases)
	     (px packages matrix)
	     (px packages device)
	     (px services device))

(use-service-modules databases networking web certbot)

(define %ssh-public-key
  "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP7gcLZzs2JiEx2kWCc8lTHOC0Gqpgcudv0QVJ4QydPg franz")

(define (cert-path host file)
  (format #f "/etc/letsencrypt/live/~a/~a.pem" host (symbol->string file)))

(define %nginx-deploy-hook
  (program-file
   "nginx-deploy-hook"
   #~(let ((pid (call-with-input-file "/var/run/nginx/pid" read)))
       (kill pid SIGHUP))))

(define %custom-server-services
  (modify-services %px-server-services
		   (guix-service-type config =>
                                      (guix-configuration
                                       (inherit config)
                                       (authorized-keys
					(append (list (local-file "/etc/guix/signing-key.pub"))
						%default-authorized-guix-keys))))))

(define %system
  (px-server-os
   (operating-system
    (host-name "matrix")
    (timezone "Europe/Berlin")
    (locale "en_US.utf8")
    
    (bootloader (bootloader-configuration
		 (bootloader grub-bootloader)
		 (target "/dev/sda")))
    
    (initrd-modules (append (list "virtio_scsi")
			    %base-initrd-modules))
    
    (file-systems (append
		   (list (file-system
			  (mount-point "/")
			  (device "/dev/sda1")
			  (type "ext4")))
		   %base-file-systems))

    (swap-devices '("/swapfile"))

    ;; Users
    (users (cons (user-account
		  (name "panther")
		  (comment "panther's account")
		  (group "users")
		  
		  (supplementary-groups '("wheel"))
		  (home-directory "/home/panther"))
		 %base-user-accounts))
    
    ;; Packages
    (packages (cons* px-database-utility px-device-identity
		     node-lts postgresql git synapse
		     ;; bcrypt
		     ;; make: error: make: unbound variable
		     python gcc-toolchain
		     %px-server-packages))
    
    ;; Services
    (services (cons*
	       ;; Device identity service for CM
	       (service px-device-identity-service-type)

	       ;; Database
	       (service redis-service-type)
	       
	       ;; Database
	       (service postgresql-service-type
			(postgresql-configuration
			 (config-file
			  (postgresql-config-file
			   (hba-file
			    (plain-file "pg_hba.conf"
					"
local   all     all                     trust
host    all     all     127.0.0.1/32    trust
host    all     all     ::1/128         md5"))))
			 (postgresql postgresql-13)))
	       
	       ;; SSL Certificates
	       (service certbot-service-type
			(certbot-configuration
			 (email "franz@pantherx.org")
			 (certificates
			  (list
			   (certificate-configuration
			    (domains '("matrix.pantherx.dev"))
			    (deploy-hook %nginx-deploy-hook))))))
	       
	       ;; Web server
	       (service nginx-service-type
			(nginx-configuration
			 (server-blocks
			  (list (nginx-server-configuration
				 (server-name '("matrix.pantherx.dev"))
				 (ssl-certificate (cert-path "matrix.pantherx.dev" 'fullchain))
				 (ssl-certificate-key (cert-path "matrix.pantherx.dev" 'privkey))
				 (locations
				  (list
				   (nginx-location-configuration
				    (uri "/")
				    (body
				     (list
				      "proxy_set_header X-Real-IP $remote_addr;"
				      "proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;"
				      "proxy_set_header X-Forwarded-Proto $scheme;"
				      "proxy_redirect off;"
				      "proxy_pass http://localhost:8008;"
				      "proxy_http_version 1.1;"
				      "proxy_set_header Upgrade $http_upgrade;"
				      "proxy_set_header Connection 'upgrade';"
				      "proxy_set_header Host $host;"
				      "proxy_cache_bypass $http_upgrade;"))))))))))
	       %custom-server-services)))
   
   #:open-ports '(("tcp" "ssh" "80" "443"))
   #:authorized-keys `(("root" ,(plain-file "panther.pub" %ssh-public-key))
		       ("panther" ,(plain-file "panther.pub" %ssh-public-key)))
   ))

(list (machine
       (operating-system %system)
       (environment managed-host-environment-type)
       (configuration (machine-ssh-configuration
		       (host-name "116.203.150.168")
		       (system "x86_64-linux")
		       (user "root")
		       (identity "id_rsa")
		       (port 22)
		       (allow-downgrades? #t)))))
