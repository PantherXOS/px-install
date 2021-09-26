# Scripts

- `install.sh` tries to resemble `px-install` in some form
- `pack-config.sh` generates a new enterprise device configuration

## Enterprise Device Configuration

This is the 2nd iteration of our semi-automated remote installation that supplies all needed information to setup and register a device.

1. Generate config with `./pack-config.sh`
2. Upload config to `https://temp.pantherx.org/install`
3. Share ID

The config is provided as `.tgz` file with the following content:

```
channels.scm
config.scm
register.sh
config.json
```
