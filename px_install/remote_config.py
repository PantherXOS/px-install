''' Get enterprise device config from S3 by ID '''

from .classes import RemoteConfig

# MOCK for now
# Should read JSON from S3


def get_enterprise_config(id: str):
    config = RemoteConfig(
        'Enterprise',
        'Europe/Berlin',
        'en_US.utf8',
        'PC',
        'Office',
        'DESKTOP',
        'RSA:2048',
        'default',
        'pantherx.org',
        'https://identity.pantherx.org'
    )
    return config
