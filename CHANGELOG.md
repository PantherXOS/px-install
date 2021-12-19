# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
