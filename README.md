# PantherX Installer

Command line options:

```
-t, --type: Installation type ['DESTOP', 'SERVER', 'ENTERPRISE'] (Default: Desktop)
-f, --firmware: Overwrite automatic detection ['BIOS', 'EFI'] (Default: Automatic)
-hn, --hostname: Computer name on the network (Default: pantherx-7xkp1)
-tz, --timezone: Computer time zone (Default: Europe/Berlin)
-l, --locale: Computer locale (Default: en_US.utf8)
-u, --username: First user username (Default: panther)
-pw, --password: First user password (Default: pantherx) - should be changed later `passwd <USERNAME>`
-d, --disk: The disk to install to (Default: /dev/sda)
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
	--firmware EFI \
	--hostname panther \
	--timezone Europe/Berlin \
	--locale en_US.utf8 \
	--username panther \
	--password pantherx \
	--key ssh-ed25519 AA ... 4QydPg franz \
	--disk /dev/sda
```

Enterprise config overwrite (fully automated):

```bash
px install --config abd1uc3z
```

Refer to `scripts/README.md` for more on enterprise configuration.

### Minimal bash-based replicate

There's a minimal, all-in-one installer bash script in `scripts/install.sh`. It replicates the python application closely. Instead of params it asks for each setting.

## TODO

Support encrypted partitions

```bash
cryptsetup luksFormat /dev/sda2
cryptsetup open --type luks /dev/sda2 my-partition
mkfs.ext4 -L my-root /dev/mapper/my-partition
```

## Use as Library

```
from px_install import installation
intallation(config)
```

The system configuration looks like this:

```
class SystemConfiguration():
    type: str
    firmware: str
    hostname: str
    timezone: str
    locale: str
    username: str
    password: str
    public_key: str
    disk: BlockDevice
```

_TODO: Document Enterprise Config library usage._

## Misc

Also included in the repository:

1. `pantherx-on-hetzner-cloud.sh` -> install PantherX on Hetzner Debian Cloud Server (need to be reconfigured after reboot)
2. `pantherx-on-digitalocean.sh` -> install PantherX on DigitalOcean Debian or Ubuntu Droplet (need to be reconfigured after reboot)

### Tests

```bash
$ python3 -m unittest -v
...
Ran 25 tests in 0.621s
```

### Debugging

Access the latest installer, booted from USB:

```bash
guix package -i python
python3 -m venv venv
source venv/bin/activate
pip3 install https://source.pantherx.org/px-install_v<LATEST_VERSION>.tgz
px-install run
```

### Development

```bash
guix environment --pure \
--ad-hoc python util-linux tar
source venv/bin/activate
pip install .
```
