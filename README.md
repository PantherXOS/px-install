# PantherX Installer

Command line options:

```
-t, --type: Installation type ['DESTOP', 'SERVER', 'ENTERPRISE'] (Default: Desktop)
-f, --firmware: Overwrite automatic detection ['BIOS', 'EFI'] (Default: Automatic)
-h, --hostname: Computer name on the network (Default: panther)
-t, --timezone: Computer time zone (Default: Europe/Berlin)
-l, --locale: Computer locale (Default: en_US.utf8)
-u, --username: First user username (Default: panther)
-p, --password: First user password (Default: pantherx) - should be changed later `passwd <USERNAME>`
-d, --disk: The disk to install to (Default: /dev/sda)
-c, --config: Overwrites all other options; installs from enterprise config settings
```

Defaults:

- 100 MB boot partition
- Remaining for data
- 4GB SWAP file

## Run

Minimal options:

```bash
# This will install the system with everything set to default
px-install
```

All Options

```bash
px-install --type DESKTOP \
	--firmware EFI \
	--hostname panther
	--timezone Europe/Berlin
	--locale en_US.utf8
	--username panther
	--password pantherx
	--disk /dev/sda
```

Enterprise config overwrite (fully automated):

```bash
px install --config abd1uc3z
```

### Minimal bash-based replicate

There's a minimal, all-in-one installer bash script in `scripts/install.sh`. It replicates the python application closely.

## TODO

Support encrypted partitions

```bash
cryptsetup luksFormat /dev/sda2
cryptsetup open --type luks /dev/sda2 my-partition
mkfs.ext4 -L my-root /dev/mapper/my-partition
```
