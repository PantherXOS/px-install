# Scripts

- `install.sh` tries to resemble `px-install` in some form
- `pack-config.sh` generates a new enterprise device configuration

## Enterprise Device Configuration

This is the 2nd iteration of our semi-automated remote installation that supplies all needed information to setup and register a device.

**Important**: The config must match the device (particularly file-systems).

1. Generate config with `./pack-config.sh`
   - Device model (Thinkstation 625, Onlogic, Calmo)
   - Channels file
   - System config gile
   - Auth server url
   - Device security (STANDARD, TPM)
   - Auth server domain
   - Device role
   - Device name
   - Device location
   - Device time zone
2. Upload config to `https://temp.pantherx.org/install`
3. Share ID

The config is provided as `.tgz` file with the following content:

```
channels.scm
config.scm
register.sh
config.json
```

### Automated upload to S3

Set S3 environment variables before running `pack-config.sh`:

```
export AWS_ACCESS_KEY=
export AWS_SECRET_KEY=
export AWS_BUCKET_URL=s3://bucket-address.com/install
```
