# Development and Integration Guide

## Use as Library

```
from px_install import installation
intallation(config)
```

The system configuration looks like this:

```python
class SystemConfiguration():
    type: str
	variant: str
    firmware: str
    hostname: str
    timezone: str
    locale: str
    username: str
    password: str
    public_key: str
    disk: BlockDevice
	use_disk_encryption: bool
```

You can also run the installation in steps:

```python
from px_install import SystemInstallation, default_system_configuration

config = default_system_configuration()

# if needed, config can be updated like this
# some or all items will be validated in the future
# if for ex. the hostname is not valid, a ValueError is thrown
config.update_hostname('domain')
config.update_timezone('Europe/Berlin')
# update_ + type, hostname, timezone, locale, username, password, public_key,  use_disk_encryption

install = SystemInstallation(config, is_enterprise_config=False)

# then you can call each manually:
install.format()
install.mount_partition()
install.create_swap()
install.generate_config()
# Not necessary as of April 2024
# install.pull()
install.install()
```

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
# for ex.:
# pip3 install https://source.pantherx.org/px-install_v0.2.2.tgz
px-install run
```

**Note** If `python3 -m venv venv` throws an error like this, just ignore it:

```bash
Error in sitecustomize; set PYTHONVERBOSE for traceback:
ValueError: '/root/.guix-profile/lib/python3.9/site-packages' is not in list
```

### Development

```bash
guix environment --pure \
--ad-hoc python util-linux tar iproute2 coreutils
python3 -m venv venv
source venv/bin/activate
pip install .
```

Quick test:

```bash
rsync -r --exclude={'venv','git','__pycache','tests','scripts'} ../px-install root@<IP>:/root
# rsync -r --exclude "venv" --exclude="git" -e "ssh -p 2222" ../px-install root@127.0.0.1:/root
cd px-install; rm -rf venv; python3 -m venv venv; source venv/bin/activate; pip3 install .; px-install run
```
