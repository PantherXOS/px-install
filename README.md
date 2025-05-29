# PantherX Installer

Command line options:

```
-t, --type: Installation type ['DESTOP', 'SERVER', 'ENTERPRISE'] (Default: Desktop)
-v, --variant: Installation variant ['DEFAULT', 'XFCE', 'MATE', 'GNOME'] (Default: LXQt)
-f, --firmware: Overwrite automatic detection ['BIOS', 'EFI'] (Default: Automatic)
-hn, --hostname: Computer name on the network (Default: pantherx-7xkp1)
-tz, --timezone: Computer time zone (Default: Europe/Berlin)
-l, --locale: Computer locale (Default: en_US.utf8)
-u, --username: First user username (Default: panther)
-pw, --password: First user password (Default: pantherx) - should be changed later `passwd <USERNAME>`
-d, --disk: The disk to install to (Default: /dev/sda)
-de, --disk_encryption: Whether to use full disk encryption (Default: False)
-c, --config: Overwrites all other options; installs from enterprise config settings
```

Defaults:

- EFI: 200 MB boot partition / BIOS: 10 MB boot partition
- Remaining for data
- 4GB SWAP file

## Run

Run with prompts:

```bash
# This will prompt you for all options (RECOMMENDED)
px-install run
```

Run with defaults:

```bash
# This will install the system with everything set to default
px-install
```

Run with command line arguments:

```bash
px-install --type DESKTOP \
    --variant XFCE \
	--firmware EFI \
	--hostname panther \
	--timezone Europe/Berlin \
	--locale en_US.utf8 \
	--username panther \
	--password pantherx \
	--key ssh-ed25519 AA ... 4QydPg franz \
	--disk /dev/sda
	--disk_encryption True
```

If you decide to use full disk encryption (`-de True / --disk_encryption True), you will be prompted for an encryption passphrase a few seconds after the installation has started:

```bash
Enter passphrase for /dev/sda2:
Verify passphrase:
```

Enterprise config overwrite (fully automated):

```bash
px-install --config abd1uc3z
```

Refer to `scripts/README.md` for more on enterprise configuration.

### Helpers

#### Wifi

To aid Wi-Fi setup:

```bash
px-install wifi-setup
```

This will:

1. Check if a valid interface is available
2. Prompt for Wi-Fi config
3. Print commands to activate Wi-Fi

#### Online Check

To check if you're online, do:

```bash
px-install network-check
```

### Minimal bash-based replicate

There's a minimal, all-in-one installer bash script in `scripts/install.sh`. It replicates the python application closely. Instead of params it asks for each setting.