'''
Write files for registration automation

- register_config.sh is the legacy version for the bash-script based device registration
- register_config.json is RemoteConfig
'''
import json

from .classes import RemoteConfig


def write_registration_files(config: RemoteConfig):
    '''write registration support files to /mnt/etc/...'''
    with open('/mnt/etc/register_config.sh', 'w') as writer:
        writer.write('export AUTH_SERVER_URL={}'.format(config.host))
        writer.write('export DEVICE_SECURITY={}'.format(config.key_security))
        writer.write('export AUTH_SERVER_DOMAIN={}'.format(config.domain))
        writer.write('export DEVICE_ROLE={}'.format(config.role))
        writer.write('export DEVICE_NAME={}'.format(config.title))
        writer.write('export DEVICE_LOCATION={}'.format(config.location))
        writer.close()

    with open('/mnt/etc/register_config.json', 'w') as writer:
        writer.write(json.dumps(config))
        writer.close()
