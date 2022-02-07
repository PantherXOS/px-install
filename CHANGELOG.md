# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
