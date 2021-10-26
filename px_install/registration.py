'''
Write files for registration automation

- register_config.sh is the legacy version for the bash-script based device registration
- register_config.json is RemoteConfig
'''
import json

from .classes import RemoteConfig, EnhancedJSONEncoder


def write_registration_files(config: RemoteConfig, path: str = '/mnt/etc'):
    '''write registration support files to /mnt/etc/...'''
    script = '{}/register_config.sh'.format(path)
    with open(script, 'w') as writer:
        writer.write('export AUTH_SERVER_URL={}'.format(config.host))
        writer.write('export DEVICE_SECURITY={}'.format(config.key_security))
        writer.write('export AUTH_SERVER_DOMAIN={}'.format(config.domain))
        writer.write('export DEVICE_ROLE={}'.format(config.role))
        writer.write('export DEVICE_NAME={}'.format(config.title))
        writer.write('export DEVICE_LOCATION={}'.format(config.location))
        writer.close()

    json_file = '{}/register_config.json'.format(path)
    with open(json_file, 'w') as writer:
        writer.write(json.dumps(config, cls=EnhancedJSONEncoder))
        writer.close()
