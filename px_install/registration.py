from .classes import RemoteConfig


def write_registration_files(config: 'RemoteConfig'):
    with open('/mnt/etc/register_config.sh', 'w') as writer:
        writer.write('export AUTH_SERVER_URL={}'.format(config.host))
        writer.write('export DEVICE_SECURITY={}'.format(config.key_security))
        writer.write('export AUTH_SERVER_DOMAIN={}'.format(config.domain))
        writer.write('export DEVICE_ROLE={}'.format(config.role))
        writer.write('export DEVICE_NAME={}'.format(config.title))
        writer.write('export DEVICE_LOCATION={}'.format(config.location))
        writer.close()
