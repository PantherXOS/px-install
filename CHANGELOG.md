# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.7]

### Fixed

- Workaround failing to install on systems where ext4 partition has `metadata_csum_seed`: enabled https://debbugs.gnu.org/cgi/bugreport.cgi?bug=70480

## [0.1.6]

### Changed

- Thanks to upstream changes, the initial pull on machines without enterprise channel is no longer required; Install is 5x faster now.

## [0.1.5]

### Fixed

- missing module import for new default `lxqt-desktop-service`

## [0.1.4-u]

### Changed

- `.gitlab-ci` fix; no application changes

## [0.1.4]

### Changed

- Replaced `px-desktop-service-type` with `lxqt-desktop-service-type`

## [0.1.3]

### Fixed

- Fixed an issue with partition sizes of 0B
- Unclosed file handle in CLI process execution

### Changed

- Removed deprecated community links
- Use GNOME as default desktop, until LXQt is working again out of the box

## [0.1.2]

### Changed

- Manually reload environment before running system init to avoid channel issues

## [0.1.0]

### Changed

- Generate system configuration from scratch
- Support new varians, including XFCE and Mate desktops

## [0.0.42]

### Fixed

- Use substitute server url for reconfigure step

## [0.0.41]

### Changed

- Adapt config to new module: `px system install` -> `px system config`
- WIP: Automatic installer retry in case of subsitute failure
- WIP: System stats during installation, to understand what's going on

## [0.0.40]

### Fixed

- Use `https://channels.pantherx.org` as online check URL (was `http`)

### Changed

- All channel branches now default to `rolling`

## [0.0.39]

### Fixed

- Use `channels.pantherx.org` as online check URL (was `138.201.123.174`)

## [0.0.38]

### Added

- New `default_system_configuration` provides a `SystemConfiguration` with best defaults

## [0.0.37]

### Added

- new `SystemInstallation` class for consumption by the GUI installer

## [0.0.36]

### Changed

- Automate manual steps Wifi setup

### Fixed

- Some system templates weren't linked-up in the setup file

## [0.0.35]

### Added

- Added support for disk encryption with cryptsetup
- Server OS system config templates

### Fixed

- Fixed an issue where Wifi setup would try to install `wpa_supplicant`

## [0.0.34]

### Changed

- Switch from `register.json` to automated registration with `px-device-identity`

## [0.0.33]

### Changed

- More verbose output when using enterprise config
- No longer delete enterprise config source to ease troubleshooting

## [0.0.32]

### Fixed

- Caught errors that weren't errors: Info written to stdout.

## [0.0.31]

### Fixed

- Fixed an error where partition size `K`; for ex. `1007K` would raise an error
- Actually retry (finally). The correct loop never ran.

### Changed

- The way subprocess related commands are handled
- Reloading disk info during pre-install check has been disabled (too many issues with `lsblk` responses)

## [0.0.30]

### Fixed

- Actually catch the error for retry to work

## [0.0.29]

### Added

- Retry option in case of network failure during pull or init

## [0.0.28]

### Fixed

- Issue related to cpuinfo output missing `brand_raw` info
- Add some timeout for SD-, and HDD-based systems to catch-up

## [0.0.27]

### Fixed

- Added timeouts to allow system to catch-up
- Limited number of times the block device config is read

## [0.0.26]

### Fixed

- Fixed installation on BIOS-types; default to GPT

## [0.0.25]

### Fixed

- `Command 'sgdisk -f 1:ef02 /dev/sda' returned non-zero exit status 3.`
- Fixed an issue that would have `sgdisk` complain about partition overlap

## [0.0.23]

### Fixed

- Exception when checking for Wi-Fi adapters on a system without Wi-Fi adapters

### Added

- Help option accessible via `help` and `--help`

### Changed

- Increased max length for error in debug qr code to 200 characters

## [0.0.22]

### Added

- Helper to configure wireless network
- Helper to determine if the device is connected to the network
- Minimum hard disk size set to larger than 19 GB

## [0.0.21]

### Fixed

- Exception handling when offline; Added QR code to open Wiki

## [0.0.20]

### Fixed

- Tweaked EFI installation scripts

## [0.0.19]

### Fixed

- Issue related to new `BlockDevice` class

## [0.0.18]

### Changed

- More robust error handling
- Better detection of disks and partitions

### Added

- QR code for easy sharing of debugging information
- Online check (packages.pantherx.org)
- More utility tests

## [0.0.17]

### Fixed

- Fixed an issue related to `nvme` disks. The partitions were missing a `p` (`nvme0n11` -> `nvme0n1p1`)

### Changed

- Refactored some code, added some info logs

## [0.0.16]

### Fixed

- `mkfs.ext4` flag `-F` is `-q` instead (ignore previous partition)

## [0.0.15]

### Fixed

- `mkfs` flag `-F` is `-I` instead (ignore previous partition)

## [0.0.14]

### Changed

- Better progress reporting
- Cleaner error output in case of command failure

## [0.0.13]

### Changed

- New approach for process execution (quiet)
- Force mkfs operations to avoid prompt

## [0.0.12]

### Changed

- Convert command arrays to string before execution

## [0.0.11]

### Changed

- All installation related subprocess commands now run directly in the shell (`shell=True`)

## [0.0.10]

### Fixed

- Fixed an issue related to package_data

## [0.0.9]

### Fixed

- Fixed an issue related to creating config dirs

### Changed

- Include swap file created during setup in system config

## [0.0.8]

### Fixed

- Fixed additional issues related to disk formatting

## [0.0.7]

### Fixed

- Fixed an issue related to disk formatting

## [0.0.6]

### Fixed

- Fixed an issue that incorrectly determined whether the system is already installed

## [0.0.5]

### Added

- 15 new tests

### Fixed

- Some casing issues
- Enterprise config download

## [0.0.4]

### Added

- Support for enterprise config
- Documented library use
- Check if supplied options match available template

### Changed

- Channels are saved to `/mnt/etc/guix/channels.scm` by default
- Adapted to new config scheme

## [0.0.3]

### Fixed

- `-h/--hostname: conflicting option string: -h`

## [0.0.2]

### Added

- Added support for SSH key

### Fixed

- Write disk and disk partition to config

## [0.0.1]

### Changed

- Initial commit
